import os

os.makedirs('templates', exist_ok=True)

html_content = '''<!DOCTYPE html>
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
        body.theme-dark .nav-active-pill { background-color: #3D3730 !important; color: #FFF !important; }

        .filter-chip {
            background-color: #FAF8F0;
            border: 1px solid #DDD0B8;
            color: #4A4238;
            transition: all 0.2s ease;
        }
        .filter-chip.active {
            background-color: #2D2721 !important;
            color: #FFFFFF !important;
            border-color: #2D2721 !important;
        }
        body.theme-dark .filter-chip {
            background-color: #26231F;
            border-color: #3D3730;
            color: #C5BBAA;
        }
        body.theme-dark .filter-chip.active {
            background-color: #E8DCC4 !important;
            color: #1C1A17 !important;
        }
        
        .widget-item { transition: all 0.25s ease-in-out; }
        .widget-hidden { display: none !important; }
    </style>
</head>
<body class="theme-standard min-h-screen flex flex-col justify-between antialiased selection:bg-stone-300 relative overflow-x-hidden">

    <!-- VÄNSTER BACKDROP & MENY DRAWER -->
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

    <!-- MAIN CONTAINER (MIN UTVECKLING DASHBOARD) -->
    <main class="flex-1 max-w-6xl w-full mx-auto px-4 py-6 space-y-6">

        <!-- RUBRIK & HANDLINGS-KNAPPAR -->
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
                <h1 class="text-2xl font-black tracking-tight">Min utveckling</h1>
                <p class="text-xs italic opacity-75 mt-0.5 font-serif">Översikt över din resa mot ditt bästa jag.</p>
            </div>
            <div class="flex items-center gap-3">
                <div class="relative">
                    <select class="falk-card text-xs font-semibold px-3 py-2 rounded-xl focus:outline-none appearance-none pr-8 cursor-pointer shadow-xs">
                        <option>1 maj – 31 maj 2024</option>
                        <option>1 apr – 30 apr 2024</option>
                        <option>1 jan – 31 dec 2024</option>
                    </select>
                    <span class="absolute right-2.5 top-2.5 pointer-events-none text-xs opacity-60">▼</span>
                </div>
                <button onclick="window.print()" class="falk-card text-xs font-semibold px-4 py-2 rounded-xl hover:opacity-80 transition-all flex items-center gap-1.5 shadow-xs">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                    <span>Exportera</span>
                </button>
            </div>
        </div>

        <!-- DYNAMISK FILTER-/SORTERINGSRAD (10 ELEMENT) -->
        <div class="falk-card p-3.5 rounded-2xl space-y-2 shadow-xs">
            <div class="flex items-center justify-between">
                <span class="text-[11px] font-bold uppercase tracking-wider text-[#8C5D37]">Filtrera vy & element:</span>
                <span class="text-[10px] opacity-60 font-medium">Klicka för att visa/dölja moduler</span>
            </div>
            <div class="flex flex-wrap gap-1.5" id="filter-chip-container">
                <button onclick="toggleWidgetFilter('all')" id="chip-all" class="filter-chip active text-xs px-3 py-1 rounded-full font-semibold">Alla</button>
                <button onclick="toggleWidgetFilter('utvecklingspoang')" id="chip-utvecklingspoang" class="filter-chip text-xs px-3 py-1 rounded-full font-medium">Utvecklingspoäng</button>
                <button onclick="toggleWidgetFilter('streak')" id="chip-streak" class="filter-chip text-xs px-3 py-1 rounded-full font-medium">Streak</button>
                <button onclick="toggleWidgetFilter('reflektioner')" id="chip-reflektioner" class="filter-chip text-xs px-3 py-1 rounded-full font-medium">Reflektioner</button>
                <button onclick="toggleWidgetFilter('vanor-uppfyllda')" id="chip-vanor-uppfyllda" class="filter-chip text-xs px-3 py-1 rounded-full font-medium">Vanor uppfyllda</button>
                <button onclick="toggleWidgetFilter('utveckling-tid')" id="chip-utveckling-tid" class="filter-chip text-xs px-3 py-1 rounded-full font-medium">Min utveckling över tid</button>
                <button onclick="toggleWidgetFilter('utvecklingshjul')" id="chip-utvecklingshjul" class="filter-chip text-xs px-3 py-1 rounded-full font-medium">Utvecklingshjul</button>
                <button onclick="toggleWidgetFilter('mina-mal')" id="chip-mina-mal" class="filter-chip text-xs px-3 py-1 rounded-full font-medium">Mina mål</button>
                <button onclick="toggleWidgetFilter('mina-vanor')" id="chip-mina-vanor" class="filter-chip text-xs px-3 py-1 rounded-full font-medium">Mina vanor</button>
                <button onclick="toggleWidgetFilter('reflektioner-humor')" id="chip-reflektioner-humor" class="filter-chip text-xs px-3 py-1 rounded-full font-medium">Reflektioner & humör</button>
                <button onclick="toggleWidgetFilter('senaste-insikter')" id="chip-senaste-insikter" class="filter-chip text-xs px-3 py-1 rounded-full font-medium">Mina senaste insikter</button>
            </div>
        </div>

        <!-- RAD 1: 4 ST KPI-KORT -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <!-- 1. Utvecklingspoäng -->
            <div data-widget="utvecklingspoang" class="widget-item falk-card p-4 rounded-2xl shadow-xs flex flex-col justify-between">
                <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-xl bg-emerald-100 text-emerald-800 flex items-center justify-center text-lg">🌱</div>
                    <div>
                        <span class="text-[11px] font-semibold opacity-70 block">Utvecklingspoäng</span>
                        <span class="text-2xl font-black">780</span>
                    </div>
                </div>
                <div class="mt-3 pt-2 border-t border-stone-200/60 flex items-center justify-between text-xs">
                    <span class="text-emerald-700 font-bold flex items-center gap-0.5">↑ 120 <span class="font-normal opacity-80 text-[11px]">från förra månaden</span></span>
                    <svg class="w-14 h-5 stroke-emerald-600 fill-none" stroke-width="2" viewBox="0 0 50 20">
                        <path d="M 0 16 L 10 14 L 20 10 L 30 11 L 40 5 L 50 2" />
                    </svg>
                </div>
            </div>

            <!-- 2. Streak -->
            <div data-widget="streak" class="widget-item falk-card p-4 rounded-2xl shadow-xs flex flex-col justify-between">
                <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-xl bg-sky-100 text-sky-800 flex items-center justify-center text-lg">🔥</div>
                    <div>
                        <span class="text-[11px] font-semibold opacity-70 block">Streak</span>
                        <span class="text-2xl font-black">23 <span class="text-xs font-normal">dagar</span></span>
                    </div>
                </div>
                <div class="mt-3 pt-2 border-t border-stone-200/60 text-xs opacity-75">
                    Bästa: <span class="font-bold">41 dagar</span>
                </div>
            </div>

            <!-- 3. Reflektioner -->
            <div data-widget="reflektioner" class="widget-item falk-card p-4 rounded-2xl shadow-xs flex flex-col justify-between">
                <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-xl bg-purple-100 text-purple-800 flex items-center justify-center text-lg">📝</div>
                    <div>
                        <span class="text-[11px] font-semibold opacity-70 block">Reflektioner</span>
                        <span class="text-2xl font-black">18</span>
                    </div>
                </div>
                <div class="mt-3 pt-2 border-t border-stone-200/60 text-xs opacity-75">
                    Denna månad
                </div>
            </div>

            <!-- 4. Vanor uppfyllda -->
            <div data-widget="vanor-uppfyllda" class="widget-item falk-card p-4 rounded-2xl shadow-xs flex flex-col justify-between">
                <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-xl bg-amber-100 text-amber-800 flex items-center justify-center text-lg">✓</div>
                    <div>
                        <span class="text-[11px] font-semibold opacity-70 block">Vanor uppfyllda</span>
                        <span class="text-2xl font-black">76%</span>
                    </div>
                </div>
                <div class="mt-3 pt-2 border-t border-stone-200/60 text-xs opacity-75">
                    Snitt denna månad
                </div>
            </div>
        </div>

        <!-- RAD 2: 3 ST MELLAN-WIDGETS -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
            
            <!-- 5. Min utveckling över tid -->
            <div data-widget="utveckling-tid" class="widget-item lg:col-span-5 falk-card p-5 rounded-2xl shadow-xs flex flex-col justify-between space-y-4">
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-1.5">
                        <h3 class="text-sm font-bold">Min utveckling över tid</h3>
                        <span class="text-xs opacity-50 cursor-pointer" title="Visar din utveckling per kategori">ⓘ</span>
                    </div>
                    <select class="bg-transparent text-xs font-semibold border border-stone-300 rounded-lg px-2 py-1">
                        <option>6 månader</option>
                        <option>3 månader</option>
                        <option>1 år</option>
                    </select>
                </div>

                <div class="flex flex-wrap gap-2.5 text-[11px] font-semibold">
                    <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>Helhet</span>
                    <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-blue-500"></span>Mindset</span>
                    <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-purple-500"></span>Hälsa</span>
                    <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-amber-500"></span>Relationer</span>
                    <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-cyan-500"></span>Produktivitet</span>
                </div>

                <div class="w-full h-44 relative pt-2">
                    <svg class="w-full h-full overflow-visible" viewBox="0 0 300 120" preserveAspectRatio="none">
                        <line x1="0" y1="0" x2="300" y2="0" stroke="#E5E7EB" stroke-dasharray="3 3"/>
                        <line x1="0" y1="30" x2="300" y2="30" stroke="#E5E7EB" stroke-dasharray="3 3"/>
                        <line x1="0" y1="60" x2="300" y2="60" stroke="#E5E7EB" stroke-dasharray="3 3"/>
                        <line x1="0" y1="90" x2="300" y2="90" stroke="#E5E7EB" stroke-dasharray="3 3"/>
                        <line x1="0" y1="120" x2="300" y2="120" stroke="#E5E7EB"/>

                        <path d="M0,80 Q60,65 120,45 T240,25 L300,15" fill="none" stroke="#10B981" stroke-width="2.5"/>
                        <path d="M0,90 Q60,75 120,55 T240,40 L300,30" fill="none" stroke="#3B82F6" stroke-width="2.5"/>
                        <path d="M0,98 Q60,85 120,70 T240,55 L300,48" fill="none" stroke="#8B5CF6" stroke-width="2.5"/>
                        <path d="M0,105 Q60,95 120,82 T240,70 L300,62" fill="none" stroke="#F59E0B" stroke-width="2.5"/>
                        <path d="M0,112 Q60,105 120,95 T240,84 L300,76" fill="none" stroke="#06B6D4" stroke-width="2.5"/>

                        <circle cx="300" cy="15" r="3.5" fill="#10B981"/>
                        <circle cx="300" cy="30" r="3.5" fill="#3B82F6"/>
                        <circle cx="300" cy="48" r="3.5" fill="#8B5CF6"/>
                        <circle cx="300" cy="62" r="3.5" fill="#F59E0B"/>
                        <circle cx="300" cy="76" r="3.5" fill="#06B6D4"/>
                    </svg>
                    <div class="flex justify-between text-[10px] opacity-60 mt-2 font-medium">
                        <span>Dec</span><span>Jan</span><span>Feb</span><span>Mar</span><span>Apr</span><span>Maj</span>
                    </div>
                </div>

                <div class="pt-2 border-t border-stone-200/60 flex items-center gap-2 text-xs text-amber-900 font-medium">
                    <span>⭐</span>
                    <p class="text-[11px]">Fin utveckling! Du har förbättrat dig mest inom <strong>Mindset</strong> och <strong>Hälsa</strong>.</p>
                </div>
            </div>

            <!-- 6. Utvecklingshjul -->
            <div data-widget="utvecklingshjul" class="widget-item lg:col-span-4 falk-card p-5 rounded-2xl shadow-xs flex flex-col justify-between space-y-3">
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-1.5">
                        <h3 class="text-sm font-bold">Utvecklingshjul</h3>
                        <span class="text-xs opacity-50 cursor-pointer" title="Dina 5 huvudområden i balans">ⓘ</span>
                    </div>
                </div>

                <div class="flex justify-center items-center py-2 relative">
                    <svg class="w-48 h-48" viewBox="0 0 200 200">
                        <polygon points="100,20 176,55 147,135 53,135 24,55" fill="none" stroke="#E5E7EB" stroke-width="1"/>
                        <polygon points="100,45 151,68 132,120 68,120 49,68" fill="none" stroke="#E5E7EB" stroke-width="1"/>
                        <polygon points="100,70 126,82 116,105 84,105 74,82" fill="none" stroke="#E5E7EB" stroke-width="1"/>

                        <line x1="100" y1="100" x2="100" y2="20" stroke="#E5E7EB"/>
                        <line x1="100" y1="100" x2="176" y2="55" stroke="#E5E7EB"/>
                        <line x1="100" y1="100" x2="147" y2="135" stroke="#E5E7EB"/>
                        <line x1="100" y1="100" x2="53" y2="135" stroke="#E5E7EB"/>
                        <line x1="100" y1="100" x2="24" y2="55" stroke="#E5E7EB"/>

                        <polygon points="100,36 155,68 131,123 73,120 35,62" fill="rgba(16, 185, 129, 0.25)" stroke="#10B981" stroke-width="2"/>

                        <circle cx="100" cy="36" r="3" fill="#10B981"/>
                        <circle cx="155" cy="68" r="3" fill="#10B981"/>
                        <circle cx="131" cy="123" r="3" fill="#10B981"/>
                        <circle cx="73" cy="120" r="3" fill="#10B981"/>
                        <circle cx="35" cy="62" r="3" fill="#10B981"/>
                    </svg>

                    <div class="absolute top-1 text-[10px] font-bold text-center w-full">Mindset<br/><span class="text-emerald-700 font-extrabold">80%</span></div>
                    <div class="absolute top-10 right-0 text-[10px] font-bold">Hälsa<br/><span class="text-emerald-700 font-extrabold">72%</span></div>
                    <div class="absolute bottom-2 right-4 text-[10px] font-bold">Relationer<br/><span class="text-emerald-700 font-extrabold">65%</span></div>
                    <div class="absolute bottom-2 left-4 text-[10px] font-bold">Produktivitet<br/><span class="text-emerald-700 font-extrabold">58%</span></div>
                    <div class="absolute top-10 left-0 text-[10px] font-bold">Självkännedom<br/><span class="text-emerald-700 font-extrabold">85%</span></div>
                </div>

                <div class="pt-2 border-t border-stone-200/60 flex items-center gap-2 text-xs bg-emerald-50/50 p-2 rounded-xl text-emerald-900">
                    <span>🌱</span>
                    <p class="text-[11px] font-semibold">Starkast inom <strong>Självkännedom</strong> – fortsätt så!</p>
                </div>
            </div>

            <!-- 7. Mina mål -->
            <div data-widget="mina-mal" class="widget-item lg:col-span-3 falk-card p-5 rounded-2xl shadow-xs flex flex-col justify-between space-y-3">
                <div class="flex items-center justify-between">
                    <h3 class="text-sm font-bold">Mina mål</h3>
                    <a href="#" class="text-xs text-amber-800 font-semibold hover:underline">Visa alla</a>
                </div>

                <div class="space-y-3">
                    <div>
                        <div class="flex items-center justify-between text-xs font-semibold mb-1">
                            <span class="flex items-center gap-1.5">☀️ Bygga morgonrutin</span>
                            <span class="text-emerald-700 font-bold">80%</span>
                        </div>
                        <div class="w-full bg-stone-200 h-2 rounded-full overflow-hidden">
                            <div class="bg-emerald-600 h-full rounded-full" style="width: 80%"></div>
                        </div>
                    </div>

                    <div>
                        <div class="flex items-center justify-between text-xs font-semibold mb-1">
                            <span class="flex items-center gap-1.5">🏋️ Träna 3x i veckan</span>
                            <span class="text-blue-700 font-bold">67%</span>
                        </div>
                        <div class="w-full bg-stone-200 h-2 rounded-full overflow-hidden">
                            <div class="bg-blue-600 h-full rounded-full" style="width: 67%"></div>
                        </div>
                    </div>

                    <div>
                        <div class="flex items-center justify-between text-xs font-semibold mb-1">
                            <span class="flex items-center gap-1.5">📚 Läsa 12 böcker i år</span>
                            <span class="text-purple-700 font-bold">50%</span>
                        </div>
                        <div class="w-full bg-stone-200 h-2 rounded-full overflow-hidden">
                            <div class="bg-purple-600 h-full rounded-full" style="width: 50%"></div>
                        </div>
                    </div>

                    <div>
                        <div class="flex items-center justify-between text-xs font-semibold mb-1">
                            <span class="flex items-center gap-1.5">🧘 Meditera dagligen</span>
                            <span class="text-amber-700 font-bold">90%</span>
                        </div>
                        <div class="w-full bg-stone-200 h-2 rounded-full overflow-hidden">
                            <div class="bg-amber-600 h-full rounded-full" style="width: 90%"></div>
                        </div>
                    </div>
                </div>

                <button class="w-full py-2 border border-dashed border-stone-300 rounded-xl text-xs font-semibold text-stone-600 hover:border-stone-500 hover:text-stone-900 transition-all flex items-center justify-center gap-1">
                    <span>+ Lägg till nytt mål</span>
                </button>
            </div>
        </div>

        <!-- RAD 3: 3 ST BOTTEN-WIDGETS -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">

            <!-- 8. Mina vanor -->
            <div data-widget="mina-vanor" class="widget-item lg:col-span-4 falk-card p-5 rounded-2xl shadow-xs flex flex-col justify-between space-y-3">
                <div class="flex items-center justify-between">
                    <h3 class="text-sm font-bold">Mina vanor</h3>
                    <a href="#" class="text-xs text-amber-800 font-semibold hover:underline">Visa alla</a>
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse text-xs">
                        <thead>
                            <tr class="border-b border-stone-200 text-[10px] font-bold text-stone-500 uppercase">
                                <th class="py-1">Vana</th>
                                <th class="py-1 text-center">M</th>
                                <th class="py-1 text-center">T</th>
                                <th class="py-1 text-center">O</th>
                                <th class="py-1 text-center">T</th>
                                <th class="py-1 text-center">F</th>
                                <th class="py-1 text-center">L</th>
                                <th class="py-1 text-center">S</th>
                                <th class="py-1 text-right">%</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-stone-100 font-medium">
                            <tr>
                                <td class="py-2 flex items-center gap-1">☀️ Morgonrutin</td>
                                <td class="text-center text-emerald-600">✓</td>
                                <td class="text-center text-emerald-600">✓</td>
                                <td class="text-center text-emerald-600">✓</td>
                                <td class="text-center text-emerald-600">✓</td>
                                <td class="text-center text-emerald-600">✓</td>
                                <td class="text-center text-emerald-600">✓</td>
                                <td class="text-center text-emerald-600">✓</td>
                                <td class="text-right font-bold text-emerald-700">86%</td>
                            </tr>
                            <tr>
                                <td class="py-2 flex items-center gap-1">🧘 Meditation</td>
                                <td class="text-center text-emerald-600">✓</td>
                                <td class="text-center text-emerald-600">✓</td>
                                <td class="text-center text-emerald-600">✓</td>
                                <td class="text-center text-emerald-600">✓</td>
                                <td class="text-center text-emerald-600">✓</td>
                                <td class="text-center text-emerald-600">✓</td>
                                <td class="text-center text-stone-300">◦</td>
                                <td class="text-right font-bold text-emerald-700">71%</td>
                            </tr>
                            <tr>
                                <td class="py-2 flex items-center gap-1">🏋️ Träning</td>
                                <td class="text-center text-emerald-600">✓</td>
                                <td class="text-center text-emerald-600">✓</td>
                                <td class="text-center text-emerald-600">✓</td>
                                <td class="text-center text-emerald-600">✓</td>
                                <td class="text-center text-stone-300">◦</td>
                                <td class="text-center text-stone-300">◦</td>
                                <td class="text-center text-stone-300">◦</td>
                                <td class="text-right font-bold text-amber-700">57%</td>
                            </tr>
                            <tr>
                                <td class="py-2 flex items-center gap-1">📚 Läsa</td>
                                <td class="text-center text-emerald-600">✓</td>
                                <td class="text-center text-emerald-600">✓</td>
                                <td class="text-center text-emerald-600">✓</td>
                                <td class="text-center text-emerald-600">✓</td>
                                <td class="text-center text-emerald-600">✓</td>
                                <td class="text-center text-emerald-600">✓</td>
                                <td class="text-center text-emerald-600">✓</td>
                                <td class="text-right font-bold text-emerald-700">86%</td>
                            </tr>
                            <tr>
                                <td class="py-2 flex items-center gap-1">💚 Tacksamhet</td>
                                <td class="text-center text-emerald-600">✓</td>
                                <td class="text-center text-emerald-600">✓</td>
                                <td class="text-center text-emerald-600">✓</td>
                                <td class="text-center text-emerald-600">✓</td>
                                <td class="text-center text-stone-300">◦</td>
                                <td class="text-center text-stone-300">◦</td>
                                <td class="text-center text-emerald-600">✓</td>
                                <td class="text-right font-bold text-emerald-700">71%</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- 9. Reflektioner & humör -->
            <div data-widget="reflektioner-humor" class="widget-item lg:col-span-4 falk-card p-5 rounded-2xl shadow-xs flex flex-col justify-between space-y-3">
                <div class="flex items-center justify-between">
                    <h3 class="text-sm font-bold">Reflektioner & humör</h3>
                    <a href="#" class="text-xs text-amber-800 font-semibold hover:underline">Visa alla</a>
                </div>

                <div class="flex items-center justify-between bg-amber-50/50 p-2.5 rounded-xl border border-amber-100">
                    <div class="flex items-center gap-2">
                        <span class="text-2xl">😃</span>
                        <div>
                            <span class="text-[10px] font-bold text-stone-500 uppercase block">Genomsnittligt humör</span>
                            <span class="text-base font-black">4,2 <span class="text-xs font-normal text-stone-500">/ 5</span></span>
                        </div>
                    </div>
                    <span class="text-xs font-bold text-emerald-700">↑ 0,6 <span class="font-normal opacity-70 text-[10px]">från förra månaden</span></span>
                </div>

                <div>
                    <span class="text-[10px] font-bold text-stone-400 block mb-1">Humör över tid</span>
                    <div class="h-24 w-full relative">
                        <svg class="w-full h-full overflow-visible" viewBox="0 0 200 60" preserveAspectRatio="none">
                            <path d="M 0,35 Q 25,15 50,25 T 100,20 T 150,30 L 200,15" fill="none" stroke="#8B5CF6" stroke-width="2"/>
                            <circle cx="0" cy="35" r="3" fill="#8B5CF6"/>
                            <circle cx="50" cy="25" r="3" fill="#8B5CF6"/>
                            <circle cx="100" cy="20" r="3" fill="#8B5CF6"/>
                            <circle cx="150" cy="30" r="3" fill="#8B5CF6"/>
                            <circle cx="200" cy="15" r="3" fill="#8B5CF6"/>
                        </svg>
                        <div class="flex justify-between text-[9px] opacity-60 mt-1">
                            <span>1 maj</span><span>8 maj</span><span>15 maj</span><span>22 maj</span><span>31 maj</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 10. Mina senaste insikter -->
            <div data-widget="senaste-insikter" class="widget-item lg:col-span-4 falk-card p-5 rounded-2xl shadow-xs flex flex-col justify-between space-y-3">
                <div class="flex items-center justify-between">
                    <h3 class="text-sm font-bold">Mina senaste insikter</h3>
                    <a href="#" class="text-xs text-amber-800 font-semibold hover:underline">Visa alla</a>
                </div>

                <div class="space-y-2.5">
                    <div class="flex items-start gap-2.5 p-2.5 rounded-xl bg-emerald-50/60 border border-emerald-100 text-xs">
                        <span class="text-lg leading-none">🌱</span>
                        <p class="text-[11px] leading-snug">Du är som mest produktiv på förmiddagen. Planera dina viktigaste uppgifter då.</p>
                    </div>

                    <div class="flex items-start gap-2.5 p-2.5 rounded-xl bg-sky-50/60 border border-sky-100 text-xs">
                        <span class="text-lg leading-none">🌙</span>
                        <p class="text-[11px] leading-snug">När du mediterar regelbundet sover du bättre och känner dig lugnare.</p>
                    </div>

                    <div class="flex items-start gap-2.5 p-2.5 rounded-xl bg-purple-50/60 border border-purple-100 text-xs">
                        <span class="text-lg leading-none">⭐</span>
                        <p class="text-[11px] leading-snug">Du växer mest när du kliver utanför din komfortzon. Fortsätt utmana dig!</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- BOTTEN-BANNER MED ACTION -->
        <div class="falk-card p-4 rounded-2xl shadow-xs flex flex-col sm:flex-row items-center justify-between gap-3 border border-[#DDD0B8]">
            <div class="flex items-center gap-3">
                <span class="text-xl">🌱</span>
                <p class="text-xs font-serif italic text-stone-700">"Kom ihåg: Framsteg, inte perfektion. Du blir bättre varje dag."</p>
            </div>
            <a href="/" class="bg-[#4E5C4B] hover:bg-[#3D493B] text-white text-xs font-semibold px-4 py-2.5 rounded-xl transition-all shrink-0 flex items-center gap-1.5">
                <span>✏️</span>
                <span>Skriv reflektion</span>
            </a>
        </div>

    </main>

    <!-- FOOTER -->
    <footer class="text-center py-4 text-[10px] font-semibold tracking-widest text-[#9C8F7A] uppercase">
        POWERED BY WAYJS
    </footer>

    <!-- INTERAKTIV LOGIK FOR TEMA & DYNAMISK FILTRERING -->
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

        // DYNAMISK WIDGET FILTRERING LOGIK (10 ELEMENT)
        function toggleWidgetFilter(targetWidget) {
            const allChips = document.querySelectorAll('.filter-chip');
            const allWidgets = document.querySelectorAll('.widget-item');

            if (targetWidget === 'all') {
                allChips.forEach(chip => chip.classList.remove('active'));
                document.getElementById('chip-all').classList.add('active');

                allWidgets.forEach(widget => {
                    widget.classList.remove('widget-hidden');
                });
            } else {
                document.getElementById('chip-all').classList.remove('active');
                const targetChip = document.getElementById('chip-' + targetWidget);
                const targetElement = document.querySelector(`[data-widget="${targetWidget}"]`);

                if (targetChip.classList.contains('active')) {
                    targetChip.classList.remove('active');
                    targetElement.classList.add('widget-hidden');
                } else {
                    targetChip.classList.add('active');
                    targetElement.classList.remove('widget-hidden');
                }

                const activeSpecificChips = document.querySelectorAll('.filter-chip.active');
                if (activeSpecificChips.length === 0) {
                    toggleWidgetFilter('all');
                }
            }
        }
    </script>
</body>
</html>
'''

with open('templates/utveckling.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("-> [SUCCESS] Dashboarden har byggts exakt enligt bilden med 10 filterbara moduler!")
