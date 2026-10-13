import os
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)

ALLOWED_ORIGINS = [
    "https://johannesfalk-prog.github.io",
    "http://localhost:8000"
]

CORS(app, resources={r"/*": {
    "origins": ALLOWED_ORIGINS,
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type"]
}})

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

MAX_SESSIONS = 100
MAX_HISTORY_MESSAGES = 8
sessions = {}

SYSTEM_PROMPT = """Du är FALK, en digital mentor baserad på WAYJS-metodiken.
Du hjälper användaren att sortera sina tankar genom icke-direktiv vägledning.
Svara alltid på idiomatisk svenska. Max 2-3 meningar per svar. Ge aldrig direkta råd,
utan ställ enstaka öppna frågor som leder till egen reflektion."""

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        response = jsonify({"status": "ok"})
        origin = request.headers.get('Origin')
        if origin in ALLOWED_ORIGINS:
            response.headers.add("Access-Control-Allow-Origin", origin)
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return response, 200

    if not client:
        return jsonify({"error": "GROQ_API_KEY saknas i miljövariabler."}), 500

    data = request.get_json() or {}
    user_message = data.get("message", "").strip()
    session_id = data.get("session_id")

    if not user_message:
        return jsonify({"error": "Meddelande saknas."}), 400

    if len(sessions) > MAX_SESSIONS:
        oldest_key = next(iter(sessions))
        del sessions[oldest_key]

    if not session_id or session_id not in sessions:
        session_id = str(uuid.uuid4())
        sessions[session_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

    sessions[session_id].append({"role": "user", "content": user_message})

    # Behåll alltid systemprompten + de senaste meddelandena för att förhindra token-overflow
    context_messages = [sessions[session_id][0]] + sessions[session_id][-MAX_HISTORY_MESSAGES:]

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=context_messages,
            temperature=0.7,
            max_tokens=500
        )
        bot_reply = response.choices[0].message.content.strip()
        sessions[session_id].append({"role": "assistant", "content": bot_reply})

        return jsonify({
            "reply": bot_reply,
            "session_id": session_id
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
