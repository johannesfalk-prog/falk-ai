import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
from groq import Groq

app = Flask(__name__)
CORS(app)

SUPABASE_URL = "https://dmerwpgvepkjirugnfzy.supabase.co"

def get_supabase_client(token=None) -> Client:
    anon_key = os.environ.get("SUPABASE_ANON_KEY")
    if not anon_key:
        raise RuntimeError("SUPABASE_ANON_KEY saknas i miljövariablerna på servern.")
    
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return create_client(SUPABASE_URL, anon_key, options={"headers": headers})

@app.route('/chat', methods=['POST'])
def chat():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Obehörig", "details": "Saknar Bearer-token"}), 401

    token = auth_header.split(' ')[1]

    # Validera token via Supabase Auth
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
        groq_client = Groq(api_key=groq_api_key)
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Du är FALK, en kognitiv samtalspartner och dagboksmotor. Svara insiktsfullt och kortfattat på svenska."},
                {"role": "user", "content": user_message}
            ],
            model="llama-3.3-70b-versatile",
        )
        ai_response = chat_completion.choices[0].message.content

        # Skriv till Supabase med användarens token (RLS)
        supabase_user_client = get_supabase_client(token=token)
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
