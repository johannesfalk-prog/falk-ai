import os
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv

load_dotenv(override=True)

app = Flask(__name__)
CORS(app)
app.json.ensure_ascii = False

api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)
sessions = {}

SYSTEM_PROMPT = """Du är Falk, den digitala mentorn bakom WAYJS.
Du har ett fågelperspektiv på människors liv och hjälper dem att navigera med större klarhet, bättre omdöme och hållbara beslut.
Du är inte terapeut, rådgivare eller lärare. Du är en klok samtalspartner.

SPRÅK OCH TONALITET:
- Skriv på perfekt, idiomatisk, naturally varm svenska.
- Använd ALDRIG engelska ord eller anglicismer.
- Använd ALDRIG ordet 'borde'.
- Säg ALDRIG meta-kommentarer som 'Jag ger inte råd' eller 'Som din mentor'. Gå direkt på samtalet.

SAMTALSMETODIK:
- Ge ALDRIG snabba lösningar, förslag eller listor på råd.
- Ställ EXAKT EN öppen fråga i slutet av ditt svar. Blanda aldrig två frågor med 'och'.
- Håll svaret kort (max 2-3 meningar totalt).
"""

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json or {}
    user_message = data.get('message', '').strip()
    session_id = data.get('session_id')

    if not user_message:
        return jsonify({'error': 'Tomt meddelande'}), 400

    if not session_id or session_id not in sessions:
        session_id = str(uuid.uuid4())
        sessions[session_id] = [{'role': 'system', 'content': SYSTEM_PROMPT}]

    history = sessions[session_id]
    history.append({'role': 'user', 'content': user_message})

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=history,
            temperature=0.5,
            max_tokens=400
        )
        bot_reply = response.choices[0].message.content
        history.append({'role': 'assistant', 'content': bot_reply})
        
        return jsonify({
            'reply': bot_reply,
            'session_id': session_id
        })
    except Exception as e:
        print(f"\n[SERVER FEL]: {e}\n")
        return jsonify({'error': str(e)}), 500

@app.route('/reset', methods=['POST'])
def reset():
    data = request.json or {}
    session_id = data.get('session_id')
    if session_id and session_id in sessions:
        del sessions[session_id]
    return jsonify({'status': 'Samtal nollställt'})

if __name__ == '__main__':
    app.run(port=5000)
