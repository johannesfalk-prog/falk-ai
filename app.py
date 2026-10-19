import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
from groq import Groq

app = Flask(__name__)
CORS(app)

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://dmerwpgvepkjirugnfzy.supabase.co")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if GROQ_API_KEY:
    GROQ_API_KEY = GROQ_API_KEY.strip()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY) if SUPABASE_SERVICE_ROLE_KEY else None
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

SYSTEM_PROMPT = """Du är FALK – en kognitiv dagbokspartner och reflektionsspegel för personlig utveckling och mental klarhet.
Din uppgift är att hjälpa användaren att utforska sina tankar, identifiera kognitiva mönster och erbjuda nya perspektiv.

Riktlinjer för dina svar:
1. Svara alltid på svenska.
2. Var empatisk, icke-dömande och kognitivt utmanande på ett mjukt sätt.
3. Håll dina svar koncisa (max 2-3 korta stycken eller en strukturerad punktlista).
4. Avsluta ofta med en öppen, reflekterande fråga som hjälper användaren att gå djupare.
5. Formatera ditt svar med ren Markdown (använd fetstil och punktlistor där det förtydligar)."""

# Aktiva produktionsmodeller på Groq (avvecklade modeller borttagna)
CANDIDATE_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama-3.2-3b-preview",
    "qwen-2.5-coder-32b"
]

def get_authenticated_user_id(req):
    auth_header = req.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None, "Saknar Authorization Bearer header"
    
    token = auth_header.split(" ")[1]
    try:
        if not supabase:
            return None, "Supabase-klienten är inte konfigurerad på servern"
        user_resp = supabase.auth.get_user(token)
        if not user_resp or not user_resp.user:
            return None, "Ogiltig eller utgången session"
        return user_resp.user.id, None
    except Exception as e:
        return None, str(e)

@app.route("/history", methods=["GET"])
def get_history():
    user_id, err = get_authenticated_user_id(request)
    if err:
        return jsonify({"error": err}), 401

    try:
        resp = supabase.table("journal_entries") \
            .select("id, user_message, ai_response, created_at") \
            .eq("user_id", user_id) \
            .order("created_at", desc=False) \
            .execute()
        
        return jsonify({"history": resp.data or []}), 200
    except Exception as e:
        return jsonify({"error": "Kunde inte hämta historik", "details": str(e)}), 500

@app.route("/chat", methods=["POST"])
def chat():
    user_id, err = get_authenticated_user_id(request)
    if err:
        return jsonify({"error": err}), 401

    if not groq_client:
        print("[ERROR] GROQ_API_KEY saknas eller är tom på servern.", file=sys.stderr)
        return jsonify({"error": "AI-motorn är inte initierad på servern."}), 500

    data = request.get_json() or {}
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "Meddelandet får inte vara tomt."}), 400

    try:
        recent_resp = supabase.table("journal_entries") \
            .select("user_message, ai_response") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(15) \
            .execute()

        raw_history = recent_resp.data or []
        raw_history.reverse()

        messages_for_groq = [{"role": "system", "content": SYSTEM_PROMPT}]
        for entry in raw_history:
            if entry.get("user_message"):
                messages_for_groq.append({"role": "user", "content": entry["user_message"]})
            if entry.get("ai_response"):
                messages_for_groq.append({"role": "assistant", "content": entry["ai_response"]})

        messages_for_groq.append({"role": "user", "content": user_message})

        ai_response = None
        last_exception_details = ""

        for model_name in CANDIDATE_MODELS:
            try:
                groq_response = groq_client.chat.completions.create(
                    messages=messages_for_groq,
                    model=model_name,
                    temperature=0.7,
                    max_tokens=1024
                )
                ai_response = groq_response.choices[0].message.content
                if ai_response:
                    print(f"[SUCCESS] Svar genererat med modell: {model_name}")
                    break
            except Exception as model_err:
                last_exception_details = str(model_err)
                print(f"[GROQ ERROR] Modell {model_name} misslyckades: {model_err}", file=sys.stderr)
                continue

        if not ai_response:
            return jsonify({
                "error": "AI-motorn kunde inte nås för tillfället. Försök igen om ett ögonblick.",
                "details": f"Groq felorsak: {last_exception_details}"
            }), 500

        supabase.table("journal_entries").insert({
            "user_id": user_id,
            "user_message": user_message,
            "ai_response": ai_response
        }).execute()

        return jsonify({"response": ai_response}), 200

    except Exception as e:
        print(f"[CRITICAL ERROR] Oväntat fel i /chat: {e}", file=sys.stderr)
        return jsonify({"error": "Ett internt fel uppstod.", "details": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
