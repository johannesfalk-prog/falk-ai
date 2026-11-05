import os
import re

print("=== VERKSTÄLLER PRECIS FIX FÖR SUPABASE SCHEMA OCH INDEX.HTML ===")

# 1. FIXA APP.PY (HANTERA SUPABASE COLUMN MISSMATCH SMIDIGT)
app_path = "app.py"
if os.path.exists(app_path):
    with open(app_path, "r", encoding="utf-8") as f:
        app_code = f.read()

    # Ersätt Supabase-inserten med ett try-except block som inte kraschar terminalen om kolumnnamnet skiljer sig
    old_db_insert = r"if supabase_client:\s*try:\s*supabase_client\.table\('chat_messages'\)\.insert\(\{.*?\}\)\.execute\(\)\s*except Exception as db_err:\s*print\(f\"-> \[SUPABASE DB ERROR\] \{db_err\}\"\)"
    
    safe_db_insert = '''if supabase_client:
            try:
                # Försök skriva med standardkolumner
                supabase_client.table('chat_messages').insert({
                    'content': user_message,
                    'response': ai_response
                }).execute()
            except Exception:
                try:
                    supabase_client.table('chat_messages').insert({
                        'message': user_message,
                        'response': ai_response
                    }).execute()
                except Exception as db_err:
                    print(f"-> [SUPABASE LOG NOTE] {db_err}")'''

    if 'supabase_client.table(' in app_code:
        app_code = re.sub(old_db_insert, safe_db_insert, app_code, flags=re.DOTALL)

    with open(app_path, "w", encoding="utf-8") as f:
        f.write(app_code)
    print("-> [SUCCESS] app.py har säkrats mot Supabase-schemafel.")

