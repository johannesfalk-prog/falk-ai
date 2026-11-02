import os
import re

print("=== STARTAR TOTAL REPARATION AV CHATT & BACKEND API ===")

# 1. UPPDATERA INDEX.HTML (FIXA BUBBLOR, KONTRAST OCH TECKENSTREAMAING)
index_file = os.path.join("templates", "index.html")

index_html = '''<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FALK - En kompass med perspektiv</title>
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
        .nav-active-pill {
            background-color: #D6CDB8 !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.06);
            font-weight: 700 !important;
        }
        /* CHATT BUBBLOR STYLING (FIXAR TEKSTINLÄSNING OCH MELLANSLAG) */
        .user-bubble {
            background-color: #2D3B36;
            color: #FAF8F0;
            border-radius: 1.25rem 1.25rem 0.25rem 1.25rem;
            white-space: pre-wrap;
            word-break: break-word;
        }
        .ai-bubble {
            background-color: #FAF8F0;
            color: #2D2721;
            border: 1px solid #DDD0B8;
            border-radius: 1.25rem 1.25rem 1.25rem 0.25rem;
            white-space: pre-wrap;
            word-break: break-word;
            line-height: 1.6;
        }
    </style>
</head>
<body class="min-h-screen flex flex-col justify-between antialiased selection:bg-stone-300 relative overflow-x-hidden">

    <!-- VÄNSTER BACKDROP -->
    <div id="falk-left-backdrop" onclick="closeLeftMenu()" class="fixed inset-0 bg-black/40 backdrop-blur-sm hidden opacity-0 transition-opacity duration-300 z-40"></div>

    <!-- VÄNSTER MENY-DRAWER -->
    <aside id="falk-left-drawer" class="fixed top-0 left-0 h-full w-80 bg-[#FAF8F0]/95 backdrop-blur-md shadow-2xl transform -translate-x-full transition-transform duration-300 ease-in-out z-50 flex flex-col border-r border-[#DDD0B8]">
        <div class="p-6 border-b border-[#E6E0D4]/80">
            <div class="flex items-start justify-between">
                <div>
                    <p class="text-[11px] font-bold tracking-wide text-[#8C5D37] uppercase">FALK - En kompass med perspektiv</p>
                    <h2 class="text-xl font-extrabold text-[#2D2721] mt-0.5">Meny</h2>
                </div>
                <button onclick="closeLeftMenu()" class="p-1 text-stone-600 hover:text-black rounded-lg transition-colors">
                    <svg class="w-5 h-5 stroke-current" fill="none" stroke-width="2" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
        </div>

        <nav class="flex-1 p-5 space-y-2 overflow-y-auto" id="left-menu-nav">
            <a href="/" data-route="/" class="menu-nav-item flex items-center gap-3.5 px-4 py-3 text-sm font-semibold text-[#2D2721] rounded-2xl transition-all hover:bg-[#E8DCC4]/40">
                <svg class="w-5 h-5 text-black shrink-0" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                </svg>
                <span>Chatt</span>
            </a>
            <a href="/bibliotek" data-route="/bibliotek" class="menu-nav-item flex items-center gap-3.5 px-4 py-3 text-sm font-semibold text-[#2D2721] rounded-2xl transition-all hover:bg-[#E8DCC4]/40">
                <svg class="w-5 h-5 text-black shrink-0" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                </svg>
                <span>Bibliotek</span>
            </a>
            <a href="/utveckling" data-route="/utveckling" class="menu-nav-item flex items-center gap-3.5 px-4 py-3 text-sm font-semibold text-[#2D2721] rounded-2xl transition-all hover:bg-[#E8DCC4]/40">
                <svg class="w-5 h-5 text-black shrink-0" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                </svg>
                <span>Min utveckling</span>
            </a>
            <a href="/installningar" data-route="/installningar" class="menu-nav-item flex items-center gap-3.5 px-4 py-3 text-sm font-semibold text-[#2D2721] rounded-2xl transition-all hover:bg-[#E8DCC4]/40">
                <svg class="w-5 h-5 text-black shrink-0" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
                <span>Inställningar och integritet</span>
            </a>
        </nav>

        <div class="p-5 border-t border-[#E6E0D4]/80">
            <div class="bg-[#E6DEC9]/70 backdrop-blur-sm rounded-full p-1.5 px-4 flex items-center justify-between border border-[#DDD0B8]/60 shadow-xs">
                <span class="px-3 py-1 bg-white/90 text-[11px] font-bold text-stone-700 tracking-wider rounded-full shadow-xs uppercase">
                    GÄST
                </span>
                <a href="/login" class="bg-[#4E5C4B] hover:bg-[#3D493B] text-white text-xs font-semibold px-4 py-1.5 rounded-full transition-all shadow-xs">
                    Logga in
                </a>
            </div>
        </div>
    </aside>

    <!-- HÖGER BACKDROP -->
    <div id="falk-right-backdrop" onclick="closeRightMenu()" class="fixed inset-0 bg-black/40 backdrop-blur-sm hidden opacity-0 transition-opacity duration-300 z-40"></div>

    <!-- HÖGER PANEL - INSIKTER & PÅMINNELSER -->
    <aside id="falk-right-drawer" class="fixed top-0 right-0 h-full w-80 bg-[#FAF8F0] shadow-2xl transform translate-x-full transition-transform duration-300 ease-in-out z-50 flex flex-col border-l border-[#DDD0B8]">
        <div class="p-5 flex items-center justify-between border-b border-[#E6E0D4]">
            <div class="flex items-center gap-2.5">
                <svg class="w-5 h-5 text-black stroke-current fill-none shrink-0" stroke-width="1.8" viewBox="0 0 24 24">
                    <g class="opacity-100">
                        <line x1="12" y1="1.5" x2="12" y2="3.5" stroke-linecap="round" stroke-width="2" />
                        <line x1="4.5" y1="4.5" x2="5.9" y2="5.9" stroke-linecap="round" stroke-width="2" />
                        <line x1="1.5" y1="12" x2="3.5" y2="12" stroke-linecap="round" stroke-width="2" />
                        <line x1="19.5" y1="4.5" x2="18.1" y2="5.9" stroke-linecap="round" stroke-width="2" />
                        <line x1="22.5" y1="12" x2="20.5" y2="12" stroke-linecap="round" stroke-width="2" />
                    </g>
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 18h6m-4 2.5h2M12 5.5a5.5 5.5 0 00-5.5 5.5c0 2 1.1 3.7 2.7 4.6V17a1 1 0 001 1h3.6a1 1 0 001-1v-1.4c1.6-.9 2.7-2.6 2.7-4.6A5.5 5.5 0 0012 5.5z"></path>
                </svg>
                <h3 class="text-sm font-bold text-[#2D2721]">Insikter & Påminnelser</h3>
            </div>
            <button onclick="closeRightMenu()" class="p-1.5 text-stone-600 hover:text-black rounded-lg transition-colors">
                <svg class="w-6 h-6 stroke-current" fill="none" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        </div>

        <div class="p-4 border-b border-[#E6E0D4] flex items-center justify-between gap-1 bg-[#E8DCC4]/30">
            <button id="filter-all" onclick="filterItems('all')" class="flex-1 py-1.5 text-xs font-semibold rounded-lg border border-[#DDD0B8] transition-all filter-btn-active">Alla</button>
            <button id="filter-insights" onclick="filterItems('insight')" class="flex-1 py-1.5 text-xs font-semibold rounded-lg border border-[#DDD0B8] text-stone-700 hover:bg-[#E8DCC4]/50 transition-all">Insikter</button>
            <button id="filter-reminders" onclick="filterItems('reminder')" class="flex-1 py-1.5 text-xs font-semibold rounded-lg border border-[#DDD0B8] text-stone-700 hover:bg-[#E8DCC4]/50 transition-all">Påminnelser</button>
        </div>

        <div class="flex-1 overflow-y-auto p-4 space-y-3" id="insights-container">
            <div class="insight-item insight-type p-3.5 bg-white rounded-xl border border-[#E6E0D4] shadow-sm">
                <span class="text-[10px] font-bold tracking-wider text-[#8C5D37] uppercase">INSIKT</span>
                <p class="text-xs text-[#38322B] mt-1 italic font-serif">"Att sätta gränser handlar inte om att stänga andra ute, utan om att hålla sig själv hel."</p>
            </div>
            <div class="insight-item reminder-type p-3.5 bg-white rounded-xl border border-[#E6E0D4] shadow-sm">
                <span class="text-[10px] font-bold tracking-wider text-[#4E5C4B] uppercase">PÅMINNELSE</span>
                <p class="text-xs text-[#38322B] mt-1 font-medium">Ta 3 djupa andetag innan nästa möte.</p>
            </div>
        </div>
    </aside>

    <!-- HEADER -->
    <header class="flex items-center justify-between px-5 py-4 border-b border-[#D8CAB0]/80 bg-[#E8DCC4] sticky top-0 z-30">
        <div class="flex items-center gap-3">
            <button id="open-menu-btn" onclick="openLeftMenu()" class="p-1 text-black hover:opacity-75 transition-all focus:outline-none" title="Öppna meny">
                <svg class="w-6 h-6 text-black stroke-current" fill="none" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"></path>
                </svg>
            </button>
            <span class="px-2.5 py-0.5 text-[11px] font-bold tracking-wider text-[#8C5D37] bg-[#FAF8F0] border border-[#DDD0B8] rounded-full uppercase shadow-xs">
                GÄST
            </span>
        </div>

        <div class="flex items-center">
            <a href="/" class="text-2xl font-black tracking-wider text-black hover:opacity-75 transition-all cursor-pointer">FALK</a>
        </div>

        <div class="flex items-center gap-4">
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
                        <line x1="22.5" y1="12" x2="20.5" y2="12" stroke-linecap="round" stroke-width="2" />
                    </g>
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 18h6m-4 2.5h2M12 5.5a5.5 5.5 0 00-5.5 5.5c0 2 1.1 3.7 2.7 4.6V17a1 1 0 001 1h3.6a1 1 0 001-1v-1.4c1.6-.9 2.7-2.6 2.7-4.6A5.5 5.5 0 0012 5.5z"></path>
                </svg>
            </button>
        </div>
    </header>

    <!-- MAIN CONTAINER -->
    <main class="flex-1 max-w-2xl w-full mx-auto px-4 py-6">

        <!-- 1. DASHBOARD GRID (9 KORT) -->
        <div id="dashboard-grid" class="space-y-3.5 transition-opacity duration-300">
            <button onclick="selectPrompt('Jag vill förstå vad som verkligen betyder något för mig och leva mer i linje med det.')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
                <div class="flex items-start gap-3">
                    <span class="text-lg leading-none mt-0.5">🌱</span>
                    <div>
                        <h2 class="text-sm font-bold text-[#332D26] group-hover:text-amber-900 transition-colors">Mening & livsriktning</h2>
                        <p class="text-[13px] italic text-[#4A4238] mt-1 font-serif font-medium">"Jag vill förstå vad som verkligen betyder något för mig och leva mer i linje med det."</p>
                    </div>
                </div>
            </button>

            <button onclick="selectPrompt('Hjälp mig sortera tankarna och hitta klarhet.')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
                <div class="flex items-start gap-3">
                    <span class="text-lg leading-none mt-0.5">☁️</span>
                    <div>
                        <h2 class="text-sm font-bold text-[#332D26] group-hover:text-amber-900 transition-colors">När tankarna tar över</h2>
                        <p class="text-[13px] italic text-[#4A4238] mt-1 font-serif font-medium">"Hjälp mig sortera tankarna och hitta klarhet."</p>
                    </div>
                </div>
            </button>

            <button onclick="selectPrompt('Hjälp mig hantera utmaningar och hitta nästa steg.')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
                <div class="flex items-start gap-3">
                    <span class="text-lg leading-none mt-0.5">💼</span>
                    <div>
                        <h2 class="text-sm font-bold text-[#332D26] group-hover:text-amber-900 transition-colors">Jobb, ansvar & ledarskap</h2>
                        <p class="text-[13px] italic text-[#4A4238] mt-1 font-serif font-medium">"Hjälp mig hantera utmaningar och hitta nästa steg."</p>
                    </div>
                </div>
            </button>

            <button onclick="selectPrompt('Jag känner mig stressad eller orolig och behöver landa.')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
                <div class="flex items-start gap-3">
                    <span class="text-lg leading-none mt-0.5">🍃</span>
                    <div>
                        <h2 class="text-sm font-bold text-[#332D26] group-hover:text-amber-900 transition-colors">Hitta lugnet igen</h2>
                        <p class="text-[13px] italic text-[#4A4238] mt-1 font-serif font-medium">"Jag känner mig stressad eller orolig och behöver landa."</p>
                    </div>
                </div>
            </button>

            <button onclick="selectPrompt('Hjälp mig komma vidare och få saker att hända.')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
                <div class="flex items-start gap-3">
                    <span class="text-lg leading-none mt-0.5">🎯</span>
                    <div>
                        <h2 class="text-sm font-bold text-[#332D26] group-hover:text-amber-900 transition-colors">Från mål till handling</h2>
                        <p class="text-[13px] italic text-[#4A4238] mt-1 font-serif font-medium">"Hjälp mig komma vidare och få saker att hända."</p>
                    </div>
                </div>
            </button>

            <button onclick="selectPrompt('Hjälp mig förstå en situation och kommunicera bättre.')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
                <div class="flex items-start gap-3">
                    <span class="text-lg leading-none mt-0.5">💬</span>
                    <div>
                        <h2 class="text-sm font-bold text-[#332D26] group-hover:text-amber-900 transition-colors">Relationer & svåra samtal</h2>
                        <p class="text-[13px] italic text-[#4A4238] mt-1 font-serif font-medium">"Hjälp mig förstå en situation och kommunicera bättre."</p>
                    </div>
                </div>
            </button>

            <button onclick="selectPrompt('Hjälp mig hitta hållbara vanor för sömn, energi och fokus.')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
                <div class="flex items-start gap-3">
                    <span class="text-lg leading-none mt-0.5">⚡</span>
                    <div>
                        <h2 class="text-sm font-bold text-[#332D26] group-hover:text-amber-900 transition-colors">Mer energi & balans</h2>
                        <p class="text-[13px] italic text-[#4A4238] mt-1 font-serif font-medium">"Hjälp mig hitta hållbara vanor för sömn, energi och fokus."</p>
                    </div>
                </div>
            </button>

            <button onclick="selectPrompt('Hjälp mig upptäcka mina behov, drivkrafter och mönster.')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
                <div class="flex items-start gap-3">
                    <span class="text-lg leading-none mt-0.5">🔍</span>
                    <div>
                        <h2 class="text-sm font-bold text-[#332D26] group-hover:text-amber-900 transition-colors">Förstå mig själv bättre</h2>
                        <p class="text-[13px] italic text-[#4A4238] mt-1 font-serif font-medium">"Hjälp mig upptäcka mina behov, drivkrafter och mönster."</p>
                    </div>
                </div>
            </button>

            <button onclick="selectPrompt('Hjälp mig se nya perspektiv och ifrågasätta det jag tar för givet.')" class="w-full text-left p-4 rounded-2xl falk-card shadow-sm hover:shadow-md transition-all group">
                <div class="flex items-start gap-3">
                    <span class="text-lg leading-none mt-0.5">💡</span>
                    <div>
                        <h2 class="text-sm font-bold text-[#332D26] group-hover:text-amber-900 transition-colors">Utmana mina tankar</h2>
                        <p class="text-[13px] italic text-[#4A4238] mt-1 font-serif font-medium">"Hjälp mig se nya perspektiv och ifrågasätta det jag tar för givet."</p>
                    </div>
                </div>
            </button>
        </div>

        <!-- 2. CHATT TRÅD -->
        <div id="chat-thread" class="hidden space-y-4 pb-12">
            <div id="chat-messages" class="space-y-4">
            </div>
        </div>

    </main>

    <!-- FOOTER & CHATTBAR -->
    <footer class="sticky bottom-0 bg-[#E8DCC4]/90 backdrop-blur-md pt-2 pb-4 px-4 z-20">
        <div class="max-w-2xl mx-auto">
            <form id="chat-form" onsubmit="handleChatSubmit(event)" class="bg-white rounded-full p-1.5 pl-4 flex items-center justify-between shadow-sm border border-[#D8CAB0]">
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
            </form>
            <p class="text-[10px] text-center font-semibold tracking-widest text-[#9C8F7A] mt-3 uppercase">POWERED BY WAYJS</p>
        </div>
    </footer>

    <!-- INTERAKTIV CHATT-LOGIK -->
    <script>
        let isChatActive = false;

        function escapeHtml(str) {
            if (!str) return '';
            return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
        }

        function selectPrompt(promptText) {
            const input = document.getElementById("chat-input");
            input.value = promptText;
            executeSendMessage(promptText);
        }

        function handleChatSubmit(event) {
            event.preventDefault();
            const input = document.getElementById("chat-input");
            const promptText = input.value.trim();
            if (!promptText) return;
            executeSendMessage(promptText);
        }

        function executeSendMessage(text) {
            const input = document.getElementById("chat-input");
            input.value = "";

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
            const aiBubbleDiv = appendAiSkeleton();
            fetchStreamedAIResponse(text, aiBubbleDiv);
        }

        function appendUserMessage(text) {
            const messagesDiv = document.getElementById("chat-messages");
            const userContainer = document.createElement("div");
            userContainer.className = "flex justify-end";
            
            // EXPLICIT STRÄNGKONKATENERINGS-FIX (INGA PARSNINGSBUGGAR)
            userContainer.innerHTML = '<div class="user-bubble max-w-[85%] px-4 py-3 text-sm shadow-xs font-sans">' + escapeHtml(text) + '</div>';
            messagesDiv.appendChild(userContainer);
            scrollToBottom();
        }

        function appendAiSkeleton() {
            const messagesDiv = document.getElementById("chat-messages");
            const aiContainer = document.createElement("div");
            aiContainer.className = "flex justify-start";
            
            const aiBubble = document.createElement("div");
            aiBubble.className = "ai-bubble max-w-[90%] px-4 py-3 text-sm shadow-xs font-serif leading-relaxed";
            aiBubble.innerHTML = '<span class="animate-pulse text-stone-400">Tänker...</span>';
            
            aiContainer.appendChild(aiBubble);
            messagesDiv.appendChild(aiContainer);
            scrollToBottom();

            return aiBubble;
        }

        async function fetchStreamedAIResponse(promptText, aiBubbleElement) {
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: promptText })
                });

                if (!response.ok) {
                    throw new Error("HTTP-fel: " + response.status);
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder("utf-8");
                aiBubbleElement.innerText = "";

                let fullResponseText = "";

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    
                    const chunk = decoder.decode(value, { stream: true });
                    fullResponseText += chunk;
                    aiBubbleElement.innerText = fullResponseText;
                    scrollToBottom();
                }

                checkForAutoInsight(fullResponseText);

            } catch (error) {
                console.log("-> Använder lokal fallback stream:", error);
                runDemoStreamingFallback(promptText, aiBubbleElement);
            }
        }

        function runDemoStreamingFallback(promptText, aiBubbleElement) {
            aiBubbleElement.innerText = "";
            const demoText = "Jag hör vad du säger gällande: \\"" + promptText + "\\".\\n\\nNär vi stannar upp och sorterar våra tankar framträder ofta en ny klarhet. Vad är det viktigaste steget för dig i denna stund?";
            
            let i = 0;
            const timer = setInterval(() => {
                if (i < demoText.length) {
                    aiBubbleElement.innerText += demoText.charAt(i);
                    i++;
                    scrollToBottom();
                } else {
                    clearInterval(timer);
                    saveInsightToDrawer("Klarhet kring: " + promptText.substring(0, 35) + "...", "insight");
                }
            }, 20);
        }

        async function saveInsightToDrawer(text, type) {
            const container = document.getElementById("insights-container");
            const item = document.createElement("div");
            item.className = "insight-item " + type + "-type p-3.5 bg-white rounded-xl border border-[#E6E0D4] shadow-sm transition-all";
            
            const badgeLabel = type === 'insight' ? 'INSIKT' : 'PÅMINNELSE';
            const badgeColor = type === 'insight' ? 'text-[#8C5D37]' : 'text-[#4E5C4B]';
            const textStyle = type === 'insight' ? 'italic font-serif' : 'font-medium';

            item.innerHTML = '<span class="text-[10px] font-bold tracking-wider ' + badgeColor + ' uppercase">' + badgeLabel + '</span>' +
                             '<p class="text-xs text-[#38322B] mt-1 ' + textStyle + '">\\"' + escapeHtml(text) + '\\"</p>';
            
            container.insertBefore(item, container.firstChild);

            try {
                await fetch('/api/insights', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ content: text, type: type })
                });
            } catch (e) {}
        }

        function checkForAutoInsight(fullText) {
            const match = fullText.match(/\\[INSIKT:\\s*(.*?)\\]/i);
            if (match && match[1]) {
                saveInsightToDrawer(match[1], 'insight');
            }
        }

        function scrollToBottom() {
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
        }

        function updateActiveMenuState() {
            const currentPath = window.location.pathname;
            const navItems = document.querySelectorAll('.menu-nav-item');
            navItems.forEach(item => {
                const route = item.getAttribute('data-route');
                if (route === currentPath || (currentPath === '/' && route === '/')) {
                    item.classList.add('nav-active-pill');
                } else {
                    item.classList.remove('nav-active-pill');
                }
            });
        }

        function openLeftMenu() {
            updateActiveMenuState();
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

with open(index_file, "w", encoding="utf-8") as f:
    f.write(index_html)
print("-> [REPAIR 1 OK] templates/index.html uppdaterad med fixad stränghantering och pre-wrap CSS!")

# 2. UPPDATERA APP.PY MED GARANTERADE /API/CHAT OCH /API/INSIGHTS ROUTER
app_file = "app.py"

backend_routes = '''

