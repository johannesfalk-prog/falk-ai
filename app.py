import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client, Client
import dialogue_router

load_dotenv()

app = Flask(__name__)
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
CORS(app, resources={r"/api/*": {"origins": allowed_origins}})

def get_openai_client():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("OPENAI_API_KEY saknas i miljövariablerna.")
    return OpenAI(api_key=key)

supabase_url = os.getenv("SUPABASE_URL", "")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "") or os.getenv("SUPABASE_KEY", "")
supabase: Client = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None

FALK_SYSTEM_PROMPT = """
Du är Falk, den digitala mentorn bakom WAYJS (The Human Navigation Company).
Du har ett fågelperspektiv på människors liv och hjälper dem att navigera med större klarhet, bättre omdöme och hållbara beslut.
Du är inte terapeut, rådgivare, lärare eller en vän som alltid håller med. Du är en klok samtalspartner.

FALKS 5 GRINDAR (THE FIVE GATES):
1. TRUTH: Skilj alltid på fakta, upplevelser, antaganden och känslor. Bekräfta känslan, aldrig tolkningen.
2. HELPFUL: Ge endast information och frågor som för användaren framåt i självinsikt.
3. TIMING: Anpassa tempot efter användarens tillstånd. Hoppa ALDRIG direkt till lösningar om användaren först behöver bli förstådd.
4. ALIGNMENT: Väga resonemanget mot användarens uttalade värderingar och Nordstjärna.
5. INDEPENDENCE: Skapa ALDRIG beroende. Om användaren ber om råd eller direktiv, ge ALDRIG bara ett svar. Presentera alltid minst 2 olika alternativ med för- och nackdelar, och lämna beslutet helt till användaren.

SAMTALETS 7 FASER (THE WAYJS DIALOGUE):
1. TRYGGHET -> 2. FÖRSTÅELSE -> 3. UTFORSKANDE -> 4. PERSPEKTIV -> 5. KLARHET -> 6. HANDLING -> 7. REFLEKTION.

TONALITET & REGLER:
- Lugn, varm, nyfiken, eftertänksam, respektfull, ödmjuk. Korta meningar.
- Använd enkla metaforer för navigering (kompass, fågelperspektiv, dimma, sidvind, nordstjärna) sparsamt.
- Säg ALDRIG: "Jag är ledsen", "Ursäkta", "Som en AI", "Du borde...", "Det är enkelt...", "Det enda du behöver göra...".
- Förbud: Skapa beroende, manipulera, döma, skuldbelägga, låtsas veta.
- Vid krav på medicinsk diagnos/recept eller terapi: "Det här ligger utanför det jag kan bedöma. Jag vill inte ge dig ett svar som riskerar att bli missvisande. Om du vill kan vi tillsammans resonera kring vilka frågor du kan ta med dig till rätt profession."
- Avsluta alltid längre samtal med en reflektionsfråga (t.ex. "Vad tar du med dig?", "Vad känns tydligare nu?").
"""

CRISIS_PATTERNS = [
    r"orkar?\s+inte\s+leva",
    r"vill\s+dö",
    r"ta\s+mitt\s+liv",
    r"avsluta\s+mitt\s+liv",
    r"självmord",
    r"skada\s+mig",
    r"ge\s+upp\s+allt"
]

def check_crisis_guardrail(text: str) -> tuple[bool, str]:
    text_normalized = re.sub(r'\s+', ' ', text.lower().strip())
    for pattern in CRISIS_PATTERNS:
        if re.search(pattern, text_normalized):
            crisis_response = (
                "Jag hör att du har det väldigt tufft just nu, men jag är en digital mentor "
                "och kan inte ge dig det stöd du behöver vid en kris. Du ska inte bära detta ensam.\n\n"
                "Kontakta akuthjälp direkt:\n"
                "• Ring 112 vid akuta situationer.\n"
                "• Självmordslinjen: Ring eller chatta på 90101 (mind.se).\n"
                "• Jourhavande medmänniska: 08-702 16 80.\n\n"
                "Prata med någon i din närhet eller sök professionell hjälp nu."
            )
            return True, crisis_response
    return False, ""