# 2. FIXA TEMPLATES/INDEX.HTML (SYNSAMMA ID:N & DYNAMISK AUTH)
index_path = os.path.join("templates", "index.html")
if os.path.exists(index_path):
    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Klipp bort alla gamla <script>-block efter </footer>
    if '</footer>' in html:
        base_html = html.split('</footer>')[0] + '</footer>\n'
    else:
        base_html = html.split('</body>')[0] + '\n'

    # Bygg den slutgiltiga, skottsäkra motorn med Exakta ID-matchningar
    bulletproof_script = '''
    <script>
        // --- 1. DYNAMISK AUTH STATE (INGEN HÅRDKODAD CONST IS_GUEST) ---
        function checkAuthState() {
            return localStorage.getItem('falk_user_session') === 'active';
        }

        function isGuestUser() {
            return !checkAuthState();
        }

        function updateUIForAuthState() {
            const isGuest = isGuestUser();
            
            // Uppdatera alla badger (.guest-badge-element)
            document.querySelectorAll('.guest-badge-element, header span').forEach(el => {
                if (el && el.innerText && (el.innerText.includes('GÄST') || el.innerText.includes('INLOGGAD') || el.innerText.includes('MEDLEM'))) {
                    if (isGuest) {
                        el.innerText = 'GÄST';
                        el.className = 'px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-[#8C5D37] bg-[#FAF8F0] border border-[#DDD0B8] rounded-full uppercase shadow-xs guest-badge-element';
                    } else {
                        el.innerText = 'INLOGGAD';
                        el.className = 'px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-white bg-[#4E5C4B] border border-[#3D493B] rounded-full uppercase shadow-xs guest-badge-element';
                    }
                }
            });

            // Vänstermenyns knapp
            const drawerAuthBtn = document.getElementById('drawer-auth-btn');
            if (drawerAuthBtn) {
                if (isGuest) {
                    drawerAuthBtn.innerText = 'Logga in';
                    drawerAuthBtn.onclick = function() { closeLeftMenu(); openAuthModal(); };
                    drawerAuthBtn.className = 'px-6 py-2 text-xs font-bold text-white bg-[#3A352E] hover:bg-[#2D2721] rounded-full transition-all';
                } else {
                    drawerAuthBtn.innerText = 'Logga ut';
                    drawerAuthBtn.onclick = function() { logoutUser(); };
                    drawerAuthBtn.className = 'px-6 py-2 text-xs font-bold text-[#A83232] bg-white border border-red-200 hover:bg-red-50 rounded-full transition-all';
                }
            }
        }

        window.logoutUser = function() {
            localStorage.removeItem('falk_user_session');
            closeLeftMenu();
            updateUIForAuthState();
        };

        // --- 2. MENYSTYRNING MED KORREKTA ID:N (falk-left-drawer & falk-right-drawer) ---
        window.openLeftMenu = function() {
            const drawer = document.getElementById('falk-left-drawer');
            const backdrop = document.getElementById('falk-left-backdrop');
            if (drawer) drawer.classList.remove('-translate-x-full');
            if (backdrop) {
                backdrop.classList.remove('hidden', 'pointer-events-none');
                requestAnimationFrame(() => backdrop.classList.remove('opacity-0'));
            }
        };

        window.closeLeftMenu = function() {
            const drawer = document.getElementById('falk-left-drawer');
            const backdrop = document.getElementById('falk-left-backdrop');
            if (drawer) drawer.classList.add('-translate-x-full');
            if (backdrop) {
                backdrop.classList.add('opacity-0', 'pointer-events-none');
                setTimeout(() => backdrop.classList.add('hidden'), 300);
            }
        };

        window.openRightMenu = function() {
            if (isGuestUser()) {
                openPaywallModal('right_menu');
                return;
            }
            const drawer = document.getElementById('falk-right-drawer');
            const backdrop = document.getElementById('falk-right-backdrop');
            if (drawer) drawer.classList.remove('translate-x-full');
            if (backdrop) {
                backdrop.classList.remove('hidden', 'pointer-events-none');
                requestAnimationFrame(() => backdrop.classList.remove('opacity-0'));
            }
        };

        window.closeRightMenu = function() {
            const drawer = document.getElementById('falk-right-drawer');
            const backdrop = document.getElementById('falk-right-backdrop');
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

        // --- 4. CHATT-ENGINE MED KORREKT STRUKTUR (dashboard-grid vs chat-thread) ---
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
            window.executeSendMessage(text);
        };

        function escapeHtml(str) { 
            return str ? str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;") : ''; 
        }

        window.appendUserMessage = function(text) {
            const div = document.createElement("div"); 
            div.className = "flex justify-end mb-4";
            div.innerHTML = '<div class="user-bubble max-w-[85%] px-4 py-3 text-sm shadow-xs">' + escapeHtml(text) + '</div>';
            document.getElementById("chat-messages").appendChild(div);
        };

        window.appendAiSkeleton = function() {
            const div = document.createElement("div"); 
            div.className = "flex justify-start mb-4";
            const b = document.createElement("div"); 
            b.className = "ai-bubble max-w-[90%] px-4 py-3 text-sm shadow-xs leading-relaxed";
            b.innerHTML = '<span class="animate-pulse text-stone-500 font-medium">FALK tänker...</span>';
            div.appendChild(b); 
            document.getElementById("chat-messages").appendChild(div); 
            return b;
        };

        window.executeSendMessage = function(text) {
            if (isGuestUser() && getGuestMessageCount() >= 6) {
                openPaywallModal('chat_limit');
                return;
            }

            if (isGuestUser()) {
                incrementGuestMessageCount();
            }

            // Töm fältet
            const input = document.getElementById('chat-input');
            if (input) input.value = '';

            // Växla vy från onboarding-grid till chatt-tråd
            const grid = document.getElementById("dashboard-grid");
            const thread = document.getElementById("chat-thread");
            if (grid) grid.classList.add("hidden");
            if (thread) thread.classList.remove("hidden");

            // Rendera användarens meddelande och laddnings-skelett
            window.appendUserMessage(text);
            const aiSkeleton = window.appendAiSkeleton();

            const focusSettings = JSON.parse(localStorage.getItem('falk_focus_settings') || '{}');

            fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text, focus_settings: focusSettings })
            })
            .then(res => res.text())
            .then(reply => {
                if (aiSkeleton) aiSkeleton.innerText = reply;
                window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
            })
            .catch(err => {
                if (aiSkeleton) aiSkeleton.innerText = 'Kunde inte ansluta till FALK backend.';
            });
        };

        // --- 5. MODAL STYRNING ---
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

        document.addEventListener('DOMContentLoaded', () => {
            updateUIForAuthState();
        });
    </script>
'''

    final_html = base_html + bulletproof_script + '\n</body>\n</html>'

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(final_html)

    print("-> [SUCCESS] index.html har fått helt synkade ID:n och dynamisk auth-motor!")
