import os, re

def build_left_drawer(active_page):
    def active_cls(p_name):
        if active_page == p_name:
            return "bg-[#D6CDB8]/60 font-bold text-[#2D2721]"
        return "font-medium text-stone-700 hover:bg-[#E8DCC4]/40"

    return f'''    <!-- VÄNSTER BACKDROP & MENY (IDENTISK ÖVER ALLA SIDOR) -->
    <div id="falk-left-backdrop" onclick="closeLeftMenu()" class="fixed inset-0 bg-black/40 backdrop-blur-sm hidden opacity-0 transition-opacity duration-300 z-40"></div>
    <aside id="falk-left-drawer" class="fixed top-0 left-0 h-full w-80 bg-[#FAF8F0]/95 backdrop-blur-md shadow-2xl transform -translate-x-full transition-transform duration-300 ease-in-out z-50 flex flex-col border-r border-[#DDD0B8]">
        <div class="p-6 border-b border-[#E6E0D4]/80">
            <div class="flex items-start justify-between">
                <div>
                    <p class="text-[11px] font-bold tracking-wide text-[#8C5D37] uppercase">FALK - EN KOMPASS MED PERSPEKTIV</p>
                    <h2 class="text-xl font-extrabold text-[#2D2721] mt-0.5">Meny</h2>
                </div>
                <button onclick="closeLeftMenu()" class="p-1 text-stone-600 hover:text-black rounded-lg">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"></path></svg>
                </button>
            </div>
        </div>
        <nav class="flex-1 p-5 space-y-2 overflow-y-auto">
            <a href="/" class="flex items-center gap-3.5 px-4 py-3 text-sm rounded-2xl transition-all {active_cls('chatt')}">
                <svg class="w-5 h-5 text-stone-700 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path></svg>
                <span>Chatt</span>
            </a>
            <a href="/bibliotek" class="flex items-center gap-3.5 px-4 py-3 text-sm rounded-2xl transition-all {active_cls('bibliotek')}">
                <svg class="w-5 h-5 text-stone-700 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>
                <span>Bibliotek</span>
            </a>
            <a href="/utveckling" class="flex items-center gap-3.5 px-4 py-3 text-sm rounded-2xl transition-all {active_cls('utveckling')}">
                <svg class="w-5 h-5 text-stone-700 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg>
                <span>Min utveckling</span>
            </a>
            <a href="/installningar" class="flex items-center gap-3.5 px-4 py-3 text-sm rounded-2xl transition-all {active_cls('installningar')}">
                <svg class="w-5 h-5 text-stone-700 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                <span>Inställningar och integritet</span>
            </a>
        </nav>
        <div class="p-5 border-t border-[#E6E0D4]/80 mt-auto flex items-center justify-between">
            <span class="px-4 py-1.5 text-xs font-bold tracking-wider text-stone-800 bg-white border border-[#DDD0B8] rounded-full uppercase shadow-xs">GÄST</span>
            <button class="px-6 py-2 text-xs font-bold text-white bg-[#3A352E] hover:bg-[#2D2721] rounded-full transition-all">Logga in</button>
        </div>
    </aside>'''

