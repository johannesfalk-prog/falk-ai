import os
import json
import traceback
from typing import List, Optional, Any, Dict
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel
from openai import OpenAI
from supabase import create_client, Client
from dotenv import load_dotenv

from prompt_builder import build_falk_system_prompt
from dialogue_router import (
    get_or_create_session, 
    evaluate_stage_transition, 
    update_session_stage,
    save_message,
    fetch_chat_history
)
from evaluator_agent import evaluate_falk_response
from safety_guardrails import evaluate_safety_and_crisis
from vector_memory import retrieve_rag_memories, store_memory_vector
from exercise_library import get_library_cards
from pdf_exporter import generate_session_pdf_html

load_dotenv()

app = FastAPI(title="FALK Engine - Robust Beta Platform")

# Oskuggad felhantering för att eliminera anonyma 500-krascher
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = str(exc)
    error_trace = traceback.format_exc()
    print(f"\n[KRITISKT BACKENDFEL] Anrop till {request.url} misslyckades:")
    print(error_trace)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": error_msg,
            "path": str(request.url.path)
        }
    )

app.mount("/static", StaticFiles(directory="static"), name="static")

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

supabase_url = os.getenv("SUPABASE_URL", "")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
supabase: Any = None
if supabase_url.startswith("http://") or supabase_url.startswith("https://"):
    try:
        supabase = create_client(supabase_url, supabase_key)
    except Exception as e:
        print(f"[Varning] Supabase client init misslyckades: {e}")

class DialogueTurnRequest(BaseModel):
    user_id: str
    session_id: str
    user_message: str

class ExportPdfRequest(BaseModel):
    session_id: str
    user_id: str

ADMIN_TOKEN = "falk_admin_2026"

@app.get("/")
async def serve_canvas():
    return FileResponse("static/index.html")

@app.get("/admin")
async def serve_admin():
    return FileResponse("static/admin.html")

@app.get("/api/library/cards")
async def api_get_cards(category: Optional[str] = None):
    return {"cards": get_library_cards(category)}

@app.post("/api/session/export-pdf")
async def api_export_pdf(req: ExportPdfRequest):
    raw_messages, _ = fetch_chat_history(req.session_id, limit=100)
    if not raw_messages:
        # Fallback om inga meddelanden hittas i DB ännu
        raw_messages = [
            {"role": "user", "content": "Startade session."},
            {"role": "assistant", "content": "Välkommen till Falk."}
        ]
    html_content = generate_session_pdf_html(req.session_id, raw_messages)
    return HTMLResponse(content=html_content)

@app.get("/api/admin/metrics")
async def api_admin_metrics(token: str = Query(...)):
    if token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Ogiltig Admin Token.")
    
    stats = {"total_sessions": 0, "total_messages": 0, "safety_interventions": 0, "active_users": 0}
    recent_logs = []

    if supabase:
        try:
            rpc_res = supabase.rpc("get_admin_dashboard_stats").execute()
            if rpc_res.data:
                stats = rpc_res.data[0]
            
            msgs_res = supabase.table("chat_messages").select("*").order("created_at", desc=True).limit(20).execute()
            for m in msgs_res.data or []:
                recent_logs.append({
                    "session_id": m.get("session_id"),
                    "user_id": m.get("user_id"),
                    "user_message": m.get("content", ""),
                    "is_safe": "Självmordslinjen" not in m.get("content", "")
                })
        except Exception as e:
            print(f"[Admin API Varning] {e}")

    return {"stats": stats, "recent_logs": recent_logs}

@app.post("/api/dialogue/turn")
async def dialogue_turn(req: DialogueTurnRequest, bg_tasks: BackgroundTasks):
    is_safe, safety_response, safety_meta = evaluate_safety_and_crisis(req.user_message)
    if not is_safe:
        bg_tasks.add_task(save_message, req.session_id, req.user_id, "user", req.user_message)
        bg_tasks.add_task(save_message, req.session_id, req.user_id, "assistant", safety_response)
        return {
            "session_id": req.session_id,
            "previous_stage": "TRYGGHET",
            "active_stage": "TRYGGHET",
            "stage_advanced": False,
            "evaluator_gate_check": {
                "passed": False,
                "violated_gates": ["SAFETY_GUARDRAIL"],
                "feedback": safety_meta.get("reason"),
                "rewrite_triggered": False
            },
            "falk_response": safety_response,
            "calibration_proposal": None
        }

    session = get_or_create_session(req.session_id, req.user_id)
    current_stage = session.get("current_stage", "TRYGGHET")
    turn_count = session.get("turn_count", 1)

    bg_tasks.add_task(save_message, req.session_id, req.user_id, "user", req.user_message)
    raw_messages, formatted_history = fetch_chat_history(req.session_id, limit=14)

    target_stage, stage_advanced = evaluate_stage_transition(
        current_stage=current_stage,
        user_message=req.user_message,
        chat_history=formatted_history
    )

    rag_context = retrieve_rag_memories(req.user_id, req.user_message, limit=2)
    base_system_prompt = build_falk_system_prompt(user_id=req.user_id, current_dialogue_stage=target_stage, user_message=req.user_message)
    system_prompt = f"{base_system_prompt}\n{rag_context}\n\nSTRIKT FORMATREGEL: Avsluta med MAX EN (1) utforskande fråga."

    gpt_messages = [{"role": "system", "content": system_prompt}]
    for m in raw_messages:
        gpt_messages.append({"role": m["role"], "content": m["content"]})

    draft_response = openai_client.chat.completions.create(
        model="gpt-4o", messages=gpt_messages, temperature=0.3
    ).choices[0].message.content

    passed, final_response, eval_res = evaluate_falk_response(
        proposed_response=draft_response, user_message=req.user_message, active_stage=target_stage
    )

    rewrite_triggered = False
    if not passed:
        rewrite_triggered = True
        rewrite_prompt = f"{system_prompt}\n\nDITT FÖRRA UTKAST UNDERKÄNDES.\nFeedback: {eval_res.get('feedback')}\nSkriv om svaret."
        gpt_messages[0] = {"role": "system", "content": rewrite_prompt}
        final_response = openai_client.chat.completions.create(
            model="gpt-4o", messages=gpt_messages, temperature=0.2
        ).choices[0].message.content

    bg_tasks.add_task(update_session_stage, req.session_id, target_stage, turn_count)
    bg_tasks.add_task(save_message, req.session_id, req.user_id, "assistant", final_response)

    return {
        "session_id": req.session_id,
        "previous_stage": current_stage,
        "active_stage": target_stage,
        "stage_advanced": stage_advanced,
        "evaluator_gate_check": {
            "passed": passed,
            "violated_gates": eval_res.get("violated_gates", []),
            "feedback": eval_res.get("feedback", ""),
            "rewrite_triggered": rewrite_triggered
        },
        "falk_response": final_response,
        "calibration_proposal": None
    }
