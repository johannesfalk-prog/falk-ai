import os

print("=== NÅR ÅTERSTÄLLNING TILL BASELINE: FALK2602 ===")

templates_dir = "templates"
os.makedirs(templates_dir, exist_ok=True)

# 1. BASELINE ORIGINAL HEADER (EXAKT BEVARAD DESIGN)
def get_original_header(title="FALK"):
    return f'''    <!-- ORIGINAL FALK HEADER (FALK2602) -->
    <header class="sticky top-0 z-30 bg-[#FAF8F0]/90 backdrop-blur-md border-b border-[#DDD0B8] px-4 py-3 flex items-center justify-between">
        <div class="flex items-center gap-3">
            <button onclick="openLeftMenu()" class="p-1.5 rounded-xl hover:bg-[#E8DCC4] text-[#2D2721] font-bold transition-all text-lg">≡</button>
            <span class="px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-[#8C5D37] bg-[#FAF8F0] border border-[#DDD0B8] rounded-full uppercase shadow-xs falk-badge-status">GÄST</span>
        </div>
        <div class="font-extrabold tracking-widest text-[#2D2721] text-base">{title}</div>
        <div class="flex items-center gap-2">
            <a href="/" class="p-1.5 rounded-xl hover:bg-[#E8DCC4] text-[#2D2721] transition-all text-sm font-bold">＋</a>
            <button onclick="openRightMenu()" class="p-1.5 rounded-xl hover:bg-[#E8DCC4] text-[#2D2721] transition-all text-base font-bold">💡</button>
        </div>
    </header>'''

# 2. BASELINE MODALS & DRAWERS
left_drawer = '''
    <!-- VÄNSTERDRAWER (NAVIGERING) -->
    <div id="falk-left-backdrop" onclick="closeLeftMenu()" class="fixed inset-0 bg-black/50 backdrop-blur-xs hidden opacity-0 transition-opacity duration-300 z-40 pointer-events-none"></div>
    <aside id="falk-left-drawer" class="fixed top-0 left-0 h-full w-72 bg-[#FAF8F0] border-r border-[#DDD0B8] shadow-2xl transform -translate-x-full transition-transform duration-300 ease-in-out z-50 flex flex-col justify-between p-6">
        <div class="space-y-6">
            <div class="flex items-center justify-between pb-4 border-b border-[#E6E0D4]">
                <div class="flex items-center gap-2">
                    <span class="font-extrabold tracking-widest text-[#2D2721] text-lg">FALK</span>
                    <span class="px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-[#8C5D37] bg-[#FAF8F0] border border-[#DDD0B8] rounded-full uppercase shadow-xs falk-badge-status">GÄST</span>
                </div>
                <button onclick="closeLeftMenu()" class="text-stone-400 hover:text-stone-800 text-lg font-bold p-1">✕</button>
            </div>
            <nav class="space-y-2 text-xs font-semibold text-stone-700">
                <a href="/" class="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-[#E8DCC4] transition-all">💬 Samtal & Kompass</a>
                <a href="/bibliotek" class="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-[#E8DCC4] transition-all">📚 Bibliotek</a>
                <a href="/utveckling" class="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-[#E8DCC4] transition-all">📈 Min utveckling</a>
                <a href="/installningar" class="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-[#E8DCC4] transition-all">⚙️ Inställningar</a>
            </nav>
        </div>
        <div class="pt-4 border-t border-[#E6E0D4]">
            <button id="drawer-auth-btn" onclick="closeLeftMenu(); openAuthModal();" class="w-full py-2.5 text-xs font-bold text-white bg-[#3A352E] hover:bg-[#2D2721] rounded-full transition-all">Logga in</button>
        </div>
    </aside>
'''

