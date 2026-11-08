import os

print("=== STARTAR APPLICERING AV HEADER-CENTRERING OCH BIBLIOTEKS-FIX ===")

# 1. UPPDATERA TEMPLATES/INDEX.HTML (CENTRERAD HEADER)
index_file = os.path.join("templates", "index.html")
if os.path.exists(index_file):
    with open(index_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Ersätt header-strukturen med absolut centrering
    old_header = '''<header class="flex items-center justify-between px-5 py-4 border-b border-[#D8CAB0]/80 bg-[#E8DCC4] sticky top-0 z-30">'''
    new_header = '''<header class="relative flex items-center justify-between px-5 py-4 border-b border-[#D8CAB0]/80 bg-[#E8DCC4] sticky top-0 z-30">'''
    
    old_logo = '''<div class="flex items-center font-black">
            <a href="/" class="text-2xl font-black tracking-wider text-black hover:opacity-75 transition-all cursor-pointer">FALK</a>
        </div>'''
    old_logo_alt = '''<div class="flex items-center">
            <a href="/" class="text-2xl font-black tracking-wider text-black hover:opacity-75 transition-all cursor-pointer">FALK</a>
        </div>'''
    
    new_logo = '''<div class="absolute left-1/2 -translate-x-1/2 flex items-center">
            <a href="/" class="text-2xl font-black tracking-wider text-black hover:opacity-75 transition-all cursor-pointer">FALK</a>
        </div>'''

    content = content.replace(old_header, new_header)
    content = content.replace(old_logo, new_logo)
    content = content.replace(old_logo_alt, new_logo)

    with open(index_file, "w", encoding="utf-8") as f:
        f.write(content)
    print("-> [SUCCESS] Header centrerad i templates/index.html")

# 2. UPPDATERA TEMPLATES/BIBLIOTEK.HTML (REN RUBRIK + INKAPSLAD I GRID)
bibliotek_file = os.path.join("templates", "bibliotek.html")
bibliotek_html = '''<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FALK - Övningar</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body.theme-standard { background-color: #E8DCC4 !important; color: #38322B; }
        body.theme-dark { background-color: #1C1A17 !important; color: #E8DCC4; }
        
        .falk-card { background-color: #FAF8F0; border: 1px solid #DDD0B8; }
        body.theme-dark .falk-card { background-color: #26231F !important; border-color: #3D3730 !important; color: #E8DCC4 !important; }
        
        .filter-btn-active { background-color: #2D2721 !important; color: #FFFFFF !important; }
        .nav-active-pill { background-color: #D6CDB8 !important; box-shadow: 0 2px 5px rgba(0,0,0,0.06); font-weight: 700 !important; }
        body.theme-dark .nav-active-pill { background-color: #3D3730 !important; color: #FFF !important; }

        .user-bubble { background-color: #4E5C4B !important; color: #FAF8F0; border-radius: 1.25rem 1.25rem 0.25rem 1.25rem; white-space: pre-wrap; word-break: break-word; }
        .ai-bubble { background-color: #FAF8F0; color: #2D2721; border: 1px solid #DDD0B8; border-radius: 1.25rem 1.25rem 1.25rem 0.25rem; white-space: pre-wrap; word-break: break-word; line-height: 1.6; }
        body.theme-dark .ai-bubble { background-color: #26231F !important; color: #E8DCC4 !important; border-color: #3D3730 !important; }
    </style>
</head>
<body class="theme-standard min-h-screen flex flex-col justify-between antialiased selection:bg-stone-300 relative overflow-x-hidden">

    <!-- VÄNSTER BACKDROP & MENY -->
    <div id="falk-left-backdrop" onclick="closeLeftMenu()" class="fixed inset-0 bg-black/40 backdrop-blur-sm hidden opacity-0 transition-opacity duration-300 z-40"></div>
    <aside id="falk-left-drawer" class="fixed top-0 left-0 h-full w-80 bg-[#FAF8F0]/95 backdrop-blur-md shadow-2xl transform -translate-x-full transition-transform duration-300 ease-in-out z-50 flex flex-col border-r border-[#DDD0B8]">
        <div class="p-6 border-b border-[#E6E0D4]/80">
            <div class="flex items-start justify-between">
                <div>
                    <p class="text-[11px] font-bold tracking-wide text-[#8C5D37] uppercase">FALK - En kompass med perspektiv</p>
                    <h2 class="text-xl font-extrabold text-[#2D2721] mt-0.5">Meny</h2>
                </div>
                <button onclick="closeLeftMenu()" class="p-1 text-stone-600 hover:text-black rounded-lg">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"></path></svg>
                </button>
            </div>
        </div>
        <nav class="flex-1 p-5 space-y-2 overflow-y-auto">
            <a href="/" data-route="/" class="menu-nav-item flex items-center gap-3.5 px-4 py-3 text-sm font-semibold text-[#2D2721] rounded-2xl hover:bg-[#E8DCC4]/40">
                <svg class="w-5 h-5 text-black" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path></svg>
                <span>Chatt</span>
            </a>
            <a href="/bibliotek" data-route="/bibliotek" class="menu-nav-item nav-active-pill flex items-center gap-3.5 px-4 py-3 text-sm font-semibold text-[#2D2721] rounded-2xl">
                <svg class="w-5 h-5 text-black" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>
                <span>Bibliotek</span>
            </a>
            <a href="/utveckling" data-route="/utveckling" class="menu-nav-item flex items-center gap-3.5 px-4 py-3 text-sm font-semibold text-[#2D2721] rounded-2xl hover:bg-[#E8DCC4]/40">
                <svg class="w-5 h-5 text-black" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg>
                <span>Min utveckling</span>
            </a>
            <a href="/installningar" data-route="/installningar" class="menu-nav-item flex items-center gap-3.5 px-4 py-3 text-sm font-semibold text-[#2D2721] rounded-2xl hover:bg-[#E8DCC4]/40">
                <svg class="w-5 h-5 text-black" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path></svg>
                <span>Inställningar och integritet</span>
            </a>
        </nav>
        <div class="p-5 border-t border-[#E6E0D4]/80">
            <div class="bg-[#E6DEC9]/70 backdrop-blur-sm rounded-full p-1.5 px-4 flex items-center justify-between border border-[#DDD0B8]/60">
                <span class="px-3 py-1 bg-white/90 text-[11px] font-bold text-stone-700 rounded-full uppercase">GÄST</span>
                <a href="/login" class="bg-[#4E5C4B] text-white text-xs font-semibold px-4 py-1.5 rounded-full">Logga in</a>
            </div>
        </div>
    </aside>

    <!-- HEADER MED ABSOLUT CENTRERING -->
    <header class="relative flex items-center justify-between px-5 py-4 border-b border-[#D8CAB0]/80 bg-transparent sticky top-0 z-30">
        <div class="flex items-center gap-3">
            <button onclick="openLeftMenu()" class="p-1 text-current"><svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"></path></svg></button>
            <span class="px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-[#8C5D37] bg-[#FAF8F0] border border-[#DDD0B8] rounded-full uppercase">GÄST</span>
        </div>
        
        <div class="absolute left-1/2 -translate-x-1/2 flex items-center">
            <a href="/" class="text-2xl font-black tracking-wider text-current">FALK</a>
        </div>

        <div class="flex items-center gap-4">
            <a href="/" class="text-current"><svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"></path></svg></a>
        </div>
    </header>

    <!-- MAIN CONTAINER -->
    <main class="flex-1 max-w-2xl w-full mx-auto px-4 py-6">

        <!-- DASHBOARD GRID (RUBRIKEN "ÖVNINGAR" LIGGER NU INUTI GRIDET OCH DÖLJS MED DET) -->
        <div id="dashboard-grid" class="space-y-3.5 transition-opacity duration-300">
            <div class="mb-4 text-center">
                <h1 class="text-xl font-extrabold">Övningar</h1>
            </div>

            <button onclick="selectPrompt('Övning Mening: Hjälp mig identifiera mina tre mest obrytbara kärnvärden i livet just nu.')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
                <div class="flex items-start gap-3">
                    <span class="text-lg leading-none mt-0.5">🌱</span>
                    <div>
                        <h2 class="text-sm font-bold group-hover:text-amber-900">Övning: Värdekompassen</h2>
                        <p class="text-[13px] italic opacity-80 mt-1 font-serif font-medium">"Hjälp mig identifiera mina tre mest obrytbara kärnvärden i livet just nu."</p>
                    </div>
                </div>
            </button>

            <button onclick="selectPrompt('Övning Tankesortering: Guide mig i att syna och ifrågasätta en tanke som gnager i mig.')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
                <div class="flex items-start gap-3">
                    <span class="text-lg leading-none mt-0.5">☁️</span>
                    <div>
                        <h2 class="text-sm font-bold group-hover:text-amber-900">Övning: Syna tanken</h2>
                        <p class="text-[13px] italic opacity-80 mt-1 font-serif font-medium">"Guide mig i att syna och ifrågasätta en tanke som gnager i mig."</p>
                    </div>
                </div>
            </button>

            <button onclick="selectPrompt('Övning Ledarskap: Hjälp mig formulera och strukturera ett svårt beslut jag skjuter på.')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
                <div class="flex items-start gap-3">
                    <span class="text-lg leading-none mt-0.5">💼</span>
                    <div>
                        <h2 class="text-sm font-bold group-hover:text-amber-900">Övning: Beslutsklarhet</h2>
                        <p class="text-[13px] italic opacity-80 mt-1 font-serif font-medium">"Hjälp mig formulera och strukturera ett svårt beslut jag skjuter på."</p>
                    </div>
                </div>
            </button>

            <button onclick="selectPrompt('Övning Lugn: Ge mig en 3-stegs mikro-reflektion för att släppa anspänning här och nu.')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
                <div class="flex items-start gap-3">
                    <span class="text-lg leading-none mt-0.5">🍃</span>
                    <div>
                        <h2 class="text-sm font-bold group-hover:text-amber-900">Övning: Lugnsankring</h2>
                        <p class="text-[13px] italic opacity-80 mt-1 font-serif font-medium">"Ge mig en 3-stegs mikro-reflektion för att släppa anspänning här och nu."</p>
                    </div>
                </div>
            </button>

            <button onclick="selectPrompt('Övning Handling: Hjälp mig bryta ned mitt viktigaste mål till en 10-minuters mikrohandling.')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
                <div class="flex items-start gap-3">
                    <span class="text-lg leading-none mt-0.5">🎯</span>
                    <div>
                        <h2 class="text-sm font-bold group-hover:text-amber-900">Övning: Mikrosteg</h2>
                        <p class="text-[13px] italic opacity-80 mt-1 font-serif font-medium">"Hjälp mig bryta ned mitt viktigaste mål till en 10-minuters mikrohandling."</p>
                    </div>
                </div>
            </button>

            <button onclick="selectPrompt('Övning Relationer: Hjälp mig förbereda mina argument inför ett tufft samtal.')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
                <div class="flex items-start gap-3">
                    <span class="text-lg leading-none mt-0.5">💬</span>
                    <div>
                        <h2 class="text-sm font-bold group-hover:text-amber-900">Övning: Samtalsförberedelse</h2>
                        <p class="text-[13px] italic opacity-80 mt-1 font-serif font-medium">"Hjälp mig förbereda mina argument inför ett tufft samtal."</p>
                    </div>
                </div>
            </button>

            <button onclick="selectPrompt('Övning Energi: Analysera mina energitjuvar under det senaste dygnet.')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
                <div class="flex items-start gap-3">
                    <span class="text-lg leading-none mt-0.5">⚡</span>
                    <div>
                        <h2 class="text-sm font-bold group-hover:text-amber-900">Övning: Kartlägg energitjuvar</h2>
                        <p class="text-[13px] italic opacity-80 mt-1 font-serif font-medium">"Analysera mina energitjuvar under det senaste dygnet."</p>
                    </div>
                </div>
            </button>

            <button onclick="selectPrompt('Övning Mönster: Hjälp mig se om jag upprepar en invand reaktion i en återkommande situation.')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
                <div class="flex items-start gap-3">
                    <span class="text-lg leading-none mt-0.5">🔍</span>
                    <div>
                        <h2 class="text-sm font-bold group-hover:text-amber-900">Övning: Mönsterkoll</h2>
                        <p class="text-[13px] italic opacity-80 mt-1 font-serif font-medium">"Hjälp mig se om jag upprepar en invand reaktion i en återkommande situation."</p>
                    </div>
                </div>
            </button>

            <button onclick="selectPrompt('Övning Perspektiv: Hjälp mig se min nuvarande utmaning ur ett utomståendes ögon.')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
                <div class="flex items-start gap-3">
                    <span class="text-lg leading-none mt-0.5">💡</span>
                    <div>
                        <h2 class="text-sm font-bold group-hover:text-amber-900">Övning: Utomstående blick</h2>
                        <p class="text-[13px] italic opacity-80 mt-1 font-serif font-medium">"Hjälp mig se min nuvarande utmaning ur ett utomståendes ögon."</p>
                    </div>
                </div>
            </button>
        </div>

        <!-- CHATT TRÅD (VISAS NÄR ÖVNING STARTAS) -->
        <div id="chat-thread" class="hidden space-y-4 pb-12">
            <div id="chat-messages" class="space-y-4"></div>
        </div>
    </main>

    <!-- FOOTER -->
    <footer class="sticky bottom-0 bg-transparent backdrop-blur-md pt-2 pb-4 px-4 z-20">
        <div class="max-w-2xl mx-auto">
            <form id="chat-form" onsubmit="handleChatSubmit(event)" class="bg-white rounded-full p-1.5 pl-4 flex items-center justify-between shadow-sm border border-[#D8CAB0]">
                <input id="chat-input" type="text" autocomplete="off" placeholder="Starta en övning eller skriv..." class="w-full text-sm bg-transparent border-none focus:outline-none text-stone-800">
                <button type="submit" class="bg-[#4E5C4B] text-white text-xs font-semibold px-4 py-2 rounded-full">Skicka</button>
            </form>
        </div>
    </footer>

    <script>
        const savedTheme = localStorage.getItem('falk_theme') || 'standard';
        document.body.className = 'theme-' + savedTheme + ' min-h-screen flex flex-col justify-between antialiased selection:bg-stone-300 relative overflow-x-hidden';

        let isChatActive = false;
        function escapeHtml(str) { return str ? str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;") : ''; }

        function selectPrompt(promptText) {
            document.getElementById("chat-input").value = promptText;
            executeSendMessage(promptText);
        }

        function handleChatSubmit(event) {
            event.preventDefault();
            const input = document.getElementById("chat-input");
            if (input.value.trim()) executeSendMessage(input.value.trim());
        }

        function executeSendMessage(text) {
            document.getElementById("chat-input").value = "";
            if (!isChatActive) {
                const grid = document.getElementById("dashboard-grid");
                const thread = document.getElementById("chat-thread");
                
                grid.classList.add("opacity-0");
                setTimeout(() => {
                    grid.classList.add("hidden");
                    thread.classList.remove("hidden");
                    isChatActive = true;
                }, 200);
            }
            appendUserMessage(text);
            const aiBubble = appendAiSkeleton();
            setTimeout(() => {
                aiBubble.innerText = 'FALK Övningsrespons: Jag guidar dig genom denna övning. Låt oss ta det steg för steg. Vad väcker frågan hos dig först?';
            }, 1000);
        }

        function appendUserMessage(text) {
            const div = document.createElement("div");
            div.className = "flex justify-end";
            div.innerHTML = '<div class="user-bubble max-w-[85%] px-4 py-3 text-sm shadow-xs">' + escapeHtml(text) + '</div>';
            document.getElementById("chat-messages").appendChild(div);
        }

        function appendAiSkeleton() {
            const div = document.createElement("div");
            div.className = "flex justify-start";
            const bubble = document.createElement("div");
            bubble.className = "ai-bubble max-w-[90%] px-4 py-3 text-sm shadow-xs leading-relaxed";
            bubble.innerHTML = '<span class="animate-pulse text-stone-500 font-medium">FALK tänker...</span>';
            div.appendChild(bubble);
            document.getElementById("chat-messages").appendChild(div);
            return bubble;
        }

        function openLeftMenu() {
            document.getElementById("falk-left-drawer").classList.remove("-translate-x-full");
            document.getElementById("falk-left-backdrop").classList.remove("hidden");
            setTimeout(() => document.getElementById("falk-left-backdrop").classList.remove("opacity-0"), 10);
        }
        function closeLeftMenu() {
            document.getElementById("falk-left-drawer").classList.add("-translate-x-full");
            document.getElementById("falk-left-backdrop").classList.add("opacity-0");
            setTimeout(() => document.getElementById("falk-left-backdrop").classList.add("hidden"), 300);
        }
    </script>
</body>
</html>
'''

with open(bibliotek_file, "w", encoding="utf-8") as f:
    f.write(bibliotek_html)
print("-> [SUCCESS] templates/bibliotek.html uppdaterad: Endast 'Övningar' som titel, döljs helt när chatten startas!")

# 3. UPPDATERA TEMPLATES/UTVECKLING.HTML (CENTRERAD HEADER)
utveckling_file = os.path.join("templates", "utveckling.html")
if os.path.exists(utveckling_file):
    with open(utveckling_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    content = content.replace(
        '<header class="flex items-center justify-between px-5 py-4 border-b border-[#D8CAB0]/80 bg-transparent sticky top-0 z-30">',
        '<header class="relative flex items-center justify-between px-5 py-4 border-b border-[#D8CAB0]/80 bg-transparent sticky top-0 z-30">'
    )
    content = content.replace(
        '<div class="flex items-center">\n            <a href="/" class="text-2xl font-black tracking-wider">FALK</a>\n        </div>',
        '<div class="absolute left-1/2 -translate-x-1/2 flex items-center">\n            <a href="/" class="text-2xl font-black tracking-wider text-current">FALK</a>\n        </div>'
    )
    content = content.replace(
        '<a href="/" class="text-2xl font-black tracking-wider">FALK</a>',
        '<div class="absolute left-1/2 -translate-x-1/2 flex items-center"><a href="/" class="text-2xl font-black tracking-wider text-current">FALK</a></div>'
    )
    
    with open(utveckling_file, "w", encoding="utf-8") as f:
        f.write(content)
    print("-> [SUCCESS] Header centrerad i templates/utveckling.html")

# 4. UPPDATERA TEMPLATES/INSTALLNINGAR.HTML (CENTRERAD HEADER)
installningar_file = os.path.join("templates", "installningar.html")
if os.path.exists(installningar_file):
    with open(installningar_file, "r", encoding="utf-8") as f:
        content = f.read()

    content = content.replace(
        '<header class="flex items-center justify-between px-5 py-4 border-b border-[#D8CAB0]/80 bg-transparent sticky top-0 z-30">',
        '<header class="relative flex items-center justify-between px-5 py-4 border-b border-[#D8CAB0]/80 bg-transparent sticky top-0 z-30">'
    )
    content = content.replace(
        '<a href="/" class="text-2xl font-black tracking-wider">FALK</a>',
        '<div class="absolute left-1/2 -translate-x-1/2 flex items-center"><a href="/" class="text-2xl font-black tracking-wider text-current">FALK</a></div>'
    )

    with open(installningar_file, "w", encoding="utf-8") as f:
        f.write(content)
    print("-> [SUCCESS] Header centrerad i templates/installningar.html")

print("\n=== REPARATION AV HEADER OCH BIBLIOTEK FULLSTÄNDIGT VERKSTÄLLD ===")
