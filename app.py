import os
import jwt
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

ALLOWED_ORIGINS = [
    "https://falk-frontend.onrender.com",
    "http://localhost:8000",
    "http://127.0.0.1:8000"
]

CORS(app, resources={r"/*": {"origins": ALLOWED_ORIGINS}}, supports_credentials=True)

SUPABASE_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET")

def verify_jwt(req):
    auth_header = req.headers.get("Authorization")
    if not auth_header:
        return None, "Authorization header saknas."

    try:
        token = auth_header.split(" ")[1]
    except IndexError:
        return None, "Ogiltigt Authorization-headerformat. Använd 'Bearer <token>'."

    if not SUPABASE_JWT_SECRET:
        return None, "SUPABASE_JWT_SECRET saknas i miljövariabler."

    try:
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, "Token har löpt ut."
    except jwt.InvalidTokenError as e:
        return None, f"Ogiltig token: {str(e)}"

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "online", "service": "FALK-AI Backend"}), 200

@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    user_payload, error = verify_jwt(request)
    if error:
        return jsonify({"error": "Obehörig", "details": error}), 401

    user_id = user_payload.get("sub")
    data = request.get_json() or {}
    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "Meddelande saknas."}), 400

    system_response = f"FALK svarar: Mottog '{user_message}' från användare {user_id}."

    return jsonify({
        "response": system_response,
        "user_id": user_id
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
