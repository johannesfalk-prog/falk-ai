import os
import re

print("=== DESTRUCTIVE SYNCHRONIZATION: UNIFIERAR MENYER & ENGINE ÖVER ALLA 4 MALLAR ===")

pages = ['index.html', 'bibliotek.html', 'utveckling.html', 'installningar.html']
templates_dir = "templates"

# 1. UNIVERSAL LEFT DRAWER HTML
left_drawer_html = '''
    <!-- UNIVERSAL LEFT DRAWER -->
    <div id="falk-left-backdrop" onclick="closeLeftMenu()" class="fixed inset-0 bg-black/50 backdrop-blur-xs hidden opacity-0 transition-opacity duration-300 z-40 pointer-events-none"></div>
    <aside id="falk-left-drawer" class="fixed top-0 left-0 h-full w-72 bg-[#FAF8F0] border-r border-[#DDD0B8] shadow-2xl transform -translate-x-full transition-transform duration-300 ease-in-out z-50 flex flex-col justify-between p-6">
        <div class="space-y-6">
            <div class="flex items-center justify-between pb-4 border-b border-[#E6E0D4]">
                <div class="flex items-center gap-2">
                    <span class="font-extrabold tracking-widest text-[#2D2721] text-lg">FALK</span>
                    <span class="px-2 py-0.5 text-[10px] font-bold text-[#8C5D37] bg-[#E8DCC4] rounded-full guest-badge-element">GÄST</span>
                </div>
                <button onclick="closeLeftMenu()" class="text-stone-400 hover:text-stone-800 text-lg font-bold p-1">✕</button>
            </div>
            <nav class="space-y-2 text-xs font-semibold text-stone-700">
                <a href="/" class="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-[#E8DCC4] transition-all">
                    <span>💬</span> Samtal & Kompass
                </a>
                <a href="/bibliotek" class="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-[#E8DCC4] transition-all">
                    <span>📚</span> Bibliotek
                </a>
                <a href="/utveckling" class="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-[#E8DCC4] transition-all">
                    <span>📈</span> Min utveckling
                </a>
                <a href="/installningar" class="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-[#E8DCC4] transition-all">
                    <span>⚙️</span> Inställningar
                </a>
            </nav>
        </div>
        <div class="pt-4 border-t border-[#E6E0D4] flex items-center justify-between">
            <button id="drawer-auth-btn" onclick="closeLeftMenu(); openAuthModal();" class="px-6 py-2 text-xs font-bold text-white bg-[#3A352E] hover:bg-[#2D2721] rounded-full transition-all">
                Logga in
            </button>
        </div>
    </aside>
'''

# 2. UNIVERSAL RIGHT DRAWER HTML
right_drawer_html = '''
    <!-- UNIVERSAL RIGHT DRAWER -->
    <div id="falk-right-backdrop" onclick="closeRightMenu()" class="fixed inset-0 bg-black/50 backdrop-blur-xs hidden opacity-0 transition-opacity duration-300 z-40 pointer-events-none"></div>
    <aside id="falk-right-drawer" class="fixed top-0 right-0 h-full w-80 bg-[#FAF8F0] border-l border-[#DDD0B8] shadow-2xl transform translate-x-full transition-transform duration-300 ease-in-out z-50 flex flex-col justify-between p-6">
        <div class="space-y-4">
            <div class="flex items-center justify-between pb-3 border-b border-[#E6E0D4]">
                <h3 class="font-extrabold text-[#2D2721] text-base">Insikter & Påminnelser</h3>
                <button onclick="closeRightMenu()" class="text-stone-400 hover:text-stone-800 text-lg font-bold p-1">✕</button>
            </div>
            <div id="right-drawer-content" class="space-y-3 text-xs text-stone-600 overflow-y-auto max-h-[calc(100vh-140px)]">
                <p class="italic text-stone-400">Dina senast sparade insikter visas här när du är inloggad.</p>
            </div>
        </div>
    </aside>
'''

# 3. UNIVERSAL PAYWALL MODAL HTML
paywall_overlay = '''
    <!-- UNIVERSAL POPUP PAYWALL MODAL -->
    <div id="falk-paywall-backdrop" onclick="closePaywallModal()" class="fixed inset-0 bg-black/60 backdrop-blur-md hidden opacity-0 transition-opacity duration-300 z-50 pointer-events-none"></div>
    <div id="falk-paywall-modal" class="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[92%] max-w-md bg-[#FAF8F0] border border-[#DDD0B8] rounded-3xl shadow-2xl hidden opacity-0 transition-all duration-300 z-50 p-6 sm:p-8 text-center space-y-5 pointer-events-none">
        <div class="mx-auto w-12 h-12 rounded-2xl bg-[#E8DCC4] border border-[#DDD0B8] flex items-center justify-center text-xl shadow-xs">🔒</div>
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
            <div class="flex items-center gap-2.5"><span class="text-[#4E5C4B] font-bold text-sm">✓</span><span class="font-medium">Obegränsad chatt, fördjupade perspektiv</span></div>
            <div class="flex items-center gap-2.5"><span class="text-[#4E5C4B] font-bold text-sm">✓</span><span class="font-medium">Spara insikter & påminnelser</span></div>
            <div class="flex items-center gap-2.5"><span class="text-[#4E5C4B] font-bold text-sm">✓</span><span class="font-medium">Full tillgång till Biblioteket</span></div>
            <div class="flex items-center gap-2.5"><span class="text-[#4E5C4B] font-bold text-sm">✓</span><span class="font-medium">Min utveckling och fler funktioner</span></div>
        </div>
        <div class="space-y-2.5 pt-1">
            <button onclick="triggerStripeCheckout()" class="w-full py-3.5 bg-[#4E5C4B] hover:bg-[#3D493B] text-white text-xs font-bold rounded-full transition-all shadow-md tracking-wider uppercase">Skapa konto</button>
            <button onclick="openAuthModal()" class="w-full py-3 bg-[#FAF8F0] hover:bg-[#E8DCC4] text-[#2D2721] border border-[#DDD0B8] text-xs font-bold rounded-full transition-all">Redan medlem? Logga in</button>
        </div>
        <button onclick="closePaywallModal()" class="text-xs font-semibold text-stone-500 hover:text-black transition-all block mx-auto pt-1">Fortsätt titta runt som gäst</button>
    </div>
'''

