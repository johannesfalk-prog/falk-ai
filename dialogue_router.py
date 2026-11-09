import os
from flask import Blueprint, request, jsonify
from supabase import create_client, Client
import openai

dialogue_bp = Blueprint("dialogue", __name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"⚠️ Supabase init warning: {e}")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

def process_turn(user_id, session_id, user_message):
    """Kärnfunktion för dialogbearbetning, kompasspoäng, journal och capabilities."""
    if not user_id or not user_message:
        return {"status": "error", "message": "Missing user_id or message"}, 400

    system_prompt = """Du är Falk, den digitala mentorn bakom WAYJS.
Du har ett fågelperspektiv på människors liv och hjälper dem att navigera med större klarhet, bättre omdöme och hållbara beslut.
Utvärdera samtalet och svara i JSON-format med följande nycklar:
- reply: Ditt svar till användaren (lugn, varm, nyfiken, eftertänksam röst).
- stage: Aktuell samtalsfas (TRYGGHET, FÖRSTÅELSE, UTFORSKANDE, PERSPEKTIV, KLARHET, HANDLING, REFLEKTION).
- compass_score: Ett objekt med direction, balance, action, reflection (heltal 0-100).
- new_chapter: Ett objekt med chapter_number, chapter_title, summary (om en ny insikt eller beslut nåtts, annars null).
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.7
        )
        import json
        res_json = json.loads(response.choices[0].message.content)

        reply = res_json.get("reply", "Jag lyssnar. Berätta mer.")
        stage = res_json.get("stage", "TRYGGHET")
        compass_score = res_json.get("compass_score", {"direction": 50, "balance": 50, "action": 50, "reflection": 50})
        new_chapter = res_json.get("new_chapter")

        # 1. Uppdatera falk_compass_score i Supabase
        if supabase:
            try:
                supabase.table("falk_compass_score").upsert({
                    "user_id": user_id,
                    "direction_score": compass_score.get("direction", 50),
                    "balance_score": compass_score.get("balance", 50),
                    "action_score": compass_score.get("action", 50),
                    "reflection_score": compass_score.get("reflection", 50)
                }, on_conflict="user_id").execute()
            except Exception as e:
                print(f"⚠️ Warning: Compass score upsert failed: {e}")

        # 2. Uppdatera falk_compass_journal i Supabase
        journal_created = False
        if supabase and new_chapter and isinstance(new_chapter, dict) and new_chapter.get("chapter_title"):
            try:
                supabase.table("falk_compass_journal").insert({
                    "user_id": user_id,
                    "chapter_number": new_chapter.get("chapter_number", 1),
                    "chapter_title": new_chapter.get("chapter_title", "Insikt"),
                    "summary": new_chapter.get("summary", "")
                }).execute()
                journal_created = True
            except Exception as e:
                print(f"⚠️ Warning: Journal insert failed: {e}")

        # 3. FALK HUMAN GROWTH FRAMEWORK (falk_capabilities)
        if supabase:
            capabilities = ["Självinsikt", "Mod", "Resiliens", "Kommunikation"]
            for cap in capabilities:
                try:
                    cap_res = supabase.table("falk_capabilities").select("*").eq("user_id", user_id).eq("capability_name", cap).execute()
                    current_score = 50
                    if cap_res.data and len(cap_res.data) > 0:
                        current_score = cap_res.data[0].get("score_level", 50)
                    new_score = min(100, current_score + 2)
                    supabase.table("falk_capabilities").upsert({
                        "user_id": user_id,
                        "capability_name": cap,
                        "score_level": new_score
                    }, on_conflict="user_id,capability_name").execute()
                except Exception as cap_err:
                    print(f"⚠️ Warning: Could not update capability {cap}: {cap_err}")

        return {
            "status": "success",
            "reply": reply,
            "stage": stage,
            "compass_score": compass_score,
            "journal_created": journal_created
        }, 200

    except Exception as e:
        return {"status": "error", "error": str(e)}, 500

@dialogue_bp.route("/turn", methods=["POST"])
def dialogue_turn():
    data = request.json or {}
    user_id = data.get("user_id")
    session_id = data.get("session_id")
    user_message = data.get("message", "").strip()
    res, status_code = process_turn(user_id, session_id, user_message)
    return jsonify(res), status_code

@dialogue_bp.route("/state/<user_id>", methods=["GET"])
def get_user_wos_state(user_id):
    if not supabase:
        return jsonify({"status": "error", "message": "Supabase connection missing"}), 500
    try:
        score_res = supabase.table("falk_compass_score").select("*").eq("user_id", user_id).execute()
        score_data = score_res.data[0] if score_res.data and len(score_res.data) > 0 else {
            "direction_score": 50, "balance_score": 50, "action_score": 50, "reflection_score": 50
        }

        journal_res = supabase.table("falk_compass_journal").select("*").eq("user_id", user_id).order("chapter_number", desc=False).execute()
        journal_data = journal_res.data if journal_res.data else []

        cap_res = supabase.table("falk_capabilities").select("*").eq("user_id", user_id).execute()
        cap_data = cap_res.data if cap_res.data else []

        return jsonify({
            "status": "success",
            "compass_score": {
                "direction": score_data.get("direction_score", 50),
                "balance": score_data.get("balance_score", 50),
                "action": score_data.get("action_score", 50),
                "reflection": score_data.get("reflection_score", 50)
            },
            "journal": journal_data,
            "capabilities": cap_data
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500
