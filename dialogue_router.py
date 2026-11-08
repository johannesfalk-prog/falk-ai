import os
from flask import Blueprint, request, jsonify
from openai import OpenAI
from supabase import create_client

dialogue_bp = Blueprint("dialogue", __name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"[ERROR] Misslyckades att initiera Supabase-klient: {e}")

openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def fetch_user_memories(user_id: str, limit: int = 5):
    """Hämtar de mest relevanta långtidsminnena för användaren från Supabase."""
    if not supabase:
        print("[WARN] fetch_user_memories: Supabase-klient är None (saknar ENV-variabler?)")
        return [], "Supabase client not initialized (missing SUPABASE_URL/KEY on Render)"
    try:
        res = supabase.table("falk_memory").select("category, content, importance_score").eq("user_id", user_id).order("importance_score", desc=True).limit(limit).execute()
        data = res.data if res.data else []
        return data, None
    except Exception as e:
        err_msg = str(e)
        print(f"[WARN] Kunde inte hämta minnen från Supabase: {err_msg}")
        return [], err_msg

def process_turn(user_id: str, user_message: str, session_id: str = None):
    # 1. Hämta långtidsminnen för användaren med felhantering
    memories, db_error = fetch_user_memories(user_id)
    memory_context = ""
    if memories:
        memory_lines = [f"- [{m.get('category', 'Memory')}]: {m.get('content')}" for m in memories]
        memory_context = "\n\n[ANVÄNDARENS SPARADE LÅNGTIDSMINNEN (The Mentor Mind™)]\n" + "\n".join(memory_lines)

    # 2. Konstruera Falk System Prompt enligt Falk Bible & Playbook
    system_prompt = (
        "Du är Falk, den digitala mentorn bakom WAYJS.\n"
        "Du har ett fågelperspektiv på människors liv och hjälper dem att navigera med större klarhet, bättre omdöme och hållbara beslut.\n"
        "Du är lugn, varm, nyfiken, intelligent, tålmodig och ärlig.\n"
        "Följ Wayjs Dialogue: Trygghet -> Förståelse -> Utforskande -> Perspektiv -> Klarhet -> Handling -> Reflektion.\n"
        "Bekräfta upplevelsen utan att ge snabba klyschiga råd eller föreläsningar."
        + memory_context
    )

    # 3. Anropa OpenAI GPT-4o
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7
        )
        reply_text = response.choices[0].message.content
        return {
            "status": "success",
            "reply": reply_text,
            "stage": "TRYGGHET",
            "engine": "Falk Core Engine v1.0.0 (OpenAI GPT-4o)",
            "user_id": user_id,
            "debug_memories_count": len(memories),
            "debug_db_error": db_error
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@dialogue_bp.route("/turn", methods=["POST"])
def dialogue_turn():
    data = request.get_json() or {}
    user_id = data.get("user_id", "default_user")
    message = data.get("message", "")
    session_id = data.get("session_id")
    
    result = process_turn(user_id, message, session_id)
    if result.get("status") == "error":
        return jsonify(result), 500
    return jsonify(result), 200