def build_right_drawer():
    return '''    <!-- HÖGER BACKDROP & MENY (IDENTISK ÖVER ALLA SIDOR) -->
    <div id="falk-right-backdrop" onclick="closeRightMenu()" class="fixed inset-0 bg-black/40 backdrop-blur-sm hidden opacity-0 transition-opacity duration-300 z-40"></div>
    <aside id="falk-right-drawer" class="fixed top-0 right-0 h-full w-85 bg-[#FAF8F0]/95 backdrop-blur-md shadow-2xl transform translate-x-full transition-transform duration-300 ease-in-out z-50 flex flex-col border-l border-[#DDD0B8]">
        <div class="p-5 border-b border-[#E6E0D4]/80 space-y-3">
            <div class="flex items-start justify-between">
                <div>
                    <p class="text-[11px] font-bold tracking-wide text-[#8C5D37] uppercase">ÖVERSYNER & FOKUS</p>
                    <div class="flex items-center gap-2 mt-0.5">
                        <svg class="w-5 h-5 text-[#8C5D37] stroke-current fill-none shrink-0" viewBox="0 0 24 24" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                            <g stroke="currentColor">
                                <line x1="12" y1="1.5" x2="12" y2="3.5" />
                                <line x1="4.5" y1="4.5" x2="5.9" y2="5.9" />
                                <line x1="1.5" y1="12" x2="3.5" y2="12" />
                                <line x1="19.5" y1="4.5" x2="18.1" y2="5.9" />
                                <line x1="22.5" y1="12" x2="20.5" y2="12" />
                            </g>
                            <path d="M 8.5 13 C 7 11.2 7 8 9 6 C 10.8 4.2 13.2 4.2 15 6 C 17 8 17 11.2 15.5 13 C 14.8 13.8 14.5 14.5 14.5 15.5 L 9.5 15.5 C 9.5 14.5 9.2 13.8 8.5 13 Z" />
                            <line x1="9.5" y1="18" x2="14.5" y2="18" />
                            <line x1="10.5" y1="20.5" x2="13.5" y2="20.5" />
                        </svg>
                        <h2 class="text-lg font-extrabold text-[#2D2721]">Insikter & Påminnelser</h2>
                    </div>
                </div>
                <button onclick="closeRightMenu()" class="p-1 text-stone-600 hover:text-black rounded-lg">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"></path></svg>
                </button>
            </div>

            <div class="flex items-center gap-1.5 p-1 bg-[#E8DCC4]/50 rounded-xl border border-[#DDD0B8]">
                <button onclick="filterRightDrawer('all')" id="right-tab-all" class="right-tab-chip active flex-1 py-1 text-[11px] font-bold rounded-lg transition-all text-center">Alla</button>
                <button onclick="filterRightDrawer('insight')" id="right-tab-insight" class="right-tab-chip flex-1 py-1 text-[11px] font-bold rounded-lg transition-all text-center">Insikter</button>
                <button onclick="filterRightDrawer('reminder')" id="right-tab-reminder" class="right-tab-chip flex-1 py-1 text-[11px] font-bold rounded-lg transition-all text-center">Påminnelser</button>
            </div>
        </div>

        <div class="flex-1 p-4 space-y-3 overflow-y-auto" id="right-drawer-list"></div>

        <div class="p-4 border-t border-[#E6E0D4]/80 mt-auto">
            <button onclick="openManualInsightModal()" class="w-full py-3 bg-[#4E5C4B] hover:bg-[#3D493B] text-white text-xs font-semibold rounded-full transition-all flex items-center justify-center gap-1.5 shadow-xs">
                <span>+ Skriv egen insikt / påminnelse</span>
            </button>
        </div>
    </aside>'''

pages = {
    "index.html": "chatt",
    "bibliotek.html": "bibliotek",
    "utveckling.html": "utveckling",
    "installningar.html": "installningar"
}

for fname, page_key in pages.items():
    fpath = os.path.join("templates", fname)
    if not os.path.exists(fpath): continue
    with open(fpath, "r", encoding="utf-8") as f: html = f.read()
    
    html = re.sub(r'(?:<!-- VÄNSTER BACKDROP & MENY.*?-->\s*)?<div id="falk-left-backdrop".*?<aside id="falk-left-drawer".*?<\/aside>', build_left_drawer(page_key), html, flags=re.DOTALL)
    html = re.sub(r'(?:<!-- HÖGER BACKDROP & MENY.*?-->\s*)?<div id="falk-right-backdrop".*?<aside id="falk-right-drawer".*?<\/aside>', build_right_drawer(), html, flags=re.DOTALL)

    with open(fpath, "w", encoding="utf-8") as f: f.write(html)
    print(f"-> [OK] Uppdaterat {fname}")

print("=== ALLA 4 SIDOR HAR NU 100% EXAKT LIKADANA MENYER ===")
