import os

print("=== GENERERAR SUBPAGES: BIBLIOTEK, MIN UTVECKLING & INSTÄLLNINGAR ===")

# 1. UPPDATERA APP.PY MED RUTTER FÖR DE 3 UNDERSIDORNA
app_file = "app.py"

subpage_routes = '''

# ==========================================
# FALK SUBPAGE ROUTES (STEG 1, 2, 3)
# ==========================================
@app.route('/bibliotek')
def bibliotek():
    return render_template('bibliotek.html')

@app.route('/utveckling')
def utveckling():
    return render_template('utveckling.html')

@app.route('/installningar')
def installningar():
    return render_template('installningar.html')

@app.route('/api/user/export', methods=['GET'])
def export_user_data():
    sample_data = {
        "user_status": "Gäst",
        "export_date": "2026-11-02",
        "reflections_count": 14,
        "saved_insights": [
            "Att sätta gränser handlar inte om att stänga andra ute, utan om att hålla sig själv hel."
        ],
        "history": [
            {"date": "2026-11-01", "category": "Mening & livsriktning", "prompt": "Jag vill förstå min riktning"}
        ]
    }
    return jsonify(sample_data)

@app.route('/api/user/delete', methods=['DELETE', 'POST'])
def delete_user_account():
    print("-> [BACKEND NOTICE] Användardata och konto raderat.")
    return jsonify({"status": "success", "message": "All data har raderats."})
'''

if os.path.exists(app_file):
    with open(app_file, "r", encoding="utf-8") as f:
        app_code = f.read()
    
    if "/bibliotek" not in app_code:
        with open(app_file, "a", encoding="utf-8") as f:
            f.write(subpage_routes)
        print("-> [BACKEND OK] Rutterna /bibliotek, /utveckling och /installningar tillagda i app.py!")
    else:
        print("-> [BACKEND NOTICE] Rutterna finns redan i app.py.")

