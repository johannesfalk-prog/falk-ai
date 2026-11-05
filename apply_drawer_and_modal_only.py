import os
import re

print("=== APPLICERAR HÖGERMENY-FILTER OCH PÅMINNELSE-MODAL (UTAN CHATT-KNAPPAR) ===")

templates_dir = "templates"
template_files = ["index.html", "bibliotek.html", "utveckling.html", "installningar.html"]

# 1. NY HÖGERMENY MED DYNAMISKA FILTERTABS OCH BOTTENKNAPP
right_drawer_html = '''    <!-- HÖGER BACKDROP & MENY (INSIKTER & PÅMINNELSER MED FILTER) -->
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

            <!-- FILTER CHIPS (ALLA / INSIKTER / PÅMINNELSER) -->
            <div class="flex items-center gap-1.5 p-1 bg-[#E8DCC4]/50 rounded-xl border border-[#DDD0B8]">
                <button onclick="filterRightDrawer('all')" id="right-tab-all" class="right-tab-chip active flex-1 py-1 text-[11px] font-bold rounded-lg transition-all text-center">Alla</button>
                <button onclick="filterRightDrawer('insight')" id="right-tab-insight" class="right-tab-chip flex-1 py-1 text-[11px] font-bold rounded-lg transition-all text-center">Insikter</button>
                <button onclick="filterRightDrawer('reminder')" id="right-tab-reminder" class="right-tab-chip flex-1 py-1 text-[11px] font-bold rounded-lg transition-all text-center">Påminnelser</button>
            </div>
        </div>

        <!-- DYNAMISK LISTA -->
        <div class="flex-1 p-4 space-y-3 overflow-y-auto" id="right-drawer-list">
            <!-- Renderas via JS -->
        </div>

        <!-- BOTTENKNAPP FÖR MANUELL SKAPANDELOGIK -->
        <div class="p-4 border-t border-[#E6E0D4]/80">
            <button onclick="openManualInsightModal()" class="w-full py-2.5 bg-[#4E5C4B] hover:bg-[#3D493B] text-white text-xs font-semibold rounded-xl transition-all flex items-center justify-center gap-1.5 shadow-xs">
                <span>+ Skriv egen insikt / påminnelse</span>
            </button>
        </div>
    </aside>'''

# 2. PÅMINNELSER & INSIKTER MODAL
reminder_modal_html = '''    <!-- MODAL FÖR SKAPANDE OCH REDIGERING AV PÅMINNELSER / INSIKTER -->
    <div id="falk-modal-backdrop" class="fixed inset-0 bg-black/50 backdrop-blur-xs hidden opacity-0 transition-opacity duration-300 z-50 flex items-center justify-center p-4">
        <div class="bg-[#FAF8F0] w-full max-w-md rounded-3xl border border-[#DDD0B8] shadow-2xl overflow-hidden p-6 space-y-5 transform scale-95 transition-transform duration-300" id="falk-modal-box">
            <div class="flex items-center justify-between border-b border-[#E6E0D4] pb-3">
                <h3 class="text-base font-extrabold text-[#2D2721]" id="modal-title">Hantera notering</h3>
                <button onclick="closeFalkModal()" class="text-stone-500 hover:text-black">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"></path></svg>
                </button>
            </div>

            <form id="falk-modal-form" onsubmit="saveModalData(event)" class="space-y-4">
                <input type="hidden" id="modal-item-id" value="">
                <input type="hidden" id="modal-item-type" value="reminder">

                <div>
                    <label class="block text-[11px] font-bold text-[#8C5D37] uppercase mb-1">Innehåll / Reflektion</label>
                    <textarea id="modal-text-input" rows="3" required class="w-full text-xs p-3 rounded-xl border border-[#DDD0B8] bg-white text-stone-800 focus:outline-none focus:ring-1 focus:ring-[#8C5D37]" placeholder="Skriv din insikt eller påminnelse här..."></textarea>
                </div>

                <div class="grid grid-cols-2 gap-2">
                    <button type="button" onclick="setModalType('insight')" id="modal-btn-type-insight" class="py-2 text-xs font-bold rounded-xl border border-[#DDD0B8] text-stone-700 bg-white">🌱 Insikt</button>
                    <button type="button" onclick="setModalType('reminder')" id="modal-btn-type-reminder" class="py-2 text-xs font-bold rounded-xl border border-[#2D2721] text-white bg-[#2D2721]">🔔 Påminnelse</button>
                </div>

                <div id="modal-reminder-options" class="space-y-3 bg-[#E8DCC4]/40 p-3.5 rounded-2xl border border-[#DDD0B8]">
                    <div>
                        <label class="block text-[10px] font-bold text-stone-600 uppercase mb-1">Hur ofta vill du påminnas?</label>
                        <select id="modal-frequency-select" onchange="toggleCustomTimeField()" class="w-full text-xs p-2 rounded-lg border border-[#DDD0B8] bg-white font-semibold">
                            <option value="tillsvidare">Tillsvidare (tills jag stänger den)</option>
                            <option value="dagligen">Varje dag</option>
                            <option value="veckovis">Varje vecka</option>
                            <option value="anpassat">Anpassat datum & tid</option>
                        </select>
                    </div>

                    <div id="modal-custom-time-group" class="hidden">
                        <label class="block text-[10px] font-bold text-stone-600 uppercase mb-1">Välj datum & tid</label>
                        <input type="datetime-local" id="modal-datetime-input" class="w-full text-xs p-2 rounded-lg border border-[#DDD0B8] bg-white font-medium">
                    </div>
                </div>

                <div class="flex items-center justify-end gap-2 pt-2">
                    <button type="button" onclick="closeFalkModal()" class="px-4 py-2 text-xs font-semibold text-stone-600 hover:text-stone-900">Avbryt</button>
                    <button type="submit" class="px-5 py-2 bg-[#4E5C4B] hover:bg-[#3D493B] text-white text-xs font-semibold rounded-xl">Spara</button>
                </div>
            </form>
        </div>
    </div>'''

