import os
import re
import shutil
import zipfile
from datetime import datetime

print("=== VERKSTÄLLER PAYWALL PÅ TOGGLE-IKON & MIKROFON SAMT SKAPAR BACKUP FALK2602 ===")

# 1. INDEKSSIDANS PAYWALL- OCH FOKUS-HTML
paywall_modal_html = '''
    <!-- UNIVERSAL POPUP PAYWALL MODAL -->
    <div id="falk-paywall-backdrop" onclick="closePaywallModal()" class="fixed inset-0 bg-black/60 backdrop-blur-md hidden opacity-0 transition-opacity duration-300 z-50"></div>
    
    <div id="falk-paywall-modal" class="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[92%] max-w-md bg-[#FAF8F0] border border-[#DDD0B8] rounded-3xl shadow-2xl hidden opacity-0 transition-all duration-300 z-50 p-6 sm:p-8 text-center space-y-5">
        <div class="mx-auto w-12 h-12 rounded-2xl bg-[#E8DCC4] border border-[#DDD0B8] flex items-center justify-center text-xl shadow-xs">
            🔒
        </div>

        <div class="space-y-1.5">
            <span class="text-[11px] font-bold tracking-widest text-[#8C5D37] uppercase">FALK PREMIUM</span>
            <h2 id="paywall-title" class="text-2xl font-black text-[#2D2721] leading-tight">Lås upp hela din kompass</h2>
            <p id="paywall-subtitle" class="text-xs text-stone-600 font-serif italic leading-relaxed max-w-sm mx-auto">
                Du har nått gränsen för gästläget. Skapa ett konto eller logga in för att fortsätta utan begränsningar.
            </p>
        </div>

        <div class="bg-white/80 border border-[#DDD0B8] rounded-2xl p-4 text-left space-y-3 text-xs text-stone-800">
            <div class="flex items-center justify-between pb-2.5 border-b border-[#E6E0D4]">
                <span class="font-bold text-[#8C5D37] text-[11px] uppercase tracking-wider">Erbjudande:</span>
                <span class="bg-[#C57B57] text-white px-3 py-1 rounded-full text-[11px] font-bold shadow-xs">
                    199 kr/mån <span class="line-through opacity-75 font-normal text-[10px] ml-1">ord. 249 kr/mån</span>
                </span>
            </div>

            <div class="flex items-center gap-2.5">
                <span class="text-[#4E5C4B] font-bold text-sm">✓</span>
                <span class="font-medium">Obegränsad chatt, fördjupade perspektiv</span>
            </div>
            <div class="flex items-center gap-2.5">
                <span class="text-[#4E5C4B] font-bold text-sm">✓</span>
                <span class="font-medium">Spara insikter & påminnelser</span>
            </div>
            <div class="flex items-center gap-2.5">
                <span class="text-[#4E5C4B] font-bold text-sm">✓</span>
                <span class="font-medium">Full tillgång till Biblioteket</span>
            </div>
            <div class="flex items-center gap-2.5">
                <span class="text-[#4E5C4B] font-bold text-sm">✓</span>
                <span class="font-medium">Min utveckling och fler funktioner</span>
            </div>
        </div>

        <div class="space-y-2.5 pt-1">
            <button onclick="alert('Omdirigerar till kassan...')" class="w-full py-3.5 bg-[#4E5C4B] hover:bg-[#3D493B] text-white text-xs font-bold rounded-full transition-all shadow-md tracking-wider uppercase">
                Skapa konto
            </button>
            <button onclick="alert('Omdirigerar till inloggning...')" class="w-full py-3 bg-[#FAF8F0] hover:bg-[#E8DCC4] text-[#2D2721] border border-[#DDD0B8] text-xs font-bold rounded-full transition-all">
                Redan medlem? Logga in
            </button>
        </div>

        <button onclick="closePaywallModal()" class="text-xs font-semibold text-stone-500 hover:text-black transition-all block mx-auto pt-1">
            Fortsätt titta runt som gäst
        </button>
    </div>
'''

