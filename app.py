import os
import traceback
import stripe
from flask import Flask, request, jsonify, render_template, redirect
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from supabase import create_client, Client
from groq import Groq
from openai import OpenAI
from memory_engine import store_memory, get_relevant_memories, should_store_memory

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip().strip('"').strip("'")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip().strip('"').strip("'")
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip().strip('"').strip("'")
if not SUPABASE_SERVICE_KEY:
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_ANON_KEY", "").strip().strip('"').strip("'")

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "").strip().strip('"').strip("'")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "").strip().strip('"').strip("'")
STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID", "").strip().strip('"').strip("'")

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY) if SUPABASE_URL and SUPABASE_SERVICE_KEY else None

SYSTEM_PROMPT = """You are FALK, an elite Socratic Cognitive Behavioral Therapy (CBT) AI guide.
YOUR CORE RULE: Never lecture, never give numbered lists, and never preach generic self-help advice.

Operating Principles:
1. Validate briefly: Acknowledge the user's emotion/statement in 1 short sentence.
2. Socratic Probe: Ask EXACTLY ONE sharp, open-ended question that highlights cognitive distortions or challenges assumptions.
3. Length Limit: Keep your entire response under 60 words.
4. Language: Always reply in Swedish.
"""

def extract_user_tier(req):
    auth_header = req.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return "00000000-0000-0000-0000-000000000000", "FREE"
    
    token = auth_header.split(" ")[1]
    if not supabase_client:
        return "00000000-0000-0000-0000-000000000000", "FREE"

    try:
        user_response = supabase_client.auth.get_user(token)
        if user_response and user_response.user:
            user_id = user_response.user.id
            try:
                prof = supabase_client.table("profiles").select("tier").eq("id", user_id).single().execute()
                if prof.data and prof.data.get("tier") == "PRO":
                    return user_id, "PRO"
            except Exception as e:
                print(f"[PROFILE LOOKUP FAIL]: {e}", flush=True)

            return user_id, "FREE"
    except Exception as e:
        print(f"[AUTH ERROR]: {e}", flush=True)

    return "00000000-0000-0000-0000-000000000000", "FREE"

def get_rate_limit_key():
    user_id, _ = extract_user_tier(request)
    if user_id != "00000000-0000-0000-0000-000000000000":
        return user_id
    return get_remote_address()

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per day"],
    storage_uri="memory://"
)

@app.route("/")
def index():
    return render_template("index.html", supabase_url=SUPABASE_URL, supabase_anon_key=SUPABASE_ANON_KEY)

@app.route("/chat", methods=["POST"])
@limiter.limit("5 per day", key_func=get_rate_limit_key) # Strict 5/day limit for FREE
def chat():
    try:
        data = request.json or {}
        user_message = data.get("message", "").strip()
        if not user_message:
            return jsonify({"error": "Meddelandet kan inte vara tomt"}), 400

        user_id, tier = extract_user_tier(request)
        memories = []

        if tier == "PRO" and user_id != "00000000-0000-0000-0000-000000000000":
            try:
                memories = get_relevant_memories(user_id, user_message)
                if should_store_memory(user_message):
                    store_memory(user_id, user_message)
            except Exception as mem_err:
                print(f"[RAG ERROR]: {mem_err}", flush=True)

        memory_context = ""
        if memories:
            memory_context = "\nRelevant historisk kontext om användaren:\n" + "\n".join([f"- {m}" for m in memories])

        ai_response = None
        used_provider = None

        if groq_client:
            for model_name in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]:
                try:
                    completion = groq_client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": f"{memory_context}\n\n{user_message}"}
                        ],
                        temperature=0.5,
                        max_tokens=150
                    )
                    ai_response = completion.choices[0].message.content
                    if ai_response:
                        used_provider = f"Groq ({model_name})"
                        break
                except Exception:
                    pass

        if not ai_response and openai_client:
            try:
                completion = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"{memory_context}\n\n{user_message}"}
                    ],
                    temperature=0.5,
                    max_tokens=150
                )
                ai_response = completion.choices[0].message.content
                used_provider = "OpenAI (gpt-4o-mini)"
            except Exception as o_err:
                print(f"[OPENAI FAIL]: {o_err}", flush=True)

        if ai_response:
            return jsonify({
                "response": ai_response,
                "tier": tier,
                "memories_retrieved": len(memories),
                "provider": used_provider
            })
            
        return jsonify({"error": "Ingen AI-leverantör kunde svara."}), 500

    except Exception as e:
        return jsonify({"error": f"Internt serverfel: {str(e)}"}), 500

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    try:
        user_id, _ = extract_user_tier(request)
        if user_id == "00000000-0000-0000-0000-000000000000":
            return jsonify({"error": "Du måste vara inloggad för att uppgradera."}), 401

        domain_url = request.host_url.rstrip('/')
        checkout_session = stripe.checkout.Session.create(
            client_reference_id=user_id,
            payment_method_types=['card'],
            line_items=[{
                'price': STRIPE_PRICE_ID,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=domain_url + '/?success=true',
            cancel_url=domain_url + '/?canceled=true',
        )
        return jsonify({'url': checkout_session.url})
    except Exception as e:
        print(f"[STRIPE CHECKOUT ERROR]: {e}", flush=True)
        return jsonify({'error': str(e)}), 500

@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        return 'Invalid signature', 400

    # Hantera lyckad betalning
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session.get('client_reference_id')
        customer_id = session.get('customer')

        if user_id and supabase_client:
            supabase_client.table("profiles").update({
                "tier": "PRO",
                "stripe_customer_id": customer_id
            }).eq("id", user_id).execute()
            print(f"[STRIPE SUCCESS]: User {user_id} uppgraderad till PRO!", flush=True)

    # Hantera avslutad prenumeration
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        customer_id = subscription.get('customer')

        if customer_id and supabase_client:
            supabase_client.table("profiles").update({
                "tier": "FREE"
            }).eq("stripe_customer_id", customer_id).execute()
            print(f"[STRIPE REVOKED]: Customer {customer_id} nedgraderad till FREE.", flush=True)

    return jsonify({'status': 'success'}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
