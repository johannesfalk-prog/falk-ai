import os

print("=== ÅTERSTÄLLER DET RIKTIGA FALK-GRÄNSSNITTET OCH ONBOARDING-KORTEN PÅ ALLA SIDOR ===")

templates_dir = "templates"
os.makedirs(templates_dir, exist_ok=True)

# 1. COMMON HEADER (EXAKT ORIGINAL)
def get_header(title="FALK"):
    return f'''    <header class="sticky top-0 z-30 bg-[#FAF8F0]/90 backdrop-blur-md border-b border-[#DDD0B8] px-4 py-3 flex items-center justify-between">
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

# 2. ISOLATED DRAWERS & MODALS
drawers_and_modals = '''
    <!-- UNIVERSAL LEFT DRAWER -->
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
                <a href="/bibliotek" onclick="return handleNavClick(event, '/bibliotek', 'bibliotek')" class="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-[#E8DCC4] transition-all">📚 Bibliotek</a>
                <a href="/utveckling" onclick="return handleNavClick(event, '/utveckling', 'utveckling')" class="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-[#E8DCC4] transition-all">📈 Min utveckling</a>
                <a href="/installningar" class="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-[#E8DCC4] transition-all">⚙️ Inställningar & integritet</a>
            </nav>
        </div>
        <div class="pt-4 border-t border-[#E6E0D4]">
            <button id="drawer-auth-btn" onclick="closeLeftMenu(); openAuthModal();" class="w-full py-2.5 text-xs font-bold text-white bg-[#3A352E] hover:bg-[#2D2721] rounded-full transition-all">Logga in</button>
        </div>
    </aside>

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

    <!-- POPUP PAYWALL MODAL -->
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
            <div class="flex items-center gap-2"><span class="text-[#4E5C4B] font-bold">✓</span><span>Full tillgång till Biblioteket</span></div>
        </div>
        <div class="space-y-2 pt-1">
            <button onclick="triggerStripeCheckout()" class="w-full py-3 bg-[#4E5C4B] hover:bg-[#3D493B] text-white text-xs font-bold rounded-full transition-all uppercase tracking-wider">Skapa konto</button>
            <button onclick="openAuthModal()" class="w-full py-2.5 bg-[#FAF8F0] hover:bg-[#E8DCC4] text-[#2D2721] border border-[#DDD0B8] text-xs font-bold rounded-full transition-all">Redan medlem? Logga in</button>
        </div>
        <button onclick="closePaywallModal()" class="text-xs font-semibold text-stone-500 hover:text-black block mx-auto pt-1">Fortsätt titta runt som gäst</button>
    </div>

    <!-- AUTH MODAL -->
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