fokus_modal_html = '''
    <!-- FOKUS MODAL -->
    <div id="falk-fokus-backdrop" onclick="closeFocusModal()" class="fixed inset-0 bg-black/50 backdrop-blur-sm hidden opacity-0 transition-opacity duration-300 z-50"></div>
    <div id="falk-fokus-modal" class="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[92%] max-w-md bg-[#FAF8F0] border border-[#DDD0B8] rounded-3xl shadow-2xl hidden opacity-0 transition-all duration-300 z-50 p-6 space-y-5">
        <div class="flex items-center justify-between pb-3 border-b border-[#E6E0D4]">
            <h2 class="text-xl font-extrabold text-[#2D2721]">Fokus</h2>
            <div class="flex items-center gap-4">
                <button onclick="resetFocusSliders()" class="text-xs font-bold text-[#C57B57] hover:underline transition-all">Återställ</button>
                <button onclick="closeFocusModal()" class="text-stone-500 hover:text-black font-bold text-lg p-1">✕</button>
            </div>
        </div>
        <div class="space-y-4">
            <div class="space-y-1">
                <div class="flex justify-between text-xs font-bold text-[#2D2721]">
                    <span>Självförtroende</span>
                    <span id="val-sjalvfortroende" class="text-[#C57B57]">50%</span>
                </div>
                <input type="range" id="slider-sjalvfortroende" min="0" max="100" value="50" oninput="updateSliderUI('sjalvfortroende')" class="falk-slider w-full">
            </div>
            <div class="space-y-1">
                <div class="flex justify-between text-xs font-bold text-[#2D2721]">
                    <span>Stresshantering</span>
                    <span id="val-stresshantering" class="text-[#C57B57]">50%</span>
                </div>
                <input type="range" id="slider-stresshantering" min="0" max="100" value="50" oninput="updateSliderUI('stresshantering')" class="falk-slider w-full">
            </div>
            <div class="space-y-1">
                <div class="flex justify-between text-xs font-bold text-[#2D2721]">
                    <span>Handlingskraft</span>
                    <span id="val-handlingskraft" class="text-[#C57B57]">50%</span>
                </div>
                <input type="range" id="slider-handlingskraft" min="0" max="100" value="50" oninput="updateSliderUI('handlingskraft')" class="falk-slider w-full">
            </div>
            <div class="space-y-1">
                <div class="flex justify-between text-xs font-bold text-[#2D2721]">
                    <span>Gränssättning</span>
                    <span id="val-granssattning" class="text-[#C57B57]">50%</span>
                </div>
                <input type="range" id="slider-granssattning" min="0" max="100" value="50" oninput="updateSliderUI('granssattning')" class="falk-slider w-full">
            </div>
            <div class="space-y-1">
                <div class="flex justify-between text-xs font-bold text-[#2D2721]">
                    <span>Motivation</span>
                    <span id="val-motivation" class="text-[#C57B57]">50%</span>
                </div>
                <input type="range" id="slider-motivation" min="0" max="100" value="50" oninput="updateSliderUI('motivation')" class="falk-slider w-full">
            </div>
        </div>
        <button onclick="saveAndApplyFocus()" class="w-full py-3 bg-[#4E5C4B] hover:bg-[#3D493B] text-white text-xs font-bold rounded-full transition-all shadow-xs">
            Verkställ Fokusinställningar
        </button>
    </div>
    <style>
        .falk-slider { -webkit-appearance: none; appearance: none; height: 8px; background: #A8BFA1; border-radius: 9999px; outline: none; }
        .falk-slider::-webkit-slider-thumb { -webkit-appearance: none; appearance: none; width: 20px; height: 20px; border-radius: 50%; background: #C57B57; cursor: pointer; box-shadow: 0 2px 5px rgba(0,0,0,0.2); transition: transform 0.15s ease; }
        .falk-slider::-webkit-slider-thumb:hover { transform: scale(1.2); }
    </style>
'''

