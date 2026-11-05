import os
import re

print("=== VERKSTÄLLER STRUKTURELL UNIFIKERING AV BADGES ('GÄST' / 'INLOGGAD') ÖVER ALLA 4 SIDOR ===")

pages = ['index.html', 'bibliotek.html', 'utveckling.html', 'installningar.html']
templates_dir = "templates"

for page in pages:
    fpath = os.path.join(templates_dir, page)
    if not os.path.exists(fpath):
        continue

    with open(fpath, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. ERSET ALLA GAMLA BADGE-ELEMENT I HEADER OCH DRAWER MED DEN ENHETLIGA KLASSEN falk-badge-status
    # Header badge replacement
    html = re.sub(
        r'<span class="px-2\.5 py-0\.5 text-\[11px\].*? uppercase shadow-xs.*?">.*?<\/span>',
        '<span class="px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-[#8C5D37] bg-[#FAF8F0] border border-[#DDD0B8] rounded-full uppercase shadow-xs falk-badge-status">GÄST</span>',
        html
    )

    # Drawer header badge replacement
    html = re.sub(
        r'<span class="px-2 py-0\.5 text-\[10px\].*? guest-badge-element">.*?<\/span>',
        '<span class="px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-[#8C5D37] bg-[#FAF8F0] border border-[#DDD0B8] rounded-full uppercase shadow-xs falk-badge-status">GÄST</span>',
        html
    )

    # 2. UPPDATERA MASTER ENGINE SKRIPTET MED STRIKT falk-badge-status TARGETING
    old_script_pattern = r'<script>\s*function checkAuthState\(\).*?<\/script>'
    
    new_engine_script = '''<script>
        function checkAuthState() {
            return localStorage.getItem('falk_user_session') === 'active';
        }

        function isGuestUser() {
            return !checkAuthState();
        }

        function updateUIForAuthState() {
            const isGuest = isGuestUser();
            
            // STRIKT DYNAMISK UPPDATERING AV ALLA BADGES PÅ ALLA SIDOR
            document.querySelectorAll('.falk-badge-status').forEach(el => {
                if (isGuest) {
                    el.innerText = 'GÄST';
                    el.className = 'px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-[#8C5D37] bg-[#FAF8F0] border border-[#DDD0B8] rounded-full uppercase shadow-xs falk-badge-status';
                } else {
                    el.innerText = 'INLOGGAD';
                    el.className = 'px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-white bg-[#4E5C4B] border border-[#3D493B] rounded-full uppercase shadow-xs falk-badge-status';
                }
            });

            // LOGGA IN / LOGGA UT KNAPP I VÄNSTERMENYN PÅ ALLA SIDOR
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
            if (typeof closeLeftMenu === 'function') closeLeftMenu();
            updateUIForAuthState();
        };

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
    </script>'''

    if re.search(old_script_pattern, html, flags=re.DOTALL):
        html = re.sub(old_script_pattern, new_engine_script, html, flags=re.DOTALL)
    else:
        html = html.replace('</body>', f'{new_engine_script}\n</body>')

    with open(fpath, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"-> [SUCCESS] Badges & Auth synkade i {page}")

print("\n=== SAMTLIGA 4 MALLAR ÄR NU 100% SYNSKRONISERADE PÅ BADGES OCH AUTH ===")
