import os, json, uuid
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
        print(f"[ERROR] Supabase init failed: {e}")

openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def fetch_user_memories(user_id: str, limit: int = 5):
    if not supabase:
        return []
    try:
        res = supabase.table("falk_memory").select("category, content, importance_score").eq("user_id", user_id).order("importance_score", desc=True).limit(limit).execute()
        return res.data if res.data else []
    except Exception as e:
        print(f"[WARN] Kunde inte hämta minnen: {e}")
        return []

def fetch_session_history(session_id: str, limit: int = 10):
    if not supabase or not session_id:
        return []
    try:
        res = supabase.table("falk_messages").select("role, content").eq("session_id", session_id).order("created_at", desc=False).limit(limit).execute()
        return res.data if res.data else []
    except Exception as e:
        print(f"[WARN] Kunde inte hämta sessionshistorik: {e}")
        return []

def save_message_to_history(session_id: str, user_id: str, role: str, content: str):
    if not supabase or not session_id:
        return
    try:
        supabase.table("falk_messages").insert({
            "session_id": session_id,
            "user_id": user_id,
            "role": role,
            "content": content
        }).execute()
    except Exception as e:
        print(f"[WARN] Kunde inte spara meddelande i historik: {e}")

def save_user_memory(user_id: str, category: str, content: str, importance_score: int = 3):
    if not supabase:
        return
    try:
        supabase.table("falk_memory").insert({
            "user_id": user_id,
            "category": category,
            "content": content,
            "importance_score": importance_score
        }).execute()
        print(f"✅ Auto-memory sparat [{category}]: {content}")
    except Exception as e:
        print(f"[WARN] Kunde inte spara minne: {e}")

def extract_and_save_new_memories(user_id: str, user_message: str):
    if not openai_client or not supabase:
        return
    try:
        extraction_prompt = (
            "Du är minnesmodulen för Falk Engine. Analysera användarens meddelande.\n"
            "Om meddelandet innehåller en tydlig Nordstjärna, Värdering, Livsmål eller Viktigt Mönster, extrahera det.\n"
            "Returnera ENDAST giltig JSON i formatet:\n"
            "{\"should_save\": true, \"category\": \"NorthStar|Values|LifeGoals|Patterns\", \"content\": \"kort sammanfattning\", \"importance_score\": 4}\n"
            "Om inget viktigt finns att spara, returnera: {\"should_save\": false}"
        )
        res = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": extraction_prompt},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        data = json.loads(res.choices[0].message.content)
        if data.get("should_save"):
            save_user_memory(
                user_id=user_id,
                category=data.get("category", "Reflections"),
                content=data.get("content", ""),
                importance_score=data.get("importance_score", 3)
            )
    except Exception as e:
        print(f"[WARN] Minnesextraktion misslyckades: {e}")

def process_turn(user_id: str, message: str, session_id: str = None):
    if not session_id:
        session_id = str(uuid.uuid4())

    memories = fetch_user_memories(user_id)
    history = fetch_session_history(session_id)

    memory_context = ""
    if memories:
        memory_lines = [f"- [{m.get('category', 'Memory')}]: {m.get('content')}" for m in memories]
        memory_context = "\n\n[ANVÄNDARENS SPARADE LÅNGTIDSMINNEN (The Mentor Mind™)]\n" + "\n".join(memory_lines)

    system_prompt = (
        "Du är Falk, den digitala mentorn bakom WAYJS.\n"
        "Du har ett fågelperspektiv på människors liv och hjälper dem att navigera med större klarhet, bättre omdöme och hållbara beslut.\n"
        "Du är lugn, varm, nyfiken, intelligent, tålmodig och ärlig.\n"
        "Du följer Wayjs Dialogue: TRYGGHET -> FÖRSTÅELSE -> UTFORSKANDE -> PERSPEKTIV -> KLARHET -> HANDLING -> REFLEKTION.\n"
        "Du bedömer vilken fas i samtalet du befinner dig i utifrån historiken och användarens meddelande, och svarar i linje med den fasen.\n"
        "Returnera ditt svar i ENDAST giltigt JSON-format enligt nedan:\n"
        "{\n"
        "  \"stage\": \"TRYGGHET|FÖRSTÅELSE|UTFORSKANDE|PERSPEKTIV|KLARHET|HANDLING|REFLEKTION\",\n"
        "  \"reply\": \"Ditt mentorala svar här...\"\n"
        "}"
        + memory_context
    )

    messages_payload = [{"role": "system", "content": system_prompt}]
    for msg in history:
        messages_payload.append({"role": msg["role"], "content": msg["content"]})
    messages_payload.append({"role": "user", "content": message})

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages_payload,
            response_format={"type": "json_object"},
            temperature=0.7
        )
        data = json.loads(response.choices[0].message.content)
        reply_text = data.get("reply", "")
        stage_text = data.get("stage", "TRYGGHET")

        save_message_to_history(session_id, user_id, "user", message)
        save_message_to_history(session_id, user_id, "assistant", reply_text)

        extract_and_save_new_memories(user_id, message)

        return {
            "status": "success",
            "reply": reply_text,
            "stage": stage_text,
            "engine": "Falk Core Engine v1.0.0 (OpenAI GPT-4o)",
            "user_id": user_id,
            "session_id": session_id
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
    
    result = process_turn(user_id=user_id, message=message, session_id=session_id)
    if result.get("status") == "error":
        return jsonify(result), 500
    return jsonify(result), 200

@dialogue_bp.route("/reset", methods=["POST"])
def dialogue_reset():
    """Rensar sessionshistoriken för en viss session."""
    data = request.get_json() or {}
    session_id = data.get("session_id")
    if not session_id or not supabase:
        return jsonify({"status": "error", "message": "Missing session_id or database connection"}), 400
    try:
        supabase.table("falk_messages").delete().eq("session_id", session_id).execute()
        return jsonify({"status": "success", "message": f"Session {session_id} history cleared successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500
