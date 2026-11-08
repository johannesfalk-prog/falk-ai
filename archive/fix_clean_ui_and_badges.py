import os
import re

print("=== TOTAL RENSNING AV INLINE-PAYWALLS OCH UNIFIKATION AV BADGES ===")

templates_dir = "templates"

# 1. UNIVERSAL OVERLAY PAYWALL MODAL (STRIKT POPUP OVERLAY - HIDDEN SOM STANDARD)
clean_paywall_modal = '''
    <!-- UNIVERSAL POPUP PAYWALL MODAL (REN OVERLAY - SYNS ALDRIG I FLÖDET) -->
    <div id="falk-paywall-backdrop" onclick="closePaywallModal()" class="fixed inset-0 bg-black/60 backdrop-blur-md hidden opacity-0 transition-opacity duration-300 z-50"></div>
    
    <div id="falk-paywall-modal" class="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[92%] max-w-md bg-[#FAF8F0] border border-[#DDD0B8] rounded-3xl shadow-2xl hidden opacity-0 transition-all duration-300 z-50 p-6 sm:p-8 text-center space-y-5">
        <div class="mx-auto w-12 h-12 rounded-2xl bg-[#E8DCC4] border border-[#DDD0B8] flex items-center justify-center text-xl shadow-xs">
            🔒
        </div>
        <div class="space-y-1.5">
            <span class="text-[11px] font-bold tracking-widest text-[#8C5D37] uppercase">FALK PREMIUM</span>
            <h2 id="paywall-title" class="text-2xl font-black text-[#2D2721] leading-tight">Lås upp hela din kompass</h2>
            <p id="paywall-subtitle" class="text-xs text-stone-600 font-serif italic leading-relaxed max-w-sm mx-auto">
                Du har nått gränsen för gästläget. Skapa ett konto eller logga in för att fortsätta utan begränsningar.
            </p>
        </div>
        <div class="bg-white/80 border border-[#DDD0B8] rounded-2xl p-4 text-left space-y-3 text-xs text-stone-800">
            <div class="flex items-center justify-between pb-2.5 border-b border-[#E6E0D4]">
                <span class="font-bold text-[#8C5D37] text-[11px] uppercase tracking-wider">Erbjudande:</span>
                <span class="bg-[#C57B57] text-white px-3 py-1 rounded-full text-[11px] font-bold shadow-xs">
                    199 kr/mån <span class="line-through opacity-75 font-normal text-[10px] ml-1">ord. 249 kr/mån</span>
                </span>
            </div>
            <div class="flex items-center gap-2.5">
                <span class="text-[#4E5C4B] font-bold text-sm">✓</span>
                <span class="font-medium">Obegränsad chatt, fördjupade perspektiv</span>
            </div>
            <div class="flex items-center gap-2.5">
                <span class="text-[#4E5C4B] font-bold text-sm">✓</span>
                <span class="font-medium">Spara insikter & påminnelser</span>
            </div>
            <div class="flex items-center gap-2.5">
                <span class="text-[#4E5C4B] font-bold text-sm">✓</span>
                <span class="font-medium">Full tillgång till Biblioteket</span>
            </div>
            <div class="flex items-center gap-2.5">
                <span class="text-[#4E5C4B] font-bold text-sm">✓</span>
                <span class="font-medium">Min utveckling och fler funktioner</span>
            </div>
        </div>
        <div class="space-y-2.5 pt-1">
            <button onclick="triggerStripeCheckout()" class="w-full py-3.5 bg-[#4E5C4B] hover:bg-[#3D493B] text-white text-xs font-bold rounded-full transition-all shadow-md tracking-wider uppercase">
                Skapa konto
            </button>
            <button onclick="openAuthModal()" class="w-full py-3 bg-[#FAF8F0] hover:bg-[#E8DCC4] text-[#2D2721] border border-[#DDD0B8] text-xs font-bold rounded-full transition-all">
                Redan medlem? Logga in
            </button>
        </div>
        <button onclick="closePaywallModal()" class="text-xs font-semibold text-stone-500 hover:text-black transition-all block mx-auto pt-1">
            Fortsätt titta runt som gäst
        </button>
    </div>
'''