# 3. MASTER JAVASCRIPT ENGINE
master_js = '''
<script id="falk-core-engine">
    function checkAuthState() {
        return localStorage.getItem('falk_user_session') === 'active';
    }

    function isGuestUser() {
        return !checkAuthState();
    }

    function updateUIForAuthState() {
        const isGuest = isGuestUser();
        
        document.querySelectorAll('.falk-badge-status').forEach(el => {
            if (isGuest) {
                el.innerText = 'GÄST';
                el.className = 'px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-[#8C5D37] bg-[#FAF8F0] border border-[#DDD0B8] rounded-full uppercase shadow-xs falk-badge-status';
            } else {
                el.innerText = 'INLOGGAD';
                el.className = 'px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-white bg-[#4E5C4B] border border-[#3D493B] rounded-full uppercase shadow-xs falk-badge-status';
            }
        });

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

    window.handleNavClick = function(event, path, reason) {
        if (isGuestUser()) {
            if (event) event.preventDefault();
            closeLeftMenu();
            openPaywallModal(reason);
            return false;
        }
        window.location.href = path;
        return true;
    };

    window.handleExportClick = function(event) {
        if (isGuestUser()) {
            if (event) event.preventDefault();
            openPaywallModal('export');
            return false;
        }
        alert('Exporterar din samtals- och insiktsdata (.json)...');
    };

    window.handleFocusClick = function() {
        if (isGuestUser()) {
            openPaywallModal('fokus');
            return;
        }
        alert('Fokus-inställningar upplåsta.');
    };

    window.handleMicClick = function() {
        if (isGuestUser()) {
            openPaywallModal('mic');
            return;
        }
        alert('Röstinmatning aktiverad.');
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

    window.selectPrompt = function(text) {
        const input = document.getElementById('chat-input');
        if (input) input.value = text;
        window.executeSendMessage(text);
    };

    window.handleChatSubmit = function(e) {
        if (e) e.preventDefault();
        const input = document.getElementById('chat-input');
        if (!input) return;
        const text = input.value.trim();
        if (!text) return;
        window.executeSendMessage(text);
    };

    window.executeSendMessage = function(text) {
        if (isGuestUser() && getGuestMessageCount() >= 6) {
            openPaywallModal('chat_limit');
            return;
        }

        if (isGuestUser()) {
            incrementGuestMessageCount();
        }

        const input = document.getElementById('chat-input');
        if (input) input.value = '';

        const grid = document.getElementById("dashboard-grid");
        const thread = document.getElementById("chat-thread");
        if (grid) grid.classList.add("hidden");
        if (thread) thread.classList.remove("hidden");

        const container = document.getElementById("chat-messages");
        if (container) {
            const userBubble = document.createElement("div");
            userBubble.className = "flex justify-end mb-4";
            userBubble.innerHTML = `<div class="max-w-[85%] sm:max-w-[75%] bg-[#4E5C4B] text-white p-4 rounded-2xl rounded-tr-none text-sm shadow-sm">${text}</div>`;
            container.appendChild(userBubble);

            const aiSkeleton = document.createElement("div");
            aiSkeleton.className = "flex justify-start mb-4";
            aiSkeleton.innerHTML = `<div class="max-w-[85%] sm:max-w-[75%] bg-white border border-[#DDD0B8] text-stone-800 p-4 rounded-2xl rounded-tl-none text-sm shadow-sm italic text-stone-500">FALK tänker...</div>`;
            container.appendChild(aiSkeleton);

            fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            })
            .then(res => res.text())
            .then(reply => {
                aiSkeleton.innerHTML = `<div class="max-w-[85%] sm:max-w-[75%] bg-white border border-[#DDD0B8] text-stone-800 p-4 rounded-2xl rounded-tl-none text-sm shadow-sm leading-relaxed whitespace-pre-line">${reply}</div>`;
                window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
            })
            .catch(err => {
                aiSkeleton.innerHTML = `<div class="max-w-[85%] sm:max-w-[75%] bg-white border border-[#DDD0B8] text-stone-800 p-4 rounded-2xl rounded-tl-none text-sm shadow-sm text-red-600">Kunde inte ansluta till FALK backend.</div>`;
            });
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
        const titleEl = document.getElementById('paywall-title');
        if (reason === 'chat_limit' && titleEl) titleEl.innerText = 'Du har nått dina 6 gratissvar för idag';
        else if (reason === 'right_menu' && titleEl) titleEl.innerText = 'Lås upp Insikter & Påminnelser';
        else if (reason === 'bibliotek' && titleEl) titleEl.innerText = 'Lås upp hela Biblioteket';
        else if (reason === 'utveckling' && titleEl) titleEl.innerText = 'Lås upp Min Utveckling';
        else if (reason === 'export' && titleEl) titleEl.innerText = 'Lås upp Dataexport';
        else if (reason === 'fokus' && titleEl) titleEl.innerText = 'Lås upp Fokus & Parameterinställningar';

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

        const isProtectedPage = window.location.pathname.includes('bibliotek') || window.location.pathname.includes('utveckling');
        if (isProtectedPage && isGuestUser()) {
            openPaywallModal(window.location.pathname.includes('bibliotek') ? 'bibliotek' : 'utveckling');
        }
    });
</script>
'''