def post_process_guardrail(user_message: str, response_text: str) -> str:
    msg_lower = user_message.lower()
    
    medical_keywords = ["diagnos", "förskriv", "medicin", "recept", "klinisk depression", "behandling"]
    if any(k in msg_lower for k in medical_keywords):
        return ("Det här ligger utanför det jag kan bedöma. Jag vill inte ge dig ett svar som riskerar att bli missvisande. "
                "Om du vill kan vi tillsammans resonera kring vilka frågor du kan ta med dig till rätt profession. "
                "Hur vill du gå vidare just nu?")
                
    cleaned = response_text
    cleaned = re.sub(r"^(jag är ledsen,?\s*men\s*|tyvärr,?\s*men\s*|som en ai,?\s*)", "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip()
    if cleaned and cleaned[0].islower():
        cleaned = cleaned[0].upper() + cleaned[1:]
        
    return cleaned

@app.route('/', methods=['GET'])
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "Falk Core Engine",
        "version": "1.0.0"
    }), 200

@app.route('/api/library/cards', methods=['GET'])
def get_library_cards():
    return jsonify({"cards": [], "total": 0})

@app.route('/api/dialogue/turn', methods=['POST'])
def dialogue_turn():
    try:
        data = request.get_json(silent=True) or {}
        user_id = data.get('user_id') or data.get('userId') or 'beta_guest'
        session_id = data.get('session_id') or data.get('sessionId') or 'sess_default'
        
        # Flexibel utläsning av användarens meddelande
        user_message = (
            data.get('message') or 
            data.get('content') or 
            data.get('prompt') or 
            data.get('user_message') or 
            ''
        ).strip()

        if not user_message:
            return jsonify({"error": "Meddelande saknas"}), 400

        # Anropa dialogue_router eller kärnmotor
        import dialogue_router
        response_data = dialogue_router.process_turn(user_id=user_id, session_id=session_id, message=user_message)
        return jsonify(response_data), 200

    except Exception as e:
        print(f"[ERROR /api/dialogue/turn]: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json() or {}
    user_message = data.get("message") or data.get("content") or data.get("prompt") or data.get("user_message") or data.get("content") or data.get("prompt") or ""
    
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


@app.route('/api/dialogue/reset', methods=['POST'])
def dialogue_reset():
    try:
        data = request.get_json() or {}
        session_id = data.get("session_id")
        user_id = data.get("user_id")
        
        if not session_id and not user_id:
            return jsonify({"status": "error", "message": "Missing session_id or user_id"}), 400
            
        import dialogue_router
        if hasattr(dialogue_router, 'supabase') and dialogue_router.supabase:
            query = dialogue_router.supabase.table("falk_messages").delete()
            if session_id:
                query = query.eq("session_id", session_id)
            elif user_id:
                query = query.eq("user_id", user_id)
            query.execute()
            return jsonify({"status": "success", "message": "Session history cleared successfully"}), 200
        else:
            return jsonify({"status": "error", "message": "Database connection not initialized"}), 500
    except Exception as e:
        print(f"[ERROR /api/dialogue/reset]: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500



from flask import render_template_string

@app.route('/chat')
def chat_page():
    html_content = """<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WAYJS | Falk Core Engine v1.0.0 (WOS Beta)</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --accent-gold: #d97706;
            --accent-blue: #3b82f6;
            --text-main: #f8fafc;
            --text-sub: #94a3b8;
            --border-color: #334155;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        body { background: var(--bg-color); color: var(--text-main); height: 100vh; display: flex; flex-direction: column; }
        
        header { background: #020617; border-bottom: 1px solid var(--border-color); padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-weight: 700; font-size: 1.2rem; letter-spacing: 1px; color: var(--accent-gold); display: flex; align-items: center; gap: 8px; }
        .badge { background: rgba(217, 119, 6, 0.2); color: var(--accent-gold); font-size: 0.75rem; padding: 3px 8px; border-radius: 12px; border: 1px solid var(--accent-gold); }

        .dashboard-container { display: flex; flex: 1; overflow: hidden; }
        
        .chat-section { flex: 1; display: flex; flex-direction: column; border-right: 1px solid var(--border-color); }
        .chat-header { padding: 12px 20px; background: rgba(30, 41, 59, 0.5); border-bottom: 1px solid var(--border-color); font-size: 0.85rem; color: var(--text-sub); display: flex; justify-content: space-between; }
        .chat-messages { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 15px; }
        .message { max-width: 80%; padding: 12px 16px; border-radius: 12px; font-size: 0.95rem; line-height: 1.5; }
        .message.user { align-self: flex-end; background: var(--accent-blue); color: white; border-bottom-right-radius: 2px; }
        .message.assistant { align-self: flex-start; background: var(--card-bg); color: var(--text-main); border: 1px solid var(--border-color); border-bottom-left-radius: 2px; }
        .stage-tag { font-size: 0.7rem; color: var(--accent-gold); text-transform: uppercase; margin-bottom: 4px; font-weight: 600; display: block; }
        
        .chat-input-container { padding: 15px 20px; background: #020617; border-top: 1px solid var(--border-color); display: flex; gap: 10px; }
        input[type="text"] { flex: 1; background: var(--card-bg); border: 1px solid var(--border-color); color: white; padding: 12px 16px; border-radius: 8px; outline: none; font-size: 0.95rem; }
        input[type="text"]:focus { border-color: var(--accent-gold); }
        button { background: var(--accent-gold); color: white; border: none; padding: 12px 24px; border-radius: 8px; font-weight: 600; cursor: pointer; transition: 0.2s; }
        button:hover { opacity: 0.9; }

        .wos-sidebar { width: 380px; background: #090d16; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 25px; }
        .sidebar-title { font-size: 0.9rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: var(--text-sub); margin-bottom: 10px; }
        
        .compass-card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 15px; }
        .score-row { margin-bottom: 12px; }
        .score-row:last-child { margin-bottom: 0; }
        .score-label { display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px; }
        .progress-bar { height: 6px; background: #334155; border-radius: 3px; overflow: hidden; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #d97706, #f59e0b); width: 50%; transition: width 0.5s ease; }

        .journal-card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 15px; }
        .journal-item { border-left: 2px solid var(--accent-gold); padding-left: 10px; margin-bottom: 12px; }
        .journal-item:last-child { margin-bottom: 0; }
        .journal-item h4 { font-size: 0.85rem; color: var(--text-main); margin-bottom: 2px; }
        .journal-item p { font-size: 0.75rem; color: var(--text-sub); line-height: 1.4; }
    </style>
</head>
<body>
    <header>
        <div class="logo">🦅 FALK CORE ENGINE <span class="badge">WOS v1.0.0</span></div>
        <div style="font-size: 0.8rem; color: var(--text-sub);" id="user-display">ID: 11111111</div>
    </header>

    <div class="dashboard-container">
        <div class="chat-section">
            <div class="chat-header">
                <span>Samtalsfas: <strong id="current-stage" style="color: var(--accent-gold);">TRYGGHET</strong></span>
                <span>Mentor Mind™: Aktiverad</span>
            </div>
            <div class="chat-messages" id="chat-messages">
                <div class="message assistant">
                    <span class="stage-tag">TRYGGHET</span>
                    Välkommen. Jag finns här från ett fågelperspektiv för att hjälpa dig navigera dina tankar och beslut. Vad funderar du på just nu?
                </div>
            </div>
            <div class="chat-input-container">
                <input type="text" id="user-input" placeholder="Skriv ditt meddelande till Falk..." onkeydown="if(event.key==='Enter') sendMessage()">
                <button onclick="sendMessage()">Skicka</button>
            </div>
        </div>

        <div class="wos-sidebar">
            <div>
                <div class="sidebar-title">The Compass Score™</div>
                <div class="compass-card">
                    <div class="score-row">
                        <div class="score-label"><span>Riktning</span><span id="score-dir">50%</span></div>
                        <div class="progress-bar"><div class="progress-fill" id="bar-dir" style="width: 50%;"></div></div>
                    </div>
                    <div class="score-row">
                        <div class="score-label"><span>Balans</span><span id="score-bal">50%</span></div>
                        <div class="progress-bar"><div class="progress-fill" id="bar-bal" style="width: 50%;"></div></div>
                    </div>
                    <div class="score-row">
                        <div class="score-label"><span>Handling</span><span id="score-act">50%</span></div>
                        <div class="progress-bar"><div class="progress-fill" id="bar-act" style="width: 50%;"></div></div>
                    </div>
                    <div class="score-row">
                        <div class="score-label"><span>Reflektion</span><span id="score-ref">50%</span></div>
                        <div class="progress-bar"><div class="progress-fill" id="bar-ref" style="width: 50%;"></div></div>
                    </div>
                </div>
            </div>

            <div>
                <div class="sidebar-title">The Compass Journal™</div>
                <div class="journal-card" id="journal-list">
                    <div class="journal-item">
                        <h4>Kapitel 1 - Startpunkten</h4>
                        <p>Första kontakten med Falk Core Engine och påbörjan av hjälteresan.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const userId = '11111111-2222-3333-4444-555555555555';
        let sessionId = 'session_' + Math.random().toString(36).substring(2, 9);

        async function sendMessage() {
            const input = document.getElementById('user-input');
            const msg = input.value.trim();
            if (!msg) return;

            const container = document.getElementById('chat-messages');
            container.innerHTML += `<div class="message user">${msg}</div>`;
            input.value = '';
            container.scrollTop = container.scrollHeight;

            try {
                const res = await fetch('/api/dialogue/turn', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: userId, session_id: sessionId, message: msg })
                });

                if (res.ok) {
                    const data = await res.json();
                    document.getElementById('current-stage').innerText = data.stage || 'TRYGGHET';
                    
                    container.innerHTML += `
                        <div class="message assistant">
                            <span class="stage-tag">${data.stage || 'MENTOR'}</span>
                            ${data.reply}
                        </div>`;
                    container.scrollTop = container.scrollHeight;

                    if (data.compass_score) {
                        updateScore('dir', data.compass_score.direction);
                        updateScore('bal', data.compass_score.balance);
                        updateScore('act', data.compass_score.action);
                        updateScore('ref', data.compass_score.reflection);
                    }
                }
            } catch (err) {
                console.error("Turn error:", err);
            }
        }

        
        window.addEventListener('DOMContentLoaded', loadUserState);

        async function loadUserState() {
            try {
                const res = await fetch(`/api/dialogue/state/${userId}`);
                if (res.ok) {
                    const data = await res.json();
                    if (data.compass_score) {
                        updateScore('dir', data.compass_score.direction);
                        updateScore('bal', data.compass_score.balance);
                        updateScore('act', data.compass_score.action);
                        updateScore('ref', data.compass_score.reflection);
                    }
                    if (data.journal && data.journal.length > 0) {
                        const jContainer = document.getElementById('journal-list');
                        jContainer.innerHTML = '';
                        data.journal.forEach(ch => {
                            jContainer.innerHTML += `
                                <div class="journal-item">
                                    <h4>Kapitel ${ch.chapter_number} - ${ch.chapter_title}</h4>
                                    <p>${ch.summary}</p>
                                </div>`;
                        });
                    }
                }
            } catch (err) {
                console.error("Failed to load user state:", err);
            }
        }

        function updateScore(id, val) {
            if (val === undefined) return;
            document.getElementById(`score-${id}`).innerText = val + '%';
            document.getElementById(`bar-${id}`).style.width = val + '%';
        }
    </script>
</body>
</html>"""
    return render_template_string(html_content)


@app.route('/api/dialogue/state/<user_id>', methods=['GET'])
def get_user_wos_state_explicit(user_id):
    from flask import jsonify
    try:
        from dialogue_router import supabase
    except ImportError:
        supabase = None

    if not supabase:
        return jsonify({"status": "error", "message": "Supabase connection missing"}), 500
    try:
        score_res = supabase.table("falk_compass_score").select("*").eq("user_id", user_id).execute()
        score_data = score_res.data[0] if score_res.data and len(score_res.data) > 0 else {
            "direction_score": 50, "balance_score": 50, "action_score": 50, "reflection_score": 50
        }

        journal_res = supabase.table("falk_compass_journal").select("*").eq("user_id", user_id).order("chapter_number", desc=False).execute()
        journal_data = journal_res.data if journal_res.data else []

        cap_res = supabase.table("falk_capabilities").select("*").eq("user_id", user_id).execute()
        cap_data = cap_res.data if cap_res.data else []

        return jsonify({
            "status": "success",
            "compass_score": {
                "direction": score_data.get("direction_score", 50),
                "balance": score_data.get("balance_score", 50),
                "action": score_data.get("action_score", 50),
                "reflection": score_data.get("reflection_score", 50)
            },
            "journal": journal_data,
            "capabilities": cap_data
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500