# 4. UNIVERSAL AUTH MODAL HTML
auth_overlay = '''
    <!-- UNIVERSAL AUTH MODAL -->
    <div id="falk-auth-backdrop" onclick="closeAuthModal()" class="fixed inset-0 bg-black/60 backdrop-blur-md hidden opacity-0 transition-opacity duration-300 z-50 pointer-events-none"></div>
    <div id="falk-auth-modal" class="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[92%] max-w-md bg-[#FAF8F0] border border-[#DDD0B8] rounded-3xl shadow-2xl hidden opacity-0 transition-all duration-300 z-50 p-6 sm:p-8 text-center space-y-5 pointer-events-none">
        <div class="mx-auto w-12 h-12 rounded-2xl bg-[#E8DCC4] border border-[#DDD0B8] flex items-center justify-center text-xl shadow-xs">🔑</div>
        <div class="space-y-1.5">
            <span class="text-[11px] font-bold tracking-widest text-[#8C5D37] uppercase">FALK KONTO</span>
            <h2 class="text-2xl font-black text-[#2D2721] leading-tight">Logga in på FALK</h2>
            <p class="text-xs text-stone-600 font-serif italic leading-relaxed">Få obegränsad tillgång till din kompass, dina insikter och Fokus-inställningar.</p>
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
            <button type="submit" class="w-full py-3.5 bg-[#4E5C4B] hover:bg-[#3D493B] text-white text-xs font-bold rounded-full transition-all shadow-md tracking-wider uppercase mt-2">Logga in & Lås upp</button>
        </form>
        <div class="pt-2 border-t border-[#E6E0D4] flex items-center justify-between text-xs">
            <button onclick="closeAuthModal()" class="text-stone-500 hover:text-black font-semibold">Avbryt</button>
            <button onclick="toggleDemoLogin()" class="text-[#C57B57] font-bold hover:underline">[Snabbtest: Logga in direkt]</button>
        </div>
    </div>
'''

# 5. UNIVERSAL MASTER JAVASCRIPT ENGINE (KÖRS PÅ ALLA 4 SIDOR)
master_engine_js = '''
    <script>
        function checkAuthState() {
            return localStorage.getItem('falk_user_session') === 'active';
        }

        function isGuestUser() {
            return !checkAuthState();
        }

        function updateUIForAuthState() {
            const isGuest = isGuestUser();
            
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
            
            // KOPPLA EXPLICIT HEADER KNAPPAR OM ATTRIBUT SAKNAS
            const headerBtns = document.querySelectorAll('header button');
            if (headerBtns.length > 0) {
                headerBtns[0].onclick = openLeftMenu;
            }
            if (headerBtns.length > 1) {
                headerBtns[headerBtns.length - 1].onclick = openRightMenu;
            }
        });
    </script>
'''

for page in pages:
    fpath = os.path.join(templates_dir, page)
    if not os.path.exists(fpath):
        continue

    with open(fpath, "r", encoding="utf-8") as f:
        html = f.read()

    # Rensa bort gamla dubblerade modaler, lådor och skriptinjektioner
    html = re.sub(r'<!-- UNIVERSAL LEFT DRAWER -->.*?<\/aside>', '', html, flags=re.DOTALL)
    html = re.sub(r'<!-- UNIVERSAL RIGHT DRAWER -->.*?<\/aside>', '', html, flags=re.DOTALL)
    html = re.sub(r'<!-- UNIVERSAL POPUP PAYWALL MODAL -->.*?<\/div>\s*<\/div>', '', html, flags=re.DOTALL)
    html = re.sub(r'<!-- UNIVERSAL AUTH MODAL -->.*?<\/div>\s*<\/div>', '', html, flags=re.DOTALL)
    
    # Rensa bort gamla script-block i slutet av filen
    if '<script>' in html:
        base_html = html.split('<script>')[0]
    else:
        base_html = html.split('</body>')[0]

    # Tagga header-knapparna med explicita onclick-attribut
    base_html = re.sub(r'(<header[^>]*>[\s\S]*?<button)', r'\1 onclick="openLeftMenu()"', base_html, count=1)

    # Bygg ihop den unifierade filen
    unified_page = base_html + '\n' + left_drawer_html + right_drawer_html + paywall_overlay + auth_overlay + master_engine_js + '\n</body>\n</html>'

    with open(fpath, "w", encoding="utf-8") as f:
        f.write(unified_page)

    print(f"-> [SYNCHRONIZED SUCCESS] {page} har fått fullständiga navigeringslådor, modaler och JS Engine!")

print("\n=== ALLA 4 MALLAR ÄR $100\%$ SYNSKRONISERADE MED SAMMA MENYLOGIK ===")