# 4. FULL INDEX.HTML (MED ALLA 8 ONBOARDING-KORT OCH CHATT-INPUT)
index_html = f'''<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FALK - Din Kognitiva Kompass</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#FAF8F0] text-stone-800 min-h-screen flex flex-col justify-between font-sans antialiased relative overflow-x-hidden pb-24">
{get_header("FALK")}

    <main class="flex-1 max-w-3xl w-full mx-auto px-4 py-6">
        <!-- DASHBOARD GRID: ALLA 8 ONBOARDING-KORT -->
        <div id="dashboard-grid" class="space-y-4">
            <div class="text-center space-y-1 mb-6">
                <h2 class="text-xl sm:text-2xl font-black text-[#2D2721]">Vad vill du utforska idag?</h2>
                <p class="text-xs sm:text-sm text-stone-600 font-serif italic">Välj ett område nedan eller skriv din egen fundering direkt i fältet.</p>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <button onclick="selectPrompt('Jag vill förstå vad som verkligen betyder något för mig och leva mer i linje med det.')" class="p-4 bg-white/90 hover:bg-white border border-[#DDD0B8] rounded-2xl text-left shadow-xs transition-all hover:border-[#8C5D37] group">
                    <div class="flex items-center gap-2 mb-1">
                        <span class="text-base">🌱</span>
                        <h3 class="font-bold text-xs text-[#2D2721] group-hover:text-[#8C5D37]">Mening & livsriktning</h3>
                    </div>
                    <p class="text-[11px] text-stone-500 italic font-serif">"Jag vill förstå vad som verkligen betyder något för mig..."</p>
                </button>

                <button onclick="selectPrompt('Hjälp mig sortera tankarna och hitta klarhet.')" class="p-4 bg-white/90 hover:bg-white border border-[#DDD0B8] rounded-2xl text-left shadow-xs transition-all hover:border-[#8C5D37] group">
                    <div class="flex items-center gap-2 mb-1">
                        <span class="text-base">☁️</span>
                        <h3 class="font-bold text-xs text-[#2D2721] group-hover:text-[#8C5D37]">När tankarna tar över</h3>
                    </div>
                    <p class="text-[11px] text-stone-500 italic font-serif">"Hjälp mig sortera tankarna och hitta klarhet."</p>
                </button>

                <button onclick="selectPrompt('Hjälp mig hantera utmaningar och hitta nästa steg.')" class="p-4 bg-white/90 hover:bg-white border border-[#DDD0B8] rounded-2xl text-left shadow-xs transition-all hover:border-[#8C5D37] group">
                    <div class="flex items-center gap-2 mb-1">
                        <span class="text-base">🏢</span>
                        <h3 class="font-bold text-xs text-[#2D2721] group-hover:text-[#8C5D37]">Jobb, ansvar & ledarskap</h3>
                    </div>
                    <p class="text-[11px] text-stone-500 italic font-serif">"Hjälp mig hantera utmaningar och hitta nästa steg."</p>
                </button>

                <button onclick="selectPrompt('Jag känner mig stressad eller orolig och behöver landa.')" class="p-4 bg-white/90 hover:bg-white border border-[#DDD0B8] rounded-2xl text-left shadow-xs transition-all hover:border-[#8C5D37] group">
                    <div class="flex items-center gap-2 mb-1">
                        <span class="text-base">🍃</span>
                        <h3 class="font-bold text-xs text-[#2D2721] group-hover:text-[#8C5D37]">Hitta lugnet igen</h3>
                    </div>
                    <p class="text-[11px] text-stone-500 italic font-serif">"Jag känner mig stressad eller orolig och behöver landa."</p>
                </button>

                <button onclick="selectPrompt('Hjälp mig komma vidare och få saker att hända.')" class="p-4 bg-white/90 hover:bg-white border border-[#DDD0B8] rounded-2xl text-left shadow-xs transition-all hover:border-[#8C5D37] group">
                    <div class="flex items-center gap-2 mb-1">
                        <span class="text-base">🎯</span>
                        <h3 class="font-bold text-xs text-[#2D2721] group-hover:text-[#8C5D37]">Från mål till handling</h3>
                    </div>
                    <p class="text-[11px] text-stone-500 italic font-serif">"Hjälp mig komma vidare och få saker att hända."</p>
                </button>

                <button onclick="selectPrompt('Hjälp mig förstå en situation och kommunicera bättre.')" class="p-4 bg-white/90 hover:bg-white border border-[#DDD0B8] rounded-2xl text-left shadow-xs transition-all hover:border-[#8C5D37] group">
                    <div class="flex items-center gap-2 mb-1">
                        <span class="text-base">💬</span>
                        <h3 class="font-bold text-xs text-[#2D2721] group-hover:text-[#8C5D37]">Relationer & svåra samtal</h3>
                    </div>
                    <p class="text-[11px] text-stone-500 italic font-serif">"Hjälp mig förstå en situation och kommunicera bättre."</p>
                </button>

                <button onclick="selectPrompt('Hjälp mig hitta hållbara vanor för sömn, energi och fokus.')" class="p-4 bg-white/90 hover:bg-white border border-[#DDD0B8] rounded-2xl text-left shadow-xs transition-all hover:border-[#8C5D37] group">
                    <div class="flex items-center gap-2 mb-1">
                        <span class="text-base">⚡</span>
                        <h3 class="font-bold text-xs text-[#2D2721] group-hover:text-[#8C5D37]">Mer energi & balans</h3>
                    </div>
                    <p class="text-[11px] text-stone-500 italic font-serif">"Hjälp mig hitta hållbara vanor för sömn..."</p>
                </button>

                <button onclick="selectPrompt('Hjälp mig upptäcka mina behov, drivkrafter och mönster.')" class="p-4 bg-white/90 hover:bg-white border border-[#DDD0B8] rounded-2xl text-left shadow-xs transition-all hover:border-[#8C5D37] group">
                    <div class="flex items-center gap-2 mb-1">
                        <span class="text-base">🔍</span>
                        <h3 class="font-bold text-xs text-[#2D2721] group-hover:text-[#8C5D37]">Förstå mig själv bättre</h3>
                    </div>
                    <p class="text-[11px] text-stone-500 italic font-serif">"Hjälp mig upptäcka mina behov, drivkrafter..."</p>
                </button>
            </div>
        </div>

        <!-- CHAT THREAD (DÖLD FRÅN BÖRJAN) -->
        <div id="chat-thread" class="hidden space-y-4">
            <div id="chat-messages" class="space-y-4"></div>
        </div>
    </main>

    <!-- FLOATING CHAT INPUT BAR AT BOTTOM -->
    <div class="fixed bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-[#FAF8F0] via-[#FAF8F0]/90 to-transparent z-20">
        <form id="chat-form" onsubmit="handleChatSubmit(event)" class="max-w-2xl mx-auto relative flex items-center bg-white border border-[#DDD0B8] rounded-full shadow-lg px-4 py-2">
            <button type="button" onclick="handleMicClick()" class="p-2 text-stone-400 hover:text-[#8C5D37] transition-all text-base">🎙️</button>
            <input type="text" id="chat-input" placeholder="Skriv till mig eller välj ett alternativ..." class="w-full px-3 py-2 bg-transparent text-xs sm:text-sm text-stone-800 focus:outline-none">
            <button type="button" onclick="handleFocusClick()" class="p-2 text-stone-400 hover:text-[#8C5D37] transition-all text-base mr-1">⚙️</button>
            <button type="submit" class="px-5 py-2 bg-[#4E5C4B] hover:bg-[#3D493B] text-white text-xs font-bold rounded-full transition-all shadow-xs">Skicka</button>
        </form>
    </div>

{drawers_and_modals}
{master_js}
</body>
</html>'''