additional_css = '''
        .right-tab-chip { background-color: transparent; color: #4A4238; }
        .right-tab-chip.active { background-color: #2D2721 !important; color: #FFFFFF !important; }
        body.theme-dark .right-tab-chip.active { background-color: #E8DCC4 !important; color: #1C1A17 !important; }
'''

system_js = '''
        let falkItems = [
            { id: 1, type: 'insight', text: 'Att sätta gränser handlar inte om att stänga ute andra, utan om att hålla dig själv hel.', created: 'Idag', frequency: null },
            { id: 2, type: 'reminder', text: 'Reflektera kring dina 3 viktigaste prioriteringar inför morgondagen.', created: 'Igår', frequency: 'dagligen', datetime: null }
        ];

        let activeRightFilter = 'all';

        function renderRightDrawer() {
            const container = document.getElementById('right-drawer-list');
            if (!container) return;

            container.innerHTML = '';
            const filtered = falkItems.filter(item => activeRightFilter === 'all' || item.type === activeRightFilter);

            if (filtered.length === 0) {
                container.innerHTML = '<div class="text-center py-8 text-xs italic text-stone-500">Inga sparade objekt i denna vy.</div>';
                return;
            }

            filtered.forEach(item => {
                const card = document.createElement('div');
                card.className = 'falk-card p-3.5 rounded-2xl border border-[#DDD0B8] shadow-xs space-y-2 relative group';
                
                const isInsight = item.type === 'insight';
                const icon = isInsight ? '🌱' : '🔔';
                const tagLabel = isInsight ? 'Insikt' : `Påminnelse (${item.frequency || 'tillsvidare'})`;
                const tagBg = isInsight ? 'bg-emerald-100/70 text-emerald-800' : 'bg-amber-100/70 text-amber-800';

                function escapeHtmlLocal(str) { return str ? str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;") : ''; }

                card.innerHTML = `
                    <div class="flex items-center justify-between">
                        <span class="text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${tagBg} flex items-center gap-1">
                            <span>${icon}</span> ${tagLabel}
                        </span>
                        <div class="flex items-center gap-1 opacity-80 group-hover:opacity-100">
                            <button onclick="editFalkItem(${item.id})" class="text-[11px] font-bold text-stone-600 hover:text-black px-1.5 py-0.5 rounded hover:bg-stone-200/60" title="Redigera">✏️</button>
                            ${isInsight ? `<button onclick="convertInsightToReminder(${item.id})" class="text-[11px] font-bold text-amber-800 hover:text-amber-950 px-1.5 py-0.5 rounded hover:bg-amber-100/60" title="Lägg till påminnelse">🔔</button>` : ''}
                            <button onclick="deleteFalkItem(${item.id})" class="text-[11px] font-bold text-red-600 hover:text-red-800 px-1.5 py-0.5 rounded hover:bg-red-100/60" title="Ta bort">✕</button>
                        </div>
                    </div>
                    <p class="text-xs ${isInsight ? 'italic font-serif' : 'font-medium'} text-stone-800 leading-relaxed">${escapeHtmlLocal(item.text)}</p>
                `;
                container.appendChild(card);
            });
        }

        function filterRightDrawer(type) {
            activeRightFilter = type;
            document.querySelectorAll('.right-tab-chip').forEach(btn => btn.classList.remove('active'));
            const activeBtn = document.getElementById('right-tab-' + type);
            if (activeBtn) activeBtn.classList.add('active');
            renderRightDrawer();
        }

        function openManualInsightModal(text = '', type = 'insight') {
            document.getElementById('modal-title').innerText = text ? 'Spara notering' : 'Skapa ny insikt / påminnelse';
            document.getElementById('modal-item-id').value = '';
            document.getElementById('modal-text-input').value = text;
            setModalType(type);
            
            const backdrop = document.getElementById('falk-modal-backdrop');
            backdrop.classList.remove('hidden');
            setTimeout(() => backdrop.classList.remove('opacity-0'), 10);
        }

        function closeFalkModal() {
            const backdrop = document.getElementById('falk-modal-backdrop');
            backdrop.classList.add('opacity-0');
            setTimeout(() => backdrop.classList.add('hidden'), 300);
        }

        function setModalType(type) {
            document.getElementById('modal-item-type').value = type;
            const btnInsight = document.getElementById('modal-btn-type-insight');
            const btnReminder = document.getElementById('modal-btn-type-reminder');
            const reminderOpts = document.getElementById('modal-reminder-options');

            if (type === 'insight') {
                btnInsight.className = 'py-2 text-xs font-bold rounded-xl border border-[#2D2721] text-white bg-[#2D2721]';
                btnReminder.className = 'py-2 text-xs font-bold rounded-xl border border-[#DDD0B8] text-stone-700 bg-white';
                reminderOpts.classList.add('hidden');
            } else {
                btnReminder.className = 'py-2 text-xs font-bold rounded-xl border border-[#2D2721] text-white bg-[#2D2721]';
                btnInsight.className = 'py-2 text-xs font-bold rounded-xl border border-[#DDD0B8] text-stone-700 bg-white';
                reminderOpts.classList.remove('hidden');
            }
        }

        function toggleCustomTimeField() {
            const val = document.getElementById('modal-frequency-select').value;
            const group = document.getElementById('modal-custom-time-group');
            if (val === 'anpassat') group.classList.remove('hidden');
            else group.classList.add('hidden');
        }

        function saveModalData(e) {
            e.preventDefault();
            const id = document.getElementById('modal-item-id').value;
            const text = document.getElementById('modal-text-input').value.trim();
            const type = document.getElementById('modal-item-type').value;
            const freq = type === 'reminder' ? document.getElementById('modal-frequency-select').value : null;
            const dt = type === 'reminder' && freq === 'anpassat' ? document.getElementById('modal-datetime-input').value : null;

            if (!text) return;

            if (id) {
                const item = falkItems.find(x => x.id == id);
                if (item) {
                    item.text = text;
                    item.type = type;
                    item.frequency = freq;
                    item.datetime = dt;
                }
            } else {
                falkItems.unshift({
                    id: Date.now(),
                    type: type,
                    text: text,
                    created: 'Nyss',
                    frequency: freq,
                    datetime: dt
                });
            }

            closeFalkModal();
            renderRightDrawer();
            openRightMenu();
        }

        function editFalkItem(id) {
            const item = falkItems.find(x => x.id == id);
            if (!item) return;

            document.getElementById('modal-title').innerText = 'Redigera ' + (item.type === 'insight' ? 'insikt' : 'påminnelse');
            document.getElementById('modal-item-id').value = item.id;
            document.getElementById('modal-text-input').value = item.text;
            setModalType(item.type);

            if (item.type === 'reminder') {
                document.getElementById('modal-frequency-select').value = item.frequency || 'tillsvidare';
                if (item.datetime) {
                    document.getElementById('modal-datetime-input').value = item.datetime;
                }
                toggleCustomTimeField();
            }

            const backdrop = document.getElementById('falk-modal-backdrop');
            backdrop.classList.remove('hidden');
            setTimeout(() => backdrop.classList.remove('opacity-0'), 10);
        }

        function convertInsightToReminder(id) {
            const item = falkItems.find(x => x.id == id);
            if (item) {
                openManualInsightModal(item.text, 'reminder');
            }
        }

        function deleteFalkItem(id) {
            falkItems = falkItems.filter(x => x.id != id);
            renderRightDrawer();
        }

        document.addEventListener('DOMContentLoaded', () => {
            renderRightDrawer();
        });
'''

for file_name in template_files:
    file_path = os.path.join(templates_dir, file_name)
    if not os.path.exists(file_path):
        continue

    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    if ".right-tab-chip" not in html and "</style>" in html:
        html = html.replace("</style>", additional_css + "\n    </style>")

    if 'id="falk-right-drawer"' in html:
        html = re.sub(r'<!-- HÖGER BACKDROP & MENY.*?<\/aside>', right_drawer_html, html, flags=re.DOTALL)

    if 'id="falk-modal-backdrop"' not in html:
        html = html.replace('</body>', reminder_modal_html + '\n</body>')

    if 'function renderRightDrawer()' not in html:
        html = html.replace('</script>', system_js + '\n    </script>')

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"-> [SUCCESS] Uppdaterade {file_name}: Högermeny-filter och Modal installerade utan chattinverkan.")

print("\n=== EXEKVERING SLUTFÖRD UTAN FEL ===")
