import os
import re

print("=== VERKSTÄLLER SKARP FIX FÖR FOKUS-MODALEN OCH TOGGLE-IKONEN ===")

# 1. HÖGKVALITATIV FOKUS MODAL (HTML + CSS)
fokus_html = '''
    <!-- FOKUS MODAL (FÄRGPALETT: #E8DCC4, #C57B57, #4E5C4B, #A8BFA1) -->
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

        <!-- 5 SLIDERS CONTAINER (DEFAULT 50%) -->
        <div class="space-y-4">
            
            <!-- 1. Självförtroende -->
            <div class="space-y-1">
                <div class="flex justify-between text-xs font-bold text-[#2D2721]">
                    <span>Självförtroende</span>
                    <span id="val-sjalvfortroende" class="text-[#C57B57]">50%</span>
                </div>
                <input type="range" id="slider-sjalvfortroende" min="0" max="100" value="50" oninput="updateSliderUI('sjalvfortroende')" class="falk-slider w-full">
            </div>

            <!-- 2. Stresshantering -->
            <div class="space-y-1">
                <div class="flex justify-between text-xs font-bold text-[#2D2721]">
                    <span>Stresshantering</span>
                    <span id="val-stresshantering" class="text-[#C57B57]">50%</span>
                </div>
                <input type="range" id="slider-stresshantering" min="0" max="100" value="50" oninput="updateSliderUI('stresshantering')" class="falk-slider w-full">
            </div>

            <!-- 3. Handlingskraft -->
            <div class="space-y-1">
                <div class="flex justify-between text-xs font-bold text-[#2D2721]">
                    <span>Handlingskraft</span>
                    <span id="val-handlingskraft" class="text-[#C57B57]">50%</span>
                </div>
                <input type="range" id="slider-handlingskraft" min="0" max="100" value="50" oninput="updateSliderUI('handlingskraft')" class="falk-slider w-full">
            </div>

            <!-- 4. Gränssättning -->
            <div class="space-y-1">
                <div class="flex justify-between text-xs font-bold text-[#2D2721]">
                    <span>Gränssättning</span>
                    <span id="val-granssattning" class="text-[#C57B57]">50%</span>
                </div>
                <input type="range" id="slider-granssattning" min="0" max="100" value="50" oninput="updateSliderUI('granssattning')" class="falk-slider w-full">
            </div>

            <!-- 5. Motivation -->
            <div class="space-y-1">
                <div class="flex justify-between text-xs font-bold text-[#2D2721]">
                    <span>Motivation</span>
                    <span id="val-motivation" class="text-[#C57B57]">50%</span>
                </div>
                <input type="range" id="slider-motivation" min="0" max="100" value="50" oninput="updateSliderUI('motivation')" class="falk-slider w-full">
            </div>

        </div>

        <!-- BOTTENKNAPP -->
        <button onclick="saveAndApplyFocus()" class="w-full py-3 bg-[#4E5C4B] hover:bg-[#3D493B] text-white text-xs font-bold rounded-full transition-all shadow-xs">
            Verkställ Fokusinställningar
        </button>
    </div>

    <!-- ANPASSAD STYLE FÖR SLIDERS (#A8BFA1 SPÅR, #C57B57 THUMB) -->
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
            transition: transform 0.15s ease;
        }
        .falk-slider::-webkit-slider-thumb:hover {
            transform: scale(1.2);
        }
    </style>
'''

# 2. BULLETPROOF JAVASCRIPT LOGIK (KOPPLAD TILL WINDOW)
fokus_script = '''
    <script>
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

            const isChanged = JSON.stringify(currentFocus) !== JSON.stringify(initialFocusState);
            localStorage.setItem('falk_focus_settings', JSON.stringify(currentFocus));
            initialFocusState = { ...currentFocus };

            window.closeFocusModal();

            if (isChanged) {
                // Växla vy till chatttråd om vi är på startskärmen
                const dash = document.getElementById("dashboard-grid");
                const thread = document.getElementById("chat-thread");
                if (dash && thread && !dash.classList.contains("hidden")) {
                    dash.classList.add("hidden");
                    thread.classList.remove("hidden");
                    if (typeof isChatActive !== 'undefined') isChatActive = true;
                }

                // Generera anpassningssvar i chatten
                const ai = appendAiSkeleton();
                setTimeout(() => {
                    ai.innerText = `Jag har registrerat dina nya Fokus-inställningar:\n\n` +
                        `• Självförtroende: ${currentFocus.sjalvfortroende}%\n` +
                        `• Stresshantering: ${currentFocus.stresshantering}%\n` +
                        `• Handlingskraft: ${currentFocus.handlingskraft}%\n` +
                        `• Gränssättning: ${currentFocus.granssattning}%\n` +
                        `• Motivation: ${currentFocus.motivation}%\n\n` +
                        `Jag har anpassat min kompass efter din nuvarande profil. Hur vill du ta dig an din utmaning just nu?`;
                }, 500);
            }
        };
    </script>
'''

# 3. UPPDATERA TEMPLATES PÅ DISKEN
for template_name in ['index.html', 'bibliotek.html', 'utveckling.html', 'installningar.html']:
    file_path = os.path.join("templates", template_name)
    if not os.path.exists(file_path):
        continue

    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Rensa gamla modal- eller skript-injektioner om de finns
    html = re.sub(r'<div id="falk-fokus-backdrop".*?<\/style>', '', html, flags=re.DOTALL)

    # Ersätt footerns toggle-knapp helt
    old_btn_pattern = r'<button type="button" class="p-1\.5 text-stone-500 hover:text-black transition-all transform rotate-90".*?<\/button>'
    new_btn_html = '<button type="button" id="focus-toggle-btn" onclick="openFocusModal()" class="p-1.5 text-stone-500 hover:text-[#C57B57] transition-all transform rotate-90 focus:outline-none" title="Öppna Fokus & Parameterinställningar"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"></path></svg></button>'

    html = re.sub(old_btn_pattern, new_btn_html, html)

    # Injektera modal och skript före </body>
    html = html.replace('</body>', f'{fokus_html}\n{fokus_script}\n</body>')

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"-> [SUCCESS] Fixat Fokus-modal & toggle-knapp i {template_name}")

print("\n=== SKARP FIX VERKSTÄLLD: KLICKA PÅ KNAPPEN I WEBBLÄSAREN NU ===")
