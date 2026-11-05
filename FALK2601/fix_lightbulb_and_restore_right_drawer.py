import os
import re

print("=== REPARERAR GLÖDLAMPA PÅ HOVER OCH ÅTERSTÄLLER HÖGERMENYN PÅ ALLA SIDOR ===")

templates_dir = "templates"
template_files = ["index.html", "bibliotek.html", "utveckling.html", "installningar.html"]

# 1. EXAKT GLÖDLAMPS-SVG MEKANIK (STATISK BILD -> STRÅLAR VID HOVER)
new_lightbulb_button = '''            <button onclick="openRightMenu()" class="group text-black hover:opacity-100 transition-all focus:outline-none p-1 relative flex items-center justify-center" title="Insikter & Påminnelser">
                <svg class="w-6 h-6 text-black stroke-current fill-none relative" viewBox="0 0 24 24" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                    <!-- Strålar runt lampan (Endast synliga vid hover) -->
                    <g class="opacity-0 group-hover:opacity-100 transition-opacity duration-200 stroke-current">
                        <line x1="12" y1="1.5" x2="12" y2="3.5" />
                        <line x1="4.5" y1="4.5" x2="5.9" y2="5.9" />
                        <line x1="1.5" y1="12" x2="3.5" y2="12" />
                        <line x1="19.5" y1="4.5" x2="18.1" y2="5.9" />
                        <line x1="22.5" y1="12" x2="20.5" y2="12" />
                    </g>
                    <!-- Glödlampskupa (Formad exakt enligt skiss) -->
                    <path d="M 8.5 13 C 7 11.2 7 8 9 6 C 10.8 4.2 13.2 4.2 15 6 C 17 8 17 11.2 15.5 13 C 14.8 13.8 14.5 14.5 14.5 15.5 L 9.5 15.5 C 9.5 14.5 9.2 13.8 8.5 13 Z" />
                    <!-- Dubbla horisontella bottenstreck -->
                    <line x1="9.5" y1="18" x2="14.5" y2="18" />
                    <line x1="10.5" y1="20.5" x2="13.5" y2="20.5" />
                </svg>
            </button>'''

# 2. COMPLETE RIGHT DRAWER HTML (INSIKTER & PÅMINNELSER)
right_drawer_html = '''    <!-- HÖGER BACKDROP & MENY (INSIKTER & PÅMINNELSER) -->
    <div id="falk-right-backdrop" onclick="closeRightMenu()" class="fixed inset-0 bg-black/40 backdrop-blur-sm hidden opacity-0 transition-opacity duration-300 z-40"></div>
    <aside id="falk-right-drawer" class="fixed top-0 right-0 h-full w-80 bg-[#FAF8F0]/95 backdrop-blur-md shadow-2xl transform translate-x-full transition-transform duration-300 ease-in-out z-50 flex flex-col border-l border-[#DDD0B8]">
        <div class="p-6 border-b border-[#E6E0D4]/80">
            <div class="flex items-start justify-between">
                <div>
                    <p class="text-[11px] font-bold tracking-wide text-[#8C5D37] uppercase">ÖVERSYNER & FOKUS</p>
                    <h2 class="text-xl font-extrabold text-[#2D2721] mt-0.5">Insikter & Påminnelser</h2>
                </div>
                <button onclick="closeRightMenu()" class="p-1 text-stone-600 hover:text-black rounded-lg">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"></path></svg>
                </button>
            </div>
        </div>
        <div class="flex-1 p-5 space-y-4 overflow-y-auto">
            <div class="falk-card p-4 rounded-2xl border border-[#DDD0B8] shadow-xs">
                <div class="flex items-center gap-2 text-[#8C5D37] mb-2">
                    <span class="text-base">🌱</span>
                    <h3 class="text-xs font-bold uppercase tracking-wider">Senaste Insikt</h3>
                </div>
                <p class="text-xs italic font-serif leading-relaxed text-stone-700">"Att sätta gränser handlar inte om att stänga ute andra, utan om att hålla dig själv hel."</p>
            </div>

            <div class="falk-card p-4 rounded-2xl border border-[#DDD0B8] shadow-xs">
                <div class="flex items-center gap-2 text-[#8C5D37] mb-2">
                    <span class="text-base">🔔</span>
                    <h3 class="text-xs font-bold uppercase tracking-wider">Aktiv Påminnelse</h3>
                </div>
                <p class="text-xs font-medium text-stone-700">Reflektera kring dina 3 viktigaste prioriteringar inför morgondagen.</p>
            </div>
        </div>
    </aside>'''

# 3. RIGHT DRAWER JAVASCRIPT FUNCTIONS
right_drawer_js = '''
        function openRightMenu() {
            const drawer = document.getElementById("falk-right-drawer");
            const backdrop = document.getElementById("falk-right-backdrop");
            if (drawer && backdrop) {
                drawer.classList.remove("translate-x-full");
                backdrop.classList.remove("hidden");
                setTimeout(() => backdrop.classList.remove("opacity-0"), 10);
            }
        }
        function closeRightMenu() {
            const drawer = document.getElementById("falk-right-drawer");
            const backdrop = document.getElementById("falk-right-backdrop");
            if (drawer && backdrop) {
                drawer.classList.add("translate-x-full");
                backdrop.classList.add("opacity-0");
                setTimeout(() => backdrop.classList.add("hidden"), 300);
            }
        }
'''

for file_name in template_files:
    file_path = os.path.join(templates_dir, file_name)
    if not os.path.exists(file_path):
        continue

    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Uppdatera glödlampans knapp i header
    html = re.sub(r'<button onclick="openRightMenu\(\)".*?</button>', new_lightbulb_button, html, flags=re.DOTALL)

    # Injektera eller ersätt högermeny
    if 'id="falk-right-drawer"' in html:
        html = re.sub(r'<!-- HÖGER BACKDROP & MENY.*?<\/aside>', right_drawer_html, html, flags=re.DOTALL)
    else:
        # Injektera före <header> eller efter <body>
        html = html.replace('<body', right_drawer_html + '\n<body')

    # Säkerställ att JS-funktionerna finns
    if 'function openRightMenu()' not in html:
        html = html.replace('</script>', right_drawer_js + '\n    </script>')

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"-> [SUCCESS] Uppdaterade {file_name}: Ny glödlampa + Högermeny återställd!")

print("\n=== SYSTEMÅTGÄRD SLUTFÖRD ===")