# 2. INLOGGNINGSMODAL HTML
clean_auth_modal = '''
    <!-- AUTH / INLOGGNINGSMODAL -->
    <div id="falk-auth-backdrop" onclick="closeAuthModal()" class="fixed inset-0 bg-black/60 backdrop-blur-md hidden opacity-0 transition-opacity duration-300 z-50"></div>
    <div id="falk-auth-modal" class="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[92%] max-w-md bg-[#FAF8F0] border border-[#DDD0B8] rounded-3xl shadow-2xl hidden opacity-0 transition-all duration-300 z-50 p-6 sm:p-8 text-center space-y-5">
        <div class="mx-auto w-12 h-12 rounded-2xl bg-[#E8DCC4] border border-[#DDD0B8] flex items-center justify-center text-xl shadow-xs">
            🔑
        </div>
        <div class="space-y-1.5">
            <span class="text-[11px] font-bold tracking-widest text-[#8C5D37] uppercase">FALK KONTO</span>
            <h2 class="text-2xl font-black text-[#2D2721] leading-tight">Logga in på FALK</h2>
            <p class="text-xs text-stone-600 font-serif italic leading-relaxed">
                Få obegränsad tillgång till din kompass, dina insikter och Fokus-inställningar.
            </p>
        </div>
        <form id="auth-form" onsubmit="handleAuthSubmit(event)" class="space-y-3 text-left">
            <div>
                <label class="block text-[11px] font-bold uppercase text-[#8C5D37] mb-1">E-postadress</label>
                <input type="email" id="auth-email" required placeholder="din.epost@doman.se" class="w-full px-4 py-2.5 bg-white border border-[#DDD0B8] rounded-xl text-xs font-medium text-stone-800 focus:outline-none focus:border-[#4E5C4B]">
            </div>
            <div>
                <label class="block text-[11px] font-bold uppercase text-[#8C5D37] mb-1">Lösenord</label>
                <input type="password" id="auth-password" required placeholder="••••••••" class="w-full px-4 py-2.5 bg-white border border-[#DDD0B8] rounded-xl text-xs font-medium text-stone-800 focus:outline-none focus:border-[#4E5C4B]">
            </div>
            <button type="submit" class="w-full py-3.5 bg-[#4E5C4B] hover:bg-[#3D493B] text-white text-xs font-bold rounded-full transition-all shadow-md tracking-wider uppercase mt-2">
                Logga in & Lås upp
            </button>
        </form>
        <div class="pt-2 border-t border-[#E6E0D4] flex items-center justify-between text-xs">
            <button onclick="closeAuthModal()" class="text-stone-500 hover:text-black font-semibold">Avbryt</button>
            <button onclick="toggleDemoLogin()" class="text-[#C57B57] font-bold hover:underline">[Snabbtest: Logga in direkt]</button>
        </div>
    </div>
'''