right_drawer = '''
    <!-- HÖGERDRAWER (INSIKTER) -->
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

paywall_modal = '''
    <!-- ISOLERAD POPUP PAYWALL MODAL -->
    <div id="falk-paywall-backdrop" onclick="closePaywallModal()" class="fixed inset-0 bg-black/60 backdrop-blur-md hidden opacity-0 transition-opacity duration-300 z-50 pointer-events-none"></div>
    <div id="falk-paywall-modal" class="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[92%] max-w-md bg-[#FAF8F0] border border-[#DDD0B8] rounded-3xl shadow-2xl hidden opacity-0 transition-all duration-300 z-50 p-6 sm:p-8 text-center space-y-5 pointer-events-none">
        <div class="mx-auto w-12 h-12 rounded-2xl bg-[#E8DCC4] border border-[#DDD0B8] flex items-center justify-center text-xl shadow-xs">🔒</div>
        <div class="space-y-1.5">
            <span class="text-[11px] font-bold tracking-widest text-[#8C5D37] uppercase">FALK PREMIUM</span>
            <h2 id="paywall-title" class="text-2xl font-black text-[#2D2721] leading-tight">Lås upp hela din kompass</h2>
            <p id="paywall-subtitle" class="text-xs text-stone-600 font-serif italic leading-relaxed max-w-sm mx-auto">Du har nått gränsen för gästläget. Skapa ett konto eller logga in för att fortsätta.</p>
        </div>
        <div class="bg-white/80 border border-[#DDD0B8] rounded-2xl p-4 text-left space-y-2.5 text-xs text-stone-800">
            <div class="flex items-center justify-between pb-2 border-b border-[#E6E0D4]">
                <span class="font-bold text-[#8C5D37] text-[11px] uppercase">Erbjudande:</span>
                <span class="bg-[#C57B57] text-white px-2.5 py-0.5 rounded-full text-[11px] font-bold">199 kr/mån</span>
            </div>
            <div class="flex items-center gap-2"><span class="text-[#4E5C4B] font-bold">✓</span><span>Obegränsad chatt & kompass</span></div>
            <div class="flex items-center gap-2"><span class="text-[#4E5C4B] font-bold">✓</span><span>Spara insikter & påminnelser</span></div>
            <div class="flex items-center gap-2"><span class="text-[#4E5C4B] font-bold">✓</span><span>Full tillgång till Bibliotek & Utveckling</span></div>
        </div>
        <div class="space-y-2 pt-1">
            <button onclick="triggerStripeCheckout()" class="w-full py-3 bg-[#4E5C4B] hover:bg-[#3D493B] text-white text-xs font-bold rounded-full transition-all uppercase tracking-wider">Skapa konto</button>
            <button onclick="openAuthModal()" class="w-full py-2.5 bg-[#FAF8F0] hover:bg-[#E8DCC4] text-[#2D2721] border border-[#DDD0B8] text-xs font-bold rounded-full transition-all">Redan medlem? Logga in</button>
        </div>
        <button onclick="closePaywallModal()" class="text-xs font-semibold text-stone-500 hover:text-black block mx-auto pt-1">Fortsätt titta runt som gäst</button>
    </div>
'''

auth_modal = '''
    <!-- ISOLERAD AUTH MODAL -->
    <div id="falk-auth-backdrop" onclick="closeAuthModal()" class="fixed inset-0 bg-black/60 backdrop-blur-md hidden opacity-0 transition-opacity duration-300 z-50 pointer-events-none"></div>
    <div id="falk-auth-modal" class="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[92%] max-w-md bg-[#FAF8F0] border border-[#DDD0B8] rounded-3xl shadow-2xl hidden opacity-0 transition-all duration-300 z-50 p-6 sm:p-8 text-center space-y-5 pointer-events-none">
        <div class="mx-auto w-12 h-12 rounded-2xl bg-[#E8DCC4] border border-[#DDD0B8] flex items-center justify-center text-xl shadow-xs">🔑</div>
        <div class="space-y-1.5">
            <span class="text-[11px] font-bold tracking-widest text-[#8C5D37] uppercase">FALK KONTO</span>
            <h2 class="text-2xl font-black text-[#2D2721] leading-tight">Logga in på FALK</h2>
        </div>
        <form onsubmit="handleAuthSubmit(event)" class="space-y-3 text-left">
            <div>
                <label class="block text-[11px] font-bold uppercase text-[#8C5D37] mb-1">E-post</label>
                <input type="email" required placeholder="din.epost@doman.se" class="w-full px-4 py-2 bg-white border border-[#DDD0B8] rounded-xl text-xs">
            </div>
            <div>
                <label class="block text-[11px] font-bold uppercase text-[#8C5D37] mb-1">Lösenord</label>
                <input type="password" required placeholder="••••••••" class="w-full px-4 py-2 bg-white border border-[#DDD0B8] rounded-xl text-xs">
            </div>
            <button type="submit" class="w-full py-3 bg-[#4E5C4B] hover:bg-[#3D493B] text-white text-xs font-bold rounded-full transition-all uppercase tracking-wider mt-2">Logga in</button>
        </form>
        <div class="pt-2 border-t border-[#E6E0D4] flex items-center justify-between text-xs">
            <button onclick="closeAuthModal()" class="text-stone-500 font-semibold">Avbryt</button>
            <button onclick="toggleDemoLogin()" class="text-[#C57B57] font-bold hover:underline">[Snabbtest: Logga in direkt]</button>
        </div>
    </div>
