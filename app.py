import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client, Client
import dialogue_router

load_dotenv()

app = Flask(__name__)
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
CORS(app, resources={r"/api/*": {"origins": allowed_origins}})

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

supabase_url = os.getenv("SUPABASE_URL", "")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "") or os.getenv("SUPABASE_KEY", "")
supabase: Client = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None

FALK_SYSTEM_PROMPT = """
Du är Falk, den digitala mentorn bakom WAYJS (The Human Navigation Company).
Du har ett fågelperspektiv på människors liv och hjälper dem att navigera med större klarhet, bättre omdöme och hållbara beslut.
Du är inte terapeut, rådgivare, lärare eller en vän som alltid håller med. Du är en klok samtalspartner.

FALKS 5 GRINDAR (THE FIVE GATES):
1. TRUTH: Skilj alltid på fakta, upplevelser, antaganden och känslor. Bekräfta känslan, aldrig tolkningen.
2. HELPFUL: Ge endast information och frågor som för användaren framåt i självinsikt.
3. TIMING: Anpassa tempot efter användarens tillstånd. Hoppa ALDRIG direkt till lösningar om användaren först behöver bli förstådd.
4. ALIGNMENT: Väga resonemanget mot användarens uttalade värderingar och Nordstjärna.
5. INDEPENDENCE: Skapa ALDRIG beroende. Om användaren ber om råd eller direktiv, ge ALDRIG bara ett svar. Presentera alltid minst 2 olika alternativ med för- och nackdelar, och lämna beslutet helt till användaren.

SAMTALETS 7 FASER (THE WAYJS DIALOGUE):
1. TRYGGHET -> 2. FÖRSTÅELSE -> 3. UTFORSKANDE -> 4. PERSPEKTIV -> 5. KLARHET -> 6. HANDLING -> 7. REFLEKTION.

TONALITET & REGLER:
- Lugn, varm, nyfiken, eftertänksam, respektfull, ödmjuk. Korta meningar.
- Använd enkla metaforer för navigering (kompass, fågelperspektiv, dimma, sidvind, nordstjärna) sparsamt.
- Säg ALDRIG: "Jag är ledsen", "Ursäkta", "Som en AI", "Du borde...", "Det är enkelt...", "Det enda du behöver göra...".
- Förbud: Skapa beroende, manipulera, döma, skuldbelägga, låtsas veta.
- Vid krav på medicinsk diagnos/recept eller terapi: "Det här ligger utanför det jag kan bedöma. Jag vill inte ge dig ett svar som riskerar att bli missvisande. Om du vill kan vi tillsammans resonera kring vilka frågor du kan ta med dig till rätt profession."
- Avsluta alltid längre samtal med en reflektionsfråga (t.ex. "Vad tar du med dig?", "Vad känns tydligare nu?").
"""

CRISIS_PATTERNS = [
    r"orkar?\s+inte\s+leva",
    r"vill\s+dö",
    r"ta\s+mitt\s+liv",
    r"avsluta\s+mitt\s+liv",
    r"självmord",
    r"skada\s+mig",
    r"ge\s+upp\s+allt"
]

def check_crisis_guardrail(text: str) -> tuple[bool, str]:
    text_normalized = re.sub(r'\s+', ' ', text.lower().strip())
    for pattern in CRISIS_PATTERNS:
        if re.search(pattern, text_normalized):
            crisis_response = (
                "Jag hör att du har det väldigt tufft just nu, men jag är en digital mentor "
                "och kan inte ge dig det stöd du behöver vid en kris. Du ska inte bära detta ensam.\n\n"
                "Kontakta akuthjälp direkt:\n"
                "• Ring 112 vid akuta situationer.\n"
                "• Självmordslinjen: Ring eller chatta på 90101 (mind.se).\n"
                "• Jourhavande medmänniska: 08-702 16 80.\n\n"
                "Prata med någon i din närhet eller sök professionell hjälp nu."
            )
            return True, crisis_response
    return False, ""

