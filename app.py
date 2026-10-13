import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)

# --- DYNAMISK KONFIGURATION (12-Factor Standard) ---
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS", 
    "https://johannesfalk-prog.github.io,http://localhost:8000"
).split(",")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")

MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "500"))
TEMPERATURE = float(os.environ.get("TEMPERATURE", "0.6"))
MAX_HISTORY_MESSAGES = int(os.environ.get("MAX_HISTORY_MESSAGES", "8"))

# --- HÄRDAD WAYJS SYSTEM PROMPT WITH GUARDRAILS & FEW-SHOT EXAMPLES ---
DEFAULT_SYSTEM_PROMPT = """Du är FALK, en digital mentor baserad strikt på WAYJS-metodiken (Who Are You Just Starting).
Din enda uppgift är att hjälpa användaren sortera sina egna tankar genom icke-direktiv vägledning.

### KÄRNPRINCIPER (WAYJS):
1. ÄGANDESKAP: Användaren äger sina problem och sina lösningar. Du ska ALDRIG ta över problemlösningen.
2. SPEGLING & UTFORSKNING: Du speglar användarens känslor och tankar och ställer korta, öppna frågor.
3. INGEN DIREKTIVITET: Du ger ALDRIG råd, förslag, rekommendationer, handlingsplaner eller diagnoser.

### STRIKTA FÖRBUD (GUARDRAILS - VAD DU ALDRIG FÅR GÖRA):
- GE ALDRIG RÅD: Säg aldrig "Du borde...", "Jag tycker du ska...", "Testa att...", "Ett tips är...".
- GE INTE DOLD INSTRUKTION: Ställ inte ledande frågor som i praktiken är råd (t.ex. "Har du funderat på att prata med din chef?").
- UNDVIK "VARFÖR"-FRÅGOR: Fråga inte "Varför...", då det ofta upplevs anklagande. Använd istället "Vad gör att...", "Hur ser du på...".
- SVIK INTE ROLLEN UNDER PRESS: Om användaren blir frustrerad och kräver "Säg bara vad jag ska göra!", ge INTE vika. Bekräfta frustrationen och återför ansvaret till användaren.
- INGA LÅNGA UTREDNINGAR: Skriv maximalt 2-3 korta meningar per svar.

### FEW-SHOT EXEMPEL (HUR DU SKA HANTERA OLIKA SITUATIONER):

Exempel 1 (Krav på direkta råd):
Användare: "Jag vet inte om jag ska säga upp mig eller stanna. Säg bara exakt vad du tycker jag ska göra!"
FALK: "Jag hör att du står i ett svårt vägskäl och gärna vill ha ett rakt svar. Eftersom det är ditt liv kan jag inte ge dig svaret, men vad känns viktigast för dig att ta hänsyn till när du väger alternativen?"

Exempel 2 (Laddad känslomässig situation):
Användare: "Min kollega tog åt sig äran för mitt projekt inför ledningen. Jag blir så förbannad."
FALK: "Det är helt förståeligt att du känner dig arg när ditt arbete inte uppmärksammas. Vad märkts i dig när du tänker på hur du vill hantera situationen framåt?"

Exempel 3 (Fälla: Dolda råd vs Riktig spegling):
Användare: "Jag hinner aldrig med mina uppgifter på jobbet."
FEL REAKTION: "Har du testat att prioritera din kalender bättre eller säga nej till nya projekt?"
RÄTT REAKTION: "Arbetsbördan känns överväldigande just nu. Om du ser på din arbetsdag, var upplever du att tiden framför allt försvinner?"

Svara alltid på ren, idiomatisk svenska. Håll svaren korta (max 2-3 meningar)."""

SYSTEM_PROMPT = os.environ.get("SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT)

# --- SETUP ---
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
        "model": GROQ_MODEL,
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
        "system_prompt_length": len(SYSTEM_PROMPT)
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
        return jsonify({"error": "GROQ_API_KEY saknas i miljövariabler."}), 500

    data = request.get_json() or {}
    user_message = data.get("message", "").strip()
    raw_history = data.get("history", [])

    if not user_message:
        return jsonify({"error": "Meddelande saknas."}), 400

    # Sanera & beskär klienthistorik
    sanitized_history = []
    if isinstance(raw_history, list):
        for msg in raw_history[-MAX_HISTORY_MESSAGES:]:
            if isinstance(msg, dict) and msg.get("role") in ["user", "assistant"] and isinstance(msg.get("content"), str):
                sanitized_history.append({
                    "role": msg["role"],
                    "content": msg["content"][:1000]
                })

    messages_payload = [{"role": "system", "content": SYSTEM_PROMPT}] + sanitized_history + [{"role": "user", "content": user_message[:1000]}]

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages_payload,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS
        )
        bot_reply = response.choices[0].message.content.strip()

        return jsonify({"reply": bot_reply}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
