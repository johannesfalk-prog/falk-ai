import os
import json
import logging
import urllib.request
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from groq import Groq

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def get_client_ip():
    if request.headers.get("CF-Connecting-IP"):
        return request.headers.get("CF-Connecting-IP")
    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For").split(",")[0].strip()
    return request.remote_addr

limiter = Limiter(
    key_func=get_client_ip,
    app=app,
    default_limits=["200 per day", "60 per hour"],
    storage_uri="memory://"
)

ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS", 
    "https://johannesfalk-prog.github.io,http://localhost:8000"
).split(",")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "500"))
TEMPERATURE = float(os.environ.get("TEMPERATURE", "0.6"))
MAX_HISTORY_MESSAGES = int(os.environ.get("MAX_HISTORY_MESSAGES", "8"))

DEFAULT_SYSTEM_PROMPT = """Du är FALK, en digital mentor baserad på WAYJS-metodiken och vetenskaplig psykoedukation.
Din uppgift är att vara en organisk, lyhörd samtalspartner som hjälper användaren sortera sina tankar.

### DYNAMISK SPRÅKANPASSNING OCH NÄRVARO:
1. ADOPTERA ANVÄNDARENS SPRÅK: Anpassa din ton, meningsbyggnad och ordval efter användarens nivå. Om användaren är rak och vardaglig, var rak och vardaglig. Om användaren är analytisk, var analytisk.
2. FÖRBUD MOT KLYSCHIGA INLEDNINGAR: Starta ALDRIG svar med "Jag hör att...", "Det låter som...", "Det verkar som...", "Jag förstår att...". Gå direkt på sak.
3. SYNTETISERANDE BEKRÄFTELSE (KOPPLA IHOP PUNKTERNA):
   - Bekräfta ELSINTE varje enskilt meddelande.
   - När du väl bekräftar, gör det genom att knyta ihop flera trådar från konversationen till en helhetsbild (t.ex. "När du beskriver både tidspressen och oron för teamet låter det som att källan är...").
   - Om det inte finns flera trådar att knyta ihop ännu: Ställ direkt en fördjupande fråga eller ge ett kort vetenskapligt perspektiv utan inledande plattskärms-empati.

### KÄRNPRINCIPER (WAYJS & VETENSKAP):
- ÄGANDESKAP: Användaren äger sina beslut och lösningar.
- MÄNSKLIG TON: Håll svaren korta (2-3 meningar). Var koncis, rak och undvik AI-artad över-artighet.
- EXPLICITA RÅD/TIPS: Om användaren ber om tips, ge ETT vetenskapligt/kliniskt ramverk utan att garantera resultat eller hitta på statistik, och avsluta med en fråga som återför reflektionen.

Svara alltid på ren, idiomatisk svenska."""

SYSTEM_PROMPT = os.environ.get("SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT)

CORS(app, resources={r"/*": {
    "origins": ALLOWED_ORIGINS,
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type"]
}})

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

def send_discord_notification(rating, reply_snippet):
    if not DISCORD_WEBHOOK_URL:
        return
    try:
        emoji = "👍" if rating == "up" else "👎"
        payload = {
            "content": f"**Ny Feedback mottagen!** {emoji}\n**Rating:** `{rating}`\n**Svarssnippet:** *\"{reply_snippet}\"*"
        }
        req = urllib.request.Request(
            DISCORD_WEBHOOK_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
        )
        urllib.request.urlopen(req)
    except Exception as e:
        app.logger.error(f"Kunde inte skicka Discord-notis: {e}")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "online", "model": GROQ_MODEL}), 200

@app.route('/feedback', methods=['POST', 'OPTIONS'])
@limiter.limit("30 per minute", exempt_when=lambda: request.method == "OPTIONS")
def feedback():
    if request.method == 'OPTIONS':
        response = jsonify({"status": "ok"})
        origin = request.headers.get('Origin')
        if origin in ALLOWED_ORIGINS:
            response.headers.add("Access-Control-Allow-Origin", origin)
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return response, 200

    data = request.get_json() or {}
    rating = data.get("rating")
    reply = data.get("reply", "")[:200]

    send_discord_notification(rating, reply)
    return jsonify({"status": "received"}), 200

@app.route('/chat', methods=['POST', 'OPTIONS'])
@limiter.limit("15 per minute", exempt_when=lambda: request.method == "OPTIONS")
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
        "X-Accel-Buffering": "no",
        "Access-Control-Allow-Origin": origin if origin in ALLOWED_ORIGINS else ALLOWED_ORIGINS[0]
    }

    return Response(generate_stream(), headers=headers)

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"error": "Du skickar meddelanden för snabbt. Vänta en minut och försök igen."}), 429

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