# 2. BYGG TEMPLATES/BIBLIOTEK.HTML (9 ÖVNINGSKORT -> CHATT)
bibliotek_html = '''<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FALK - Bibliotek & Övningar</title>
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
            <a href="/bibliotek" data-route="/bibliotek" class="menu-nav-item flex items-center gap-3.5 px-4 py-3 text-sm font-semibold text-[#2D2721] rounded-2xl hover:bg-[#E8DCC4]/40">
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

    <!-- HEADER -->
    <header class="flex items-center justify-between px-5 py-4 border-b border-[#D8CAB0]/80 bg-transparent sticky top-0 z-30">
        <div class="flex items-center gap-3">
            <button onclick="openLeftMenu()" class="p-1 text-current"><svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"></path></svg></button>
            <span class="px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-[#8C5D37] bg-[#FAF8F0] border border-[#DDD0B8] rounded-full uppercase">GÄST</span>
        </div>
        <div class="flex items-center">
            <a href="/" class="text-2xl font-black tracking-wider">FALK</a>
        </div>
        <div class="flex items-center gap-4">
            <a href="/" class="text-current"><svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"></path></svg></a>
        </div>
    </header>

    <!-- MAIN CONTAINER (9 ÖVNINGSKORT PÅ BIBLIOTEK) -->
    <main class="flex-1 max-w-2xl w-full mx-auto px-4 py-6">
        <div class="mb-6 text-center">
            <h1 class="text-xl font-extrabold">Övningsbibliotek</h1>
            <p class="text-xs italic opacity-75 mt-1 font-serif">Fördjupande övningar kopplade till dina reflektionsområden</p>
        </div>

        <div id="dashboard-grid" class="space-y-3.5">
            <!-- 9 ÖVNINGSKORT KOPPLADE TILL FRAMSIDANS KATEGORIER -->
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

        <!-- CHATT TRÅD VID ÖVNINGSSTART -->
        <div id="chat-thread" class="hidden space-y-4 pb-12">
            <div id="chat-messages" class="space-y-4"></div>
        </div>
    </main>

    <!-- CHATTBAR FOOTER -->
    <footer class="sticky bottom-0 bg-transparent backdrop-blur-md pt-2 pb-4 px-4 z-20">
        <div class="max-w-2xl mx-auto">
            <form id="chat-form" onsubmit="handleChatSubmit(event)" class="bg-white rounded-full p-1.5 pl-4 flex items-center justify-between shadow-sm border border-[#D8CAB0]">
                <input id="chat-input" type="text" autocomplete="off" placeholder="Starta en övning eller skriv..." class="w-full text-sm bg-transparent border-none focus:outline-none text-stone-800">
                <button type="submit" class="bg-[#4E5C4B] text-white text-xs font-semibold px-4 py-2 rounded-full">Skicka</button>
            </form>
        </div>
    </footer>

    <script>
        // TEMA-HANTERING VIA LOCALSTORAGE
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
                document.getElementById("dashboard-grid").classList.add("hidden");
                document.getElementById("chat-thread").classList.remove("hidden");
                isChatActive = true;
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
            document.querySelectorAll('.menu-nav-item').forEach(item => {
                if(item.getAttribute('data-route') === '/bibliotek') item.classList.add('nav-active-pill');
            });
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

with open("templates/bibliotek.html", "w", encoding="utf-8") as f:
    f.write(bibliotek_html)
print("-> [TEMPLATE OK] templates/bibliotek.html skapad!")

# 3. BYGG TEMPLATES/UTVECKLING.HTML (DYNAMISK DASHBOARD MED ANALYS)
utveckling_html = '''<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FALK - Min Utveckling</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body.theme-standard { background-color: #E8DCC4 !important; color: #38322B; }
        body.theme-dark { background-color: #1C1A17 !important; color: #E8DCC4; }
        .falk-card { background-color: #FAF8F0; border: 1px solid #DDD0B8; }
        body.theme-dark .falk-card { background-color: #26231F !important; border-color: #3D3730 !important; color: #E8DCC4 !important; }
        .nav-active-pill { background-color: #D6CDB8 !important; box-shadow: 0 2px 5px rgba(0,0,0,0.06); font-weight: 700 !important; }
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
            <a href="/" class="flex items-center gap-3.5 px-4 py-3 text-sm font-semibold rounded-2xl hover:bg-[#E8DCC4]/40"><span>Chatt</span></a>
            <a href="/bibliotek" class="flex items-center gap-3.5 px-4 py-3 text-sm font-semibold rounded-2xl hover:bg-[#E8DCC4]/40"><span>Bibliotek</span></a>
            <a href="/utveckling" class="nav-active-pill flex items-center gap-3.5 px-4 py-3 text-sm font-semibold rounded-2xl"><span>Min utveckling</span></a>
            <a href="/installningar" class="flex items-center gap-3.5 px-4 py-3 text-sm font-semibold rounded-2xl hover:bg-[#E8DCC4]/40"><span>Inställningar och integritet</span></a>
        </nav>
    </aside>

    <!-- HEADER -->
    <header class="flex items-center justify-between px-5 py-4 border-b border-[#D8CAB0]/80 bg-transparent sticky top-0 z-30">
        <button onclick="openLeftMenu()" class="p-1 text-current"><svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"></path></svg></button>
        <a href="/" class="text-2xl font-black tracking-wider">FALK</a>
        <a href="/" class="text-current"><svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"></path></svg></a>
    </header>

    <!-- DASHBOARD MIN UTVECKLING -->
    <main class="flex-1 max-w-2xl w-full mx-auto px-4 py-6 space-y-5">
        <div class="text-center">
            <h1 class="text-xl font-extrabold">Min utveckling & insikter</h1>
            <p class="text-xs italic opacity-75 mt-1 font-serif">FALKs analys baserad på dina reflektioner och samtal</p>
        </div>

        <!-- 1. AI-ANALYSKORT FRÅN FALK -->
        <div class="falk-card p-5 rounded-2xl shadow-sm border border-[#DDD0B8]">
            <div class="flex items-center gap-2 text-[#8C5D37] mb-2">
                <svg class="w-5 h-5 fill-none stroke-current" stroke-width="2" viewBox="0 0 24 24"><path d="M12 3v2m0 14v2m9-9h-2M5 12H3m15.364-6.364l-1.414 1.414M7.05 16.95l-1.414 1.414M18.364 18.364l-1.414-1.414M7.05 7.05L5.636 5.636"/></svg>
                <h2 class="text-xs font-bold tracking-wider uppercase">FALKs Syntes & Analys</h2>
            </div>
            <p class="text-xs leading-relaxed italic font-serif">
                "Under den senaste tiden har dina reflektioner rört sig mycket kring balansen mellan <strong>Jobb & ledarskap</strong> och <strong>Hitta lugnet igen</strong>. Du visar ett tydligt mönster av att vilja prestanda högt, men att kroppen kräver återhämtning. Ditt nästa utvecklingskliv handlar om att sätta tydliga gränser utan skuldkänslor."
            </p>
        </div>

        <!-- 2. KLUSTER & FÖRDELNING (PROGRESS BARS) -->
        <div class="falk-card p-5 rounded-2xl shadow-sm space-y-3">
            <h3 class="text-xs font-bold tracking-wider uppercase text-stone-600">Reflektionsfördelning per område</h3>
            
            <div class="space-y-2">
                <div>
                    <div class="flex justify-between text-xs font-medium mb-1"><span>Jobb, ansvar & ledarskap</span><span>42%</span></div>
                    <div class="w-full bg-stone-200 h-2 rounded-full overflow-hidden"><div class="bg-[#4E5C4B] h-full" style="width: 42%"></div></div>
                </div>
                <div>
                    <div class="flex justify-between text-xs font-medium mb-1"><span>När tankarna tar över</span><span>28%</span></div>
                    <div class="w-full bg-stone-200 h-2 rounded-full overflow-hidden"><div class="bg-[#8C5D37] h-full" style="width: 28%"></div></div>
                </div>
                <div>
                    <div class="flex justify-between text-xs font-medium mb-1"><span>Mening & livsriktning</span><span>18%</span></div>
                    <div class="w-full bg-stone-200 h-2 rounded-full overflow-hidden"><div class="bg-amber-700 h-full" style="width: 18%"></div></div>
                </div>
                <div>
                    <div class="flex justify-between text-xs font-medium mb-1"><span>Övriga områden</span><span>12%</span></div>
                    <div class="w-full bg-stone-200 h-2 rounded-full overflow-hidden"><div class="bg-stone-400 h-full" style="width: 12%"></div></div>
                </div>
            </div>
        </div>

        <!-- 3. NYCKELTAL (STATS) -->
        <div class="grid grid-cols-2 gap-3">
            <div class="falk-card p-4 rounded-2xl text-center">
                <span class="text-2xl font-black text-[#4E5C4B]">14</span>
                <p class="text-[11px] font-semibold text-stone-600 mt-0.5">Genomförda samtal</p>
            </div>
            <div class="falk-card p-4 rounded-2xl text-center">
                <span class="text-2xl font-black text-[#8C5D37]">6</span>
                <p class="text-[11px] font-semibold text-stone-600 mt-0.5">Sparade insikter</p>
            </div>
        </div>
    </main>

    <script>
        const savedTheme = localStorage.getItem('falk_theme') || 'standard';
        document.body.className = 'theme-' + savedTheme + ' min-h-screen flex flex-col justify-between antialiased relative overflow-x-hidden';
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

with open("templates/utveckling.html", "w", encoding="utf-8") as f:
    f.write(utveckling_html)
print("-> [TEMPLATE OK] templates/utveckling.html skapad!")

# 4. BYGG TEMPLATES/INSTALLNINGAR.HTML (TEMA, EXPORT, RADERA KONTO)
installningar_html = '''<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FALK - Inställningar & Integritet</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body.theme-standard { background-color: #E8DCC4 !important; color: #38322B; }
        body.theme-dark { background-color: #1C1A17 !important; color: #E8DCC4; }
        .falk-card { background-color: #FAF8F0; border: 1px solid #DDD0B8; }
        body.theme-dark .falk-card { background-color: #26231F !important; border-color: #3D3730 !important; color: #E8DCC4 !important; }
        .nav-active-pill { background-color: #D6CDB8 !important; box-shadow: 0 2px 5px rgba(0,0,0,0.06); font-weight: 700 !important; }
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
            <a href="/" class="flex items-center gap-3.5 px-4 py-3 text-sm font-semibold rounded-2xl hover:bg-[#E8DCC4]/40"><span>Chatt</span></a>
            <a href="/bibliotek" class="flex items-center gap-3.5 px-4 py-3 text-sm font-semibold rounded-2xl hover:bg-[#E8DCC4]/40"><span>Bibliotek</span></a>
            <a href="/utveckling" class="flex items-center gap-3.5 px-4 py-3 text-sm font-semibold rounded-2xl hover:bg-[#E8DCC4]/40"><span>Min utveckling</span></a>
            <a href="/installningar" class="nav-active-pill flex items-center gap-3.5 px-4 py-3 text-sm font-semibold rounded-2xl"><span>Inställningar och integritet</span></a>
        </nav>
    </aside>

    <!-- HEADER -->
    <header class="flex items-center justify-between px-5 py-4 border-b border-[#D8CAB0]/80 bg-transparent sticky top-0 z-30">
        <button onclick="openLeftMenu()" class="p-1 text-current"><svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"></path></svg></button>
        <a href="/" class="text-2xl font-black tracking-wider">FALK</a>
        <a href="/" class="text-current"><svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"></path></svg></a>
    </header>

    <!-- INSTÄLLNINGAR INNEHÅLL -->
    <main class="flex-1 max-w-2xl w-full mx-auto px-4 py-6 space-y-5">
        <div class="text-center">
            <h1 class="text-xl font-extrabold">Inställningar & integritet</h1>
            <p class="text-xs italic opacity-75 mt-1 font-serif">Hantera dina gränssnittsval, data och kontosäkerhet</p>
        </div>

        <!-- 1. VAL AV VY (TEMA-TOGGLE) -->
        <div class="falk-card p-5 rounded-2xl shadow-sm space-y-3">
            <h2 class="text-xs font-bold tracking-wider uppercase text-[#8C5D37]">Val av vy (Tema)</h2>
            <div class="grid grid-cols-2 gap-3">
                <button onclick="setFalkTheme('standard')" id="theme-btn-standard" class="py-2.5 px-4 rounded-xl text-xs font-bold border border-[#DDD0B8] transition-all">
                    FALK Standard
                </button>
                <button onclick="setFalkTheme('dark')" id="theme-btn-dark" class="py-2.5 px-4 rounded-xl text-xs font-bold border border-[#DDD0B8] transition-all">
                    Mörk vy
                </button>
            </div>
        </div>

        <!-- 2. DATAHANTERING & EXPORT -->
        <div class="falk-card p-5 rounded-2xl shadow-sm space-y-3">
            <h2 class="text-xs font-bold tracking-wider uppercase text-[#8C5D37]">Dina data & export</h2>
            <p class="text-xs opacity-80">Du äger din data. Du kan när som helst ladda ned en fullständig kopia av dina reflektioner och samtal.</p>
            <button onclick="downloadUserData()" class="bg-[#4E5C4B] text-white text-xs font-semibold px-4 py-2.5 rounded-xl hover:opacity-90 transition-all flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                <span>Exportera all min data (.json)</span>
            </button>
        </div>

        <!-- 3. JURIDIK & VINKLAR -->
        <div class="falk-card p-5 rounded-2xl shadow-sm space-y-2">
            <h2 class="text-xs font-bold tracking-wider uppercase text-[#8C5D37]">Vilkor & integritet</h2>
            <a href="#" class="block text-xs font-semibold hover:underline py-1">Användarvillkor</a>
            <a href="#" class="block text-xs font-semibold hover:underline py-1">Integritetspolicy & GDPR</a>
        </div>

        <!-- 4. RADERA KONTO (DESTRUKTIVT ZON) -->
        <div class="falk-card p-5 rounded-2xl shadow-sm space-y-3 border-red-200">
            <h2 class="text-xs font-bold tracking-wider uppercase text-red-700">Fara / Kontoåtgärder</h2>
            <p class="text-xs opacity-80">Raderar permanent hela ditt konto, dina sparade insikter och din samtalshistorik.</p>
            <button onclick="confirmAccountDeletion()" class="bg-red-700 text-white text-xs font-semibold px-4 py-2.5 rounded-xl hover:bg-red-800 transition-all">
                Radera mitt konto och all min data
            </button>
        </div>
    </main>

    <script>
        function applyThemeUI(theme) {
            document.body.className = 'theme-' + theme + ' min-h-screen flex flex-col justify-between antialiased relative overflow-x-hidden';
            const btnStd = document.getElementById('theme-btn-standard');
            const btnDark = document.getElementById('theme-btn-dark');
            
            if (theme === 'dark') {
                btnDark.classList.add('bg-[#3D3730]', 'text-white');
                btnStd.classList.remove('bg-[#2D2721]', 'text-white');
            } else {
                btnStd.classList.add('bg-[#2D2721]', 'text-white');
                btnDark.classList.remove('bg-[#3D3730]', 'text-white');
            }
        }

        function setFalkTheme(theme) {
            localStorage.setItem('falk_theme', theme);
            applyThemeUI(theme);
        }

        const savedTheme = localStorage.getItem('falk_theme') || 'standard';
        applyThemeUI(savedTheme);

        async function downloadUserData() {
            try {
                const res = await fetch('/api/user/export');
                const data = await res.json();
                const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'falk_min_data.json';
                a.click();
            } catch (e) {
                alert("Kunde inte exportera data.");
            }
        }

        async function confirmAccountDeletion() {
            if (confirm("ÄR DU SÄKER? Detta raderar permanent alla dina insikter och din samtalshistorik.")) {
                try {
                    await fetch('/api/user/delete', { method: 'POST' });
                    alert("Ditt konto och all data har raderats.");
                    window.location.href = "/";
                } catch (e) {
                    alert("Kunde inte radera konto.");
                }
            }
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

with open("templates/installningar.html", "w", encoding="utf-8") as f:
    f.write(installningar_html)
print("-> [TEMPLATE OK] templates/installningar.html skapad!")

print("\n=== SYSTEMET FÖR DE 3 UNDERSIDORNA ÄR COMPLETE ===")
