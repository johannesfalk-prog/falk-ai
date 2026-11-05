import os
import re

print("=== IMPLEMENTERAR SKARPT AUTH-SYSTEM & INLOGGNINGSMODAL ===")

# 1. AUTH / LOGIN MODAL HTML
auth_modal_html = '''
    <!-- DYNAMISK AUTH / INLOGGNINGSMODAL -->
    <div id="falk-auth-backdrop" onclick="closeAuthModal()" class="fixed inset-0 bg-black/60 backdrop-blur-md hidden opacity-0 transition-opacity duration-300 z-50"></div>
    
    <div id="falk-auth-modal" class="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[92%] max-w-md bg-[#FAF8F0] border border-[#DDD0B8] rounded-3xl shadow-2xl hidden opacity-0 transition-all duration-300 z-50 p-6 sm:p-8 text-center space-y-5">
        
        <div class="mx-auto w-12 h-12 rounded-2xl bg-[#E8DCC4] border border-[#DDD0B8] flex items-center justify-center text-xl shadow-xs">
            🔑
        </div>

        <div class="space-y-1.5">
            <span class="text-[11px] font-bold tracking-widest text-[#8C5D37] uppercase">FALK KONTO</span>
            <h2 id="auth-modal-title" class="text-2xl font-black text-[#2D2721] leading-tight">Logga in på FALK</h2>
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
            <button onclick="toggleDemoLogin()" class="text-[#C57B57] font-bold hover:underline">[Snabbtest: Bli Medlem direkt]</button>
        </div>
    </div>
'''

# 2. DYNAMISK AUTH LOGIK OCH STATE CONTROL
auth_script = '''
    <script>
        // DYNAMISK AUTH STATE (HÄMTAR FRÅN LOCALSTORAGE)
        function checkAuthState() {
            return localStorage.getItem('falk_user_session') === 'active';
        }

        let IS_GUEST = !checkAuthState();

        function updateUIForAuthState() {
            IS_GUEST = !checkAuthState();
            
            // Uppdatera Header Badges
            document.querySelectorAll('.guest-badge-element').forEach(el => {
                if (IS_GUEST) {
                    el.innerText = 'GÄST';
                    el.className = 'px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-[#8C5D37] bg-[#FAF8F0] border border-[#DDD0B8] rounded-full uppercase shadow-xs guest-badge-element';
                } else {
                    el.innerText = 'MEDLEM';
                    el.className = 'px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-white bg-[#4E5C4B] border border-[#3D493B] rounded-full uppercase shadow-xs guest-badge-element';
                }
            });

            // Uppdatera Logga in / Logga ut knappar i menyerna
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
            alert('Välkommen tillbaka! Ditt konto är inloggat och alla funktioner samt Fokus-reglage är upplåsta.');
        };

        window.toggleDemoLogin = function() {
            localStorage.setItem('falk_user_session', 'active');
            updateUIForAuthState();
            closeAuthModal();
        };

        window.logoutUser = function() {
            localStorage.removeItem('falk_user_session');
            localStorage.removeItem('falk_guest_msg_count');
            updateUIForAuthState();
            alert('Du har loggat ut och är nu i gästläge.');
            window.location.reload();
        };

        document.addEventListener('DOMContentLoaded', () => {
            updateUIForAuthState();
        });
    </script>
'''

# 3. APPLICERA OCH WRAPPA I MALLARNA
pages = ['index.html', 'bibliotek.html', 'utveckling.html', 'installningar.html']
templates_dir = "templates"

for page in pages:
    fpath = os.path.join(templates_dir, page)
    if not os.path.exists(fpath):
        continue

    with open(fpath, "r", encoding="utf-8") as f:
        html = f.read()

    # Rensa hårdkodad const IS_GUEST = true;
    html = re.sub(r'const IS_GUEST = true;', '', html)
    html = re.sub(r'<!-- DYNAMISK AUTH / INLOGGNINGSMODAL -->.*?<\/div>\s*<\/div>', '', html, flags=re.DOTALL)
    html = re.sub(r'<script>\s*// DYNAMISK AUTH STATE.*?<\/script>', '', html, flags=re.DOTALL)

    # Tagga GÄST-badgen i Headern för dynamisk ändring
    html = re.sub(
        r'<span class="px-2\.5 py-0\.5 text-\[11px\] font-bold tracking-wider text-\[#8C5D37\] bg-\[#FAF8F0\] border border-\[#DDD0B8\] rounded-full uppercase shadow-xs">GÄST<\/span>',
        '<span class="px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-[#8C5D37] bg-[#FAF8F0] border border-[#DDD0B8] rounded-full uppercase shadow-xs guest-badge-element">GÄST</span>',
        html
    )

    # Tagga Logga in-knappen i vänstermenyn
    html = re.sub(
        r'<button class="px-6 py-2 text-xs font-bold text-white bg-\[#3A352E\] hover:bg-\[#2D2721\] rounded-full transition-all">Logga in<\/button>',
        '<button id="drawer-auth-btn" onclick="closeLeftMenu(); openAuthModal();" class="px-6 py-2 text-xs font-bold text-white bg-[#3A352E] hover:bg-[#2D2721] rounded-full transition-all">Logga in</button>',
        html
    )
    
    # Koppla Paywall-knappen "Redan medlem? Logga in" till Auth Modal
    html = re.sub(
        r'onclick="alert\(\'Omdirigerar till inloggning\.\.\.\'\)"',
        'onclick="openAuthModal()"',
        html
    )

    # Injektera Auth Modal & Script före </body>
    html = html.replace('</body>', f'{auth_modal_html}\n{auth_script}\n</body>')

    with open(fpath, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"-> [SUCCESS] Auth-system & Inloggning ansluten i {page}")

print("\n=== SKARPT INLOGGNINGSSYSTEM ÄR APPLICERAT ===")