with open(os.path.join(templates_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)

# 5. FULL INSTALLNINGAR.HTML (MED ALLA DATA & EXPORTSEKTIONER)
installningar_html = f'''<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inställningar & Integritet - FALK</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#FAF8F0] text-stone-800 min-h-screen flex flex-col justify-between font-sans antialiased relative overflow-x-hidden">
{get_header("INSTÄLLNINGAR")}

    <main class="flex-1 max-w-2xl w-full mx-auto px-4 py-6 space-y-6">
        <!-- VYN OCH TEMA -->
        <div class="bg-white/90 border border-[#DDD0B8] rounded-3xl p-6 shadow-xs space-y-4">
            <div class="flex items-center justify-between pb-3 border-b border-[#E6E0D4]">
                <h3 class="font-bold text-sm text-[#2D2721] uppercase tracking-wider">UTSEENDE & VYER</h3>
            </div>
            <div class="grid grid-cols-2 gap-3">
                <button class="py-3 px-4 bg-[#2D2721] text-white text-xs font-bold rounded-2xl shadow-xs">FALK Standard</button>
                <button class="py-3 px-4 bg-white border border-[#DDD0B8] text-stone-700 text-xs font-bold rounded-2xl hover:bg-[#FAF8F0]">Mörk vy</button>
            </div>
        </div>

        <!-- DINA DATA & EXPORT -->
        <div class="bg-white/90 border border-[#DDD0B8] rounded-3xl p-6 shadow-xs space-y-4">
            <div class="space-y-1">
                <h3 class="font-bold text-xs text-[#8C5D37] uppercase tracking-wider">DINA DATA & EXPORT</h3>
                <p class="text-xs text-stone-600 font-serif italic">Du äger din data. Du kan när som helst ladda ned en fullständig kopia av dina reflektioner och samtal.</p>
            </div>
            <button onclick="return handleExportClick(event)" class="px-5 py-2.5 bg-[#4E5C4B] hover:bg-[#3D493B] text-white text-xs font-bold rounded-xl transition-all shadow-xs flex items-center gap-2">
                <span>📥</span> Exportera all min data (.json)
            </button>
        </div>

        <!-- VILLKOR & INTEGRITET -->
        <div class="bg-white/90 border border-[#DDD0B8] rounded-3xl p-6 shadow-xs space-y-3">
            <h3 class="font-bold text-xs text-[#8C5D37] uppercase tracking-wider">VILLKOR & INTEGRITET</h3>
            <div class="space-y-2 text-xs font-semibold text-stone-700">
                <a href="#" class="block hover:underline">Användarvillkor</a>
                <a href="#" class="block hover:underline">Integritetspolicy & GDPR</a>
            </div>
        </div>

        <!-- FARA / KONTOÅTGÄRDER -->
        <div class="bg-red-50/50 border border-red-200 rounded-3xl p-6 shadow-xs space-y-3">
            <div class="space-y-1">
                <h3 class="font-bold text-xs text-[#A83232] uppercase tracking-wider">FARA / KONTOÅTGÄRDER</h3>
                <p class="text-xs text-stone-600 italic">Raderar permanent hela ditt konto, dina sparade insikter och din samtalshistorik.</p>
            </div>
            <button onclick="alert('Konto-radering kräver bekräftelse via e-post.')" class="px-5 py-2.5 bg-[#A83232] hover:bg-red-800 text-white text-xs font-bold rounded-xl transition-all shadow-xs">
                Radera mitt konto och all min data
            </button>
        </div>
    </main>

{drawers_and_modals}
{master_js}
</body>
</html>'''

with open(os.path.join(templates_dir, "installningar.html"), "w", encoding="utf-8") as f:
    f.write(installningar_html)

# 6. FULL BIBLIOTEK.HTML & UTVECKLING.HTML
bibliotek_html = f'''<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bibliotek - FALK</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#FAF8F0] text-stone-800 min-h-screen flex flex-col justify-between font-sans antialiased relative overflow-x-hidden">
{get_header("BIBLIOTEK")}

    <main class="flex-1 max-w-3xl w-full mx-auto px-4 py-6 space-y-6">
        <div class="bg-white/90 border border-[#DDD0B8] rounded-3xl p-6 shadow-xs space-y-3">
            <h2 class="text-xl font-bold text-[#2D2721]">Perspektiv & Övningar</h2>
            <p class="text-xs text-stone-600 font-serif italic">Här samlas mentala modeller, fördjupande övningar och ramverk när du är inloggad.</p>
        </div>
    </main>

{drawers_and_modals}
{master_js}
</body>
</html>'''

utveckling_html = f'''<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Min utveckling - FALK</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#FAF8F0] text-stone-800 min-h-screen flex flex-col justify-between font-sans antialiased relative overflow-x-hidden">
{get_header("MIN UTVECKLING")}

    <main class="flex-1 max-w-3xl w-full mx-auto px-4 py-6 space-y-6">
        <div class="bg-white/90 border border-[#DDD0B8] rounded-3xl p-6 shadow-xs space-y-3">
            <h2 class="text-xl font-bold text-[#2D2721]">Din Kognitiva Utveckling</h2>
            <p class="text-xs text-stone-600 font-serif italic">Analys av dina mönster, styrkor och reflektionsresor.</p>
        </div>
    </main>

{drawers_and_modals}
{master_js}
</body>
</html>'''

with open(os.path.join(templates_dir, "bibliotek.html"), "w", encoding="utf-8") as f:
    f.write(bibliotek_html)

with open(os.path.join(templates_dir, "utveckling.html"), "w", encoding="utf-8") as f:
    f.write(utveckling_html)

print("-> [RESTORED] Alla 4 sidor har återställts till sin FULLA OCH RIKA UI-struktur!")