paywall_and_focus_script = '''
    <script>
        const IS_GUEST = true;
        const MAX_GUEST_MESSAGES = 6;

        function getGuestMessageCount() {
            return parseInt(localStorage.getItem('falk_guest_msg_count') || '0');
        }

        function incrementGuestMessageCount() {
            const count = getGuestMessageCount() + 1;
            localStorage.setItem('falk_guest_msg_count', count.toString());
            return count;
        }

        window.openPaywallModal = function(reason = 'general') {
            const titleEl = document.getElementById('paywall-title');
            const subEl = document.getElementById('paywall-subtitle');
            
            if (subEl) subEl.innerText = 'Du har nått gränsen för gästläget. Skapa ett konto eller logga in för att fortsätta utan begränsningar.';

            if (reason === 'chat_limit') {
                if (titleEl) titleEl.innerText = 'Du har nått dina 6 gratissvar';
            } else if (reason === 'right_menu') {
                if (titleEl) titleEl.innerText = 'Lås upp Insikter & Påminnelser';
            } else if (reason === 'bibliotek') {
                if (titleEl) titleEl.innerText = 'Lås upp hela Biblioteket';
            } else if (reason === 'utveckling') {
                if (titleEl) titleEl.innerText = 'Lås upp Min Utveckling';
            } else if (reason === 'export') {
                if (titleEl) titleEl.innerText = 'Lås upp Dataexport';
            } else if (reason === 'fokus') {
                if (titleEl) titleEl.innerText = 'Lås upp Fokus & Parameterinställningar';
            } else if (reason === 'mic') {
                if (titleEl) titleEl.innerText = 'Lås upp Röstinmatning';
            }

            const bd = document.getElementById("falk-paywall-backdrop");
            const md = document.getElementById("falk-paywall-modal");
            if (bd && md) {
                bd.classList.remove("hidden");
                md.classList.remove("hidden");
                requestAnimationFrame(() => {
                    bd.classList.remove("opacity-0");
                    md.classList.remove("opacity-0");
                });
            }
        };

        window.closePaywallModal = function() {
            const bd = document.getElementById("falk-paywall-backdrop");
            const md = document.getElementById("falk-paywall-modal");
            if (bd && md) {
                bd.classList.add("opacity-0");
                md.classList.add("opacity-0");
                setTimeout(() => {
                    bd.classList.add("hidden");
                    md.classList.add("hidden");
                }, 300);
            }
        };

        // --- FOKUS MODAL LOGIC ---
        let initialFocusState = { sjalvfortroende: 50, stresshantering: 50, handlingskraft: 50, granssattning: 50, motivation: 50 };

        window.updateSliderUI = function(key) {
            const el = document.getElementById('slider-' + key);
            const lbl = document.getElementById('val-' + key);
            if (el && lbl) lbl.innerText = el.value + '%';
        };

        window.openFocusModal = function() {
            const saved = localStorage.getItem('falk_focus_settings');
            if (saved) {
                try {
                    initialFocusState = JSON.parse(saved);
                    Object.keys(initialFocusState).forEach(k => {
                        const el = document.getElementById('slider-' + k);
                        if (el) {
                            el.value = initialFocusState[k];
                            window.updateSliderUI(k);
                        }
                    });
                } catch(e){}
            }
            const bd = document.getElementById("falk-fokus-backdrop");
            const md = document.getElementById("falk-fokus-modal");
            if (bd && md) {
                bd.classList.remove("hidden");
                md.classList.remove("hidden");
                requestAnimationFrame(() => {
                    bd.classList.remove("opacity-0");
                    md.classList.remove("opacity-0");
                });
            }
        };

        window.closeFocusModal = function() {
            const bd = document.getElementById("falk-fokus-backdrop");
            const md = document.getElementById("falk-fokus-modal");
            if (bd && md) {
                bd.classList.add("opacity-0");
                md.classList.add("opacity-0");
                setTimeout(() => {
                    bd.classList.add("hidden");
                    md.classList.add("hidden");
                }, 300);
            }
        };

        window.resetFocusSliders = function() {
            ['sjalvfortroende', 'stresshantering', 'handlingskraft', 'granssattning', 'motivation'].forEach(k => {
                const el = document.getElementById('slider-' + k);
                if (el) {
                    el.value = 50;
                    window.updateSliderUI(k);
                }
            });
        };

        window.saveAndApplyFocus = function() {
            const currentFocus = {
                sjalvfortroende: parseInt(document.getElementById('slider-sjalvfortroende').value),
                stresshantering: parseInt(document.getElementById('slider-stresshantering').value),
                handlingskraft: parseInt(document.getElementById('slider-handlingskraft').value),
                granssattning: parseInt(document.getElementById('slider-granssattning').value),
                motivation: parseInt(document.getElementById('slider-motivation').value)
            };

            localStorage.setItem('falk_focus_settings', JSON.stringify(currentFocus));
            initialFocusState = { ...currentFocus };
            window.closeFocusModal();
        };
    </script>
'''

