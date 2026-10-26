from falk_prompt import get_falk_system_prompt
import os
import traceback
import stripe
from datetime import datetime, timezone
from flask import Flask, request, jsonify, render_template, g, Response
import json
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

BASE_SYSTEM_PROMPT = """Du är FALK – en elitcoach och expert inom Neurolingvistisk Programmering (NLP) och Sokratisk dialog.
Din uppgift är att hjälpa användaren att nå kognitiv klarhet, utmana sina egna antaganden och hitta sina egna svar.

DINA NLP-KÄRNPRINCIPER:
1. LINGVISTISK INTERCEPTION (Meta-modellen):
   - Identifiera och utmana generaliseringar ("alla", "aldrig", "ingen").
   - Utmana förvrängningar och tankeläsning ("han tror att...", "det kommer bli katastrof").
   - Omvandla passiva nominaliseringar till aktiva handlingar ("det finns inget hopp" -> "vad kan du göra just nu?").

2. REFRAMING (Omramning):
   - Hjälp användaren att skifta ram från Hinder -> Resurs, och från Problem -> Möjlighet.
   - Ändra skala eller tidslinje när tankarna låser sig ("Hur ser du på detta om 3 år?").

3. STRUKTUR I DINA SVAR:
   - Max 2-4 meningar per svar. Var extremt koncis och kraftfull.
   - Ge ALDRIG långa punktlistor om användaren inte uttryckligen ber om det.
   - Avsluta NÄSTAN ALLTID med EN enda knivskarp, öppen Sokratisk fråga.
   - Använd ett lugnt, gles, akademiskt och direkt språk ("En kompass med perspektiv").
"""

def build_system_prompt(focus_data=None):
    prompt = BASE_SYSTEM_PROMPT
    if focus_data and isinstance(focus_data, dict):
        focus_instructions = []
        if focus_data.get("confidence", 50) > 60:
            focus_instructions.append("Focus on strengthening self-confidence and self-worth.")
        if focus_data.get("stress", 50) > 60:
            focus_instructions.append("Focus heavily on stress reduction, grounding, and calming the mind.")
        if focus_data.get("action", 50) > 60:
            focus_instructions.append("Focus on agency, decisive action, and practical small steps.")
        if focus_data.get("boundaries", 50) > 60:
            focus_instructions.append("Focus on setting clear personal boundaries and saying no.")
        if focus_data.get("motivation", 50) > 60:
            focus_instructions.append("Focus on internal motivation, drive, and personal values.")
        
        if focus_instructions:
            prompt += "\nCURRENT USER FOCUS PRIORITIES:\n- " + "\n- ".join(focus_instructions) + "\n"
    return prompt

def generate_session_title(user_message):
    if not groq_client:
        return user_message[:25]
    try:
        res = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Skapa en ultrakort sammanfattande rubrik (2-4 ord på svenska) för ett samtal som börjar med användarens meddelande. Svara enbart med rubriken utan citationstecken."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=effective_max_tokens,
            temperature=0.3
        )
        title = res.choices[0].message.content.strip().replace('"', '')
        return title if title else user_message[:25]
    except Exception:
        return user_message[:25]

def get_current_user_context():
    if 'user_context' in g:
        return g.user_context

    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    elif request.args.get("token"):
        token = request.args.get("token")

    if not token or not supabase_client:
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
    return "6 per day"

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

@app.route("/api/resolve-username", methods=["POST"])
def resolve_username():
    data = request.json or {}
    identifier = data.get("identifier", "").strip()
    
    if "@" in identifier:
        return jsonify({"email": identifier})
    
    if supabase_client:
        try:
            res = supabase_client.table("profiles").select("email").eq("username", identifier).execute()
            if res.data and len(res.data) > 0:
                return jsonify({"email": res.data[0]["email"]})
        except Exception as e:
            print(f"[USERNAME RESOLVE FAIL]: {e}", flush=True)
            
    return jsonify({"error": "Användarnamnet kunde inte hittas."}), 404

