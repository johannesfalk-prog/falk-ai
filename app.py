import os
import traceback
import stripe
from datetime import datetime, timezone
from flask import Flask, request, jsonify, render_template, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
from supabase import create_client, Client
from groq import Groq
from openai import OpenAI
from memory_engine import store_memory, get_relevant_memories, should_store_memory

app = Flask(__name__)
CORS(app)

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=2, x_proto=1, x_host=1, x_prefix=1)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip().strip('"').strip("'")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip().strip('"').strip("'")
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "").strip().strip('"').strip("'")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip().strip('"').strip("'")
if not SUPABASE_SERVICE_KEY:
    SUPABASE_SERVICE_KEY = SUPABASE_ANON_KEY

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "").strip().strip('"').strip("'")
STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID", "").strip().strip('"').strip("'")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "").strip().strip('"').strip("'")

stripe.api_key = STRIPE_SECRET_KEY

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY) if SUPABASE_URL and SUPABASE_SERVICE_KEY else None

SYSTEM_PROMPT = """You are FALK, an elite Socratic CBT guide.
STRICT NEGATIVE CONSTRAINTS:
- NEVER start your response with "Det låter som", "Det verkar som", or "Jag hör att".
- NEVER give numbered lists, generic self-help advice, or preach.

OPERATING RULES:
1. Direct Answer Safety Valve: If the user asks a direct fact question (e.g., "vad gjorde X?"), answer directly in EXACTLY 1 factual sentence first.
2. Socratic Probe: Ask EXACTLY ONE sharp, open-ended question challenging cognitive assumptions or exploring the specific thought.
3. Max Length: Entire response MUST be under 45 words.
4. Language: Always reply in natural Swedish.
"""

def get_current_user_context():
    if 'user_context' in g:
        return g.user_context

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        g.user_context = ("00000000-0000-0000-0000-000000000000", "FREE")
        return g.user_context

    token = auth_header.split(" ")[1]
    if not supabase_client:
        g.user_context = ("00000000-0000-0000-0000-000000000000", "FREE")
        return g.user_context

    try:
        user_response = supabase_client.auth.get_user(token)
        if user_response and user_response.user:
            user_id = user_response.user.id
            try:
                prof = supabase_client.table("profiles").select("tier, trial_ends_at").eq("id", user_id).single().execute()
                if prof.data:
                    tier = prof.data.get("tier")
                    trial_ends = prof.data.get("trial_ends_at")
                    
                    is_trial_active = False
                    if trial_ends:
                        trial_date = datetime.fromisoformat(trial_ends.replace('Z', '+00:00'))
                        if trial_date > datetime.now(timezone.utc):
                            is_trial_active = True

                    if tier == "PRO" or is_trial_active:
                        g.user_context = (user_id, "PRO")
                        return g.user_context
            except Exception as e:
                print(f"[PROFILE LOOKUP FAIL]: {e}", flush=True)

            g.user_context = (user_id, "FREE")
            return g.user_context
    except Exception as e:
        print(f"[AUTH ERROR]: {e}", flush=True)

    g.user_context = ("00000000-0000-0000-0000-000000000000", "FREE")
    return g.user_context

def get_rate_limit_key():
    user_id, _ = get_current_user_context()
    if user_id != "00000000-0000-0000-0000-000000000000":
        return user_id
    
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.remote_addr or get_remote_address()

def get_rate_limit_val():
    _, tier = get_current_user_context()
    if tier == "PRO":
        return "60 per day"
    return "5 per day"

limiter = Limiter(
    get_rate_limit_key,
    app=app,
    default_limits=["100 per day"],
    storage_uri="memory://"
)

@app.errorhandler(429)
def ratelimit_handler(e):
    _, tier = get_current_user_context()
    limit_str = "60 meddelanden" if tier == "PRO" else "5 meddelanden"
    return jsonify({
        "error": f"Du har nått din dagliga gräns på {limit_str}. Välkommen tillbaka imorgon eller uppgradera till PRO.",
        "limit_reached": True,
        "tier": tier
    }), 429

@app.route("/")
def index():
    return render_template("index.html", supabase_url=SUPABASE_URL, supabase_anon_key=SUPABASE_ANON_KEY)

@app.route("/api/sessions", methods=["GET", "POST"])
def handle_sessions():
    user_id, _ = get_current_user_context()
    if user_id == "00000000-0000-0000-0000-000000000000":
        return jsonify({"error": "Obehörig"}), 401

    if request.method == "POST":
        data = request.json or {}
        title = data.get("title", "Nytt samtalsrum")
        res = supabase_client.table("chat_sessions").insert({"user_id": user_id, "title": title}).execute()
        return jsonify(res.data[0] if res.data else {})

    res = supabase_client.table("chat_sessions").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    return jsonify(res.data or [])

