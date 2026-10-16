import os
import json
import time
import logging
import concurrent.futures
from collections import defaultdict
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
PRIMARY_MODEL = "openai/gpt-oss-120b"

RATE_LIMIT_REQUESTS = 20
RATE_LIMIT_WINDOW = 60
ip_request_history = defaultdict(list)

def is_rate_limited(ip_address):
    now = time.time()
    ip_request_history[ip_address] = [t for t in ip_request_history[ip_address] if now - t < RATE_LIMIT_WINDOW]
    if len(ip_request_history[ip_address]) >= RATE_LIMIT_REQUESTS:
        return True
    ip_request_history[ip_address].append(now)
    return False

BASE_SYSTEM_PROMPT = """
Du är FALK – en digital mentor baserad på WAYJS-metodiken.
Din uppgift är att ställa klargörande, reflekterande frågor och hjälpa användaren att sortera sina tankar, värderingar och mönster.
Ge inte förhastade råd. Håll svaren korta, precisa och dialogdrivna.

VIKTIGA REGLER:
1. Ställ ALDRIG mer än 1 till 2 frågor per meddelande. Undvik långa punktlistor.
2. SYFTNINGSUPPLÖSNING: Om användaren svarar med en relativ syftning (t.ex. "det förstnämnda", "det sista", "alternativ A", "det tidigare", "ja", "nej"), MÅSTE du analysera ditt eget förra meddelande, identifiera vad användaren syftar på och driva dialogen vidare utifrån det faktiska sakinnehållet. Citera eller upprepa ALDRIG användarens syftningsord bokstavligen.
"""

MEMORY_EXTRACTION_PROMPT = """
Du är en kognitiv minnesmotor för FALK. Analysera användarens meddelande och den befintliga profilen, och returnera en UPPDATERAD JSON-profil.

STRIKT REGEL: Begränsa listorna 'varderingar' och 'identifierade_monster' till MAXIMALTVIS 5 objekt vardera.

Returnera ENBART ett giltigt JSON-objekt utan markdown och utan förklarande text:
{
  "aktuellt_fokus": "Sträng med användarens huvudsakliga fokus just nu",
  "identifierade_monster": ["mönster 1", "mönster 2"],
  "senaste_insikt": "Kort sträng med senaste insikten",
  "varderingar": ["värdering 1", "värdering 2"]
}
"""

DEFAULT_PROFILE_TEMPLATE = {
    "schema_version": "1.0",
    "aktuellt_fokus": "Odefinierat",
    "identifierade_monster": [],
    "senaste_insikt": "Ingen ännu",
    "varderingar": []
}

def sanitize_profile(profile):
    if not isinstance(profile, dict):
        return dict(DEFAULT_PROFILE_TEMPLATE)
    sanitized = dict(DEFAULT_PROFILE_TEMPLATE)
    sanitized.update(profile)
    sanitized["varderingar"] = list(sanitized.get("varderingar", []))[:5]
    sanitized["identifierade_monster"] = list(sanitized.get("identifierade_monster", []))[:5]
    return sanitized

def generate_chat_response(user_message, current_profile, history=None, modifier=None):
    try:
        system_prompt = BASE_SYSTEM_PROMPT
        max_tokens = 250

        if modifier == "shorter":
            system_prompt += "\nEXTRA INSTRUKTION: Gör svaret extremt kortfattat och koncist (max 2 meningar)."
            max_tokens = 120
        elif modifier == "longer":
            system_prompt += "\nEXTRA INSTRUKTION: Utveckla resonemanget något djupare med mer kontextuell reflektion."
            max_tokens = 450
        elif modifier == "regenerate":
            system_prompt += "\nEXTRA INSTRUKTION: Formulera om ditt förra svar helt ur en ny vinkel."

        messages = [
            {"role": "system", "content": f"{system_prompt}\nBefintlig kognitiv profil (Långtidsminne): {json.dumps(current_profile, ensure_ascii=False)}"}
        ]

        if history and isinstance(history, list):
            sanitized_history = history[-6:]
            for msg in sanitized_history:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    messages.append({"role": msg["role"], "content": msg["content"]})

        if not history or (history and history[-1].get("content") != user_message):
            messages.append({"role": "user", "content": user_message})

        completion = client.chat.completions.create(
            model=PRIMARY_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=max_tokens
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Fel i generate_chat_response: {e}")
        return "Kunde inte generera ett svar just nu. Vad vill du utforska istället?"

def extract_memory_updates(user_message, current_profile):
    try:
        active_profile = sanitize_profile(current_profile)
        messages = [
            {"role": "system", "content": MEMORY_EXTRACTION_PROMPT},
            {"role": "user", "content": f"Befintlig profil: {json.dumps(active_profile, ensure_ascii=False)}\nNytt meddelande: {user_message}"}
        ]
        completion = client.chat.completions.create(
            model=PRIMARY_MODEL,
            messages=messages,
            temperature=0.2,
            max_tokens=250,
            response_format={"type": "json_object"}
        )
        raw_json = completion.choices[0].message.content.strip()
        parsed = json.loads(raw_json)
        return sanitize_profile(parsed)
    except Exception as e:
        logger.error(f"Fel i extract_memory_updates: {e}")
        return sanitize_profile(current_profile)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"active_model": PRIMARY_MODEL, "status": "ok"}), 200

@app.route("/chat", methods=["POST"])
def chat():
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr or '127.0.0.1').split(',')[0].strip()
    
    if is_rate_limited(client_ip):
        return jsonify({"response": "Du skickar meddelanden för snabbt. Vänta en stund och försök igen."}), 429

    try:
        data = request.get_json() or {}
        user_message = data.get("message", "").strip()
        current_profile = sanitize_profile(data.get("user_profile", {}))
        history = data.get("history", [])
        modifier = data.get("modifier", None)

        if not user_message:
            return jsonify({"error": "Meddelandet kan inte vara tomt"}), 400

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_chat = executor.submit(generate_chat_response, user_message, current_profile, history, modifier)
            future_memory = executor.submit(extract_memory_updates, user_message, current_profile)

            bot_response = future_chat.result()
            updated_profile = future_memory.result()

        return jsonify({
            "response": bot_response,
            "user_profile": updated_profile
        }), 200
    except Exception as e:
        logger.error(f"Kritiskt fel i /chat route: {e}")
        return jsonify({
            "response": "Ett internt fel uppstod i motorn. Försök igen om ett ögonblick.",
            "user_profile": sanitize_profile(request.get_json().get("user_profile", {}) if request.get_json() else {})
        }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
