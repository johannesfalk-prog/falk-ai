import os

print("=== STARTAR ÅTERSTÄLLNING AV IKO NER OCH SOLID HEADER ===")

# 1. TEMPLATES UTKAST OCH REPARATION
templates_dir = "templates"

# COMMON HEADER COMPONENT (SOLID BAKGRUND + CENTRERAD FALK + GLÖDLAMPA)
header_html = '''    <!-- HEADER (SOLID BAKGRUND, ABSOLUT CENTRERING, GLÖDLAMPA) -->
    <header class="relative flex items-center justify-between px-5 py-4 border-b border-[#D8CAB0]/80 bg-[#E8DCC4] sticky top-0 z-30 transition-colors duration-200">
        <div class="flex items-center gap-3 z-10">
            <button id="open-menu-btn" onclick="openLeftMenu()" class="p-1 text-black hover:opacity-75 transition-all focus:outline-none" title="Öppna meny">
                <svg class="w-6 h-6 text-black stroke-current" fill="none" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"></path>
                </svg>
            </button>
            <span class="px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-[#8C5D37] bg-[#FAF8F0] border border-[#DDD0B8] rounded-full uppercase shadow-xs">
                GÄST
            </span>
        </div>

        <div class="absolute left-1/2 -translate-x-1/2 flex items-center">
            <a href="/" class="text-2xl font-black tracking-wider text-black hover:opacity-75 transition-all cursor-pointer">FALK</a>
        </div>

        <div class="flex items-center gap-4 z-10">
            <a href="/" class="text-black hover:opacity-75 transition-all" title="Startsida / Ny chat">
                <svg class="w-5 h-5 text-black stroke-current" fill="none" stroke-width="2.2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"></path>
                </svg>
            </a>

            <button onclick="openRightMenu()" class="group text-black hover:opacity-100 transition-all focus:outline-none p-0.5" title="Insikter & Påminnelser">
                <svg class="w-6 h-6 text-black stroke-current fill-none" stroke-width="1.8" viewBox="0 0 24 24">
                    <g class="opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                        <line x1="12" y1="1.5" x2="12" y2="3.5" stroke-linecap="round" stroke-width="2" />
                        <line x1="4.5" y1="4.5" x2="5.9" y2="5.9" stroke-linecap="round" stroke-width="2" />
                        <line x1="1.5" y1="12" x2="3.5" y2="12" stroke-linecap="round" stroke-width="2" />
                        <line x1="19.5" y1="4.5" x2="18.1" y2="5.9" stroke-linecap="round" stroke-width="2" />
                        <line x1="22.5" y1="12" x2="20.5" y2="20.5" stroke-linecap="round" stroke-width="2" />
                    </g>
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 18h6m-4 2.5h2M12 5.5a5.5 5.5 0 00-5.5 5.5c0 2 1.1 3.7 2.7 4.6V17a1 1 0 001 1h3.6a1 1 0 001-1v-1.4c1.6-.9 2.7-2.6 2.7-4.6A5.5 5.5 0 0012 5.5z"></path>
                </svg>
            </button>
        </div>
    </header>'''

# COMMON FOOTER / CHAT FORM COMPONENT (MIKROFON + TOGGLE + SKICKA)
footer_chat_form = '''            <form id="chat-form" onsubmit="handleChatSubmit(event)" class="bg-white rounded-full p-1.5 pl-4 flex items-center justify-between shadow-sm border border-[#D8CAB0]">
                <div class="flex items-center gap-3 flex-1">
                    <svg class="w-5 h-5 text-stone-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path>
                    </svg>
                    <input id="chat-input" type="text" autocomplete="off" placeholder="Skriv till mig eller välj ett alternativ..." class="w-full text-sm bg-transparent border-none focus:outline-none text-stone-800 placeholder-stone-400">
                </div>
                <div class="flex items-center gap-2">
                    <button type="button" class="p-1.5 text-stone-500 hover:text-black transition-all transform rotate-90" title="Inställningar">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"></path>
                        </svg>
                    </button>
                    <button type="submit" class="bg-[#4E5C4B] hover:bg-[#3D493B] text-white text-xs font-semibold px-4 py-2 rounded-full transition-all cursor-pointer">
                        Skicka
                    </button>
                </div>
            </form>'''

# CSS STYLING FOR DARK MODE HEADER SOLIDITY
dark_header_css = '''
        body.theme-dark header {
            background-color: #1C1A17 !important;
            border-color: #3D3730 !important;
        }
        body.theme-dark header a, body.theme-dark header button {
            color: #E8DCC4 !important;
        }
'''

def update_file(filename):
    path = os.path.join(templates_dir, filename)
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    # Add dark mode CSS rule if missing
    if "body.theme-dark header" not in html and "</style>" in html:
        html = html.replace("</style>", dark_header_css + "\n    </style>")

    # Replace header block
    import re
    html = re.sub(r'<header.*?</header>', header_html, html, flags=re.DOTALL)

    # Replace chat-form inside footer if present
    if '<form id="chat-form"' in html:
        html = re.sub(r'<form id="chat-form".*?</form>', footer_chat_form, html, flags=re.DOTALL)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"-> [SUCCESS] {filename} uppdaterad med återställda ikoner och solid header.")

for t in ["index.html", "bibliotek.html", "utveckling.html", "installningar.html"]:
    update_file(t)

print("\n=== ÅTERSTÄLLNING FULLSTÄNDIGT SLUTFÖRD ===")
