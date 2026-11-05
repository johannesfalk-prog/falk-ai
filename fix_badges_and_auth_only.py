import os
import re

print("=== ÅTERSTÄLLER HEADER-DESIGN & APPLICERAR ENBART BADGE- OCH AUTH-LOGIK ===")

pages = ['index.html', 'bibliotek.html', 'utveckling.html', 'installningar.html']
templates_dir = "templates"

# REN ORIGINAL-HEADER MED FALK-LOGO OCH ORIGINALIKONER
clean_header_html = '''<header class="sticky top-0 z-30 bg-[#FAF8F0]/90 backdrop-blur-md border-b border-[#DDD0B8] px-4 py-3 flex items-center justify-between">
    <div class="flex items-center gap-3">
        <button onclick="openLeftMenu()" class="p-1.5 rounded-xl hover:bg-[#E8DCC4] text-[#2D2721] font-bold transition-all text-lg">≡</button>
        <span class="px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-[#8C5D37] bg-[#FAF8F0] border border-[#DDD0B8] rounded-full uppercase shadow-xs falk-badge-status">GÄST</span>
    </div>
    <div class="font-extrabold tracking-widest text-[#2D2721] text-base">FALK</div>
    <div class="flex items-center gap-2">
        <a href="/" class="p-1.5 rounded-xl hover:bg-[#E8DCC4] text-[#2D2721] transition-all text-sm font-bold">＋</a>
        <button onclick="openRightMenu()" class="p-1.5 rounded-xl hover:bg-[#E8DCC4] text-[#2D2721] transition-all text-base font-bold">💡</button>
    </div>
</header>'''

# ISOLERAD MOTOR FÖR BADGES OCH AUTH
badge_auth_js = '''
<script>
    function checkAuthState() {
        return localStorage.getItem('falk_user_session') === 'active';
    }

    function isGuestUser() {
        return !checkAuthState();
    }

    function updateUIForAuthState() {
        const isGuest = isGuestUser();
        
        // 1. UPPDATERA ALLA BADGES PÅ ALLA SIDOR (ENBART TEXT OCH FÄRG)
        document.querySelectorAll('.falk-badge-status, .guest-badge-element').forEach(el => {
            if (isGuest) {
                el.innerText = 'GÄST';
                el.className = 'px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-[#8C5D37] bg-[#FAF8F0] border border-[#DDD0B8] rounded-full uppercase shadow-xs falk-badge-status';
            } else {
                el.innerText = 'INLOGGAD';
                el.className = 'px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-white bg-[#4E5C4B] border border-[#3D493B] rounded-full uppercase shadow-xs falk-badge-status';
            }
        });

        // 2. UPPDATERA LOGGA IN / LOGGA UT KNAPP I VÄNSTERMENYN
        const drawerAuthBtn = document.getElementById('drawer-auth-btn');
        if (drawerAuthBtn) {
            if (isGuest) {
                drawerAuthBtn.innerText = 'Logga in';
                drawerAuthBtn.onclick = function() { if (typeof closeLeftMenu === 'function') closeLeftMenu(); openAuthModal(); };
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
        if (typeof closePaywallModal === 'function') closePaywallModal();
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

    document.addEventListener('DOMContentLoaded', () => {
        updateUIForAuthState();
    });
</script>
'''

for page in pages:
    fpath = os.path.join(templates_dir, page)
    if not os.path.exists(fpath):
        continue

    with open(fpath, "r", encoding="utf-8") as f:
        html = f.read()

    # Återställ headern exakt
    html = re.sub(r'<header[^>]*>.*?</header>', clean_header_html, html, flags=re.DOTALL)

    # Ersätt/injektera den renodlade JS-motorn
    if 'function updateUIForAuthState' in html:
        html = re.sub(r'<script>\s*function checkAuthState\(\).*?<\/script>', badge_auth_js, html, flags=re.DOTALL)
    else:
        html = html.replace('</body>', f'{badge_auth_js}\n</body>')

    with open(fpath, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"-> [SUCCESS] Header återställd och badge-logik isolerad i {page}")

print("\n=== HEADER DESSIGN ÅTERSTÄLLD. BADGES & AUTH-LOGIK ISOLERAD ===")
