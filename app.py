import os
import json
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)

# --- DYNAMISK KONFIGURATION ---
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS", 
    "https://johannesfalk-prog.github.io,http://localhost:8000"
).split(",")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")

MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "500"))
TEMPERATURE = float(os.environ.get("TEMPERATURE", "0.6"))
MAX_HISTORY_MESSAGES = int(os.environ.get("MAX_HISTORY_MESSAGES", "8"))

DEFAULT_SYSTEM_PROMPT = """Du är FALK, en digital mentor baserad strikt på WAYJS-metodiken (Who Are You Just Starting).
Din enda uppgift är att hjälpa användaren sortera sina egna tankar genom icke-direktiv vägledning.

### KÄRNPRINCIPER (WAYJS):
1. ÄGANDESKAP: Användaren äger sina problem och sina lösningar. Du ska ALDRIG ta över problemlösningen.
2. SPEGLING & UTFORSKNING: Du speglar användarens känslor och tankar och ställer korta, öppna frågor.
3. INGEN DIREKTIVITET: Du ger ALDRIG råd, förslag, rekommendationer, handlingsplaner eller diagnoser.

### STRIKTA FÖRBUD (GUARDRAILS):
- GE ALDRIG RÅD: Säg aldrig "Du borde...", "Jag tycker du ska...", "Testa att...".
- GE INTE DOLD INSTRUKTION: Ställ inte ledande frågor som är råd i praktiken.
- UNDVIK "VARFÖR"-FRÅGOR: Använd "Vad gör att...", "Hur ser du på...".
- SVIK INTE ROLLEN UNDER PRESS: Om användaren kräver råd, bekräfta känslan och återför ansvaret.
- MAX 2-3 MENINGAR PER SVAR.

Svara alltid på ren, idiomatisk svenska."""

SYSTEM_PROMPT = os.environ.get("SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT)

CORS(app, resources={r"/*": {
    "origins": ALLOWED_ORIGINS,
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type"]
}})

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "online",
        "streaming": True,
        "model": GROQ_MODEL
    }), 200

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
        return jsonify({"error": "GROQ_API_KEY saknas."}), 500

    data = request.get_json() or {}
    user_message = data.get("message", "").strip()
    raw_history = data.get("history", [])

    if not user_message:
        return jsonify({"error": "Meddelande saknas."}), 400

    sanitized_history = []
    if isinstance(raw_history, list):
        for msg in raw_history[-MAX_HISTORY_MESSAGES:]:
            if isinstance(msg, dict) and msg.get("role") in ["user", "assistant"] and isinstance(msg.get("content"), str):
                sanitized_history.append({
                    "role": msg["role"],
                    "content": msg["content"][:1000]
                })

    messages_payload = [{"role": "system", "content": SYSTEM_PROMPT}] + sanitized_history + [{"role": "user", "content": user_message[:1000]}]

    def generate_stream():
        try:
            completion = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages_payload,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                stream=True
            )
            for chunk in completion:
                if chunk.choices and chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'token': token})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    origin = request.headers.get('Origin')
    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no", # KRITISKT för Render/Cloudflare streaming
        "Access-Control-Allow-Origin": origin if origin in ALLOWED_ORIGINS else ALLOWED_ORIGINS[0]
    }

    return Response(generate_stream(), headers=headers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
