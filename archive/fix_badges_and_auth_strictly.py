import os
import re

print("=== STRIKT ISOLERING: UPPDATERAR ENBART BADGES OCH IN/UTLOGGNING ===")

pages = ['index.html', 'bibliotek.html', 'utveckling.html', 'installningar.html']
templates_dir = "templates"

# EXAKT ISOLERAD MOTOR FÖR BADGES OCH AUTH (RÖR INGET ANNAT)
isolated_auth_engine = '''
<script id="falk-auth-core-engine">
    function checkAuthState() {
        return localStorage.getItem('falk_user_session') === 'active';
    }

    function isGuestUser() {
        return !checkAuthState();
    }

    function updateUIForAuthState() {
        const isGuest = isGuestUser();
        
        // 1. UPPDATERA ENBART ALLA BADGES PÅ ALLA SIDOR (TEXT OCH KLASS)
        document.querySelectorAll('.falk-badge-status, .guest-badge-element').forEach(el => {
            if (isGuest) {
                el.innerText = 'GÄST';
                el.className = 'px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-[#8C5D37] bg-[#FAF8F0] border border-[#DDD0B8] rounded-full uppercase shadow-xs falk-badge-status';
            } else {
                el.innerText = 'INLOGGAD';
                el.className = 'px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-white bg-[#4E5C4B] border border-[#3D493B] rounded-full uppercase shadow-xs falk-badge-status';
            }
        });

        // 2. UPPDATERA ENBART LOGGA IN / LOGGA UT KNAPPEN I VÄNSTERMENYN
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

    # Tagga alla befintliga status-spans i HTML utan att ändra deras omgivande layout eller ikoner
    html = re.sub(
        r'<span class="[^"]*font-bold[^"]*uppercase[^"]*">GÄST</span>',
        '<span class="px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-[#8C5D37] bg-[#FAF8F0] border border-[#DDD0B8] rounded-full uppercase shadow-xs falk-badge-status">GÄST</span>',
        html
    )
    html = re.sub(
        r'<span class="[^"]*font-bold[^"]*uppercase[^"]*">INLOGGAD</span>',
        '<span class="px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-white bg-[#4E5C4B] border border-[#3D493B] rounded-full uppercase shadow-xs falk-badge-status">INLOGGAD</span>',
        html
    )

    # Rensa bort gamla auth-skript om de existerar
    html = re.sub(r'<script id="falk-auth-core-engine">.*?</script>', '', html, flags=re.DOTALL)

    # Injektera den isolerade auth-motorn precis före </body>
    if '</body>' in html:
        html = html.replace('</body>', f'{isolated_auth_engine}\n</body>')
    else:
        html += isolated_auth_engine

    with open(fpath, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"-> [STRICT SUCCESS] {page}: Badges märkta och auth-motor isolerad utan UI-påverkan.")

print("\n=== KORRIGERING KLAR: ENBART BADGES OCH AUTH-TILLSTÅND ÄR PÅVERKADE ===")
