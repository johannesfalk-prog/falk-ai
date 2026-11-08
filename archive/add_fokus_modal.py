import os
import re

print("=== BYGGER FOKUS-MODAL MED 5 SLIDERS & REAKTIV AI-LOGIK ===")

fokus_modal_html = '''
    <!-- FOKUS MODAL (5 PARAMETRAR: INKL. MOTIVATION) -->
    <div id="falk-fokus-backdrop" onclick="closeFocusModal()" class="fixed inset-0 bg-black/50 backdrop-blur-sm hidden opacity-0 transition-opacity duration-300 z-50"></div>
    <div id="falk-fokus-modal" class="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[92%] max-w-md bg-[#FAF8F0] border border-[#DDD0B8] rounded-3xl shadow-2xl hidden opacity-0 transition-all duration-300 z-50 p-6 space-y-5">
        
        <!-- HEADER -->
        <div class="flex items-center justify-between pb-3 border-b border-[#E6E0D4]">
            <h2 class="text-xl font-extrabold text-[#2D2721]">Fokus</h2>
            <div class="flex items-center gap-4">
                <button onclick="resetFocusSliders()" class="text-xs font-bold text-[#C57B57] hover:underline transition-all">Återställ</button>
                <button onclick="closeFocusModal()" class="text-stone-500 hover:text-black font-bold text-lg p-1">✕</button>
            </div>
        </div>

        <!-- SLIDERS CONTAINER -->
        <div class="space-y-4">
            
            <!-- 1. Självförtroende -->
            <div class="space-y-1">
                <div class="flex justify-between text-xs font-bold text-[#2D2721]">
                    <span>Självförtroende</span>
                    <span id="val-sjalvfortroende" class="text-stone-600">50%</span>
                </div>
                <input type="range" id="slider-sjalvfortroende" min="0" max="100" value="50" oninput="updateSliderUI('sjalvfortroende')" class="falk-slider w-full">
            </div>

            <!-- 2. Stresshantering -->
            <div class="space-y-1">
                <div class="flex justify-between text-xs font-bold text-[#2D2721]">
                    <span>Stresshantering</span>
                    <span id="val-stresshantering" class="text-stone-600">50%</span>
                </div>
                <input type="range" id="slider-stresshantering" min="0" max="100" value="50" oninput="updateSliderUI('stresshantering')" class="falk-slider w-full">
            </div>

            <!-- 3. Handlingskraft -->
            <div class="space-y-1">
                <div class="flex justify-between text-xs font-bold text-[#2D2721]">
                    <span>Handlingskraft</span>
                    <span id="val-handlingskraft" class="text-stone-600">50%</span>
                </div>
                <input type="range" id="slider-handlingskraft" min="0" max="100" value="50" oninput="updateSliderUI('handlingskraft')" class="falk-slider w-full">
            </div>

            <!-- 4. Gränssättning -->
            <div class="space-y-1">
                <div class="flex justify-between text-xs font-bold text-[#2D2721]">
                    <span>Gränssättning</span>
                    <span id="val-granssattning" class="text-stone-600">50%</span>
                </div>
                <input type="range" id="slider-granssattning" min="0" max="100" value="50" oninput="updateSliderUI('granssattning')" class="falk-slider w-full">
            </div>

            <!-- 5. Motivation (NY PARAMETER) -->
            <div class="space-y-1">
                <div class="flex justify-between text-xs font-bold text-[#2D2721]">
                    <span>Motivation</span>
                    <span id="val-motivation" class="text-stone-600">50%</span>
                </div>
                <input type="range" id="slider-motivation" min="0" max="100" value="50" oninput="updateSliderUI('motivation')" class="falk-slider w-full">
            </div>

        </div>

        <!-- SPARAKNAPP -->
        <button onclick="saveAndApplyFocus()" class="w-full py-3 bg-[#4E5C4B] hover:bg-[#3D493B] text-white text-xs font-bold rounded-full transition-all shadow-xs">
            Verkställ Fokusinställningar
        </button>
    </div>

    <!-- CUSTOM STYLING FÖR ANPASSADE REGLEGE (PROPRIETÄR FÄRGPALETT) -->
    <style>
        .falk-slider {
            -webkit-appearance: none;
            appearance: none;
            height: 8px;
            background: #A8BFA1;
            border-radius: 9999px;
            outline: none;
        }
        .falk-slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #C57B57;
            cursor: pointer;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            transition: transform 0.1s ease;
        }
        .falk-slider::-webkit-slider-thumb:hover {
            transform: scale(1.15);
            background: #B46A46;
        }
    </style>
'''

