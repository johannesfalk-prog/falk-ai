import os, json
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

def process_turn(user_id=None, session_id=None, message=None, user_message=None, **kwargs):
    """Kärnfunktion för dialogbearbetning, kompasspoäng, journal och capabilities."""
    actual_message = (message or user_message or "").strip()
    
    if not user_id or not actual_message:
        return {"status": "error", "message": "Missing user_id or message"}

    system_prompt = """Du är Falk, den digitala mentorn bakom WAYJS.
Du har ett fågelperspektiv på människors liv och hjälper dem att navigera med större klarhet, bättre omdöme och hållbara beslut.
Utvärdera samtalet och svara i JSON-format med följande nycklar:
- reply: Ditt svar till användaren (lugn, varm, nyfiken, eftertänksam röst).
- stage: Aktuell samtalsfas (TRYGGHET, FÖRSTÅELSE, UTFORSKANDE, PERSPEKTIV, KLARHET, HANDLING, REFLEKTION).
- compass_score: Ett objekt med direction, balance, action, reflection (heltal 0-100).
- new_chapter: Ett objekt med chapter_number, chapter_title, summary (skapa ALLTID ett kapitel vid nya insikter, annars null).


Du MÅSTE utvärdera följande 4 mänskliga förmågor utifrån användarens meddelande:
- Självinsikt (0-3 poäng)
- Mod (0-3 poäng)
- Resiliens (0-3 poäng)
- Kommunikation (0-3 poäng)

Ge höga poäng (2-3) ENDAST till förmågor som tydligt tränades eller uppvisades. Ge 0 poäng till de som inte berördes.

Du SKALL returnera ett giltigt JSON-objekt med följande nycklar:
{
  "stage": "UTFORSKANDE",
  "reply": "Ditt mentorssvar här...",
  "compass_score": {"direction": 50, "balance": 50, "action": 50, "reflection": 50},
  "capabilities_trained": {
    "Självinsikt": 0,
    "Mod": 0,
    "Resiliens": 0,
    "Kommunikation": 0
  }
}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": actual_message}
    ]

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.7
        )
        res_json = json.loads(response.choices[0].message.content)

        reply = res_json.get("reply", "Jag lyssnar. Berätta mer.")
        stage = res_json.get("stage", "TRYGGHET")
        compass_score = res_json.get("compass_score", {"direction": 50, "balance": 50, "action": 50, "reflection": 50})
        new_chapter = res_json.get("new_chapter")

        # 1. Uppdatera falk_compass_score i Supabase
        if supabase:
            try:
                existing_score = supabase.table("falk_compass_score").select("*").eq("user_id", user_id).execute()
                score_payload = {
                    "user_id": user_id,
                    "direction_score": compass_score.get("direction", 50),
                    "balance_score": compass_score.get("balance", 50),
                    "action_score": compass_score.get("action", 50),
                    "reflection_score": compass_score.get("reflection", 50)
                }
                if existing_score.data and len(existing_score.data) > 0:
                    supabase.table("falk_compass_score").update(score_payload).eq("user_id", user_id).execute()
                else:
                    supabase.table("falk_compass_score").insert(score_payload).execute()
            except Exception as e:
                print(f"⚠️ Warning: Compass score save failed: {e}")

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
        trained_caps = res_json.get("capabilities_trained", {}) if isinstance(res_json, dict) else {}
        capabilities_map = {
            "Självinsikt": trained_caps.get("Självinsikt", 0),
            "Mod": trained_caps.get("Mod", 0),
            "Resiliens": trained_caps.get("Resiliens", 0),
            "Kommunikation": trained_caps.get("Kommunikation", 0)
        }
        
        for cap_name, increment in capabilities_map.items():
            try:
                inc_val = int(increment) if isinstance(increment, (int, float)) else 0
            except ValueError:
                inc_val = 0

            cap_res = supabase.table("falk_capabilities").select("*").eq("user_id", user_id).eq("capability_name", cap_name).execute()
            
            if cap_res.data:
                current_score = cap_res.data[0].get("score_level", 50)
                new_score = min(100, current_score + inc_val)
                supabase.table("falk_capabilities").update({
                    "score_level": new_score,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }).eq("id", cap_res.data[0]["id"]).execute()
            else:
                initial_score = 50 + inc_val
                supabase.table("falk_capabilities").insert({
                    "user_id": user_id,
                    "capability_name": cap_name,
                    "capability_category": "Personal",
                    "score_level": initial_score,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }).execute()
        

        return {
            "status": "success",
            "reply": reply,
            "stage": stage,
            "compass_score": compass_score,
            "journal_created": journal_created,
            "cap_errors": cap_errors
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}

@dialogue_bp.route("/turn", methods=["POST"])
def dialogue_turn():
    data = request.json or {}
    user_id = data.get("user_id")
    session_id = data.get("session_id")
    msg = data.get("message") or data.get("user_message", "")
    res = process_turn(user_id=user_id, session_id=session_id, message=msg)
    status_code = 200 if res.get("status") == "success" else 500
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
