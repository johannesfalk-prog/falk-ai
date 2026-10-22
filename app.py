import os
import traceback
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from supabase import create_client, Client
from groq import Groq
from openai import OpenAI
from memory_engine import store_memory, get_relevant_memories, should_store_memory

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip().strip('"').strip("'")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip().strip('"').strip("'")
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip().strip('"').strip("'")
if not SUPABASE_SERVICE_KEY:
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_ANON_KEY", "").strip().strip('"').strip("'")

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY) if SUPABASE_URL and SUPABASE_SERVICE_KEY else None

SYSTEM_PROMPT = """You are FALK, an elite Socratic Cognitive Behavioral Therapy (CBT) AI guide.
YOUR CORE RULE: Never lecture, never give numbered lists, and never preach generic self-help advice.

Operating Principles:
1. Validate briefly: Acknowledge the user's emotion/statement in 1 short sentence.
2. Direct Clarity Safety Valve: If the user explicitly asks for clarification ("what perspective?", "what do you mean?", "who?"), answer directly in 1 sentence BEFORE asking your probe. Do NOT evade direct questions.
3. Socratic Probe: Ask EXACTLY ONE sharp, open-ended question that highlights cognitive distortions or challenges assumptions.
4. Length Limit: Keep your entire response under 60 words.
5. Language: Always reply in Swedish.
"""

def extract_user_tier(req):
    auth_header = req.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return "00000000-0000-0000-0000-000000000000", "FREE"
    
    token = auth_header.split(" ")[1]
    if not supabase_client:
        return "00000000-0000-0000-0000-000000000000", "FREE"

    try:
        user_response = supabase_client.auth.get_user(token)
        if user_response and user_response.user:
            user_id = user_response.user.id
            try:
                prof = supabase_client.table("profiles").select("tier").eq("id", user_id).single().execute()
                if prof.data and prof.data.get("tier") == "PRO":
                    return user_id, "PRO"
            except Exception as e:
                print(f"[PROFILE LOOKUP FAIL]: {e}", flush=True)

            return user_id, "FREE"
    except Exception as e:
        print(f"[AUTH ERROR]: {e}", flush=True)

    return "00000000-0000-0000-0000-000000000000", "FREE"

def get_rate_limit_key():
    user_id, _ = extract_user_tier(request)
    if user_id != "00000000-0000-0000-0000-000000000000":
        return user_id
    return get_remote_address()

def get_rate_limit_val():
    _, tier = extract_user_tier(request)
    if tier == "PRO":
        return "60 per day"
    return "5 per day"

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per day"],
    storage_uri="memory://"
)

@app.errorhandler(429)
def ratelimit_handler(e):
    user_id, tier = extract_user_tier(request)
    limit_str = "60 meddelanden" if tier == "PRO" else "5 meddelanden"
    return jsonify({
        "error": f"Du har nått din dagliga gräns på {limit_str}. Välkommen tillbaka imorgon eller uppgradera till PRO.",
        "limit_reached": True,
        "tier": tier
    }), 429

@app.route("/")
def index():
    return render_template("index.html", supabase_url=SUPABASE_URL, supabase_anon_key=SUPABASE_ANON_KEY)

@app.route("/chat", methods=["POST"])
@limiter.limit(get_rate_limit_val, key_func=get_rate_limit_key)
def chat():
    try:
        data = request.json or {}
        user_message = data.get("message", "").strip()
        if not user_message:
            return jsonify({"error": "Meddelandet kan inte vara tomt"}), 400

        user_id, tier = extract_user_tier(request)
        memories = []

        if tier == "PRO" and user_id != "00000000-0000-0000-0000-000000000000":
            try:
                memories = get_relevant_memories(user_id, user_message)
                if should_store_memory(user_message):
                    store_memory(user_id, user_message)
            except Exception as mem_err:
                print(f"[RAG ERROR]: {mem_err}", flush=True)

        memory_context = ""
        if memories:
            memory_context = "\nRelevant historisk kontext om användaren:\n" + "\n".join([f"- {m}" for m in memories])

        ai_response = None
        used_provider = None

        if groq_client:
            for model_name in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]:
                try:
                    completion = groq_client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": f"{memory_context}\n\n{user_message}"}
                        ],
                        temperature=0.5,
                        max_tokens=150
                    )
                    ai_response = completion.choices[0].message.content
                    if ai_response:
                        used_provider = f"Groq ({model_name})"
                        break
                except Exception:
                    pass

        if not ai_response and openai_client:
            try:
                completion = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"{memory_context}\n\n{user_message}"}
                    ],
                    temperature=0.5,
                    max_tokens=150
                )
                ai_response = completion.choices[0].message.content
                used_provider = "OpenAI (gpt-4o-mini)"
            except Exception as o_err:
                print(f"[OPENAI FAIL]: {o_err}", flush=True)

        if ai_response:
            return jsonify({
                "response": ai_response,
                "tier": tier,
                "memories_retrieved": len(memories),
                "provider": used_provider
            })
            
        return jsonify({"error": "Ingen AI-leverantör kunde svara."}), 500

    except Exception as e:
        return jsonify({"error": f"Internt serverfel: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