'''

# 3. BASELINE CORE ENGINE SCRIPT (ISOLERAD STATEMANAGEMENT)
core_engine_script = '''
<script id="falk-core-engine">
    function checkAuthState() {
        return localStorage.getItem('falk_user_session') === 'active';
    }

    function isGuestUser() {
        return !checkAuthState();
    }

    function updateUIForAuthState() {
        const isGuest = isGuestUser();
        
        // UNIFIERA BADGES ÖVER ALLA SIDOR
        document.querySelectorAll('.falk-badge-status').forEach(el => {
            if (isGuest) {
                el.innerText = 'GÄST';
                el.className = 'px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-[#8C5D37] bg-[#FAF8F0] border border-[#DDD0B8] rounded-full uppercase shadow-xs falk-badge-status';
            } else {
                el.innerText = 'INLOGGAD';
                el.className = 'px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-white bg-[#4E5C4B] border border-[#3D493B] rounded-full uppercase shadow-xs falk-badge-status';
            }
        });

        // DRAWER AUTH-BUTTON
        const drawerAuthBtn = document.getElementById('drawer-auth-btn');
        if (drawerAuthBtn) {
            if (isGuest) {
                drawerAuthBtn.innerText = 'Logga in';
                drawerAuthBtn.onclick = function() { closeLeftMenu(); openAuthModal(); };
                drawerAuthBtn.className = 'w-full py-2.5 text-xs font-bold text-white bg-[#3A352E] hover:bg-[#2D2721] rounded-full transition-all';
            } else {
                drawerAuthBtn.innerText = 'Logga ut';
                drawerAuthBtn.onclick = function() { logoutUser(); };
                drawerAuthBtn.className = 'w-full py-2.5 text-xs font-bold text-[#A83232] bg-white border border-red-200 hover:bg-red-50 rounded-full transition-all';
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

    document.addEventListener('DOMContentLoaded', () => {
        updateUIForAuthState();
    });
</script>
'''

# 4. WRITE CLEAN TEMPLATES
pages = {
    'index.html': 'FALK',
    'bibliotek.html': 'BIBLIOTEK',
    'utveckling.html': 'MIN UTVECKLING',
    'installningar.html': 'INSTÄLLNINGAR'
}

for page, title in pages.items():
    fpath = os.path.join(templates_dir, page)
    header = get_original_header(title)
    
    body_content = f'''<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - FALK</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#FAF8F0] text-stone-800 min-h-screen flex flex-col justify-between font-sans antialiased relative overflow-x-hidden">
{header}
    <main class="flex-1 max-w-4xl w-full mx-auto p-4 sm:p-6 space-y-6">
        <div class="bg-white/80 border border-[#DDD0B8] rounded-3xl p-6 shadow-sm">
            <h2 class="text-xl font-bold text-[#2D2721] mb-2">{title}</h2>
            <p class="text-xs text-stone-600">Välkommen till {title.lower()}-ytan i FALK platformen.</p>
        </div>
    </main>
{left_drawer}
{right_drawer}
{paywall_modal}
{auth_modal}
{core_engine_script}
</body>
</html>'''

    with open(fpath, "w", encoding="utf-8") as f:
        f.write(body_content)
    print(f"-> [RESTORED] {page} has been reset to FALK2602 baseline.")

print("\n=== FALK2602 BASELINE HAS BEEN FULLY RESTORED ACROSS ALL 4 PAGES ===")
