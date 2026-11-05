import os

print("=== FIXERAR EXAKT FALK26 SPECIFIKATION I TEMPLATES/INDEX.HTML ===")

templates_dir = "templates"
os.makedirs(templates_dir, exist_ok=True)

falk26_code = '''<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, interactive-widget=resizes-content">
    <title>FALK – Din kompass med perspektiv</title>
    <link rel="manifest" href="/manifest.json">
    <link rel="icon" type="image/svg+xml" href="/icon.svg">
    <meta name="theme-color" content="#E8DCC4">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/dompurify/3.0.6/purify.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.min.js"></script>
    <style>
        :root {
            /* EXAKT FÄRGPALETT FALK26 */
            --warm-beige: #E8DCC4;
            --warm-beige-light: #F7F3E9;
            --terracotta: #C57B57;
            --deep-olive: #4E5C4B;
            --soft-sage: #A8BFA1;
            
            --text-dark: #2C352B;
            --text-muted: #6B7B68;
            --white: #FFFFFF;
            --card-shadow: 0 4px 15px rgba(78, 92, 75, 0.08);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            background-color: var(--warm-beige-light);
            color: var(--text-dark);
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        /* HEADER NAV: HAMBURGER VÄNSTER, GLÖDLAMPA HÖGER */
        .header-nav {
            position: relative;
            background-color: var(--warm-beige-light);
            padding: 12px 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            max-width: 768px;
            margin: 0 auto;
            width: 100%;
            border-bottom: 1px solid rgba(78, 92, 75, 0.15);
            z-index: 10;
        }

        .header-left-group, .header-right-group {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .icon-nav-btn {
            background-color: var(--white);
            color: var(--deep-olive);
            border: 1px solid rgba(78, 92, 75, 0.2);
            width: 38px;
            height: 38px;
            border-radius: 12px;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
            box-shadow: var(--card-shadow);
        }

        .icon-nav-btn:hover { background-color: var(--warm-beige); }

        .badge-pill {
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.7rem;
            font-weight: 800;
            letter-spacing: 0.6px;
            text-transform: uppercase;
        }

        .badge-pill.guest {
            background-color: var(--warm-beige);
            color: var(--terracotta);
            border: 1px solid var(--terracotta);
        }

        .badge-pill.logged-in {
            background-color: var(--deep-olive);
            color: var(--white);
            border: 1px solid var(--deep-olive);
        }

        .header-brand-title {
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            font-size: 1.4rem;
            font-weight: 900;
            color: var(--deep-olive);
            letter-spacing: 1.2px;
            cursor: pointer;
        }

        /* MAIN CONTAINER */
        .main-container {
            flex: 1;
            overflow-y: auto;
            padding: 16px 20px;
            display: flex;
            flex-direction: column;
            gap: 16px;
            max-width: 768px;
            margin: 0 auto;
            width: 100%;
        }

        .welcome-card {
            background-color: var(--white);
            border-radius: 16px;
            padding: 20px;
            box-shadow: var(--card-shadow);
            border: 1px solid rgba(78, 92, 75, 0.08);
            margin-bottom: 8px;
        }

        .welcome-card h2 { font-size: 1.15rem; color: var(--deep-olive); font-weight: 800; margin-bottom: 4px; }
        .welcome-card p { font-size: 0.92rem; color: var(--text-muted); line-height: 1.4; }

        .prompt-grid { display: flex; flex-direction: column; gap: 10px; }
        .prompt-grid.hidden { display: none !important; }

        .prompt-card {
            background-color: var(--white);
            border: 1px solid rgba(78, 92, 75, 0.12);
            border-radius: 14px;
            padding: 14px 18px;
            text-align: left;
            cursor: pointer;
            box-shadow: var(--card-shadow);
            transition: transform 0.15s ease, border-color 0.15s ease;
        }

        .prompt-card:hover { border-color: var(--terracotta); }
        .prompt-card:active { transform: scale(0.98); }
        .prompt-title { font-weight: 700; font-size: 0.95rem; color: var(--deep-olive); margin-bottom: 4px; }
        .prompt-desc { font-size: 0.88rem; color: var(--text-muted); line-height: 1.4; }

        /* CHAT MESSAGES */
        .chat-messages { display: flex; flex-direction: column; gap: 12px; }
        .message-wrapper { display: flex; flex-direction: column; max-width: 88%; }
        .message-wrapper.user { align-self: flex-end; }
        .message-wrapper.ai { align-self: flex-start; }

        .message { padding: 12px 16px; border-radius: 16px; font-size: 0.95rem; line-height: 1.45; word-break: break-word; }
        .message.user { background-color: var(--deep-olive); color: var(--white); border-bottom-right-radius: 4px; }
        .message.ai { background-color: var(--white); color: var(--text-dark); border: 1px solid rgba(78, 92, 75, 0.12); border-bottom-left-radius: 4px; box-shadow: var(--card-shadow); }

        /* INPUT FOOTER */
        .input-footer {
            background-color: var(--warm-beige-light);
            padding: 12px 20px;
            border-top: 1px solid rgba(78, 92, 75, 0.1);
            display: flex;
            align-items: center;
            gap: 8px;
            max-width: 768px;
            margin: 0 auto;
            width: 100%;
        }

        .input-wrapper {
            flex: 1;
            background-color: var(--white);
            border-radius: 24px;
            border: 1px solid rgba(78, 92, 75, 0.2);
            box-shadow: var(--card-shadow);
        }

        .input-wrapper input {
            width: 100%; padding: 12px 18px; border: none; background: transparent; font-size: 0.95rem; color: var(--text-dark); outline: none;
        }

        .icon-btn {
            width: 42px; height: 42px; border-radius: 50%; border: 1px solid rgba(78, 92, 75, 0.15); background-color: var(--white); color: var(--deep-olive); display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: var(--card-shadow); flex-shrink: 0; transition: all 0.2s ease;
        }

        .icon-btn.listening { background-color: var(--terracotta); color: var(--white); border-color: var(--terracotta); }

        .send-btn {
            background-color: var(--deep-olive); color: var(--white); border: none; padding: 0 20px; height: 42px; border-radius: 21px; font-weight: 700; font-size: 0.9rem; cursor: pointer; flex-shrink: 0;
        }

        /* DRAWERS */
        .drawer-overlay {
            position: fixed; top: 0; left: 0; right: 0; bottom: 0; background-color: rgba(44, 53, 43, 0.4); display: flex; z-index: 1000; opacity: 0; pointer-events: none; transition: opacity 0.25s ease;
        }
        .drawer-overlay.active { opacity: 1; pointer-events: auto; }
        .drawer-overlay.right-drawer { justify-content: flex-end; }
        .drawer-overlay.right-drawer .drawer-card { transform: translateX(100%); }
        .drawer-overlay.left-drawer { justify-content: flex-start; }
        .drawer-overlay.left-drawer .drawer-card { transform: translateX(-100%); }

        .drawer-card {
            background-color: var(--warm-beige-light); width: 85%; max-width: 320px; height: 100vh; padding: 24px; overflow-y: auto; transition: transform 0.3s cubic-bezier(0.1, 0.9, 0.2, 1); box-shadow: 0 0 25px rgba(0,0,0,0.15); display: flex; flex-direction: column; justify-content: space-between;
        }
        .drawer-overlay.active .drawer-card { transform: translateX(0); }

        .drawer-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; padding-bottom: 12px; border-bottom: 1px solid rgba(78, 92, 75, 0.15); }
        .drawer-header h3 { color: var(--deep-olive); font-size: 1.1rem; font-weight: 800; }
        .close-btn { background: none; border: none; font-size: 1.3rem; color: var(--text-muted); cursor: pointer; }

        .drawer-menu-nav { display: flex; flex-direction: column; gap: 8px; }
        .drawer-menu-item {
            display: flex; align-items: center; gap: 12px; padding: 12px 14px; background-color: var(--white); border: 1px solid rgba(78, 92, 75, 0.12); border-radius: 12px; color: var(--text-dark); text-decoration: none; font-weight: 700; font-size: 0.88rem; transition: all 0.15s ease;
        }
        .drawer-menu-item:hover { background-color: var(--warm-beige); border-color: var(--terracotta); }

        .auth-drawer-btn {
            width: 100%; padding: 12px; border-radius: 20px; font-weight: 800; font-size: 0.85rem; border: none; cursor: pointer; transition: all 0.2s ease; text-transform: uppercase; letter-spacing: 0.5px;
        }
        .auth-drawer-btn.login { background-color: var(--deep-olive); color: var(--white); }
        .auth-drawer-btn.logout { background-color: var(--white); color: #9B1C1C; border: 1px solid #F8B4B4; }

        /* FOKUS MODAL */
        .focus-modal-card {
            background-color: var(--white); border-radius: 24px; padding: 24px; width: 90%; max-width: 420px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); border: 1px solid rgba(78, 92, 75, 0.1);
        }
        .focus-modal-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
        .focus-modal-header h3 { font-size: 1.25rem; font-weight: 800; color: var(--deep-olive); }
        .slider-group { display: flex; flex-direction: column; gap: 14px; margin-top: 14px; }
        .slider-item { display: flex; flex-direction: column; gap: 4px; }
        .slider-label-row { display: flex; justify-content: space-between; font-weight: 700; font-size: 0.88rem; color: var(--text-dark); }
        .slider-item input[type="range"] { width: 100%; accent-color: var(--terracotta); cursor: pointer; }

        .hidden { display: none !important; }
    </style>
</head>
<body>

    <!-- HEADER NAV: HAMBURGER VÄNSTER, GLÖDLAMPA HÖGER -->
    <header class="header-nav">
        <div class="header-left-group">
            <button class="icon-nav-btn" title="Meny" onclick="openLeftDrawer()">≡</button>
            <span class="badge-pill guest falk-badge-status" id="header-badge">GÄST</span>
        </div>
        
        <div class="header-brand-title" onclick="startNewChat()">FALK</div>
        
        <div class="header-right-group">
            <button class="icon-nav-btn" title="Ny chatt" onclick="startNewChat()">＋</button>
            <button class="icon-nav-btn" title="Insikter & Påminnelser" onclick="openRightDrawer()">💡</button>
        </div>
    </header>

    <!-- MAIN CONTAINER -->
    <main class="main-container">
        <div class="welcome-card" id="welcome-card">
            <h2>Välkommen till FALK</h2>
            <p>Din kognitiva kompass för reflektion och vägledning.</p>
        </div>

        <section class="prompt-grid" id="prompt-grid">
            <div class="prompt-card" onclick="selectPrompt('Jag vill förstå vad som verkligen betyder något för mig och leva mer i linje med det.')">
                <div class="prompt-title">✨ Mening & livsriktning</div>
                <div class="prompt-desc">"Jag vill förstå vad som verkligen betyder något för mig och leva mer i linje med det."</div>
            </div>
            <div class="prompt-card" onclick="selectPrompt('Hjälp mig sortera tankarna och hitta klarhet.')">
                <div class="prompt-title">💭 När tankarna tar över</div>
                <div class="prompt-desc">"Hjälp mig sortera tankarna och hitta klarhet."</div>
            </div>
            <div class="prompt-card" onclick="selectPrompt('Hjälp mig hantera utmaningar och hitta nästa steg.')">
                <div class="prompt-title">💼 Jobb, ansvar & ledarskap</div>
                <div class="prompt-desc">"Hjälp mig hantera utmaningar och hitta nästa steg."</div>
            </div>
            <div class="prompt-card" onclick="selectPrompt('Jag känner mig stressad eller orolig och behöver landa.')">
                <div class="prompt-title">🌱 Hitta lugnet igen</div>
                <div class="prompt-desc">"Jag känner mig stressad eller orolig och behöver landa."</div>
            </div>
            <div class="prompt-card" onclick="selectPrompt('Hjälp mig komma vidare och få saker att hända.')">
                <div class="prompt-title">🎯 Från mål till handling</div>
                <div class="prompt-desc">"Hjälp mig komma vidare och få saker att hända."</div>
            </div>
            <div class="prompt-card" onclick="selectPrompt('Hjälp mig förstå en situation och kommunicera bättre.')">
                <div class="prompt-title">💬 Relationer & svåra samtal</div>
                <div class="prompt-desc">"Hjälp mig förstå en situation och kommunicera bättre."</div>
            </div>
            <div class="prompt-card" onclick="selectPrompt('Hjälp mig hitta hållbara vanor för sömn, energi och fokus.')">
                <div class="prompt-title">⚡ Mer energi & balans</div>
                <div class="prompt-desc">"Hjälp mig hitta hållbara vanor för sömn, energi och fokus."</div>
            </div>
            <div class="prompt-card" onclick="selectPrompt('Hjälp mig upptäcka mina behov, drivkrafter och mönster.')">
                <div class="prompt-title">🔍 Förstå mig själv bättre</div>
                <div class="prompt-desc">"Hjälp mig upptäcka mina behov, drivkrafter och mönster."</div>
            </div>
            <div class="prompt-card" onclick="selectPrompt('Hjälp mig se nya perspektiv och ifrågasätta det jag tar för givet.')">
                <div class="prompt-title">🧩 Utmana mina tankar</div>
                <div class="prompt-desc">"Hjälp mig se nya perspektiv och ifrågasätta det jag tar för givet."</div>
            </div>
        </section>

        <div class="chat-messages" id="chat-messages"></div>
    </main>

    <!-- FOOTER INPUT BAR -->
    <footer class="input-footer">
        <div class="input-wrapper">
            <input type="text" id="chat-message" placeholder="Skriv till mig eller välj ett alternativ..." onkeydown="if(event.key==='Enter') sendMessage()">
        </div>
        
        <button class="icon-btn" id="mic-btn" title="Röstinmatning" onclick="toggleSpeechRecognition()">🎙️</button>
        
        <button class="icon-btn" title="Kognitivt Fokus" onclick="openFocusModal()">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="4" y1="21" x2="4" y2="14"></line><line x1="4" y1="10" x2="4" y2="3"></line>
                <line x1="12" y1="21" x2="12" y2="12"></line><line x1="12" y1="8" x2="12" y2="3"></line>
                <line x1="20" y1="21" x2="20" y2="16"></line><line x1="20" y1="12" x2="20" y2="3"></line>
                <line x1="1" y1="14" x2="7" y2="14"></line><line x1="9" y1="8" x2="15" y2="8"></line>
                <line x1="17" y1="16" x2="23" y2="16"></line>
            </svg>
        </button>

        <button class="send-btn" id="send-btn" onclick="sendMessage()">Skicka</button>
    </footer>

    <!-- VÄNSTERDRAWER (NAVIGERING) -->
    <div class="drawer-overlay left-drawer" id="left-drawer" onclick="if(event.target===this) closeLeftDrawer()">
        <div class="drawer-card">
            <div>
                <div class="drawer-header">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <h3>FALK</h3>
                        <span class="badge-pill guest falk-badge-status" id="menu-badge">GÄST</span>
                    </div>
                    <button class="close-btn" onclick="closeLeftDrawer()">✕</button>
                </div>
                <nav class="drawer-menu-nav">
                    <a href="/" class="drawer-menu-item"><span>💬</span> Samtal & Kompass</a>
                    <a href="/bibliotek" class="drawer-menu-item"><span>📚</span> Bibliotek</a>
                    <a href="/utveckling" class="drawer-menu-item"><span>📈</span> Min utveckling</a>
                    <a href="/installningar" class="drawer-menu-item"><span>⚙️</span> Inställningar & Integritet</a>
                </nav>
            </div>
            <div>
                <button class="auth-drawer-btn login" id="drawer-auth-btn" onclick="toggleAuthSession()">Logga in</button>
            </div>
        </div>
    </div>

    <!-- HÖGERDRAWER (INSIKTER & PÅMINNELSER) -->
    <div class="drawer-overlay right-drawer" id="right-drawer" onclick="if(event.target===this) closeRightDrawer()">
        <div class="drawer-card">
            <div class="drawer-header">
                <h3>Insikter & Påminnelser</h3>
                <button class="close-btn" onclick="closeRightDrawer()">✕</button>
            </div>
            <div style="font-size: 0.85rem; color: var(--text-muted); font-style: italic;">
                Dina sparade kognitiva mönster och påminnelser visas här när du är inloggad.
            </div>
        </div>
    </div>

    <!-- FOKUS MODAL -->
    <div class="drawer-overlay" id="focus-modal" style="align-items: center; justify-content: center;" onclick="if(event.target===this) closeFocusModal()">
        <div class="focus-modal-card">
            <div class="focus-modal-header">
                <h3>Fokus</h3>
                <button class="close-btn" onclick="closeFocusModal()">✕</button>
            </div>
            <div class="slider-group">
                <div class="slider-item">
                    <div class="slider-label-row"><span>Självförtroende</span><span id="val-confidence">50%</span></div>
                    <input type="range" id="slider-confidence" min="0" max="100" value="50" oninput="updateSlider('confidence', this.value)">
                </div>
                <div class="slider-item">
                    <div class="slider-label-row"><span>Stresshantering</span><span id="val-stress">50%</span></div>
                    <input type="range" id="slider-stress" min="0" max="100" value="50" oninput="updateSlider('stress', this.value)">
                </div>
                <div class="slider-item">
                    <div class="slider-label-row"><span>Handlingskraft</span><span id="val-action">50%</span></div>
                    <input type="range" id="slider-action" min="0" max="100" value="50" oninput="updateSlider('action', this.value)">
                </div>
            </div>
        </div>
    </div>

    <script>
        const BACKEND_URL = "https://falk-ai.onrender.com";

        function checkAuthState() {
            return localStorage.getItem('falk_user_session') === 'active';
        }

        function updateAuthStateUI() {
            const isLoggedIn = checkAuthState();
            document.querySelectorAll('.falk-badge-status').forEach(el => {
                if (isLoggedIn) {
                    el.innerText = 'INLOGGAD';
                    el.className = 'badge-pill logged-in falk-badge-status';
                } else {
                    el.innerText = 'GÄST';
                    el.className = 'badge-pill guest falk-badge-status';
                }
            });

            const authBtn = document.getElementById('drawer-auth-btn');
            if (authBtn) {
                if (isLoggedIn) {
                    authBtn.innerText = 'Logga ut';
                    authBtn.className = 'auth-drawer-btn logout';
                } else {
                    authBtn.innerText = 'Logga in';
                    authBtn.className = 'auth-drawer-btn login';
                }
            }
        }

        function toggleAuthSession() {
            if (checkAuthState()) {
                localStorage.removeItem('falk_user_session');
            } else {
                localStorage.setItem('falk_user_session', 'active');
            }
            updateAuthStateUI();
            closeLeftDrawer();
        }

        function openLeftDrawer() { document.getElementById('left-drawer').classList.add('active'); }
        function closeLeftDrawer() { document.getElementById('left-drawer').classList.remove('active'); }
        function openRightDrawer() { document.getElementById('right-drawer').classList.add('active'); }
        function closeRightDrawer() { document.getElementById('right-drawer').classList.remove('active'); }

        function openFocusModal() { document.getElementById('focus-modal').classList.add('active'); }
        function closeFocusModal() { document.getElementById('focus-modal').classList.remove('active'); }
        function updateSlider(key, val) { document.getElementById(`val-${key}`).textContent = `${val}%`; }

        function selectPrompt(promptText) {
            document.getElementById("chat-message").value = promptText;
            sendMessage();
        }

        function startNewChat() {
            document.getElementById("chat-messages").innerHTML = "";
            document.getElementById("prompt-grid").classList.remove("hidden");
        }

        function sendMessage() {
            const input = document.getElementById("chat-message");
            const text = input.value.trim();
            if (!text) return;

            document.getElementById("prompt-grid").classList.add("hidden");
            const container = document.getElementById("chat-messages");

            const userMsg = document.createElement("div");
            userMsg.className = "message-wrapper user";
            userMsg.innerHTML = `<div class="message user">${text}</div>`;
            container.appendChild(userMsg);

            input.value = "";

            const aiSkeleton = document.createElement("div");
            aiSkeleton.className = "message-wrapper ai";
            aiSkeleton.innerHTML = `<div class="message ai" style="font-style: italic; opacity: 0.7;">FALK tänker...</div>`;
            container.appendChild(aiSkeleton);

            fetch(`${BACKEND_URL}/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text })
            })
            .then(res => res.json())
            .then(data => {
                aiSkeleton.innerHTML = `<div class="message ai">${data.response || "Inget svar."}</div>`;
            })
            .catch(() => {
                aiSkeleton.innerHTML = `<div class="message ai" style="color: red;">Kunde inte ansluta till backend.</div>`;
            });
        }

        let speechRecognition = null;
        function toggleSpeechRecognition() {
            const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRec) { alert("Din webbläsare stöder inte röstinmatning."); return; }
            
            speechRecognition = new SpeechRec();
            speechRecognition.lang = 'sv-SE';
            speechRecognition.onresult = (e) => {
                document.getElementById("chat-message").value = e.results[0][0].transcript;
            };
            speechRecognition.start();
        }

        document.addEventListener('DOMContentLoaded', () => {
            updateAuthStateUI();
        });
    </script>
</body>
</html>'''

with open(os.path.join("templates", "index.html"), "w", encoding="utf-8") as f:
    f.write(falk26_code)

print("-> [SUCCESS] FALK26 är nu permanent fixerad i templates/index.html!")
