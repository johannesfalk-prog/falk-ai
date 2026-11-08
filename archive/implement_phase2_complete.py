import os
import re

print("=== IMPLEMENTERAR FAS 2A, 2B & 2C (SUPABASE + STRIPE + FOKUS) ===")

# 1. UPPDATERA APP.PY MED FOKUS-PROMPT, SUPABASE & STRIPE CHECKOUT
app_code = '''import os
import json
from flask import Flask, render_template, request, jsonify, redirect, session
import openai
import stripe
from supabase import create_client, Client

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "falk-secret-key-2026")

# KONFIGURERA ENVIROMENT KEYS
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID")
stripe.api_key = STRIPE_SECRET_KEY

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")

supabase_client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("-> [SUPABASE] Ansluten till databasen.")
    except Exception as e:
        print(f"-> [SUPABASE WARNING] Kunde inte initiera client: {e}")

# RUTTER FOR HUVUDSIDOR
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/bibliotek')
def bibliotek():
    return render_template('bibliotek.html')

@app.route('/utveckling')
def utveckling():
    return render_template('utveckling.html')

@app.route('/installningar')
def installningar():
    return render_template('installningar.html')

# FAS 2A & 2B: CHATT-ENDPUNKT MED FOKUS-INJEKTION & SUPABASE-LOGGNING
@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.json or {}
    user_message = data.get('message', '')
    focus = data.get('focus_settings', {})

    sjalvfortroende = focus.get('sjalvfortroende', 50)
    stresshantering = focus.get('stresshantering', 50)
    handlingskraft = focus.get('handlingskraft', 50)
    granssattning = focus.get('granssattning', 50)
    motivation = focus.get('motivation', 50)

    # BYGG DYNAMISK SYSTEM-PROMPT BASERAD PÅ ANVÄNDARENS FOKUS-PARAMETRAR
    system_prompt = f"""Du är FALK – en kognitiv kompass och reflektionspartner.
Användarens nuvarande tillstånd och parametrar (0-100%):
- Självförtroende: {sjalvfortroende}%
- Stresshantering: {stresshantering}%
- Handlingskraft: {handlingskraft}%
- Gränssättning: {granssattning}%
- Motivation: {motivation}%

Riktlinjer för svar baserat på parametrarna:
- Om Stresshantering är låg (<40%): Svara extra lugnande, metodiskt och i korta stycken.
- Om Handlingskraft är hög (>70%): Ge konkreta, utmanande steg och ställ direkt aktiverande frågor.
- Om Självförtroende är lågt (<40%): Validera användarens styrkor och undvik konfrontativ ton.
- Om Gränssättning är låg (<40%): Hjälp användaren att identifiera var de behöver säga nej.
- Bevara alltid FALKs grundton: Genuin, klok, jordnära och skarp utan klyschor."""

    try:
        if OPENAI_API_KEY:
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7
            )
            ai_response = response.choices[0].message.content
        else:
            ai_response = f"[SIMULERAT SVAR MED FOKUS-ANPASSNING]\n\nJag ser att din Handlingskraft är {handlingskraft}% och Stresshantering är {stresshantering}%. Vad är ditt nästa konkreta steg?"

        # SPARA TILL SUPABASE (CHAT_MESSAGES) OM ANSLUTEN
        if supabase_client:
            try:
                supabase_client.table('chat_messages').insert({
                    'message': user_message,
                    'response': ai_response,
                    'focus_data': focus
                }).execute()
            except Exception as db_err:
                print(f"-> [SUPABASE DB ERROR] {db_err}")

        return ai_response

    except Exception as e:
        print(f"-> [CHAT API ERROR] {e}")
        return jsonify({"error": str(e)}), 500

# FAS 2C: STRIPE CHECKOUT ROUTING
@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        domain_url = request.host_url.rstrip('/')
        if STRIPE_SECRET_KEY and STRIPE_PRICE_ID:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': STRIPE_PRICE_ID,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=domain_url + '/?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + '/?canceled=true',
            )
            return jsonify({'url': checkout_session.url})
        else:
            # Fallback om nycklar saknas under utveckling
            return jsonify({'url': domain_url + '/?checkout_demo=true'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
'''

with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code)
print("-> [SUCCESS] app.py har uppdaterats med Supabase, Stripe och Fokus-payload!")

# 2. UPPDATERA FRONT-END JAVASCRIPT I INDEX.HTML FÖR ATT SKICKA FOKUS OCH KOPPLA KASSAN
index_path = os.path.join("templates", "index.html")
if os.path.exists(index_path):
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Uppdatera executeSendMessage till att hämta localStorage falk_focus_settings
    old_exec = r'fetch\(\'/api/chat\',\s*\{\s*method:\s*\'POST\',\s*headers:\s*\{\s*\'Content-Type\':\s*\'application/json\'\s*\},\s*body:\s*JSON\.stringify\(\{\s*message:\s*text\s*\}\)\s*\}\)'
    new_exec = '''const focusSettings = JSON.parse(localStorage.getItem('falk_focus_settings') || '{}');
            fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text, focus_settings: focusSettings })
            })'''

    html = re.sub(old_exec, new_exec, html)

    # Uppdatera Kassa-knappen i Paywall Modal från alert till Stripe Checkout-anrop
    old_btn = r'onclick="alert\(\'Omdirigerar till kassan\.\.\.\'\)"'
    new_btn = 'onclick="triggerStripeCheckout()"'
    html = re.sub(old_btn, new_btn, html)

    # Injektera triggerStripeCheckout i skriptet
    stripe_js = '''
        window.triggerStripeCheckout = function() {
            fetch('/create-checkout-session', { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    if (data.url) {
                        window.location.href = data.url;
                    } else {
                        alert('Kassan laddas: ' + JSON.stringify(data));
                    }
                })
                .catch(err => alert('Kassafeil: ' + err));
        };
    '''
    html = html.replace('</script>', f'{stripe_js}\n</script>', 1)

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("-> [SUCCESS] index.html har kopplats till Fokus-payload och Stripe Checkout!")

print("\n=== FAS 2A, 2B & 2C ÄR SKARPT INTEGRERADE ===")