index_path = os.path.join('templates', 'index.html')
if os.path.exists(index_path):
    with open(index_path, 'r', encoding='utf-8') as f:
        idx = f.read()

    idx = re.sub(r'<!-- UNIVERSAL POPUP PAYWALL MODAL -->.*?<\/div>\s*<\/div>', '', idx, flags=re.DOTALL)
    idx = re.sub(r'<!-- FOKUS MODAL -->.*?<\/style>', '', idx, flags=re.DOTALL)
    idx = re.sub(r'<script>\s*const IS_GUEST = true;.*?<\/script>', '', idx, flags=re.DOTALL)

    old_footer = re.search(r'<footer.*</footer>', idx, re.DOTALL)
    new_footer = '''<footer class="sticky bottom-0 bg-transparent backdrop-blur-md pt-2 pb-4 px-4 z-20">
        <div class="max-w-2xl mx-auto">
            <form id="chat-form" onsubmit="handleChatSubmit(event)" class="bg-white rounded-full p-1.5 pl-4 flex items-center justify-between shadow-sm border border-[#D8CAB0]">
                <div class="flex items-center gap-3 flex-1">
                    <button type="button" onclick="if(typeof IS_GUEST !== 'undefined' && IS_GUEST){ openPaywallModal('mic'); } else { alert('Röstinmatning aktiveras...'); }" class="p-1 text-stone-400 hover:text-[#C57B57] transition-all focus:outline-none shrink-0" title="Röstinmatning">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path></svg>
                    </button>
                    <input id="chat-input" type="text" autocomplete="off" placeholder="Skriv till mig eller välj ett alternativ..." class="w-full text-sm bg-transparent border-none focus:outline-none text-stone-800 placeholder-stone-400">
                </div>
                <div class="flex items-center gap-2">
                    <button type="button" id="focus-toggle-btn" onclick="if(typeof IS_GUEST !== 'undefined' && IS_GUEST){ openPaywallModal('fokus'); } else { openFocusModal(); }" class="p-1.5 text-stone-500 hover:text-[#C57B57] transition-all transform rotate-90 focus:outline-none" title="Fokus & Parameterinställningar">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"></path></svg>
                    </button>
                    <button type="submit" class="bg-[#4E5C4B] hover:bg-[#3D493B] text-white text-xs font-semibold px-4 py-2 rounded-full transition-all">Skicka</button>
                </div>
            </form>
        </div>
    </footer>'''

    if old_footer:
        idx = idx.replace(old_footer.group(0), new_footer)

    idx = idx.replace('</body>', f'{paywall_modal_html}\n{fokus_modal_html}\n{paywall_and_focus_script}\n</body>')

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(idx)

    print("-> [SUCCESS] index.html har skrivits om med skarpa Paywall-triggers.")

# SKAPA SÄKERHETSKOPIA FALK2602
backup_name = "FALK2602"
zip_filename = f"{backup_name}.zip"
folder_filename = backup_name

if os.path.exists(zip_filename):
    os.remove(zip_filename)
if os.path.exists(folder_filename):
    shutil.rmtree(folder_filename)

ignore_patterns = shutil.ignore_patterns('__pycache__', '*.pyc', '.git', 'venv', '.env', 'FALK26*', 'backup*')
shutil.copytree('.', folder_filename, ignore=ignore_patterns)

with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(folder_filename):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, folder_filename)
            zipf.write(file_path, arcname)

print(f"-> [SUCCESS] Backup {backup_name}.zip skapad framgångsrikt!")
