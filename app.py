import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client, ClientOptions
from groq import Groq

app = Flask(__name__)
CORS(app)

SUPABASE_URL = "https://dmerwpgvepkjirugnfzy.supabase.co"

def get_supabase_client(token=None) -> Client:
    anon_key = os.environ.get("SUPABASE_ANON_KEY")
    if not anon_key:
        raise RuntimeError("SUPABASE_ANON_KEY saknas i miljövariablerna på servern.")
    
    if token:
        opts = ClientOptions(headers={"Authorization": f"Bearer {token}"})
        return create_client(SUPABASE_URL, anon_key, options=opts)
    
    return create_client(SUPABASE_URL, anon_key)

@app.route('/history', methods=['GET'])
def get_history():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Obehörig", "details": "Saknar Bearer-token"}), 401

    token = auth_header.split(' ')[1]

    try:
        # Validera token
        supabase_admin = get_supabase_client()
        user_response = supabase_admin.auth.get_user(token)
        if not user_response or not user_response.user:
            return jsonify({"error": "Obehörig", "details": "Ogiltig token"}), 401
        
        user_id = user_response.user.id

        # Hämta de 20 senaste inläggen sorterade kronologiskt (äldst först för chattvy)
        supabase_user_client = get_supabase_client(token=token)
        history_response = supabase_user_client.table("journal_entries")\
            .select("user_message, ai_response, created_at")\
            .eq("user_id", user_id)\
            .order("created_at", desc=False)\
            .limit(20)\
            .execute()

        return jsonify({"history": history_response.data or []})

    except Exception as e:
        return jsonify({"error": "Serverfel", "details": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Obehörig", "details": "Saknar Bearer-token"}), 401

    token = auth_header.split(' ')[1]

    try:
        supabase_admin = get_supabase_client()
        user_response = supabase_admin.auth.get_user(token)
        if not user_response or not user_response.user:
            return jsonify({"error": "Obehörig", "details": "Ogiltig eller utgången token"}), 401
        user_id = user_response.user.id
    except Exception as e:
        return jsonify({"error": "Obehörig", "details": f"Token-validering misslyckades: {str(e)}"}), 401

    data = request.get_json() or {}
    user_message = data.get('message', '').strip()
    if not user_message:
        return jsonify({"error": "Bad Request", "details": "Meddelande saknas"}), 400

    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        return jsonify({"error": "Serverfel", "details": "GROQ_API_KEY saknas i serverns miljövariabler"}), 500

    try:
        supabase_user_client = get_supabase_client(token=token)

        # Hämta tidigare dagbokskontext (senaste 5 inläggen)
        history_response = supabase_user_client.table("journal_entries")\
            .select("user_message, ai_response")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(5)\
            .execute()

        messages = [
            {"role": "system", "content": "Du är FALK, en kognitiv samtalspartner och dagboksmotor. Svara insiktsfullt, reflektivt och kortfattat på svenska. Använd tidigare kontext för att bygga en kontinuerlig förståelse för användaren."}
        ]

        if history_response.data:
            for entry in reversed(history_response.data):
                messages.append({"role": "user", "content": entry.get("user_message", "")})
                messages.append({"role": "assistant", "content": entry.get("ai_response", "")})

        messages.append({"role": "user", "content": user_message})

        groq_client = Groq(api_key=groq_api_key)
        selected_model = os.environ.get("GROQ_MODEL")

        if not selected_model:
            try:
                models_list = groq_client.models.list()
                valid_chat_models = [m.id for m in models_list.data if "whisper" not in m.id.lower()]
                selected_model = valid_chat_models[0] if valid_chat_models else "llama-3.3-70b-versatile"
            except Exception:
                selected_model = "llama-3.3-70b-versatile"

        chat_completion = groq_client.chat.completions.create(
            messages=messages,
            model=selected_model,
        )
        ai_response = chat_completion.choices[0].message.content

        # Skriv till Supabase
        supabase_user_client.table("journal_entries").insert({
            "user_id": user_id,
            "user_message": user_message,
            "ai_response": ai_response
        }).execute()

        return jsonify({"response": ai_response})

    except Exception as e:
        return jsonify({"error": "Serverfel", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
