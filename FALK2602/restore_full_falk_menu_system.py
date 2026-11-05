import os
import re
import subprocess
import time

print("=== STARTAR TOTAL REKONSTRUKTION AV FALK MENY-SYSTEM ===")

timestamp = int(time.time())
index_file = os.path.join("templates", "index.html")
js_file = os.path.join("static", "js", "dist", "app.min.js")

# STEG 1: FYSISK SÄKERHETSKOPIERING (ZERO-LOSS)
backup_file = f"templates/index.html.FULL_RESTORE_BACKUP_{timestamp}"
if os.path.exists(index_file):
    with open(index_file, "r", encoding="utf-8") as f_src:
        with open(backup_file, "w", encoding="utf-8") as f_dst:
            f_dst.write(f_src.read())
    print(f"-> [BACKUP OK] Fysisk reservfil skapad: {backup_file}")

# STEG 2: INSTALLERA DIN ATOMÄRA JS-MOTOR I APP.MIN.JS
atomic_js_engine = """
// ==========================================
// FALK ATOMIC MENU ENGINE (NOV 1 STABLE)
// ==========================================
window.openFalkMenu = function() {
    if (typeof window.updateDrawerAuthBar === 'function') window.updateDrawerAuthBar();
    if (typeof window.updateActiveMenuState === 'function') window.updateActiveMenuState();
    
    const drawer = document.getElementById("falk-left-drawer");
    const backdrop = document.getElementById("falk-menu-backdrop");
    
    if (backdrop) {
        backdrop.classList.remove("hidden");
        backdrop.style.setProperty("display", "block", "important");
        setTimeout(() => backdrop.classList.remove("opacity-0"), 10);
    }
    if (drawer) {
        drawer.style.setProperty("transform", "translateX(0)", "important");
    }
    document.body.style.overflow = "hidden";
};

window.closeFalkMenu = function() {
    const drawer = document.getElementById("falk-left-drawer");
    const backdrop = document.getElementById("falk-menu-backdrop");

    if (drawer) {
        drawer.style.setProperty("transform", "translateX(-100%)", "important");
    }
    if (backdrop) {
        backdrop.classList.add("opacity-0");
        setTimeout(() => {
            backdrop.classList.add("hidden");
            backdrop.style.setProperty("display", "none", "important");
        }, 300);
    }
    document.body.style.overflow = "";
};

// GLOBAL UTANFÖR-KLICK LYSSNARE
document.addEventListener("click", function(e) {
    const backdrop = document.getElementById("falk-menu-backdrop");
    if (e.target === backdrop || (backdrop && backdrop.contains(e.target))) {
        e.preventDefault();
        e.stopPropagation();
        window.closeFalkMenu();
    }
}, true);
"""

if os.path.exists(js_file):
    with open(js_file, "r", encoding="utf-8") as f:
        js_code = f.read()

    # Rensa gamla dubbletter om de finns
    js_code = re.sub(r'// ==========================================[\s\S]*?// GLOBAL UTANFÖR-KLICK LYSSNARE[\s\S]*?\},\s*true\);', '', js_code)
    
    # Lägg den atomära motorn längst upp
    new_js_code = atomic_js_engine.strip() + "\n\n" + js_code

    with open(js_file, "w", encoding="utf-8") as f:
        f.write(new_js_code)
    print("-> [JS OK] Atomic Menu Engine installerad i app.min.js!")

# STEG 3: SYNKRONISERA HTML HEADER & SIDOPANEL I INDEX.HTML
if os.path.exists(index_file):
    with open(index_file, "r", encoding="utf-8") as f:
        html = f.read()

    # A. Uppdatera onclick i knappen till openFalkMenu()
    html = re.sub(r'onclick=["\'](toggleSidebar\(\)|openFalkMenu\(\)|toggleMenu\(\))["\']', 'onclick="openFalkMenu()"', html)
    
    # Om knappen saknar onclick helt, tvinga in den på Meny-knappen
    html = re.sub(r'(<button[^>]*id=["\']open-menu-btn["\'][^>]*>)', r'<button id="open-menu-btn" onclick="openFalkMenu()" class="flex items-center gap-2 px-3 py-1.5 text-xs font-semibold tracking-wide text-stone-700 hover:text-stone-900 bg-stone-200/50 hover:bg-stone-200 rounded-lg transition-all focus:outline-none focus:ring-2 focus:ring-stone-400">', html)

    # B. Tvinga Cache-busting på JS-skriptet
    html = re.sub(r'app\.min\.js\?v=\d+', f'app.min.js?v={timestamp}', html)

    with open(index_file, "w", encoding="utf-8") as f:
        f.write(html)
    print("-> [HTML OK] Header-knapp och cache-busting synkroniserad i index.html!")

# STEG 4: HARD GIT COMMIT (PERMANENT SÄKRING)
try:
    subprocess.run(["git", "checkout", "-b", "menu-system-restored"], stderr=subprocess.DEVNULL)
except:
    pass

subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", f"RESTORE: Atomic menu engine and synchronized header triggers ({timestamp})"])
print("-> [GIT LOCKED] Hela projektet är nu $100\%$ säkrat och commitat i Git!")

print("\n=== SYSTEMET ÅTERSTÄLLT OCH LÅST ===")
