import os
import uuid
import json
import threading
from flask import Flask, request, jsonify, make_response, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from supabase import create_client, Client
from groq import Groq
import openai
from playbooks import detect_playbook_llm
from prompt_engine import FalkPromptEngine

load_dotenv()

app = Flask(__name__, template_folder="templates")
app.secret_key = os.getenv("FLASK_SECRET_KEY", "falk_secret_fallback")

CORS(app, supports_credentials=True, origins=["http://localhost:5001", "http://127.0.0.1:5001"])

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

USER_COMPASS_STATE = {
    "default": {"personal": 75, "relation": 65, "work": 82, "life": 58}
}
GUEST_MESSAGE_COUNTS = {}
MAX_GUEST_MESSAGES = 6

def get_session_identity():
    user_id = request.headers.get("X-User-ID")
    guest_uuid = request.cookies.get("guest_uuid")
    if not guest_uuid and not user_id:
        guest_uuid = str(uuid.uuid4())
    return user_id, guest_uuid

def async_post_conversation_worker(user_id, guest_uuid, user_message, falk_response):
    try:
        session_key = user_id or guest_uuid or "default"
        current_scores = USER_COMPASS_STATE.get(session_key, USER_COMPASS_STATE["default"].copy())

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

        USER_COMPASS_STATE[session_key] = current_scores

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
    except Exception as e:
        print(f"❌ Worker error: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/gdpr/consent', methods=['POST'])
def gdpr_consent():
    data = request.json or {}
    if not data.get("is_18_plus"):
        return jsonify({"error": "Du måste vara 18 år eller äldre."}), 403
    
    user_id, guest_uuid = get_session_identity()
    resp = make_response(jsonify({"status": "success", "message": "Samtycke registrerat."}))
    if guest_uuid and not request.cookies.get("guest_uuid"):
        resp.set_cookie("guest_uuid", guest_uuid, httponly=True, max_age=31536000, samesite='Lax')
    return resp, 200

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    user_id, guest_uuid = get_session_identity()
    session_key = user_id or guest_uuid or "default"
    scores = USER_COMPASS_STATE.get(session_key, USER_COMPASS_STATE["default"])
    guest_count = GUEST_MESSAGE_COUNTS.get(guest_uuid, 0) if not user_id else 0
    
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

    # Giltig UUID-sträng som fungerar med Supabase UUID-kolumner
    new_user_id = str(uuid.uuid4())

    if guest_uuid in USER_COMPASS_STATE:
        USER_COMPASS_STATE[new_user_id] = USER_COMPASS_STATE.pop(guest_uuid)
    else:
        USER_COMPASS_STATE[new_user_id] = USER_COMPASS_STATE["default"].copy()

    if guest_uuid in GUEST_MESSAGE_COUNTS:
        GUEST_MESSAGE_COUNTS.pop(guest_uuid)

    try:
        supabase.table("user_memories").update({"user_id": new_user_id}).eq("guest_uuid", guest_uuid).execute()
        supabase.table("chat_sessions").update({"user_id": new_user_id}).eq("guest_uuid", guest_uuid).execute()
    except Exception as e:
        print(f"⚠️ Migreringsvarning i Supabase: {e}")

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
    modifier_type = data.get("modifier_type")

    if not user_message:
        return jsonify({"error": "Meddelande saknas."}), 400

    user_id, guest_uuid = get_session_identity()

    if not user_id:
        current_count = GUEST_MESSAGE_COUNTS.get(guest_uuid, 0)
        if current_count >= MAX_GUEST_MESSAGES:
            session_key = guest_uuid or "default"
            scores = USER_COMPASS_STATE.get(session_key, USER_COMPASS_STATE["default"])
            return jsonify({
                "error": "GUEST_LIMIT_REACHED",
                "response": "Vi har nått gränsen för vår kostnadsfria provsession (6 meddelanden). Skapa ditt konto för att låsa upp obegränsad tillgång och bevara din utveckling.",
                "limit_reached": True,
                "compass_scores": scores
            }), 402
        GUEST_MESSAGE_COUNTS[guest_uuid] = current_count + 1

    if not session_id:
        session_payload = {
            "user_id": user_id if user_id else None,
            "guest_uuid": guest_uuid if not user_id else None,
            "title": user_message[:30] + "..."
        }
        try:
            s_res = supabase.table("chat_sessions").insert(session_payload).execute()
            if s_res.data:
                session_id = s_res.data[0]["id"]
        except Exception as e:
            print(f"⚠️ Supabase session error: {e}")

    active_playbook = detect_playbook_llm(groq_client, user_message)

    context_str = ""
    try:
        emb_res = openai_client.embeddings.create(input=user_message, model="text-embedding-3-small")
        query_vector = emb_res.data[0].embedding
        rpc_res = supabase.rpc("match_user_memories", {
            "query_embedding": query_vector,
            "match_threshold": 0.3,
            "match_count": 3
        }).execute()
        if rpc_res.data:
            memories = [m['content'] for m in rpc_res.data]
            context_str = "- " + "\n- ".join(memories)
    except Exception as e:
        print(f"⚠️ RAG-fel: {e}")

    system_content = FalkPromptEngine.build_system_prompt(
        active_playbook=active_playbook,
        modifier_type=modifier_type,
        RAG_context=context_str
    )

    messages_payload = [{"role": "system", "content": system_content}, {"role": "user", "content": user_message}]

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=messages_payload,
            model="openai/gpt-oss-120b",
            temperature=0.2
        )
        falk_response = chat_completion.choices[0].message.content.strip()
    except Exception as e:
        return jsonify({"error": f"Groq API Error: {str(e)}"}), 500

    threading.Thread(
        target=async_post_conversation_worker,
        args=(user_id, guest_uuid, user_message, falk_response)
    ).start()

    resp = make_response(jsonify({
        "response": falk_response, 
        "session_id": session_id,
        "guest_messages_left": max(0, MAX_GUEST_MESSAGES - GUEST_MESSAGE_COUNTS.get(guest_uuid, 0)) if not user_id else 999
    }))
    if guest_uuid and not request.cookies.get("guest_uuid"):
        resp.set_cookie("guest_uuid", guest_uuid, httponly=True, max_age=31536000, samesite='Lax')
    return resp, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