def post_process_guardrail(user_message: str, response_text: str) -> str:
    msg_lower = user_message.lower()
    
    medical_keywords = ["diagnos", "förskriv", "medicin", "recept", "klinisk depression", "behandling"]
    if any(k in msg_lower for k in medical_keywords):
        return ("Det här ligger utanför det jag kan bedöma. Jag vill inte ge dig ett svar som riskerar att bli missvisande. "
                "Om du vill kan vi tillsammans resonera kring vilka frågor du kan ta med dig till rätt profession. "
                "Hur vill du gå vidare just nu?")
                
    cleaned = response_text
    cleaned = re.sub(r"^(jag är ledsen,?\s*men\s*|tyvärr,?\s*men\s*|som en ai,?\s*)", "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip()
    if cleaned and cleaned[0].islower():
        cleaned = cleaned[0].upper() + cleaned[1:]
        
    return cleaned

@app.route('/', methods=['GET'])
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "Falk Core Engine",
        "version": "1.0.0"
    }), 200

@app.route('/api/library/cards', methods=['GET'])
def get_library_cards():
    return jsonify({"cards": [], "total": 0})

@app.route('/api/dialogue/turn', methods=['POST'])
def dialogue_turn():
    try:
        data = request.json or {}
        user_id = data.get('user_id', 'beta_guest')
        session_id = data.get('session_id', 'sess_default')
        user_message = data.get('user_message', '')

        if not user_message:
            return jsonify({"error": "Meddelande saknas"}), 400

        is_crisis, crisis_msg = check_crisis_guardrail(user_message)
        if is_crisis:
            dialogue_router.save_message(session_id, user_id, 'user', user_message)
            dialogue_router.save_message(session_id, user_id, 'assistant', crisis_msg)
            return jsonify({
                "session_id": session_id,
                "active_stage": "TRYGGHET",
                "falk_response": crisis_msg
            })

        sess_data = dialogue_router.get_or_create_session(session_id, user_id)
        current_stage = sess_data.get("current_stage", "TRYGGHET")
        messages, history_text = dialogue_router.fetch_chat_history(session_id, limit=14)

        try:
            new_stage, _ = dialogue_router.evaluate_stage_transition(current_stage, user_message, history_text)
        except Exception as stage_err:
            print(f"[Varning] Stage evaluation misslyckades, behåller {current_stage}: {stage_err}")
            new_stage = current_stage

        system_prompt = f"{FALK_SYSTEM_PROMPT}\n\nAKTUELT SAMTALSSTADIUM: [{new_stage}]"
        
        gpt_messages = [{"role": "system", "content": system_prompt}]
        for m in messages:
            gpt_messages.append({"role": m.get("role", "user"), "content": m.get("content", "")})
        gpt_messages.append({"role": "user", "content": user_message})

        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=gpt_messages,
                temperature=0.3,
                timeout=15.0
            )
            raw_response = response.choices[0].message.content
            final_response = post_process_guardrail(user_message, raw_response)
        except Exception as llm_err:
            print(f"[Kritiskt Fel vid LLM-anrop]: {llm_err}")
            final_response = (
                "Jag behöver stanna upp ett ögonblick för att samla tankarna. "
                "Det verkar vara en tillfällig störning i vår förbindelse. "
                "Vad är det viktigaste du vill att vi ska fokusera på när du är redo?"
            )

        dialogue_router.save_message(session_id, user_id, 'user', user_message)
        dialogue_router.save_message(session_id, user_id, 'assistant', final_response)
        dialogue_router.update_session_stage(session_id, new_stage, sess_data.get("turn_count", 1))

        return jsonify({
            "session_id": session_id,
            "active_stage": new_stage,
            "falk_response": final_response
        })

    except Exception as e:
        print(f"[Kritiskt Ohanterat Fel i Dialogue Turn]: {e}")
        return jsonify({
            "session_id": data.get('session_id', 'sess_default') if 'data' in locals() else 'sess_default',
            "active_stage": "TRYGGHET",
            "falk_response": "Jag behöver stanna upp ett ögonblick. Kan du upprepa din senaste tanke?"
        }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5001)), debug=False)
