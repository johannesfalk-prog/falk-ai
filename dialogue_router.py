import os
import json
import uuid
from typing import Dict, Any, Tuple, List
from openai import OpenAI
from supabase import create_client, Client
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("[Kritiskt] OPENAI_API_KEY saknas i miljövariablerna eller .env-filen.")
    return OpenAI(api_key=api_key)

supabase_url = os.getenv("SUPABASE_URL", "")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY", "")
supabase: Any = None
if supabase_url.startswith("http://") or supabase_url.startswith("https://"):
    try:
        supabase = create_client(supabase_url, supabase_key)
    except Exception as e:
        print(f"[Varning] Supabase kunde inte initieras i router: {e}")

STAGES = [
    "TRYGGHET",
    "FORSTAELSE",
    "UTFORSKANDE",
    "PERSPEKTIV",
    "KLARHET",
    "HANDLING",
    "REFLEKTION"
]

def sanitize_uuid(val: str) -> str:
    if not val:
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, "falk.default"))
    try:
        return str(uuid.UUID(val))
    except ValueError:
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"falk.{val}"))

def get_or_create_session(session_id: str, user_id: str) -> Dict[str, Any]:
    safe_session_id = sanitize_uuid(session_id)
    safe_user_id = sanitize_uuid(user_id)
    
    if not supabase:
        return {"session_id": safe_session_id, "user_id": safe_user_id, "current_stage": "TRYGGHET", "turn_count": 1}

    try:
        res = supabase.table("dialogue_sessions").select("*").eq("session_id", safe_session_id).execute()
        if res.data and len(res.data) > 0:
            return res.data[0]
        
        new_session = {
            "session_id": safe_session_id,
            "user_id": safe_user_id,
            "current_stage": "TRYGGHET",
            "turn_count": 1
        }
        supabase.table("dialogue_sessions").insert(new_session).execute()
        return new_session
    except Exception as e:
        print(f"[Fel] Sessionshantering misslyckades: {e}")
        return {"session_id": safe_session_id, "user_id": safe_user_id, "current_stage": "TRYGGHET", "turn_count": 1}

def save_message(session_id: str, user_id: str, role: str, content: str):
    try:
        data = {
            "session_id": session_id,
            "user_id": user_id,
            "role": role,
            "content": content
        }
        res = supabase.table("dialogue_messages").insert(data).execute()
        return res
    except Exception as e:
        print(f"[KRITISKT DB-FEL i save_message]: {e}")
        raise e


def fetch_chat_history(session_id: str, limit: int = 14) -> Tuple[List[Dict[str, str]], str]:
    if not supabase:
        return [], ""

    safe_session_id = sanitize_uuid(session_id)
    try:
        res = supabase.table("dialogue_messages") \
            .select("role, content") \
            .eq("session_id", safe_session_id) \
            .order("created_at", desc=False) \
            .limit(limit) \
            .execute()
        
        messages = res.data if res.data else []
        formatted_history = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in messages])
        return messages, formatted_history
    except Exception as e:
        print(f"[Fel] Kunde inte hämta samtalshistorik: {e}")
        return [], ""

def evaluate_stage_transition(current_stage: str, user_message: str, chat_history: str) -> Tuple[str, bool]:
    classifier_prompt = f"""
Du är State Machine-utvärderaren för Falk (WAYJS Dialogue Router).
Aktuell fas just nu: [{current_stage}]

DIN UPPGIFT: Analysera om samtalet har mognat för att ta ett kliv till nästa fas i THE WAYJS DIALOGUE.

KRITERIER FÖR FASÖVERGÅNGAR:
1. TRYGGHET -> FORSTAELSE: Användaren har uttryckt sitt initiala tillstånd och börjar ge kontext.
2. FORSTAELSE -> UTFORSKANDE: Användaren beskriver orsakssamband, relationer eller egna mönster ("Jag ser att jag alltid...").
3. UTFORSKANDE -> PERSPEKTIV: Användaren söker nya synvinklar, utmanar sina antaganden eller ber om vägledning om nästa steg.
4. PERSPEKTIV -> KLARHET: Användaren sammanfattar sin egen insikt eller landar i sin Nordstjärna/värdering.
5. KLARHET -> HANDLING: Användaren utformar eller efterfrågar en konkret handling.
6. HANDLING -> REFLEKTION: Användaren utvärderar ett genomfört steg, summerar sina insikter eller delar vad de tar med sig från samtalet.

Regel: Skifta fas NÄR användarens meddelande uppfyller kriterierna för nästa nivå. Stå inte kvar i gammal fas om användaren börjar analyser mönster eller söka perspektiv.

Returnera ENDAST JSON:
{{
  "target_stage": "EN_AV_DE_7_FASERNA",
  "reason": "Kort motivering till fasval"
}}
"""

    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": classifier_prompt},
                {"role": "user", "content": f"Samtalshistorik:\n{chat_history}\n\nSenaste användarmeddelande:\n{user_message}"}
            ],
            temperature=0.0
        )
        res = json.loads(response.choices[0].message.content)
        target_stage = res.get("target_stage", current_stage)
        reason = res.get("reason", "")
        
        print(f"[Router Debug] Nuvarande: {current_stage} -> Ny: {target_stage} | Orsak: {reason}")
        
        if target_stage not in STAGES:
            target_stage = current_stage

        current_idx = STAGES.index(current_stage)
        target_idx = STAGES.index(target_stage)

        if target_idx < current_idx:
            target_stage = current_stage

        stage_advanced = target_idx > current_idx
        return target_stage, stage_advanced
    except Exception as e:
        print(f"[Fel] Utvärdering av fas misslyckades: {e}")
        return current_stage, False

def update_session_stage(session_id: str, new_stage: str, turn_count: int):
    if not supabase:
        return
    safe_session_id = sanitize_uuid(session_id)
    try:
        supabase.table("dialogue_sessions").update({
            "current_stage": new_stage,
            "turn_count": turn_count + 1,
            "updated_at": "now()"
        }).eq("session_id", safe_session_id).execute()
    except Exception as e:
        print(f"[Fel] Kunde inte uppdatera session i Supabase: {e}")