# 3. UNIFIERAD JAVASCRIPT LOGIK FÖR BADGES ("GÄST" / "INLOGGAD") OCH SPÄRRAR
unified_script = '''
    <script>
        function checkAuthState() {
            return localStorage.getItem('falk_user_session') === 'active';
        }

        let IS_GUEST = !checkAuthState();

        function updateUIForAuthState() {
            IS_GUEST = !checkAuthState();
            
            // UNIFIERA ALLA BADGES PÅ ALLA SIDOR ("GÄST" ELLER "INLOGGAD")
            document.querySelectorAll('.falk-badge-status').forEach(el => {
                if (IS_GUEST) {
                    el.innerText = 'GÄST';
                    el.className = 'px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-[#8C5D37] bg-[#FAF8F0] border border-[#DDD0B8] rounded-full uppercase shadow-xs falk-badge-status';
                } else {
                    el.innerText = 'INLOGGAD';
                    el.className = 'px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-white bg-[#4E5C4B] border border-[#3D493B] rounded-full uppercase shadow-xs falk-badge-status';
                }
            });

            // LOGGA IN / LOGGA UT KNAPP I VÄNSTERMENYN
            const drawerAuthBtn = document.getElementById('drawer-auth-btn');
            if (drawerAuthBtn) {
                if (IS_GUEST) {
                    drawerAuthBtn.innerText = 'Logga in';
                    drawerAuthBtn.onclick = function() { if(typeof closeLeftMenu === 'function') closeLeftMenu(); openAuthModal(); };
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

        // 24-TIMMARS RULLANDE GÄSTGRÄNS
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

        window.openPaywallModal = function(reason = 'general') {
            const titleEl = document.getElementById('paywall-title');
            const subEl = document.getElementById('paywall-subtitle');
            
            if (subEl) subEl.innerText = 'Du har nått gränsen för gästläget. Skapa ett konto eller logga in för att fortsätta utan begränsningar.';

            if (reason === 'chat_limit') {
                if (titleEl) titleEl.innerText = 'Du har nått dina 6 gratissvar för idag';
            } else if (reason === 'right_menu') {
                if (titleEl) titleEl.innerText = 'Lås upp Insikter & Påminnelser';
            } else if (reason === 'bibliotek') {
                if (titleEl) titleEl.innerText = 'Lås upp hela Biblioteket';
            } else if (reason === 'utveckling') {
                if (titleEl) titleEl.innerText = 'Lås upp Min Utveckling';
            } else if (reason === 'export') {
                if (titleEl) titleEl.innerText = 'Lås upp Dataexport';
            } else if (reason === 'fokus') {
                if (titleEl) titleEl.innerText = 'Lås upp Fokus & Parameterinställningar';
            } else if (reason === 'mic') {
                if (titleEl) titleEl.innerText = 'Lås upp Röstinmatning';
            }

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
                .then(data => {
                    if (data.url) window.location.href = data.url;
                })
                .catch(err => console.error(err));
        };

        document.addEventListener('DOMContentLoaded', () => {
            updateUIForAuthState();
        });
    </script>
'''

pages = ['index.html', 'installningar.html']
for page in pages:
    fpath = os.path.join(templates_dir, page)
    if not os.path.exists(fpath):
        continue

    with open(fpath, "r", encoding="utf-8") as f:
        html = f.read()

    # Rensa bort alla gamla dubblerade Paywall-block och skript
    html = re.sub(r'<!-- UNIVERSAL POPUP PAYWALL MODAL.*?<\/div>\s*<\/div>', '', html, flags=re.DOTALL)
    html = re.sub(r'<!-- AUTH / INLOGGNINGSMODAL.*?<\/div>\s*<\/div>', '', html, flags=re.DOTALL)
    html = re.sub(r'<script>\s*function checkAuthState\(\).*?<\/script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<script>\s*const IS_GUEST = true;.*?<\/script>', '', html, flags=re.DOTALL)

    # Ersätt alla gamla Badges med .falk-badge-status
    html = re.sub(
        r'<span class="px-2\.5 py-0\.5 text-\[11px\].*? uppercase shadow-xs.*?">.*?<\/span>',
        '<span class="px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-[#8C5D37] bg-[#FAF8F0] border border-[#DDD0B8] rounded-full uppercase shadow-xs falk-badge-status">GÄST</span>',
        html
    )

    # Injektera modaler & script rent före </body>
    main_parts = html.split('</body>')
    clean_body = main_parts[0]
    new_html = clean_body + clean_paywall_modal + clean_auth_modal + unified_script + '\n</body>' + main_parts[1]

    with open(fpath, "w", encoding="utf-8") as f:
        f.write(new_html)

    print(f"-> [CLEANUP SUCCESS] {page} är helt rengjord från inline-paywalls och uppdaterad med .falk-badge-status")

print("\n=== SKRIPTET HAR RENSAT FLÖDET OCH KOPPLAT ALlA BADGES ===")
