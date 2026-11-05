import os

app_file = "app.py"

backend_routes = '''

# ==========================================
# FALK BACKEND CHAT & INSIGHTS API (STEG 2)
# ==========================================
from flask import Response, stream_with_context, request, jsonify
import time

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json() or {}
    user_message = data.get('message', '')

    def generate():
        reply_prefix = f"Jag hör vad du säger gällande: '{user_message}'. "
        reply_body = "När vi stannar upp och sorterar våra tankar framträder ofta en tydlig väg framåt. Vad är det viktigaste steget för dig just nu?"
        
        full_text = reply_prefix + reply_body
        for word in full_text.split(" "):
            yield word + " "
            time.sleep(0.04)

    return Response(stream_with_context(generate()), mimetype='text/plain')

@app.route('/api/insights', methods=['POST'])
def api_insights():
    data = request.get_json() or {}
    # Här kan du persistera till databasen
    print(f"-> [BACKEND INSIGHT SAVED] {data}")
    return jsonify({"status": "success", "received": data})
'''

if os.path.exists(app_file):
    with open(app_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "/api/chat" not in content:
        with open(app_file, "a", encoding="utf-8") as f:
            f.write(backend_routes)
        print("-> [SUCCESS] Backend endpoints /api/chat och /api/insights har lagts till i app.py!")
    else:
        print("-> [NOTICE] /api/chat finns redan i app.py.")