@app.route("/api/sessions/<session_id>/messages", methods=["GET"])
def get_session_messages(session_id):
    user_id, _ = get_current_user_context()
    if user_id == "00000000-0000-0000-0000-000000000000":
        return jsonify({"error": "Obehörig"}), 401

    res = supabase_client.table("chat_messages").select("*").eq("session_id", session_id).order("created_at", desc=False).execute()
    return jsonify(res.data or [])

@app.route("/api/journal", methods=["GET", "POST"])
def handle_journal():
    user_id, _ = get_current_user_context()
    if user_id == "00000000-0000-0000-0000-000000000000":
        return jsonify({"error": "Obehörig"}), 401

    if request.method == "POST":
        data = request.json or {}
        mood_score = data.get("mood_score")
        entry_text = data.get("entry_text", "").strip()

        if not mood_score or not entry_text:
            return jsonify({"error": "Både skattning och text krävs."}), 400

        res = supabase_client.table("journal_entries").insert({
            "user_id": user_id,
            "mood_score": mood_score,
            "entry_text": entry_text
        }).execute()
        return jsonify(res.data[0] if res.data else {})

    res = supabase_client.table("journal_entries").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    return jsonify(res.data or [])

# GDPR FULL ACCOUNT & DATA DELETION
@app.route("/delete-user-data", methods=["DELETE"])
def delete_user_data():
    user_id, _ = get_current_user_context()
    if user_id == "00000000-0000-0000-0000-000000000000":
        return jsonify({"error": "Obehörig"}), 401

    try:
        if supabase_client:
            # 1. Radera applikationsdata
            supabase_client.table("user_memories").delete().eq("user_id", user_id).execute()
            supabase_client.table("journal_entries").delete().eq("user_id", user_id).execute()
            supabase_client.table("chat_sessions").delete().eq("user_id", user_id).execute()
            supabase_client.table("profiles").delete().eq("id", user_id).execute()
            
            # 2. Radera auth-konto via Admin API (Artikel 17)
            try:
                supabase_client.auth.admin.delete_user(user_id)
            except Exception as admin_err:
                print(f"[AUTH ADMIN DELETE FAIL]: {admin_err}", flush=True)

        return jsonify({"status": "success", "message": "All data och ditt konto har raderats permanent."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    try:
        user_id, _ = get_current_user_context()
        if user_id == "00000000-0000-0000-0000-000000000000":
            return jsonify({"error": "Du måste vara inloggad för att uppgradera till PRO."}), 401

        checkout_session = stripe.checkout.Session.create(
            line_items=[{'price': STRIPE_PRICE_ID, 'quantity': 1}],
            mode='subscription',
            client_reference_id=user_id,
            success_url=request.host_url + '?payment=success',
            cancel_url=request.host_url + '?payment=cancelled',
        )
        return jsonify({"url": checkout_session.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/stripe-webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature")

    if not STRIPE_WEBHOOK_SECRET or not sig_header:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        return jsonify({"error": "Invalid signature"}), 400

    event_type = getattr(event, "type", None) or event.get("type")
    data_object = getattr(getattr(event, "data", None), "object", {}) or event.get("data", {}).get("object", {})

    if event_type == "checkout.session.completed":
        user_id = getattr(data_object, "client_reference_id", None) or data_object.get("client_reference_id")
        customer_id = getattr(data_object, "customer", None) or data_object.get("customer")

        if user_id and supabase_client:
            supabase_client.table("profiles").update({"tier": "PRO", "stripe_customer_id": customer_id}).eq("id", user_id).execute()

    return jsonify({"status": "success"}), 200

@app.route("/chat", methods=["POST"])
@limiter.limit(get_rate_limit_val, key_func=get_rate_limit_key)
def chat():
    try:
        data = request.json or {}
        user_message = data.get("message", "").strip()
        session_id = data.get("session_id")

        if not user_message:
            return jsonify({"error": "Meddelandet kan inte vara tomt"}), 400

        user_id, tier = get_current_user_context()
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
            for model_name in ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"]:
                try:
                    completion = groq_client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": f"{memory_context}\n\n{user_message}"}
                        ],
                        temperature=0.4,
                        max_tokens=120
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
                    temperature=0.4,
                    max_tokens=120
                )
                ai_response = completion.choices[0].message.content
                used_provider = "OpenAI (gpt-4o-mini)"
            except Exception:
                pass

        if ai_response:
            if session_id and user_id != "00000000-0000-0000-0000-000000000000":
                try:
                    supabase_client.table("chat_messages").insert([
                        {"session_id": session_id, "sender": "user", "content": user_message},
                        {"session_id": session_id, "sender": "bot", "content": ai_response}
                    ]).execute()
                except Exception as db_err:
                    print(f"[CHAT MSG DB SAVE FAIL]: {db_err}", flush=True)

            return jsonify({
                "response": ai_response,
                "tier": tier,
                "memories_retrieved": len(memories),
                "provider": used_provider
            })
            
        return jsonify({"error": "Ingen AI-leverantör kunde svara."}), 500

    except Exception as e:
        return jsonify({"error": f"Internt serverfel: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
