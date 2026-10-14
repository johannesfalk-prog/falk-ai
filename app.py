import os
import json
import time
import logging
import urllib.request
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

RATE_LIMIT_STORE = {}

def check_rate_limit(ip, limit=15, window=60):
    now = time.time()
    timestamps = RATE_LIMIT_STORE.get(ip, [])
    valid_timestamps = [t for t in timestamps if now - t < window]
    if len(valid_timestamps) >= limit:
        return False
    valid_timestamps.append(now)
    RATE_LIMIT_STORE[ip] = valid_timestamps
    return True

def get_client_ip():
    if request.headers.get("CF-Connecting-IP"):
        return request.headers.get("CF-Connecting-IP")
    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For").split(",")[0].strip()
    return request.remote_addr

ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS", 
    "https://johannesfalk-prog.github.io,http://localhost:8000"
).split(",")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "600"))
TEMPERATURE = float(os.environ.get("TEMPERATURE", "0.3"))
MAX_HISTORY_MESSAGES = int(os.environ.get("MAX_HISTORY_MESSAGES", "10"))

VALIDATED_SLEEP_TRACKS = {
    "lofi": "https://www.youtube.com/watch?v=jfKfPfyJRdk",
    "rain": "https://www.youtube.com/watch?v=mPZkdNFkNps"
}

BASE_SYSTEM_PROMPT = f"""Du är FALK, en digital mentor baserad på WAYJS-metodiken och vetenskaplig psykoedukation.

### AKUT KRISPROTOKOLL (STRIKTASTE REGELN - GÅR FÖRE ALLT ANNAT):
- Om användaren uttrycker självmordstankar, önskan att avsluta sitt liv, självskada eller akut hopplöshet:
  1. Lämna OMEDELBART krisinformation: Ring 112 vid akutfara, Självmordslinjen på 90101 (dygnet runt), eller Psykakuten/1177.
  2. Uppmana varmt och kort att prata med någon närstående eller professionell.
  3. ABSOLUT FÖRBUD: Ställ INGA coachingfrågor, ge INGA övningar och ställ INGA reflektionsfrågor i krisläge. Avsluta meddelandet direkt efter krisstödsinformationen.

### GRUNDLAGAR FÖR DIALOG:
1. "VARFÖR" FÖRE "HUR" OCH "VAD":
   - Hjälp användaren utforska underliggande drivkrafter och orsaker INNAN du går in på åtgärder.
   - FÖRBUD MOT TONDÖVHET: Ställ ALDRIG "Varför är detta smärtsamt?" vid uppenbara svek, otrohet, sorg eller kränkningar. Bekräfta situationen med värdighet och fråga vad personen behöver just nu.

2. MAX 1 FRÅGA PER SVAR (TOTALFÖRBUD MOT FRÅGEBATTERIER):
   - Ställ ALDRIG mer än EN (1) enskild fördjupande fråga per meddelande.
   - Det är TOTALT FÖRBUD mot att skicka listor med frågor.

3. ABSOLUT FÖRBUD MOT KLYSCHOR OCH ANGLICISMER:
   - Skriv ALDRIG "Jag hör att...", "Jag hör vad du säger...", "Det låter som...", "Det verkar som...". Gå direkt på kärnan utan inledande fraser.
   - Skriv ALDRIG "bli ljugen för". Använd "när någon ljuger för en", "att bli sviken" eller "när ett löfte bryts".

4. PRESENTERA – ALDRIG FÖRESLÅ ELLER REKOMMENDERA:
   - Ge aldrig order ("Du borde...", "Jag föreslår..."). Beskriv verktyg och perspektiv neutralt.

5. SÖMNPROTOKOLL:
   - Vid sömnproblem, fråga om tillåtelse att dela ljudspår: {VALIDATED_SLEEP_TRACKS['lofi']} eller {VALIDATED_SLEEP_TRACKS['rain']}.
"""

MODE_DIRECTIVES = {
    "wayjs": "\n### PERSPEKTIV: WAYJS HELHET (STANDARD)\nFokusera på helhetsbilden och användarens underliggande drivkraft.",
    "kbt": "\n### PERSPEKTIV: KBT\nFokusera på samspelet mellan automatiska tankar, känslor och beteendemönster.",
    "act": "\n### PERSPEKTIV: ACT\nFokusera på kärnvärderingar, acceptans och psykologisk flexibilitet.",
    "sol": "\n### PERSPEKTIV: LÖSNINGSFOKUSERAT\nFokusera på användarens befintliga styrkor och tidigare undantag."
}

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
    rating = str(data.get("rating") or "").strip()
    reply = str(data.get("reply") or "")[:200]

    send_discord_notification(rating, reply)
    return jsonify({"status": "received"}), 200

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

    ip = get_client_ip()
    if not check_rate_limit(ip, limit=15, window=60):
        return jsonify({"error": "Du skickar meddelanden för snabbt. Vänta en minut."}), 429

    if not client:
        return jsonify({"error": "GROQ_API_KEY saknas."}), 500

    data = request.get_json() or {}
    
    user_message = str(data.get("message") or "").strip()
    raw_history = data.get("history") or []
    mode = str(data.get("mode") or "wayjs").strip()
    directive = str(data.get("directive") or "").strip()

    if not user_message and not directive:
        return jsonify({"error": "Meddelande saknas."}), 400

    sanitized_history = []
    if isinstance(raw_history, list):
        for msg in raw_history[-MAX_HISTORY_MESSAGES:]:
            if isinstance(msg, dict) and msg.get("role") in ["user", "assistant"] and isinstance(msg.get("content"), str):
                sanitized_history.append({
                    "role": msg["role"],
                    "content": msg["content"][:1000]
                })

    mode_instruction = MODE_DIRECTIVES.get(mode, MODE_DIRECTIVES["wayjs"])
    effective_prompt = BASE_SYSTEM_PROMPT + mode_instruction

    if directive == "shorter":
        effective_prompt += "\n\nSÄRSKILD INSTRUKTION: Gör svaret extremt kort (max 1-2 meningar)."
    elif directive == "longer":
        effective_prompt += "\n\nSÄRSKILD INSTRUKTION: Ge ett mer fördjupat svar."

    messages_payload = [{"role": "system", "content": effective_prompt}] + sanitized_history
    if user_message:
        messages_payload.append({"role": "user", "content": user_message[:1000]})

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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
