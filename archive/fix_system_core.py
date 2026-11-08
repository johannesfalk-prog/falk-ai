import os
import re

print("=== DESTRUCTIVE REPAIR: FIXAR SUPABASE SCHEMA, KLICK-FÄLLA OCH CHATTRENDERARE ===")

# 1. FIXA APP.PY (STOPPA PGRST204 SUPABASE SCHEMA-FEL)
app_path = "app.py"
if os.path.exists(app_path):
    with open(app_path, "r", encoding="utf-8") as f:
        app_code = f.read()

    # Ersätt insättningen så att den inte kräver focus_data-kolumnen som saknas i Supabase
    old_insert = r"supabase_client\.table\('chat_messages'\)\.insert\(\{\s*'message':\s*user_message,\s*'response':\s*ai_response,\s*'focus_data':\s*focus\s*\}\)\.execute\(\)"
    new_insert = "supabase_client.table('chat_messages').insert({'message': user_message, 'response': ai_response}).execute()"
    
    app_code = re.sub(old_insert, new_insert, app_code)
    
    # Fallback om mönstret var annorlunda utformat
    if 'focus_data' in app_code:
        app_code = app_code.replace("'focus_data': focus", "")
        app_code = app_code.replace(",}", "}")

    with open(app_path, "w", encoding="utf-8") as f:
        f.write(app_code)
    print("-> [SUCCESS] app.py har anpassats till Supabase-schemat (PGRST204 åtgärdat)!")

