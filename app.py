import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import jwt
from memory_engine import store_memory, get_relevant_memories, should_store_memory

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

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
        return "00000000-0000-0000-0000-000000000000", "FREE"
    token = auth_header.split(" ")[1]
    if SUPABASE_JWT_SECRET:
        try:
            decoded = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"], options={"verify_aud": False})
            user_id = decoded.get("sub", "00000000-0000-0000-0000-000000000000")
            return user_id, "PRO"
        except Exception as e:
            print(f"[JWT DECODE ERROR]: {e}", flush=True)
    return "00000000-0000-0000-0000-000000000000", "FREE"

@app.route("/")
def index():
    return render_template(
        "index.html",
        supabase_url=SUPABASE_URL,
        supabase_anon_key=SUPABASE_ANON_KEY
    )

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "Meddelandet kan inte vara tomt"}), 400

    user_id, tier = extract_user_id(request)
    memories = []
    
    if tier == "PRO" and user_id != "00000000-0000-0000-0000-000000000000":
        memories = get_relevant_memories(user_id, user_message)
        if should_store_memory(user_message):
            store_memory(user_id, user_message)

    memory_context = ""
    if memories:
        memory_context = "\nRelevant historisk kontext om användaren:\n" + "\n".join([f"- {m}" for m in memories])

    try:
        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"{memory_context}\n\n{user_message}"}
                ],
                "temperature": 0.5,
                "max_tokens": 150
            },
            timeout=8.0
        )
        if res.status_code == 200:
            ai_response = res.json()["choices"][0]["message"]["content"]
            return jsonify({
                "response": ai_response,
                "tier": tier,
                "memories_retrieved": len(memories)
            })
        else:
            print(f"[GROQ ERROR]: {res.status_code} - {res.text}", flush=True)
            return jsonify({"error": "Kunde inte generera svar från AI."}), 500
    except Exception as e:
        print(f"[CHAT EXCEPTION]: {e}", flush=True)
        return jsonify({"error": "Internt serverfel."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
