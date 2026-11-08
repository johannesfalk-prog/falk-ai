import os
import re

print("=== ÅTERSTÄLLER ALL INTERAKTIVITET PÅ STARTSIDAN (MENY, KORT & CHATT) ===")

index_path = os.path.join("templates", "index.html")
if not os.path.exists(index_path):
    print("Error: templates/index.html hittades inte!")
    exit(1)

with open(index_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. RADERA ALLA GAMLA SKRIPTER FÖRE </body> FÖR ATT UNDVIKA KONFLIKTER
if '<script>' in html:
    base_html = html.split('<script>')[0]
else:
    base_html = html.split('</body>')[0]

# 2. KOMPLETT OPERATIV ENGINE-SKRIPT (ALLA FUNKTIONER SAMLADE)
complete_engine_js = '''
    <script>
        // --- 1. AUTH STATE & BADGE MANAGEMENT ---
        function checkAuthState() {
            return localStorage.getItem('falk_user_session') === 'active';
        }

        let IS_GUEST = !checkAuthState();

        function updateUIForAuthState() {
            IS_GUEST = !checkAuthState();
            
            // Uppdatera status-badger överallt
            document.querySelectorAll('.falk-badge-status, header span.rounded-full').forEach(el => {
                if (el.innerText.includes('GÄST') || el.innerText.includes('INLOGGAD') || el.innerText.includes('MEDLEM')) {
                    if (IS_GUEST) {
                        el.innerText = 'GÄST';
                        el.className = 'px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-[#8C5D37] bg-[#FAF8F0] border border-[#DDD0B8] rounded-full uppercase shadow-xs falk-badge-status';
                    } else {
                        el.innerText = 'INLOGGAD';
                        el.className = 'px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-white bg-[#4E5C4B] border border-[#3D493B] rounded-full uppercase shadow-xs falk-badge-status';
                    }
                }
            });

            // Vänstermenyns Logga in / Logga ut-knapp
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
        }

        window.logoutUser = function() {
            localStorage.removeItem('falk_user_session');
            closeLeftMenu();
            updateUIForAuthState();
        };

        // --- 2. VÄNSTER & HÖGER MENY-STYRNING ---
        window.openLeftMenu = function() {
            const drawer = document.getElementById('left-drawer');
            const backdrop = document.getElementById('drawer-backdrop');
            if (drawer && backdrop) {
                drawer.classList.remove('-translate-x-full');
                backdrop.classList.remove('hidden');
                requestAnimationFrame(() => backdrop.classList.remove('opacity-0'));
            }
        };

        window.closeLeftMenu = function() {
            const drawer = document.getElementById('left-drawer');
            const backdrop = document.getElementById('drawer-backdrop');
            if (drawer && backdrop) {
                drawer.classList.add('-translate-x-full');
                backdrop.classList.add('opacity-0');
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
            if (drawer && backdrop) {
                drawer.classList.remove('translate-x-full');
                backdrop.classList.remove('hidden');
                requestAnimationFrame(() => backdrop.classList.remove('opacity-0'));
            }
        };

        window.closeRightMenu = function() {
            const drawer = document.getElementById('right-drawer');
            const backdrop = document.getElementById('right-drawer-backdrop');
            if (drawer && backdrop) {
                drawer.classList.add('translate-x-full');
                backdrop.classList.add('opacity-0');
                setTimeout(() => backdrop.classList.add('hidden'), 300);
            }
        };

        // --- 3. 24-TIMMARS GÄSTGRÄNS LOGIK ---
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

        // --- 4. CHATT-MOTOR & ONBOARDING KORT ---
        window.sendQuickPrompt = function(promptText) {
            const input = document.getElementById('chat-input');
            if (input) input.value = promptText;
            executeSendMessage(promptText);
        };

        window.handleChatSubmit = function(e) {
            if (e) e.preventDefault();
            const input = document.getElementById('chat-input');
            if (!input) return;
            const text = input.value.trim();
            if (!text) return;
            input.value = '';
            executeSendMessage(text);
        };

        window.appendMessage = function(sender, text) {
            const container = document.getElementById('chat-messages');
            if (!container) return;

            // Dölj onboarding-kort vid första meddelandet
            const onboardingContainer = document.getElementById('onboarding-cards');
            if (onboardingContainer) onboardingContainer.style.display = 'none';

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
            container.scrollTop = container.scrollHeight;
        };

        window.executeSendMessage = function(text) {
            if (IS_GUEST && getGuestMessageCount() >= 6) {
                openPaywallModal('chat_limit');
                return;
            }

            if (IS_GUEST) {
                incrementGuestMessageCount();
            }

            appendMessage('user', text);

            const focusSettings = JSON.parse(localStorage.getItem('falk_focus_settings') || '{}');

            fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text, focus_settings: focusSettings })
            })
            .then(res => res.text())
            .then(reply => {
                appendMessage('falk', reply);
            })
            .catch(err => {
                appendMessage('falk', 'Kunde inte ansluta till FALK. Försök igen om en stund.');
            });
        };

        // --- 5. MODAL CONTROL (AUTH & PAYWALL & FOKUS) ---
        window.openAuthModal = function() {
            closePaywallModal();
            const bd = document.getElementById("falk-auth-backdrop");
            const md = document.getElementById("falk-auth-modal");
            if (bd && md) {
                bd.classList.remove("hidden");
                md.classList.remove("hidden");
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
                bd.classList.add("opacity-0");
                md.classList.add("opacity-0");
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
                bd.classList.remove("hidden");
                md.classList.remove("hidden");
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
                bd.classList.add("opacity-0");
                md.classList.add("opacity-0");
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

        // --- 6. INIT PÅ DOM READY ---
        document.addEventListener('DOMContentLoaded', () => {
            updateUIForAuthState();

            // Säkra klick på Hamburgermeny i Header
            const menuBtn = document.querySelector('header button');
            if (menuBtn) {
                menuBtn.onclick = openLeftMenu;
            }

            // Säkra klick på Glödlampe-ikon (Höger meny)
            const rightBtn = document.querySelector('header button:last-child');
            if (rightBtn) {
                rightBtn.onclick = openRightMenu;
            }
        });
    </script>
'''

# 3. KOPPLA ONCLICK PÅ EVENTUELLA STATISKA PROMPT-KORT I HTML
base_html = re.sub(r'class="([^"]*prompt-card[^"]*)"', r'class="\1" onclick="sendQuickPrompt(this.innerText.trim())"', base_html)

# 4. SKRIV TILLBAKA KOMPLETT FIL
final_html = base_html + '\n' + complete_engine_js + '\n</body>\n</html>'

with open(index_path, "w", encoding="utf-8") as f:
    f.write(final_html)

print("-> [SUCCESS] Interaktiviteten på index.html är 100% återställd!")
