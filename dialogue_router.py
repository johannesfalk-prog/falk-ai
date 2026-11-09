# Falk Core Engine v1.0.0 - Production Gold Release (Hardened WOS Logic)
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

def update_compass_score(user_id: str, direction: int, balance: int, action: int, reflection: int):
    if not supabase:
        print("[WARN] Supabase saknas för update_compass_score")
        return False
    try:
        data = {
            "user_id": user_id,
            "direction_score": direction,
            "balance_score": balance,
            "action_score": action,
            "reflection_score": reflection
        }
        res = supabase.table("falk_compass_score").upsert(data, on_conflict="user_id").execute()
        print(f"📊 Compass Score uppdaterad för user {user_id}: D:{direction} B:{balance} A:{action} R:{reflection}")
        return True
    except Exception as e:
        print(f"[ERROR] Kunde inte uppdatera Compass Score i Supabase: {e}")
        return False

def add_journal_chapter(user_id: str, title: str, summary: str):
    if not supabase:
        print("[WARN] Supabase saknas för add_journal_chapter")
        return False
    try:
        res = supabase.table("falk_compass_journal").select("chapter_number").eq("user_id", user_id).order("chapter_number", desc=True).limit(1).execute()
        next_ch = 1
        if res.data and len(res.data) > 0:
            next_ch = res.data[0]["chapter_number"] + 1
        
        supabase.table("falk_compass_journal").insert({
            "user_id": user_id,
            "chapter_number": next_ch,
            "chapter_title": title,
            "summary": summary
        }).execute()
        print(f"📖 Nytt Journal-kapitel sparat: Kapitel {next_ch} - {title}")
        return True
    except Exception as e:
        print(f"[ERROR] Kunde inte spara journal-kapitel i Supabase: {e}")
        return False

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
            supabase.table("falk_memory").insert({
                "user_id": user_id,
                "category": data.get("category", "Reflections"),
                "content": data.get("content", ""),
                "importance_score": data.get("importance_score", 3)
            }).execute()
            print(f"✅ Auto-memory sparat: {data.get('content')}")
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
        "Du ser världen från ovan (Bird's Eye View). Du hjälper människor att navigera med större klarhet, bättre omdöme och hållbara beslut.\n"
        "Du utvärderar också användarens dynamiska utvecklingsindex (The Compass Score: Riktning, Balans, Handling, Reflektion, skalan 0-100).\n"
        "Du SKALL också identifiera om användaren gör ett framsteg, fattar ett viktiga livsbeslut eller sätter en ny riktning. Om så är fallet, sätter du new_journal_chapter.create till true och ger ett kapitelnamn och sammanfattning.\n"
        "Returnera ditt svar i ENDAST giltigt JSON-format enligt nedan:\n"
        "{\n"
        "  \"stage\": \"TRYGGHET|FÖRSTÅELSE|UTFORSKANDE|PERSPEKTIV|KLARHET|HANDLING|REFLEKTION\",\n"
        "  \"reply\": \"Ditt mentorala svar här...\",\n"
        "  \"compass_score\": {\"direction\": 60, \"balance\": 55, \"action\": 65, \"reflection\": 70},\n"
        "  \"new_journal_chapter\": {\"create\": true, \"title\": \"Kapitelns titel\", \"summary\": \"Kort sammanfattning av framsteget\"}\n"
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
        compass = data.get("compass_score", {"direction": 50, "balance": 50, "action": 50, "reflection": 50})
        journal = data.get("new_journal_chapter", {})

        save_message_to_history(session_id, user_id, "user", message)
        save_message_to_history(session_id, user_id, "assistant", reply_text)

        # Skriv exekvering till Supabase
        update_compass_score(user_id, compass.get("direction", 50), compass.get("balance", 50), compass.get("action", 50), compass.get("reflection", 50))
        
        # Om skapa journal om create är True eller om titeln är angiven
        if journal.get("create") or journal.get("title"):
            add_journal_chapter(user_id, journal.get("title", "Ett nytt steg"), journal.get("summary", "Insikt under samtalet."))

        extract_and_save_new_memories(user_id, message)

        return {
            "status": "success",
            "reply": reply_text,
            "stage": stage_text,
            "compass_score": compass,
            "journal_created": bool(journal.get("create") or journal.get("title")),
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
    data = request.get_json() or {}
    session_id = data.get("session_id")
    if not session_id or not supabase:
        return jsonify({"status": "error", "message": "Missing session_id or database connection"}), 400
    try:
        supabase.table("falk_messages").delete().eq("session_id", session_id).execute()
        return jsonify({"status": "success", "message": f"Session {session_id} history cleared successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


@dialogue_bp.route("/state/<user_id>", methods=["GET"])
def get_user_wos_state(user_id):
    if not supabase:
        return jsonify({"status": "error", "message": "Supabase connection missing"}), 500
    try:
        # Hämta senast sparade score
        score_res = supabase.table("falk_compass_score").select("*").eq("user_id", user_id).execute()
        score_data = score_res.data[0] if score_res.data and len(score_res.data) > 0 else {
            "direction_score": 50, "balance_score": 50, "action_score": 50, "reflection_score": 50
        }

        # Hämta journal-kapitel
        journal_res = supabase.table("falk_compass_journal").select("*").eq("user_id", user_id).order("chapter_number", desc=False).execute()
        journal_data = journal_res.data if journal_res.data else []

        return jsonify({
            "status": "success",
            "compass_score": {
                "direction": score_data.get("direction_score", 50),
                "balance": score_data.get("balance_score", 50),
                "action": score_data.get("action_score", 50),
                "reflection": score_data.get("reflection_score", 50)
            },
            "journal": journal_data
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500
