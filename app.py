import os
import json
import logging
import concurrent.futures
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

BASE_SYSTEM_PROMPT = """
Du är FALK – en digital mentor baserad på WAYJS-metodiken.
Din uppgift är att ställa klargörande, reflekterande frågor och hjälpa användaren att sortera sina tankar, värderingar och mönster.
Ge inte förhastade råd. Håll svaren korta, precisa och dialogdrivna.
VIKTIG REGEL: Ställ ALDRIG mer än 1 till 2 frågor per meddelande. Undvik långa punktlistor.
"""

MEMORY_EXTRACTION_PROMPT = """
Du är en kognitiv minnesmotor för FALK. Analysera användarens meddelande och den befintliga profilen, och returnera en UPPDATERAD JSON-profil.

STRIKT REGEL: Begränsa listorna 'varderingar' och 'identifierade_monster' till MAXIMALTVIS 5 objekt vardera.

Returnera ENBART ett giltigt JSON-objekt utan markdown, utan färgkodning och utan förklarande text.
JSON-strukturen SKALL exakt följa detta format:
{
  "aktuellt_fokus": "Sträng med användarens huvudsakliga fokus just nu",
  "identifierade_monster": ["mönster 1", "mönster 2"],
  "senaste_insikt": "Kort sträng med senaste insikten",
  "varderingar": ["värdering 1", "värdering 2"]
}
"""

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

        # Inkludera upp till de senaste 6 meddelandena (3 dialogturer) för konversationstråd
        if history and isinstance(history, list):
            sanitized_history = history[-6:]
            for msg in sanitized_history:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    messages.append({"role": msg["role"], "content": msg["content"]})

        # Lägg till det aktuella meddelandet om det inte redan är sista elementet i history
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
        messages = [
            {"role": "system", "content": MEMORY_EXTRACTION_PROMPT},
            {"role": "user", "content": f"Befintlig profil: {json.dumps(current_profile, ensure_ascii=False)}\nNytt meddelande: {user_message}"}
        ]
        completion = client.chat.completions.create(
            model=PRIMARY_MODEL,
            messages=messages,
            temperature=0.2,
            max_tokens=250,
            response_format={"type": "json_object"}
        )
        raw_json = completion.choices[0].message.content.strip()
        return json.loads(raw_json)
    except Exception as e:
        logger.error(f"Fel i extract_memory_updates: {e}")
        return current_profile

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"active_model": PRIMARY_MODEL, "status": "ok"}), 200

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json() or {}
        user_message = data.get("message", "").strip()
        current_profile = data.get("user_profile", {})
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
            "user_profile": request.get_json().get("user_profile", {}) if request.get_json() else {}
        }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