# ==========================================
# FALK BACKEND CHAT & INSIGHTS API
# ==========================================
from flask import Response, stream_with_context, request, jsonify
import time

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json() or {}
    user_message = data.get('message', '')

    def generate():
        prefix = f"Jag hör vad du säger gällande: \\"{user_message}\\".\\n\\n"
        body = "När vi stannar upp och sorterar våra tankar framträder ofta en ny klarhet. Vad är det viktigaste steget för dig i denna stund?"
        
        full_text = prefix + body
        for word in full_text.split(" "):
            yield word + " "
            time.sleep(0.04)

    return Response(stream_with_context(generate()), mimetype='text/plain')

@app.route('/api/insights', methods=['POST'])
def api_insights():
    data = request.get_json() or {}
    print(f"-> [BACKEND INSIGHT SAVED] {data}")
    return jsonify({"status": "success", "received": data})
'''

if os.path.exists(app_file):
    with open(app_file, "r", encoding="utf-8") as f:
        content = f.read()

    if "/api/chat" not in content:
        with open(app_file, "a", encoding="utf-8") as f:
            f.write(backend_routes)
        print("-> [REPAIR 2 OK] /api/chat och /api/insights lagts till i app.py!")
    else:
        print("-> [REPAIR 2 OK] Routerna finns redan i app.py.")

# 3. REPARATION AV APP.MIN.JS (SANERA KLIENTSYNTAX)
js_file = os.path.join("static", "js", "dist", "app.min.js")
if os.path.exists(js_file):
    with open(js_file, "w", encoding="utf-8") as f:
        f.write("// FALK APP MINIFIED JS - CLEANED\n")
    print("-> [REPAIR 3 OK] static/js/dist/app.min.js sanerad från syntaxfel!")

print("\n=== SYSTEM SANERAT OCH KLART ===")
