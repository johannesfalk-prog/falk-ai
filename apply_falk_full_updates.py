import os

target_file = os.path.join("templates", "index.html")

target_html = '''<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FALK - En kompass med AI</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {
            background-color: #E8DCC4 !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #38322B;
        }
        .falk-card {
            background-color: #FAF8F0;
            border: 1px solid #DDD0B8;
        }
        .filter-btn-active {
            background-color: #2D2721 !important;
            color: #FFFFFF !important;
        }
    </style>
</head>
<body class="min-h-screen flex flex-col justify-between antialiased selection:bg-stone-300 relative overflow-x-hidden">

    <!-- VÄNSTER BACKDROP -->
    <div id="falk-left-backdrop" onclick="closeLeftMenu()" class="fixed inset-0 bg-black/40 backdrop-blur-sm hidden opacity-0 transition-opacity duration-300 z-40"></div>

    <!-- VÄNSTER MENY-DRAWER (Punkt 7) -->
    <aside id="falk-left-drawer" class="fixed top-0 left-0 h-full w-80 bg-[#FAF8F0] shadow-2xl transform -translate-x-full transition-transform duration-300 ease-in-out z-50 flex flex-col border-r border-[#DDD0B8]">
        <div class="p-5 flex items-center justify-between border-b border-[#E6E0D4]">
            <span class="text-xs font-bold tracking-widest text-[#8C5D37] uppercase">MENY</span>
            <button onclick="closeLeftMenu()" class="p-1.5 text-stone-600 hover:text-black rounded-lg transition-colors">
                <svg class="w-6 h-6 stroke-current" fill="none" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        </div>
        <nav class="flex-1 p-5 space-y-3">
            <a href="/" class="flex items-center gap-3 px-4 py-3 text-sm font-semibold text-[#2D2721] hover:bg-[#E8DCC4]/50 rounded-xl transition-all">
                <svg class="w-5 h-5 text-black" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                </svg>
                <span>Chatt</span>
            </a>
            <a href="/bibliotek" class="flex items-center gap-3 px-4 py-3 text-sm font-semibold text-[#2D2721] hover:bg-[#E8DCC4]/50 rounded-xl transition-all">
                <svg class="w-5 h-5 text-black" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                </svg>
                <span>Bibliotek</span>
            </a>
            <a href="/utveckling" class="flex items-center gap-3 px-4 py-3 text-sm font-semibold text-[#2D2721] hover:bg-[#E8DCC4]/50 rounded-xl transition-all">
                <svg class="w-5 h-5 text-black" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                </svg>
                <span>Min utveckling</span>
            </a>
            <a href="/installningar" class="flex items-center gap-3 px-4 py-3 text-sm font-semibold text-[#2D2721] hover:bg-[#E8DCC4]/50 rounded-xl transition-all">
                <svg class="w-5 h-5 text-black" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
                <span>Inställningar och integritet</span>
            </a>
        </nav>
    </aside>

    <!-- HÖGER BACKDROP -->
    <div id="falk-right-backdrop" onclick="closeRightMenu()" class="fixed inset-0 bg-black/40 backdrop-blur-sm hidden opacity-0 transition-opacity duration-300 z-40"></div>

    <!-- HÖGER PANEL - INSIKTER & PÅMINNELSER (Punkt 6) -->
    <aside id="falk-right-drawer" class="fixed top-0 right-0 h-full w-80 bg-[#FAF8F0] shadow-2xl transform translate-x-full transition-transform duration-300 ease-in-out z-50 flex flex-col border-l border-[#DDD0B8]">
        <div class="p-5 flex items-center justify-between border-b border-[#E6E0D4]">
            <div class="flex items-center gap-2">
                <svg class="w-5 h-5 text-black" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9.663 17h4.673M12 3a7 7 0 00-7 7c0 2.38 1.156 4.49 2.94 5.823l.06.044v2.133a1 1 0 001 1h8a1 1 0 001-1v-2.133l.06-.044A6.994 6.994 0 0019 10a7 7 0 00-7-7z"></path>
                </svg>
                <h3 class="text-sm font-bold text-[#2D2721]">Insikter & Påminnelser</h3>
            </div>
            <button onclick="closeRightMenu()" class="p-1.5 text-stone-600 hover:text-black rounded-lg transition-colors">
                <svg class="w-6 h-6 stroke-current" fill="none" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        </div>

        <!-- FILTER-KNAPPAR -->
        <div class="p-4 border-b border-[#E6E0D4] flex items-center justify-between gap-1 bg-[#E8DCC4]/30">
            <button id="filter-all" onclick="filterItems('all')" class="flex-1 py-1.5 text-xs font-semibold rounded-lg border border-[#DDD0B8] transition-all filter-btn-active">Alla</button>
            <button id="filter-insights" onclick="filterItems('insight')" class="flex-1 py-1.5 text-xs font-semibold rounded-lg border border-[#DDD0B8] text-stone-700 hover:bg-[#E8DCC4]/50 transition-all">Insikter</button>
            <button id="filter-reminders" onclick="filterItems('reminder')" class="flex-1 py-1.5 text-xs font-semibold rounded-lg border border-[#DDD0B8] text-stone-700 hover:bg-[#E8DCC4]/50 transition-all">Påminnelser</button>
        </div>

        <!-- INNEHÅLLSLISTA -->
        <div class="flex-1 overflow-y-auto p-4 space-y-3" id="insights-container">
            <!-- Eksempel Insikt -->
            <div class="insight-item insight-type p-3.5 bg-white rounded-xl border border-[#E6E0D4] shadow-sm">
                <span class="text-[10px] font-bold tracking-wider text-[#8C5D37] uppercase">INSIKT</span>
                <p class="text-xs text-[#38322B] mt-1 italic font-serif">"Att sätta gränser handlar inte om att stänga andra ute, utan om att hålla sig själv hel."</p>
            </div>
            <!-- Eksempel Påminnelse -->
            <div class="insight-item reminder-type p-3.5 bg-white rounded-xl border border-[#E6E0D4] shadow-sm">
                <span class="text-[10px] font-bold tracking-wider text-[#4E5C4B] uppercase">PÅMINNELSE</span>
                <p class="text-xs text-[#38322B] mt-1 font-medium">Ta 3 djupa andetag innan nästa möte.</p>
            </div>
        </div>
    </aside>

    <!-- HEADER (Punkt 1, 2, 3, 4, 5) -->
    <header class="flex items-center justify-between px-5 py-4 border-b border-[#D8CAB0]/80 bg-[#E8DCC4] sticky top-0 z-30">
        <!-- VÄNSTER: MENYKNAPP (Punkt 7) -->
        <div class="flex items-center gap-3">
            <button id="open-menu-btn" onclick="openLeftMenu()" class="flex items-center gap-2 text-black hover:opacity-70 transition-all focus:outline-none">
                <svg class="w-5 h-5 text-black stroke-current" fill="none" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"></path>
                </svg>
                <span class="text-xs font-bold tracking-widest text-[#8C5D37] uppercase">GÄST</span>
            </button>
        </div>

        <!-- MITTEN: FALK LOGGA (Punkt 3, 4) -->
        <div class="flex items-center">
            <a href="/" class="text-xl font-black tracking-wider text-black hover:opacity-75 transition-all cursor-pointer">FALK</a>
        </div>

        <!-- HÖGER: IKONER (+) OCH GLÖDLAMPA (Punkt 1, 2, 5, 6) -->
        <div class="flex items-center gap-4">
            <!-- + IKON (Punkt 5) -->
            <a href="/" class="text-black hover:opacity-75 transition-all" title="Startsida / Ny chat">
                <svg class="w-5 h-5 text-black stroke-current" fill="none" stroke-width="2.2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"></path>
                </svg>
            </a>
            <!-- GLÖDLAMPA SVG IKON (Punkt 1, 2, 6) -->
            <button onclick="openRightMenu()" class="text-black hover:opacity-75 transition-all focus:outline-none" title="Insikter & Påminnelser">
                <svg class="w-5 h-5 text-black stroke-current" fill="none" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9.663 17h4.673M12 3a7 7 0 00-7 7c0 2.38 1.156 4.49 2.94 5.823l.06.044v2.133a1 1 0 001 1h8a1 1 0 001-1v-2.133l.06-.044A6.994 6.994 0 0019 10a7 7 0 00-7-7z"></path>
                </svg>
            </button>
        </div>
    </header>

    <!-- MAIN DASHBOARD (9 KORT) -->
    <main class="flex-1 max-w-2xl w-full mx-auto px-4 py-6 space-y-3.5">
        <button onclick="selectPrompt('Mening & livsriktning')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
            <div class="flex items-start gap-3">
                <span class="text-lg leading-none mt-0.5">🌱</span>
                <div>
                    <h2 class="text-sm font-bold text-[#332D26] group-hover:text-amber-900 transition-colors">Mening & livsriktning</h2>
                    <p class="text-xs italic text-[#7C7368] mt-1 font-serif">"Jag vill förstå vad som verkligen betyder något för mig och leva mer i linje med det."</p>
                </div>
            </div>
        </button>

        <button onclick="selectPrompt('När tankarna tar över')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
            <div class="flex items-start gap-3">
                <span class="text-lg leading-none mt-0.5">☁️</span>
                <div>
                    <h2 class="text-sm font-bold text-[#332D26] group-hover:text-amber-900 transition-colors">När tankarna tar över</h2>
                    <p class="text-xs italic text-[#7C7368] mt-1 font-serif">"Hjälp mig sortera tankarna och hitta klarhet."</p>
                </div>
            </div>
        </button>

        <button onclick="selectPrompt('Jobb, ansvar & ledarskap')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
            <div class="flex items-start gap-3">
                <span class="text-lg leading-none mt-0.5">💼</span>
                <div>
                    <h2 class="text-sm font-bold text-[#332D26] group-hover:text-amber-900 transition-colors">Jobb, ansvar & ledarskap</h2>
                    <p class="text-xs italic text-[#7C7368] mt-1 font-serif">"Hjälp mig hantera utmaningar och hitta nästa steg."</p>
                </div>
            </div>
        </button>

        <button onclick="selectPrompt('Hitta lugnet igen')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
            <div class="flex items-start gap-3">
                <span class="text-lg leading-none mt-0.5">🍃</span>
                <div>
                    <h2 class="text-sm font-bold text-[#332D26] group-hover:text-amber-900 transition-colors">Hitta lugnet igen</h2>
                    <p class="text-xs italic text-[#7C7368] mt-1 font-serif">"Jag känner mig stressad eller orolig och behöver landa."</p>
                </div>
            </div>
        </button>

        <button onclick="selectPrompt('Från mål till handling')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
            <div class="flex items-start gap-3">
                <span class="text-lg leading-none mt-0.5">🎯</span>
                <div>
                    <h2 class="text-sm font-bold text-[#332D26] group-hover:text-amber-900 transition-colors">Från mål till handling</h2>
                    <p class="text-xs italic text-[#7C7368] mt-1 font-serif">"Hjälp mig komma vidare och få saker att hända."</p>
                </div>
            </div>
        </button>

        <button onclick="selectPrompt('Relationer & svåra samtal')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
            <div class="flex items-start gap-3">
                <span class="text-lg leading-none mt-0.5">💬</span>
                <div>
                    <h2 class="text-sm font-bold text-[#332D26] group-hover:text-amber-900 transition-colors">Relationer & svåra samtal</h2>
                    <p class="text-xs italic text-[#7C7368] mt-1 font-serif">"Hjälp mig förstå en situation och kommunicera bättre."</p>
                </div>
            </div>
        </button>

        <button onclick="selectPrompt('Mer energi & balans')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
            <div class="flex items-start gap-3">
                <span class="text-lg leading-none mt-0.5">⚡</span>
                <div>
                    <h2 class="text-sm font-bold text-[#332D26] group-hover:text-amber-900 transition-colors">Mer energi & balans</h2>
                    <p class="text-xs italic text-[#7C7368] mt-1 font-serif">"Hjälp mig hitta hållbara vanor för sömn, energi och fokus."</p>
                </div>
            </div>
        </button>

        <button onclick="selectPrompt('Förstå mig själv bättre')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
            <div class="flex items-start gap-3">
                <span class="text-lg leading-none mt-0.5">🔍</span>
                <div>
                    <h2 class="text-sm font-bold text-[#332D26] group-hover:text-amber-900 transition-colors">Förstå mig själv bättre</h2>
                    <p class="text-xs italic text-[#7C7368] mt-1 font-serif">"Hjälp mig upptäcka mina behov, drivkrafter och mönster."</p>
                </div>
            </div>
        </button>

        <button onclick="selectPrompt('Utmana mina tankar')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
            <div class="flex items-start gap-3">
                <span class="text-lg leading-none mt-0.5">💡</span>
                <div>
                    <h2 class="text-sm font-bold text-[#332D26] group-hover:text-amber-900 transition-colors">Utmana mina tankar</h2>
                    <p class="text-xs italic text-[#7C7368] mt-1 font-serif">"Hjälp mig se nya perspektiv och ifrågasätta det jag tar för givet."</p>
                </div>
            </div>
        </button>
    </main>

    <!-- FOOTER & CHATTBAR -->
    <footer class="sticky bottom-0 bg-[#E8DCC4]/90 backdrop-blur-md pt-2 pb-4 px-4 z-20">
        <div class="max-w-2xl mx-auto">
            <div class="bg-white rounded-full p-1.5 pl-4 flex items-center justify-between shadow-sm border border-[#D8CAB0]">
                <div class="flex items-center gap-3 flex-1">
                    <svg class="w-5 h-5 text-stone-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path>
                    </svg>
                    <input type="text" placeholder="Skriv till mig eller välj ett alternativ..." class="w-full text-sm bg-transparent border-none focus:outline-none text-stone-800 placeholder-stone-400">
                </div>
                <div class="flex items-center gap-2">
                    <!-- TOGGLE IKON ROTERAD 90 GRADER (Punkt 9) -->
                    <button class="p-1.5 text-stone-500 hover:text-black transition-all transform rotate-90" title="Inställningar">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"></path>
                        </svg>
                    </button>
                    <!-- SKICKA KNAPP GRÖN #4E5C4B (Punkt 8) -->
                    <button class="bg-[#4E5C4B] hover:bg-[#3D493B] text-white text-xs font-semibold px-4 py-2 rounded-full transition-all">
                        Skicka
                    </button>
                </div>
            </div>
            <p class="text-[10px] text-center font-semibold tracking-widest text-[#9C8F7A] mt-3 uppercase">POWERED BY WAYJS</p>
        </div>
    </footer>

    <!-- INTERAKTIV LOGIK FÖR VÄNSTER OCH HÖGER MENY -->
    <script>
        // VÄNSTER MENY (Punkt 7)
        function openLeftMenu() {
            const drawer = document.getElementById("falk-left-drawer");
            const backdrop = document.getElementById("falk-left-backdrop");
            backdrop.classList.remove("hidden");
            setTimeout(() => backdrop.classList.remove("opacity-0"), 10);
            drawer.classList.remove("-translate-x-full");
            document.body.style.overflow = "hidden";
        }

        function closeLeftMenu() {
            const drawer = document.getElementById("falk-left-drawer");
            const backdrop = document.getElementById("falk-left-backdrop");
            drawer.classList.add("-translate-x-full");
            backdrop.classList.add("opacity-0");
            setTimeout(() => {
                backdrop.classList.add("hidden");
            }, 300);
            document.body.style.overflow = "";
        }

        // HÖGER MENY (Punkt 6)
        function openRightMenu() {
            const drawer = document.getElementById("falk-right-drawer");
            const backdrop = document.getElementById("falk-right-backdrop");
            backdrop.classList.remove("hidden");
            setTimeout(() => backdrop.classList.remove("opacity-0"), 10);
            drawer.classList.remove("translate-x-full");
            document.body.style.overflow = "hidden";
        }

        function closeRightMenu() {
            const drawer = document.getElementById("falk-right-drawer");
            const backdrop = document.getElementById("falk-right-backdrop");
            drawer.classList.add("translate-x-full");
            backdrop.classList.add("opacity-0");
            setTimeout(() => {
                backdrop.classList.add("hidden");
            }, 300);
            document.body.style.overflow = "";
        }

        // FILTER-LOGIK I HÖGER MENY
        function filterItems(type) {
            const items = document.querySelectorAll('.insight-item');
            const btnAll = document.getElementById('filter-all');
            const btnIns = document.getElementById('filter-insights');
            const btnRem = document.getElementById('filter-reminders');

            [btnAll, btnIns, btnRem].forEach(b => b.classList.remove('filter-btn-active'));

            if (type === 'all') {
                btnAll.classList.add('filter-btn-active');
                items.forEach(i => i.style.display = 'block');
            } else if (type === 'insight') {
                btnIns.classList.add('filter-btn-active');
                items.forEach(i => i.classList.contains('insight-type') ? i.style.display = 'block' : i.style.display = 'none');
            } else if (type === 'reminder') {
                btnRem.classList.add('filter-btn-active');
                items.forEach(i => i.classList.contains('reminder-type') ? i.style.display = 'block' : i.style.display = 'none');
            }
        }
    </script>
    <script src="/static/js/dist/app.min.js?v=9999"></script>
</body>
</html>
'''

with open(target_file, "w", encoding="utf-8") as f:
    f.write(target_html)

print("-> [SUCCESS] Alla 9 punkter genomförda direkt i templates/index.html (Ingen säkerhetskopia skapad)!")