# 2. FIXA TEMPLATES/INDEX.HTML (RENSA KLICKFÄLLA OCH RENDERA CHATTBUBBLOR)
index_path = os.path.join("templates", "index.html")
if os.path.exists(index_path):
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Klipp bort gamla skript
    if '<script>' in html:
        base_html = html.split('<script>')[0]
    else:
        base_html = html.split('</body>')[0]

    # Skriv en helt skottsäker motor utan pointer-lock fällor
    master_engine = '''
    <script>
        // --- 1. AUTH & BADGE CONTROL ---
        function checkAuthState() {
            return localStorage.getItem('falk_user_session') === 'active';
        }

        let IS_GUEST = !checkAuthState();

        function updateUIForAuthState() {
            try {
                IS_GUEST = !checkAuthState();
                
                document.querySelectorAll('.falk-badge-status, header span.rounded-full').forEach(el => {
                    if (el && el.innerText) {
                        if (IS_GUEST) {
                            el.innerText = 'GÄST';
                            el.className = 'px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-[#8C5D37] bg-[#FAF8F0] border border-[#DDD0B8] rounded-full uppercase shadow-xs falk-badge-status';
                        } else {
                            el.innerText = 'INLOGGAD';
                            el.className = 'px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-white bg-[#4E5C4B] border border-[#3D493B] rounded-full uppercase shadow-xs falk-badge-status';
                        }
                    }
                });

                const drawerAuthBtn = document.getElementById('drawer-auth-btn');
                if (drawerAuthBtn) {
                    if (IS_GUEST) {
                        drawerAuthBtn.innerText = 'Logga in';
                        drawerAuthBtn.onclick = function() { closeLeftMenu(); openAuthModal(); };
                        drawerAuthBtn.className = 'px-6 py-2 text-xs font-bold text-white bg-[#3A352E] hover:bg-[#2D2721] rounded-full transition-all';
                    } else {
                        drawerAuthBtn.innerText = 'Logga ut';
                        drawerAuthBtn.onclick = function() { logoutUser(); };
                        drawerAuthBtn.className = 'px-6 py-2 text-xs font-bold text-[#A83232] bg-white border border-red-200 hover:bg-red-50 rounded-full transition-all';
                    }
                }
            } catch (e) {
                console.error("Auth state update exception:", e);
            }
        }

        window.logoutUser = function() {
            localStorage.removeItem('falk_user_session');
            closeLeftMenu();
            updateUIForAuthState();
        };

        // --- 2. MENY-STYRNING ---
        window.openLeftMenu = function() {
            const drawer = document.getElementById('left-drawer');
            const backdrop = document.getElementById('drawer-backdrop');
            if (drawer) drawer.classList.remove('-translate-x-full');
            if (backdrop) {
                backdrop.classList.remove('hidden', 'pointer-events-none');
                requestAnimationFrame(() => backdrop.classList.remove('opacity-0'));
            }
        };

        window.closeLeftMenu = function() {
            const drawer = document.getElementById('left-drawer');
            const backdrop = document.getElementById('drawer-backdrop');
            if (drawer) drawer.classList.add('-translate-x-full');
            if (backdrop) {
                backdrop.classList.add('opacity-0', 'pointer-events-none');
                setTimeout(() => backdrop.classList.add('hidden'), 300);
            }
        };

        window.openRightMenu = function() {
            if (IS_GUEST) {
                openPaywallModal('right_menu');
                return;
            }
            const drawer = document.getElementById('right-drawer');
            const backdrop = document.getElementById('right-drawer-backdrop');
            if (drawer) drawer.classList.remove('translate-x-full');
            if (backdrop) {
                backdrop.classList.remove('hidden', 'pointer-events-none');
                requestAnimationFrame(() => backdrop.classList.remove('opacity-0'));
            }
        };

        window.closeRightMenu = function() {
            const drawer = document.getElementById('right-drawer');
            const backdrop = document.getElementById('right-drawer-backdrop');
            if (drawer) drawer.classList.add('translate-x-full');
            if (backdrop) {
                backdrop.classList.add('opacity-0', 'pointer-events-none');
                setTimeout(() => backdrop.classList.add('hidden'), 300);
            }
        };

        // --- 3. 24-TIMMARS GÄSTGRÄNS ---
        function checkDailyReset() {
            const now = Date.now();
            const lastReset = parseInt(localStorage.getItem('falk_guest_reset_time') || '0');
            const TWENTY_FOUR_HOURS = 24 * 60 * 60 * 1000;
            if (!lastReset || (now - lastReset) > TWENTY_FOUR_HOURS) {
                localStorage.setItem('falk_guest_msg_count', '0');
                localStorage.setItem('falk_guest_reset_time', now.toString());
            }
        }

        function getGuestMessageCount() {
            checkDailyReset();
            return parseInt(localStorage.getItem('falk_guest_msg_count') || '0');
        }

        function incrementGuestMessageCount() {
            checkDailyReset();
            const count = getGuestMessageCount() + 1;
            localStorage.setItem('falk_guest_msg_count', count.toString());
            return count;
        }

        // --- 4. CHATT-ENGINE & DIRECT RENDERER ---
        window.selectPrompt = function(promptText) {
            const input = document.getElementById('chat-input');
            if (input) input.value = promptText;
            window.executeSendMessage(promptText);
        };
        window.sendQuickPrompt = window.selectPrompt;

        window.handleChatSubmit = function(e) {
            if (e) e.preventDefault();
            const input = document.getElementById('chat-input');
            if (!input) return;
            const text = input.value.trim();
            if (!text) return;
            input.value = '';
            window.executeSendMessage(text);
        };

        window.appendMessage = function(sender, text) {
            // Dölj alla onboarding-element permanent
            document.querySelectorAll('#onboarding-cards, .grid').forEach(el => {
                if (el) el.style.display = 'none';
            });

            // Hitta eller skapa chatt-behållaren
            let container = document.getElementById('chat-messages');
            if (!container) {
                const mainArea = document.querySelector('main') || document.body;
                container = document.createElement('div');
                container.id = 'chat-messages';
                container.className = 'w-full max-w-2xl mx-auto p-4 space-y-4 overflow-y-auto';
                mainArea.appendChild(container);
            }

            container.style.display = 'block';

            const msgDiv = document.createElement('div');
            msgDiv.className = sender === 'user' 
                ? 'flex justify-end mb-4' 
                : 'flex justify-start mb-4';

            const innerBubble = document.createElement('div');
            innerBubble.className = sender === 'user'
                ? 'max-w-[85%] sm:max-w-[75%] bg-[#4E5C4B] text-white p-4 rounded-2xl rounded-tr-none text-sm shadow-sm'
                : 'max-w-[85%] sm:max-w-[75%] bg-white border border-[#DDD0B8] text-stone-800 p-4 rounded-2xl rounded-tl-none text-sm shadow-sm leading-relaxed whitespace-pre-line';

            innerBubble.innerText = text;
            msgDiv.appendChild(innerBubble);
            container.appendChild(msgDiv);
            
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
        };

        window.executeSendMessage = function(text) {
            if (IS_GUEST && getGuestMessageCount() >= 6) {
                openPaywallModal('chat_limit');
                return;
            }

            if (IS_GUEST) {
                incrementGuestMessageCount();
            }

            window.appendMessage('user', text);

            const input = document.getElementById('chat-input');
            if (input) input.value = '';

            const focusSettings = JSON.parse(localStorage.getItem('falk_focus_settings') || '{}');

            fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text, focus_settings: focusSettings })
            })
            .then(res => res.text())
            .then(reply => {
                window.appendMessage('falk', reply);
            })
            .catch(err => {
                console.error("Chat fetch error:", err);
                window.appendMessage('falk', 'Kunde inte ansluta till FALK backend.');
            });
        };

        // --- 5. MODAL CONTROL (WITH POINTER-EVENTS SAFETY) ---
        window.openAuthModal = function() {
            closePaywallModal();
            const bd = document.getElementById("falk-auth-backdrop");
            const md = document.getElementById("falk-auth-modal");
            if (bd && md) {
                bd.classList.remove("hidden", "pointer-events-none");
                md.classList.remove("hidden", "pointer-events-none");
                requestAnimationFrame(() => {
                    bd.classList.remove("opacity-0");
                    md.classList.remove("opacity-0");
                });
            }
        };

        window.closeAuthModal = function() {
            const bd = document.getElementById("falk-auth-backdrop");
            const md = document.getElementById("falk-auth-modal");
            if (bd && md) {
                bd.classList.add("opacity-0", "pointer-events-none");
                md.classList.add("opacity-0", "pointer-events-none");
                setTimeout(() => {
                    bd.classList.add("hidden");
                    md.classList.add("hidden");
                }, 300);
            }
        };

        window.handleAuthSubmit = function(e) {
            e.preventDefault();
            localStorage.setItem('falk_user_session', 'active');
            updateUIForAuthState();
            closeAuthModal();
        };

        window.toggleDemoLogin = function() {
            localStorage.setItem('falk_user_session', 'active');
            updateUIForAuthState();
            closeAuthModal();
        };

        window.openPaywallModal = function(reason = 'general') {
            const titleEl = document.getElementById('paywall-title');
            if (reason === 'chat_limit' && titleEl) titleEl.innerText = 'Du har nått dina 6 gratissvar för idag';

            const bd = document.getElementById("falk-paywall-backdrop");
            const md = document.getElementById("falk-paywall-modal");
            if (bd && md) {
                bd.classList.remove("hidden", "pointer-events-none");
                md.classList.remove("hidden", "pointer-events-none");
                requestAnimationFrame(() => {
                    bd.classList.remove("opacity-0");
                    md.classList.remove("opacity-0");
                });
            }
        };

        window.closePaywallModal = function() {
            const bd = document.getElementById("falk-paywall-backdrop");
            const md = document.getElementById("falk-paywall-modal");
            if (bd && md) {
                bd.classList.add("opacity-0", "pointer-events-none");
                md.classList.add("opacity-0", "pointer-events-none");
                setTimeout(() => {
                    bd.classList.add("hidden");
                    md.classList.add("hidden");
                }, 300);
            }
        };

        window.triggerStripeCheckout = function() {
            fetch('/create-checkout-session', { method: 'POST' })
                .then(r => r.json())
                .then(data => { if (data.url) window.location.href = data.url; })
                .catch(err => console.error(err));
        };

        // --- 6. ATTACH EXPLICIT HANDLERS ON DOM READY ---
        document.addEventListener('DOMContentLoaded', () => {
            updateUIForAuthState();
            
            // Tvinga dolda backdrops att ha pointer-events-none
            document.querySelectorAll('#falk-auth-backdrop, #falk-paywall-backdrop, #drawer-backdrop, #right-drawer-backdrop').forEach(el => {
                if (el.classList.contains('hidden')) {
                    el.classList.add('pointer-events-none');
                }
            });
        });
    </script>
'''

    final_html = base_html + '\n' + master_engine + '\n</body>\n</html>'

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(final_html)

    print("-> [SUCCESS] index.html har säkrats mot klickfällor och chatt-renderaren är aktiv!")
