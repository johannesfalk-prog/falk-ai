import os, json
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
    """Hämtar de mest relevanta långtidsminnena för användaren från Supabase."""
    if not supabase:
        return []
    try:
        res = supabase.table("falk_memory").select("category, content, importance_score").eq("user_id", user_id).order("importance_score", desc=True).limit(limit).execute()
        return res.data if res.data else []
    except Exception as e:
        print(f"[WARN] Kunde inte hämta minnen: {e}")
        return []

def save_user_memory(user_id: str, category: str, content: str, importance_score: int = 3):
    """Sparar ett nytt långtidsminne för användaren i Supabase."""
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
    """Analyserar om användarens meddelande innehåller viktig information att spara."""
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
    # 1. Hämta befintliga långtidsminnen
    memories = fetch_user_memories(user_id)
    memory_context = ""
    if memories:
        memory_lines = [f"- [{m.get('category', 'Memory')}]: {m.get('content')}" for m in memories]
        memory_context = "\n\n[ANVÄNDARENS SPARADE LÅNGTIDSMINNEN (The Mentor Mind™)]\n" + "\n".join(memory_lines)

    # 2. Falk System Prompt (Falk Bible Kap 11)
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
                {"role": "user", "content": message}
            ],
            temperature=0.7
        )
        reply_text = response.choices[0].message.content

        # 4. Asynkron/Bakgrundskörning för att utvärdera om nya minnen ska sparas
        extract_and_save_new_memories(user_id, message)

        return {
            "status": "success",
            "reply": reply_text,
            "stage": "TRYGGHET",
            "engine": "Falk Core Engine v1.0.0 (OpenAI GPT-4o)",
            "user_id": user_id
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
