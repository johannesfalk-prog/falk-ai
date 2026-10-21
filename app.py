import os, time
from collections import defaultdict
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from groq import Groq
from memory_engine import store_memory, get_relevant_memories, should_store_memory, supabase

load_dotenv()

app = Flask(__name__)
CORS(app)

groq_api_key = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=groq_api_key, timeout=12.0) if groq_api_key else None

RATE_LIMIT_STORE = defaultdict(list)
LIGHT_LIMIT_PER_MINUTE = 5

def is_rate_limited(ip_address: str) -> bool:
    now = time.time()
    RATE_LIMIT_STORE[ip_address] = [t for t in RATE_LIMIT_STORE[ip_address] if now - t < 60]
    if len(RATE_LIMIT_STORE[ip_address]) >= LIGHT_LIMIT_PER_MINUTE:
        return True
    RATE_LIMIT_STORE[ip_address].append(now)
    return False

def verify_supabase_jwt(auth_header: str):
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    try:
        user_response = supabase.auth.get_user(token)
        if user_response and user_response.user:
            return user_response.user.id
    except Exception as e:
        print(f"[AUTH ERROR]: Ogiltigt JWT: {e}", flush=True)
    return None

SYSTEM_PROMPT_PRO = """You are FALK PRO, an autonomous cognitive mentor grounded in Socratic dialogue and Cognitive Behavioral Therapy (CBT).
You have access to the user's long-term memory.
1. SILENTLY AUDIT FOR COGNITIVE DISTORTIONS (Catastrophizing, All-or-Nothing, Mind Reading, Emotional Reasoning, Overgeneralization).
2. IF DISTORTION IS PRESENT: Ask EXACTLY ONE sharp, challenging Socratic question.
3. IF NO DISTORTION: Provide a concise, grounded response integrating retrieved context memories.
4. TONE: Grounded, direct, clear Swedish."""

SYSTEM_PROMPT_LIGHT = """You are FALK LIGHT, a fast Socratic CBT auditor.
1. SILENTLY AUDIT FOR COGNITIVE DISTORTIONS in the user's input.
2. IF DISTORTION IS PRESENT: Ask EXACTLY ONE sharp Socratic question examining their assumption.
3. IF NO DISTORTION: Provide a concise 1-2 sentence response.
4. TONE: Grounded, direct, clear Swedish."""

@app.route("/")
def index():
    return render_template(
        "index.html",
        supabase_url=os.getenv("SUPABASE_URL", ""),
        supabase_anon_key=os.getenv("SUPABASE_ANON_KEY", "")
    )

@app.route("/chat", methods=["POST"])
def chat():
    client_ip = request.remote_addr or "127.0.0.1"
    auth_header = request.headers.get("Authorization", "")
    
    # Om auth_header saknas eller är ogiltig blir authenticated_user_id = None (faller tillbaka till LIGHT)
    authenticated_user_id = verify_supabase_jwt(auth_header)
    is_pro = bool(authenticated_user_id)

    data = request.get_json() or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "Message is required"}), 400
    if len(message) > 2000:
        return jsonify({"error": "Message exceeds maximum length of 2000 characters"}), 400

    if not is_pro and is_rate_limited(client_ip):
        print(f"[SECURITY]: IP {client_ip} rate-limited på LIGHT tier.", flush=True)
        return jsonify({
            "error": "Minutkvot uppnådd för gratisversionen. Vänta 60 sekunder eller logga in på PRO.",
            "retry_after_seconds": 60
        }), 429

    memories = []
    
    if is_pro:
        user_id = authenticated_user_id
        print(f"\n[PRO TIER VERIFIERAD VIA JWT]: User UUID: {user_id}", flush=True)
        try:
            memories = get_relevant_memories(user_id, message)
            print(f" -> [PRO MEMORY]: Hämtade {len(memories)} minnen via HF API.", flush=True)
        except Exception as e:
            print(f" -> [PRO MEMORY ERROR]: {e}", flush=True)

        if should_store_memory(message):
            try:
                store_memory(user_id, message, category="reflection")
                print(" -> [PRO MEMORY]: Minne sparat till Supabase via HF API.", flush=True)
            except Exception as e:
                print(f" -> [PRO STORE ERROR]: {e}", flush=True)

        memory_context = "\n".join([f"- {m}" for m in memories]) if memories else "Inga tidigare minnen."
        full_system_prompt = f"{SYSTEM_PROMPT_PRO}\n\n[RELEVANT USER MEMORIES]:\n{memory_context}"
        models_to_try = ["openai/gpt-oss-20b", "gemma2-9b-it"]

    else:
        print(f"\n[LIGHT TIER]: IP: {client_ip} (Anonym förfrågan)", flush=True)
        full_system_prompt = SYSTEM_PROMPT_LIGHT
        models_to_try = ["openai/gpt-oss-20b", "gemma2-9b-it", "mixtral-8x7b-32768"]

    if not groq_client:
        return jsonify({"error": "GROQ_API_KEY missing from server environment"}), 500

    response_text = None
    errors = []

    for model in models_to_try:
        try:
            print(f" -> Exekverar LLM ({model})...", flush=True)
            completion = groq_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": full_system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.6,
                max_tokens=512
            )
            response_text = completion.choices[0].message.content
            print(f" -> [SUCCESS]: Svar genererat från {model}.", flush=True)
            break
        except Exception as e:
            print(f" -> [LLM ERROR] {model}: {e}", flush=True)
            errors.append(f"{model}: {str(e)}")

    if not response_text:
        return jsonify({"error": "All LLM model attempts failed", "details": errors}), 500

    return jsonify({
        "response": response_text,
        "tier": "PRO" if is_pro else "LIGHT",
        "memories_retrieved": len(memories)
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)
