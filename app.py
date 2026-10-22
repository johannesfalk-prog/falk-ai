import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import jwt
from groq import Groq
from openai import OpenAI
from memory_engine import store_memory, get_relevant_memories, should_store_memory

app = Flask(__name__)
CORS(app)

# Rensa miljövariabler
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip().strip('"').strip("'")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip().strip('"').strip("'")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "").strip().strip('"').strip("'")
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "").strip()

# Initiera klienter
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

SYSTEM_PROMPT = """You are FALK, an elite Socratic Cognitive Behavioral Therapy (CBT) AI guide.
YOUR CORE RULE: Never lecture, never give numbered lists, and never preach generic self-help advice.

Operating Principles:
1. Validate briefly: Acknowledge the user's emotion/statement in 1 short sentence.
2. Socratic Probe: Ask EXACTLY ONE sharp, open-ended question that highlights cognitive distortions or challenges assumptions.
3. Length Limit: Keep your entire response under 60 words.
4. Language: Always reply in Swedish.
"""

def extract_user_id(req):
    auth_header = req.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        print("[AUTH DEBUG]: Ingen Bearer-header hittades.", flush=True)
        return "00000000-0000-0000-0000-000000000000", "FREE"
    
    token = auth_header.split(" ")[1]
    
    if not SUPABASE_JWT_SECRET:
        print("[AUTH DEBUG]: SUPABASE_JWT_SECRET saknas helt i miljövariabler!", flush=True)
        return "00000000-0000-0000-0000-000000000000", "FREE"

    try:
        # Läs av token-header dynamiskt för att förhindra InvalidAlgorithmError
        header = jwt.get_unverified_header(token)
        token_alg = header.get("alg", "HS256")
        
        # Inkludera alla tillåtna Supabase-algoritmer
        allowed_algs = list(set([token_alg, "HS256", "HS384", "HS512", "RS256"]))

        decoded = jwt.decode(
            token, 
            SUPABASE_JWT_SECRET, 
            algorithms=allowed_algs, 
            options={"verify_aud": False}
        )
        user_id = decoded.get("sub", "00000000-0000-0000-0000-000000000000")
        print(f"[AUTH SUCCESS]: Token godkänd för User ID: {user_id}", flush=True)
        return user_id, "PRO"

    except jwt.ExpiredSignatureError:
        print("[JWT ERROR]: Token har gått ut (ExpiredSignatureError).", flush=True)
    except jwt.InvalidSignatureError:
        print("[JWT ERROR]: Ogiltig signatur! SUPABASE_JWT_SECRET matchar inte Supabase.", flush=True)
    except Exception as e:
        print(f"[JWT ERROR]: Dekodning misslyckades: {type(e).__name__} - {str(e)}", flush=True)

    return "00000000-0000-0000-0000-000000000000", "FREE"

@app.route("/")
def index():
    return render_template("index.html", supabase_url=SUPABASE_URL, supabase_anon_key=SUPABASE_ANON_KEY)

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json or {}
        user_message = data.get("message", "").strip()
        if not user_message:
            return jsonify({"error": "Meddelandet kan inte vara tomt"}), 400

        user_id, tier = extract_user_id(request)
        memories = []

        if tier == "PRO" and user_id != "00000000-0000-0000-0000-000000000000":
            try:
                memories = get_relevant_memories(user_id, user_message)
                if should_store_memory(user_message):
                    store_memory(user_id, user_message)
            except Exception as mem_err:
                print(f"[MEMORY SAFELY ISOLATED]: {mem_err}", flush=True)

        memory_context = ""
        if memories:
            memory_context = "\nRelevant historisk kontext om användaren:\n" + "\n".join([f"- {m}" for m in memories])

        ai_response = None
        used_provider = None

        # 1. Försök med Groq SDK
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
                except Exception as g_err:
                    print(f"[GROQ FAIL {model_name}]: {g_err}", flush=True)

        # 2. Resilient Fallback till OpenAI (gpt-4o-mini)
        if not ai_response and openai_client:
            try:
                print("[FALLBACK]: Kopplar om till OpenAI gpt-4o-mini...", flush=True)
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
                print(f"[OPENAI FALLBACK FAIL]: {o_err}", flush=True)

        if ai_response:
            return jsonify({
                "response": ai_response,
                "tier": tier,
                "memories_retrieved": len(memories),
                "provider": used_provider
            })
        else:
            return jsonify({"error": "Både Groq och OpenAI fallback misslyckades."}), 500

    except Exception as e:
        print(f"[CHAT EXCEPTION]: {e}", flush=True)
        return jsonify({"error": f"Internt serverfel: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
