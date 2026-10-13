import os
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

SYSTEM_PROMPT = """Du är FALK, en digital mentor baserad på WAYJS-metodiken.
Du hjälper användaren att sortera sina tankar genom icke-direktiv vägledning.
Svara alltid på idiomatisk svenska. Max 2-3 meningar per svar. Ge aldrig direkta råd,
utan ställ enstaka öppna frågor som leder till egen reflektion."""

MAX_HISTORY_MESSAGES = 8

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
    raw_history = data.get("history", [])

    if not user_message:
        return jsonify({"error": "Meddelande saknas."}), 400

    # Hård validering & beskärning av klienthistorik (Säkerhetsspärr mot skräp/injection)
    sanitized_history = []
    if isinstance(raw_history, list):
        for msg in raw_history[-MAX_HISTORY_MESSAGES:]:
            if isinstance(msg, dict) and msg.get("role") in ["user", "assistant"] and isinstance(msg.get("content"), str):
                sanitized_history.append({
                    "role": msg["role"],
                    "content": msg["content"][:1000] # Hårt tak på tecken per meddelande
                })

    messages_payload = [{"role": "system", "content": SYSTEM_PROMPT}] + sanitized_history + [{"role": "user", "content": user_message[:1000]}]

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages_payload,
            temperature=0.7,
            max_tokens=500
        )
        bot_reply = response.choices[0].message.content.strip()

        return jsonify({"reply": bot_reply}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