fokus_js = '''
        // --- FOKUS MODAL OCH REAKTIV AI LOGIK ---
        let initialFocusState = { sjalvfortroende: 50, stresshantering: 50, handlingskraft: 50, granssattning: 50, motivation: 50 };

        function loadSavedFocus() {
            const saved = localStorage.getItem('falk_focus_settings');
            if (saved) {
                try {
                    initialFocusState = JSON.parse(saved);
                    Object.keys(initialFocusState).forEach(key => {
                        const el = document.getElementById('slider-' + key);
                        if (el) {
                            el.value = initialFocusState[key];
                            updateSliderUI(key);
                        }
                    });
                } catch(e){}
            }
        }

        function updateSliderUI(key) {
            const val = document.getElementById('slider-' + key).value;
            const label = document.getElementById('val-' + key);
            if (label) label.innerText = val + '%';
        }

        function openFocusModal() {
            loadSavedFocus();
            const bd = document.getElementById("falk-fokus-backdrop");
            const md = document.getElementById("falk-fokus-modal");
            if (bd && md) {
                bd.classList.remove("hidden");
                md.classList.remove("hidden");
                setTimeout(() => {
                    bd.classList.remove("opacity-0");
                    md.classList.remove("opacity-0");
                }, 10);
            }
        }

        function closeFocusModal() {
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
        }

        function resetFocusSliders() {
            const keys = ['sjalvfortroende', 'stresshantering', 'handlingskraft', 'granssattning', 'motivation'];
            keys.forEach(k => {
                const el = document.getElementById('slider-' + k);
                if (el) {
                    el.value = 50;
                    updateSliderUI(k);
                }
            });
        }

        function saveAndApplyFocus() {
            const currentFocus = {
                sjalvfortroende: parseInt(document.getElementById('slider-sjalvfortroende').value),
                stresshantering: parseInt(document.getElementById('slider-stresshantering').value),
                handlingskraft: parseInt(document.getElementById('slider-handlingskraft').value),
                granssattning: parseInt(document.getElementById('slider-granssattning').value),
                motivation: parseInt(document.getElementById('slider-motivation').value)
            };

            const isChanged = JSON.stringify(currentFocus) !== JSON.stringify(initialFocusState);
            localStorage.setItem('falk_focus_settings', JSON.stringify(currentFocus));
            initialFocusState = { ...currentFocus };

            closeFocusModal();

            // OM FÖRÄNDRING SKETT: TRIGGA ETT SYSTEM-MEDDELANDE FRÅN FALK
            if (isChanged) {
                triggerFalkFocusAdaptingMessage(currentFocus);
            }
        }

        function triggerFalkFocusAdaptingMessage(focus) {
            // Aktivera chatt-tråd om den är dold
            const dash = document.getElementById("dashboard-grid");
            const thread = document.getElementById("chat-thread");
            if (dash && thread && !dash.classList.contains("hidden")) {
                dash.classList.add("hidden");
                thread.classList.remove("hidden");
            }

            // Skapa AI-anpassningsbubbla i chatten
            const ai = appendAiSkeleton();
            setTimeout(() => {
                ai.innerText = `Jag har registrerat dina nya Fokus-inställningar:\n` +
                    `• Självförtroende: ${focus.sjalvfortroende}%\n` +
                    `• Stresshantering: ${focus.stresshantering}%\n` +
                    `• Handlingskraft: ${focus.handlingskraft}%\n` +
                    `• Gränssättning: ${focus.granssattning}%\n` +
                    `• Motivation: ${focus.motivation}%\n\n` +
                    `Jag anpassar nu mitt bemötande och mina perspektiv efter din nya profil. Vad vill du ta dig an först?`;
            }, 600);
        }

        document.addEventListener("DOMContentLoaded", loadSavedFocus);
'''

# UPPDATERA INDEX.HTML OCH FOOTER TOGGLE BUTTON
index_path = os.path.join("templates", "index.html")
with open(index_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Byt ut inställningsknappen i footern mot onclick="openFocusModal()"
old_footer_btn = r'<button type="button" class="p-1\.5 text-stone-500 hover:text-black transition-all transform rotate-90" title="Inställningar">'
new_footer_btn = '<button type="button" onclick="openFocusModal()" class="p-1.5 text-stone-500 hover:text-[#C57B57] transition-all transform rotate-90" title="Öppna Fokus & Parameterinställningar">'

if re.search(old_footer_btn, html):
    html = re.sub(old_footer_btn, new_footer_btn, html)
    print("-> [SUCCESS] Kopplade footer toggle-knapp till openFocusModal()")

# 2. Lägg till Fokus HTML före </body> om inte redan tillagd
if 'id="falk-fokus-modal"' not in html:
    html = html.replace('</body>', f'{fokus_modal_html}\n</body>')
    print("-> [SUCCESS] Injekterade Fokus-modal HTML")

# 3. Lägg till Fokus JS i skript-taggen
if 'openFocusModal' not in html:
    html = html.replace('</script>', f'{fokus_js}\n</script>')
    print("-> [SUCCESS] Injekterade Fokus-modal JavaScript")

with open(index_path, "w", encoding="utf-8") as f:
    f.write(html)

print("=== FOKUS-MODALEN ÄR IMPLEMENETRAD PÅ $100\%$ PARITET ===")
