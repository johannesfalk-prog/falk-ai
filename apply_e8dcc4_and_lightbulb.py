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
    </style>
</head>
<body class="min-h-screen flex flex-col justify-between antialiased selection:bg-stone-300">

    <!-- HEADER -->
    <header class="flex items-center justify-between px-5 py-4 border-b border-[#D8CAB0]/80 bg-[#E8DCC4] sticky top-0 z-40">
        <div class="flex items-center gap-3">
            <button id="open-menu-btn" onclick="openFalkMenu()" class="flex items-center gap-2 text-stone-800 hover:opacity-70 transition-all focus:outline-none">
                <svg class="w-5 h-5 stroke-current" fill="none" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"></path>
                </svg>
                <span class="text-xs font-bold tracking-widest text-[#8C5D37] uppercase">GÄST</span>
            </button>
        </div>

        <div class="flex items-center">
            <h1 class="text-lg font-bold tracking-wider text-[#2D2721]">FALK</h1>
        </div>

        <div class="flex items-center gap-4 text-stone-800">
            <button onclick="startNewChat()" class="hover:opacity-70 transition-all" title="Ny konversation">
                <svg class="w-5 h-5 stroke-current" fill="none" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"></path>
                </svg>
            </button>
            <a href="/reflektioner" class="hover:opacity-70 transition-all" title="Reflektioner">
                <!-- GLÖDLAMPA IKON -->
                <svg class="w-5 h-5 stroke-current" fill="none" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9.663 17h4.673M12 3a7 7 0 00-7 7c0 2.38 1.156 4.49 2.94 5.823l.06.044v2.133a1 1 0 001 1h8a1 1 0 001-1v-2.133l.06-.044A6.994 6.994 0 0019 10a7 7 0 00-7-7z"></path>
                </svg>
            </a>
        </div>
    </header>

    <!-- MAIN DASHBOARD (9 KORT) -->
    <main class="flex-1 max-w-2xl w-full mx-auto px-4 py-6 space-y-3.5">

        <!-- Card 1 -->
        <button onclick="selectPrompt('Mening & livsriktning')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
            <div class="flex items-start gap-3">
                <span class="text-lg leading-none mt-0.5">🌱</span>
                <div>
                    <h2 class="text-sm font-bold text-[#332D26] group-hover:text-amber-900 transition-colors">Mening & livsriktning</h2>
                    <p class="text-xs italic text-[#7C7368] mt-1 font-serif">"Jag vill förstå vad som verkligen betyder något för mig och leva mer i linje med det."</p>
                </div>
            </div>
        </button>

        <!-- Card 2 -->
        <button onclick="selectPrompt('När tankarna tar över')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
            <div class="flex items-start gap-3">
                <span class="text-lg leading-none mt-0.5">☁️</span>
                <div>
                    <h2 class="text-sm font-bold text-[#332D26] group-hover:text-amber-900 transition-colors">När tankarna tar över</h2>
                    <p class="text-xs italic text-[#7C7368] mt-1 font-serif">"Hjälp mig sortera tankarna och hitta klarhet."</p>
                </div>
            </div>
        </button>

        <!-- Card 3 -->
        <button onclick="selectPrompt('Jobb, ansvar & ledarskap')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
            <div class="flex items-start gap-3">
                <span class="text-lg leading-none mt-0.5">💼</span>
                <div>
                    <h2 class="text-sm font-bold text-[#332D26] group-hover:text-amber-900 transition-colors">Jobb, ansvar & ledarskap</h2>
                    <p class="text-xs italic text-[#7C7368] mt-1 font-serif">"Hjälp mig hantera utmaningar och hitta nästa steg."</p>
                </div>
            </div>
        </button>

        <!-- Card 4 -->
        <button onclick="selectPrompt('Hitta lugnet igen')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
            <div class="flex items-start gap-3">
                <span class="text-lg leading-none mt-0.5">🍃</span>
                <div>
                    <h2 class="text-sm font-bold text-[#332D26] group-hover:text-amber-900 transition-colors">Hitta lugnet igen</h2>
                    <p class="text-xs italic text-[#7C7368] mt-1 font-serif">"Jag känner mig stressad eller orolig och behöver landa."</p>
                </div>
            </div>
        </button>

        <!-- Card 5 -->
        <button onclick="selectPrompt('Från mål till handling')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
            <div class="flex items-start gap-3">
                <span class="text-lg leading-none mt-0.5">🎯</span>
                <div>
                    <h2 class="text-sm font-bold text-[#332D26] group-hover:text-amber-900 transition-colors">Från mål till handling</h2>
                    <p class="text-xs italic text-[#7C7368] mt-1 font-serif">"Hjälp mig komma vidare och få saker att hända."</p>
                </div>
            </div>
        </button>

        <!-- Card 6 -->
        <button onclick="selectPrompt('Relationer & svåra samtal')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
            <div class="flex items-start gap-3">
                <span class="text-lg leading-none mt-0.5">💬</span>
                <div>
                    <h2 class="text-sm font-bold text-[#332D26] group-hover:text-amber-900 transition-colors">Relationer & svåra samtal</h2>
                    <p class="text-xs italic text-[#7C7368] mt-1 font-serif">"Hjälp mig förstå en situation och kommunicera bättre."</p>
                </div>
            </div>
        </button>

        <!-- Card 7 -->
        <button onclick="selectPrompt('Mer energi & balans')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
            <div class="flex items-start gap-3">
                <span class="text-lg leading-none mt-0.5">⚡</span>
                <div>
                    <h2 class="text-sm font-bold text-[#332D26] group-hover:text-amber-900 transition-colors">Mer energi & balans</h2>
                    <p class="text-xs italic text-[#7C7368] mt-1 font-serif">"Hjälp mig hitta hållbara vanor för sömn, energi och fokus."</p>
                </div>
            </div>
        </button>

        <!-- Card 8 -->
        <button onclick="selectPrompt('Förstå mig själv bättre')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
            <div class="flex items-start gap-3">
                <span class="text-lg leading-none mt-0.5">🔍</span>
                <div>
                    <h2 class="text-sm font-bold text-[#332D26] group-hover:text-amber-900 transition-colors">Förstå mig själv bättre</h2>
                    <p class="text-xs italic text-[#7C7368] mt-1 font-serif">"Hjälp mig upptäcka mina behov, drivkrafter och mönster."</p>
                </div>
            </div>
        </button>

        <!-- Card 9 -->
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
    <footer class="sticky bottom-0 bg-[#E8DCC4]/90 backdrop-blur-md pt-2 pb-4 px-4">
        <div class="max-w-2xl mx-auto">
            <div class="bg-white rounded-full p-1.5 pl-4 flex items-center justify-between shadow-sm border border-[#D8CAB0]">
                <div class="flex items-center gap-3 flex-1">
                    <svg class="w-5 h-5 text-stone-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path>
                    </svg>
                    <input type="text" placeholder="Skriv till mig eller välj ett alternativ..." class="w-full text-sm bg-transparent border-none focus:outline-none text-stone-800 placeholder-stone-400">
                </div>
                <div class="flex items-center gap-2">
                    <button class="p-1.5 text-stone-400 hover:text-stone-600 transition-all">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"></path>
                        </svg>
                    </button>
                    <button class="bg-[#2D3B36] text-white text-xs font-semibold px-4 py-2 rounded-full hover:bg-[#232F2B] transition-all">
                        Skicka
                    </button>
                </div>
            </div>
            <p class="text-[10px] text-center font-semibold tracking-widest text-[#9C8F7A] mt-3 uppercase">POWERED BY WAYJS</p>
        </div>
    </footer>

    <script src="/static/js/dist/app.min.js?v=9999"></script>
</body>
</html>
'''

with open(target_file, "w", encoding="utf-8") as f:
    f.write(target_html)

print("-> [SUCCESS] Färg #E8DCC4 och glödlampa-ikon uppdaterad direkt i templates/index.html (Ingen backup skapad)!")
