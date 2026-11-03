from flask import Flask, render_template, request, jsonify, Response, stream_with_context
import time

app = Flask(__name__)

# ==========================================
# 1. HUVUDSIDOR & SUBPAGES
# ==========================================

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

# ==========================================
# 2. CHATT & INSIGHTS API
# ==========================================

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json() or {}
    user_message = data.get('message', '')
    
    # Simulera betänketid i backend
    time.sleep(1.0)

    reply_prefix = f"Jag hör vad du säger gällande: \"{user_message}\".\n\n"
    reply_body = "När vi stannar upp och sorterar våra tankar framträder ofta en ny klarhet. Vad är det viktigaste steget för dig i denna stund?"
    
    return reply_prefix + reply_body, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/api/insights', methods=['POST'])
def api_insights():
    data = request.get_json() or {}
    print(f"-> [BACKEND INSIGHT SAVED] {data}")
    return jsonify({"status": "success", "received": data})

@app.route('/api/user/export', methods=['GET'])
def export_user_data():
    sample_data = {
        "user_status": "Gäst",
        "export_date": "2026-11-02",
        "reflections_count": 18,
        "saved_insights": [
            "Att sätta gränser handlar inte om att stänga andra ute, utan om att hålla sig själv hel."
        ],
        "history": [
            {"date": "2026-11-01", "category": "Mening & livsriktning", "prompt": "Jag vill förstå min riktning"}
        ]
    }
    return jsonify(sample_data)

@app.route('/api/user/delete', methods=['DELETE', 'POST'])
def delete_user_account():
    print("-> [BACKEND NOTICE] Användardata och konto raderat.")
    return jsonify({"status": "success", "message": "All data har raderats."})

if __name__ == '__main__':
    print("=== FALK BACKEND SERVER STARTAR PÅ PORT 5001 ===")
    app.run(host='0.0.0.0', port=5001, debug=True)
