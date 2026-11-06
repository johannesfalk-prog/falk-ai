import os
import uuid
import json
import threading
import logging
from flask import Flask, request, jsonify, make_response, session
from flask_cors import CORS
from dotenv import load_dotenv
from supabase import create_client, Client
from groq import Groq
import openai
from prompt_engine import ModularPromptEngine as FalkPromptEngine, analyze_intent_and_phase_fast
from state_machine import FalkStateMachine

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("falk-backend")

app = Flask(__name__, template_folder="templates")
app.secret_key = os.getenv("FLASK_SECRET_KEY", "falk_secret_fallback")

raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000,http://127.0.0.1:3000,http://localhost:5001,http://127.0.0.1:5001,https://falk-backend.onrender.com")
allowed_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

CORS(app, supports_credentials=True, resources={r"/api/*": {
    "origins": [
        "https://wayjs.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    "allow_headers": ["Content-Type", "Authorization", "Cookie"],
    "methods": ["GET", "POST", "OPTIONS"]
}})

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

MAX_GUEST_MESSAGES = 6
DEFAULT_SCORES = {"personal": 75, "relation": 65, "work": 82, "life": 58}

def get_session_identity():
    # Säker utläsning av session
    user_id = None
    try:
        user_id = session.get("user_id")
    except Exception:
        pass
    
    # Dual-Layer för guest_uuid: JSON Payload (ITP-säker) -> Cookie -> Ny UUID
    req_data = request.get_json(silent=True) or {}
    guest_uuid = req_data.get("guest_uuid") or request.cookies.get("guest_uuid")
    
    if not guest_uuid:
        guest_uuid = str(uuid.uuid4())
        
    return user_id, guest_uuid

def load_session_metadata(session_id):
    """Hämtar hela metadata-objektet för en session från Supabase."""
    if not session_id:
        return {}
    try:
        res = supabase.table("chat_sessions").select("metadata").eq("id", session_id).execute()
        if res.data and len(res.data) > 0:
            meta = res.data[0].get("metadata")
            if isinstance(meta, str):
                return json.loads(meta)
            elif isinstance(meta, dict):
                return meta
    except Exception as e:
        logger.error(f"⚠️ Supabase metadata load error: {e}")
    return {}

def load_compass_state(user_id, guest_uuid):
    try:
        query = supabase.table("chat_sessions").select("metadata").order("created_at", desc=True).limit(1)
        if user_id:
            res = query.eq("user_id", user_id).execute()
        elif guest_uuid:
            res = query.eq("guest_uuid", guest_uuid).execute()
        else:
            return DEFAULT_SCORES.copy()

        if res.data and len(res.data) > 0 and res.data[0].get("metadata"):
            meta = res.data[0]["metadata"]
            if isinstance(meta, str):
                meta = json.loads(meta)
            if "compass_scores" in meta:
                return meta["compass_scores"]
    except Exception as e:
        logger.error(f"⚠️ Supabase load error: {e}")
    return DEFAULT_SCORES.copy()

def get_guest_message_count(guest_uuid):
    if not guest_uuid:
        return 0
    try:
        res = supabase.table("chat_sessions").select("id", count="exact").eq("guest_uuid", guest_uuid).execute()
        return res.count if res.count is not None else len(res.data or [])
    except Exception as e:
        logger.error(f"⚠️ Supabase count error: {e}")
        return 0

def async_post_conversation_worker(user_id, guest_uuid, session_id, user_message, falk_response):
    logger.info(f"🔄 Bakgrundsarbetare startad för session: {session_id}")
    try:
        current_meta = load_session_metadata(session_id)
        current_scores = current_meta.get("compass_scores", load_compass_state(user_id, guest_uuid))
        history_list = current_meta.get("history_log", [])

        # Lägg till senaste turen i historikloggen
        history_list.append({"role": "user", "content": user_message})
        history_list.append({"role": "assistant", "content": falk_response})

        analysis_prompt = f"""
        Analysera följande dialog för FALK/WAYJS:
        Användare: "{user_message}"
        Falk: "{falk_response}"
        Nuvarande kompass: {current_scores}

        Returnera JSON:
        {{
          "insight": "Mening eller null",
          "compass_deltas": {{"personal": 0, "relation": 0, "work": 0, "life": 0}}
        }}
        """

        res = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": analysis_prompt}],
            model="openai/gpt-oss-120b",
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        output = json.loads(res.choices[0].message.content)

        deltas = output.get("compass_deltas", {})
        for k in ["personal", "relation", "work", "life"]:
            d = int(deltas.get(k, 0))
            current_scores[k] = max(0, min(100, current_scores[k] + d))

        if session_id:
            updated_meta = {
                "compass_scores": current_scores,
                "history_log": history_list[-12:]  # Spara de senaste 12 meddelandena
            }
            supabase.table("chat_sessions").update({
                "metadata": json.dumps(updated_meta)
            }).eq("id", session_id).execute()
            logger.info(f"✅ Supabase session metadata & historik uppdaterad för session {session_id}")

        insight = output.get("insight")
        if insight and insight.lower() != "null":
            emb_res = openai_client.embeddings.create(input=insight, model="text-embedding-3-small")
            embedding_vector = emb_res.data[0].embedding
            payload = {
                "user_id": user_id if user_id else None,
                "guest_uuid": guest_uuid if not user_id else None,
                "content": insight,
                "embedding": embedding_vector,
                "category": "general"
            }
            supabase.table("user_memories").insert(payload).execute()
            logger.info("✅ Nytt användarminne lagrat i Supabase.")
    except Exception as e:
        logger.error(f"❌ Worker error: {e}")

@app.route('/')
def index():
    return jsonify({"status": "online", "service": "Falk AI Engine", "version": "1.3"}), 200

@app.route('/api/gdpr/consent', methods=['POST'])
def gdpr_consent():
    data = request.json or {}
    if not data.get("is_18_plus"):
        return jsonify({"error": "Du måste vara 18 år eller äldre."}), 403
    
    user_id, guest_uuid = get_session_identity()
    resp = make_response(jsonify({"status": "success", "message": "Samtycke registrerat."}))
    if guest_uuid and not request.cookies.get("guest_uuid"):
        resp.set_cookie("guest_uuid", guest_uuid, httponly=True, max_age=31536000, samesite='None', secure=True)
    return resp, 200

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    user_id, guest_uuid = get_session_identity()
    scores = load_compass_state(user_id, guest_uuid)
    guest_count = get_guest_message_count(guest_uuid) if not user_id else 0
    
    return jsonify({
        "user_badge": "GUEST" if not user_id else "PREMIUM",
        "guest_messages_left": max(0, MAX_GUEST_MESSAGES - guest_count),
        "compass_scores": scores
    }), 200

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json or {}
    email = data.get("email", "").strip()
    user_id, guest_uuid = get_session_identity()

    if not email:
        return jsonify({"error": "E-postadress krävs."}), 400

    new_user_id = str(uuid.uuid4())

    try:
        supabase.table("user_memories").update({"user_id": new_user_id}).eq("guest_uuid", guest_uuid).execute()
        supabase.table("chat_sessions").update({"user_id": new_user_id}).eq("guest_uuid", guest_uuid).execute()
    except Exception as e:
        logger.warning(f"⚠️ Migreringsvarning i Supabase: {e}")

    return jsonify({
        "status": "success",
        "message": "Konto skapat och din Kompass har sparats!",
        "user_id": new_user_id
    }), 200

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json or {}
    user_message = data.get("message", "").strip()
    session_id = data.get("session_id")
    raw_history = data.get("history")

    if not user_message:
        return jsonify({"error": "Meddelande saknas."}), 400

    user_id, guest_uuid = get_session_identity()

    if not user_id:
        current_count = get_guest_message_count(guest_uuid)
        if current_count >= MAX_GUEST_MESSAGES:
            scores = load_compass_state(user_id, guest_uuid)
            return jsonify({
                "error": "GUEST_LIMIT_REACHED",
                "response": "Vi har nått gränsen för vår kostnadsfria provsession (6 meddelanden). Skapa ditt konto för att låsa upp obegränsad tillgång och bevara din utveckling.",
                "limit_reached": True,
                "compass_scores": scores
            }), 402

    if not session_id:
        current_scores = load_compass_state(user_id, guest_uuid)
        session_payload = {
            "user_id": user_id if user_id else None,
            "guest_uuid": guest_uuid if not user_id else None,
            "title": user_message[:30] + "...",
            "metadata": json.dumps({"compass_scores": current_scores, "history_log": []})
        }
        try:
            s_res = supabase.table("chat_sessions").insert(session_payload).execute()
            if s_res.data:
                session_id = s_res.data[0]["id"]
        except Exception as e:
            logger.error(f"⚠️ Supabase session error: {e}")

    # RESOLVA HISTORIK: 1) Från request payload 2) Fallback från Supabase session metadata
    effective_history = []
    if isinstance(raw_history, list) and len(raw_history) > 0:
        effective_history = raw_history
    elif session_id:
        db_meta = load_session_metadata(session_id)
        effective_history = db_meta.get("history_log", [])

    # Formatera historiksträng till 7-fasdetektorn
    history_str = ""
    if len(effective_history) > 0:
        formatted_turns = []
        for turn in effective_history[-6:]:
            role = "Användare" if turn.get("role") == "user" else "Falk"
            formatted_turns.append(f"{role}: {turn.get('content', '')}")
        history_str = "\n".join(formatted_turns)

    # Detektera kris och säkerhetsgränser FÖRST
    # Använd den snabba konsoliderade motorn (Kris, Fas & Playbook i 1 anrop)
    intent_data = analyze_intent_and_phase_fast(groq_client, user_message, history_str)
    crisis_status = intent_data.get('crisis_status', 'NONE')
    current_phase = intent_data.get('phase', 1)
    active_playbook = intent_data.get('playbook', 'GENERELL')

    # Automatisk fasklassificering med garanterad historikkontext

    context_str = ""
    try:
        emb_res = openai_client.embeddings.create(input=user_message, model="text-embedding-3-small")
        query_vector = emb_res.data[0].embedding
        rpc_res = supabase.rpc("match_user_memories", {
            "query_embedding": query_vector,
            "match_threshold": 0.3,
            "match_count": 3,
            "p_guest_uuid": guest_uuid,
            "p_user_id": user_id if user_id else None
        }).execute()
        if rpc_res.data:
            memories = [m['content'] for m in rpc_res.data]
            context_str = "- " + "\n- ".join(memories)
    except Exception as e:
        logger.error(f"⚠️ RAG-fel: {e}")

    current_scores = load_compass_state(user_id, guest_uuid)

    system_content = FalkPromptEngine.compile_5_layer_prompt(
        compass_scores=current_scores,
        playbook=active_playbook,
        RAG_context=context_str,
                phase=current_phase,
        crisis_status=crisis_status
    )

    messages_payload = [{"role": "system", "content": system_content}]
    for turn in effective_history[-6:]:
        messages_payload.append({"role": turn.get("role", "user"), "content": turn.get("content", "")})
    messages_payload.append({"role": "user", "content": user_message})

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=messages_payload,
            model="openai/gpt-oss-120b",
            temperature=0.2
        )
        falk_response = chat_completion.choices[0].message.content.strip()
        falk_response = FalkPromptEngine.deterministic_post_processing(falk_response, user_message)
    except Exception as e:
        return jsonify({"error": f"Groq API Error: {str(e)}"}), 500

    worker_thread = threading.Thread(
        target=async_post_conversation_worker,
        args=(user_id, guest_uuid, session_id, user_message, falk_response)
    )
    worker_thread.daemon = True
    worker_thread.start()

    guest_left = max(0, MAX_GUEST_MESSAGES - (get_guest_message_count(guest_uuid) + 1)) if not user_id else 999
    resp = make_response(jsonify({
        "response": falk_response, 
        "session_id": session_id,
        "current_phase": current_phase,
        "guest_messages_left": guest_left
    }))
    if guest_uuid and not request.cookies.get("guest_uuid"):
        resp.set_cookie("guest_uuid", guest_uuid, httponly=True, max_age=31536000, samesite='None', secure=True)
    return resp, 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=False)


@app.errorhandler(Exception)
def handle_exception(e):
    import traceback
    logger.error(f"💥 UNHANDLED RUNTIME CRASH: {str(e)}")
    logger.error(traceback.format_exc())
    return jsonify({
        "error": str(e),
        "type": type(e).__name__,
        "traceback": traceback.format_exc().splitlines()[-3:]
    }), 500