@app.route('/api/profile', methods=['GET'])
def get_profile():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"status": "guest", "message": "No auth token provided"}), 200
        # Om token finns men misslyckas, fånga felet städat
        return jsonify({"status": "ok", "profile": {}}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 200
@app.route('/api/sessions', methods=['GET', 'POST'])
def handle_sessions():
    try:
        if request.method == 'POST':
            data = request.get_json() or {}
            session_id = data.get('id', 'session_default')
            return jsonify({"status": "ok", "id": session_id}), 200
        return jsonify([]), 200
    except Exception as e:
        return jsonify({"status": "ok"}), 200
@app.route("/api/sessions/<session_id>/messages", methods=["GET"])
def get_session_messages(session_id):
    user_id, _ = get_current_user_context()
    if user_id == "00000000-0000-0000-0000-000000000000":
        return jsonify({"error": "Obehörig"}), 401

    res = supabase_client.table("chat_messages").select("*").eq("session_id", session_id).order("created_at", desc=False).execute()
    return jsonify(res.data or [])

@app.route('/api/journal', methods=['GET'])
def get_journal():
    try:
        # Returnera tom lista vid fel eller saknad auth istället för 500
        return jsonify([]), 200
    except Exception as e:
        return jsonify([]), 200
@app.route("/api/export-user-data", methods=["GET"])
def export_user_data():
    user_id, _ = get_current_user_context()
    if user_id == "00000000-0000-0000-0000-000000000000":
        return jsonify({"error": "Obehörig"}), 401

    try:
        profile = supabase_client.table("profiles").select("*").eq("id", user_id).execute().data
        memories = supabase_client.table("user_memories").select("*").eq("user_id", user_id).execute().data
        sessions = supabase_client.table("chat_sessions").select("*").eq("user_id", user_id).execute().data
        journals = supabase_client.table("journal_entries").select("*").eq("user_id", user_id).execute().data

        all_data = {
            "export_date": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "profile": profile,
            "user_memories": memories,
            "chat_sessions": sessions,
            "journal_entries": journals
        }

        json_output = json.dumps(all_data, indent=2, ensure_ascii=False)
        return Response(
            json_output,
            mimetype="application/json",
            headers={"Content-Disposition": f"attachment;filename=falk_userdata_{user_id[:8]}.json"}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/delete-user-data", methods=["DELETE"])
def delete_user_data():
    user_id, _ = get_current_user_context()
    if user_id == "00000000-0000-0000-0000-000000000000":
        return jsonify({"error": "Obehörig"}), 401

    try:
        if supabase_client:
            supabase_client.table("user_memories").delete().eq("user_id", user_id).execute()
            supabase_client.table("journal_entries").delete().eq("user_id", user_id).execute()
            supabase_client.table("chat_sessions").delete().eq("user_id", user_id).execute()
            supabase_client.table("profiles").delete().eq("id", user_id).execute()
            
            try:
                supabase_client.auth.admin.delete_user(user_id)
            except Exception as admin_err:
                print(f"[AUTH ADMIN DELETE FAIL]: {admin_err}", flush=True)

        return jsonify({"status": "success", "message": "All data och ditt konto har raderats permanent."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json or {}
        user_message = data.get("message", "").strip()
        session_id = data.get("session_id")
        focus_data = data.get("focus")

        if not user_message:
            return jsonify({"error": "Meddelandet kan inte vara tomt"}), 400

        user_id, tier = get_current_user_context()

        # Identifiera om användaren är oinloggad gäst eller registrerad medlem
        is_guest = (user_id == "00000000-0000-0000-0000-000000000000" or not user_id)
        is_pro = (tier == "PRO" and not is_guest)
        effective_max_tokens = 750 if is_pro else 350

        # Gästkvotering (Max 6 meddelanden) gäller ENBART oinloggade gäster
        if is_guest:
            from datetime import datetime
            today_str = datetime.now().strftime("%Y-%m-%d")
            raw_cookie = request.cookies.get("falk_guest_count", "")
            
            if ":" in raw_cookie:
                c_count, c_date = raw_cookie.split(":", 1)
                guest_count = int(c_count) if c_date == today_str and c_count.isdigit() else 0
            else:
                # Gamla cookies utan datumstämpel är ogiltiga -> Nollställ direkt!
                guest_count = 0

            if guest_count >= 6:
                return jsonify({
                    "error": "GUEST_LIMIT_REACHED",
                    "message": "Du har nått din dagliga gratiskvot (6 meddelanden). Välkommen tillbaka imorgon när din kvot återställts, eller uppgradera till FALK Premium för obegränsad tillgång direkt."
                }), 403

        memories = []
        if is_pro:
            try:
                memories = get_relevant_memories(user_id, user_message)
                if should_store_memory(user_message):
                    store_memory(user_id, user_message)
            except Exception as mem_err:
                print(f"[RAG ERROR]: {mem_err}", flush=True)

        memory_context = ""
        if memories:
            memory_context = "\nRelevant historisk kontext om användaren:\n" + "\n".join([f"- {m}" for m in memories])

        system_prompt = get_falk_system_prompt() + "\n\n" + build_system_prompt(focus_data)

        ai_response = None
        used_provider = None

        if groq_client:
            for model_name in ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"]:
                try:
                    completion = groq_client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"{memory_context}\n\n{user_message}"}
                        ],
                        temperature=0.4,
                        max_tokens=effective_max_tokens
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
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"{memory_context}\n\n{user_message}"}
                    ],
                    temperature=0.4,
                    max_tokens=effective_max_tokens
                )
                ai_response = completion.choices[0].message.content
                used_provider = "OpenAI (gpt-4o-mini)"
            except Exception:
                pass

        if not ai_response:
            return jsonify({"error": "Kunde inte generera svar från AI-tjänsten."}), 500

        resp = jsonify({"response": ai_response, "provider": used_provider})

        # Uppdatera gästcookie
        if not is_pro:
            from datetime import datetime
            today_str = datetime.now().strftime("%Y-%m-%d")
            raw_cookie = request.cookies.get("falk_guest_count", "")
            
            if ":" in raw_cookie:
                c_count, c_date = raw_cookie.split(":", 1)
                guest_count = int(c_count) if c_date == today_str and c_count.isdigit() else 0
            else:
                # Gamla cookies utan datumstämpel är ogiltiga -> Nollställ direkt!
                guest_count = 0
            resp.set_cookie("falk_guest_count", f"{guest_count + 1}:{today_str}", max_age=86400, path="/", samesite="Lax")

        return resp, 200

    except Exception as e:
        print(f"[CHAT ERROR]: {e}", flush=True)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)


@app.errorhandler(500)
def handle_500_error(e):
    from flask import jsonify
    return jsonify({"error": "Internal server error", "details": str(e)}), 500
