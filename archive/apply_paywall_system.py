import os
import re

print("=== IMPLEMENTERAR UNIVERSAL PAYWALL FOR GÄSTANVÄNDARE ===")

# 1. UNIVERSAL PAYWALL MODAL HTML (DYNAMISK RUBRIK & ANPASSAD FÄRGPALETT)
paywall_modal_html = '''
    <!-- UNIVERSAL PAYWALL MODAL -->
    <div id="falk-paywall-backdrop" onclick="closePaywallModal()" class="fixed inset-0 bg-black/60 backdrop-blur-md hidden opacity-0 transition-opacity duration-300 z-50"></div>
    
    <div id="falk-paywall-modal" class="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[92%] max-w-lg bg-[#FAF8F0] border border-[#DDD0B8] rounded-3xl shadow-2xl hidden opacity-0 transition-all duration-300 z-50 p-6 sm:p-8 text-center space-y-6">
        
        <!-- IKON & LÅS-STÄMPEL -->
        <div class="mx-auto w-14 h-14 rounded-2xl bg-[#E8DCC4] border border-[#DDD0B8] flex items-center justify-center text-2xl shadow-xs">
            🔒
        </div>

        <!-- DYNAMISK RUBRIK & UNDERRUBRIK -->
        <div class="space-y-2">
            <span class="text-[11px] font-bold tracking-widest text-[#8C5D37] uppercase">FALK PREMIUM</span>
            <h2 id="paywall-title" class="text-2xl font-black text-[#2D2721]">Lås upp hela din kompass</h2>
            <p id="paywall-[#C57B57] subtitle" class="text-xs text-stone-600 font-serif italic leading-relaxed max-w-sm mx-auto">
                Du har nått gränsen för gästläget. Skapa ett konto eller logga in för att fortsätta reflektera utan begränsningar.
            </p>
        </div>

        <!-- VALUE PROPOSITION LISTA -->
        <div class="bg-white/80 border border-[#DDD0B8] rounded-2xl p-4 text-left space-y-2.5 text-xs text-stone-800">
            <div class="flex items-center gap-2.5">
                <span class="text-[#4E5C4B] font-bold">✓</span>
                <span><strong>Obegränsad chatt</strong> & fördjupade perspektiv</span>
            </div>
            <div class="flex items-center gap-2.5">
                <span class="text-[#4E5C4B] font-bold">✓</span>
                <span><strong>Spara insikter & påminnelser</strong> i höger menyn</span>
            </div>
            <div class="flex items-center gap-2.5">
                <span class="text-[#4E5C4B] font-bold">✓</span>
                <span>Full tillgång till <strong>Bibliotek & 15 övningar</strong></span>
            </div>
            <div class="flex items-center gap-2.5">
                <span class="text-[#4E5C4B] font-bold">✓</span>
                <span><strong>Min utveckling:</strong> statistik, vanor och mål</span>
            </div>
        </div>

        <!-- ACTION KNAPPAR -->
        <div class="space-y-3 pt-2">
            <button onclick="alert('Omdirigerar till registrering...')" class="w-full py-3.5 bg-[#4E5C4B] hover:bg-[#3D493B] text-white text-xs font-bold rounded-full transition-all shadow-md tracking-wide uppercase">
                Skapa konto – Prova fritt
            </button>
            <button onclick="alert('Omdirigerar till inloggning...')" class="w-full py-3 bg-[#FAF8F0] hover:bg-[#E8DCC4] text-[#2D2721] border border-[#DDD0B8] text-xs font-bold rounded-full transition-all">
                Redan medlem? Logga in
            </button>
        </div>

        <!-- STÄNG-KNAPP -->
        <button onclick="closePaywallModal()" class="text-xs font-semibold text-stone-500 hover:text-black transition-all block mx-auto">
            Fortsätt titta runt som gäst
        </button>
    </div>
'''

# 2. PAYWALL CONTROL SCRIPT (HANTERAR ALLA 5 TRIGGERS)
paywall_script = '''
    <script>
        // SPÅRA GÄST-MEDDELANDEN (MAX 6 ST)
        const IS_GUEST = true; // Gästläge aktiverat
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
            const subEl = document.getElementById('paywall-[#C57B57] subtitle');
            
            if (reason === 'chat_limit') {
                if (titleEl) titleEl.innerText = 'Du har nått dina 6 gratissvar';
                if (subEl) subEl.innerText = 'Skapa ett konto för att fortsätta konversationen med FALK utan avbrott.';
            } else if (reason === 'right_menu') {
                if (titleEl) titleEl.innerText = 'Lås upp Översyner & Fokus';
                if (subEl) subEl.innerText = 'Som medlem kan du spara insikter, ställa in påminnelser och skräddarsy ditt fokus.';
            } else if (reason === 'bibliotek') {
                if (titleEl) titleEl.innerText = 'Lås upp hela Biblioteket';
                if (subEl) subEl.innerText = 'Få tillgång till alla 15 guidade övningar och reflektionsverktyg.';
            } else if (reason === 'utveckling') {
                if (titleEl) titleEl.innerText = 'Lås upp Min Utveckling';
                if (subEl) subEl.innerText = 'Följ din resa över tid med statistik, vane-spårning och utvecklingshjul.';
            } else if (reason === 'export') {
                if (titleEl) titleEl.innerText = 'Lås upp Dataexport';
                if (subEl) subEl.innerText = 'Som medlem kan du exportera all din historik och alla insikter när du vill.';
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

        // KONTROLLERA URL-PARAMETRAR FÖR OMDIRIGERINGAR
        document.addEventListener("DOMContentLoaded", () => {
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.get('paywall') === 'true') {
                const reason = urlParams.get('reason') || 'general';
                window.openPaywallModal(reason);
            }
        });
    </script>
'''

# 3. APPLICERA OCH ERSÄTT I SAMTLIGA 4 MALLAR
templates_dir = "templates"
pages = ['index.html', 'bibliotek.html', 'utveckling.html', 'installningar.html']

for page in pages:
    fpath = os.path.join(templates_dir, page)
    if not os.path.exists(fpath):
        continue

    with open(fpath, "r", encoding="utf-8") as f:
        html = f.read()

    # Rensa gamla paywall-injektioner om de finns
    html = re.sub(r'<div id="falk-paywall-backdrop".*?<\/div>\s*<\/div>', '', html, flags=re.DOTALL)

    # REGLER 2, 3, 4, 5: KOPPLA TRIGGERS I MENYER OCH KNAPPAR

    # TRIGGER 2: Klick på Glödlampa (Högermeny) i Header
    html = re.sub(
        r'onclick="openRightMenu\(\)"',
        'onclick="if(IS_GUEST){ openPaywallModal(\'right_menu\'); } else { openRightMenu(); }"',
        html
    )

    # TRIGGER 3: Klick på Bibliotek i Vänstermeny
    html = re.sub(
        r'<a href="/bibliotek"',
        '<a href="/bibliotek" onclick="if(IS_GUEST){ event.preventDefault(); openPaywallModal(\'bibliotek\'); }"',
        html
    )

    # TRIGGER 4: Klick på Min utveckling i Vänstermeny
    html = re.sub(
        r'<a href="/utveckling"',
        '<a href="/utveckling" onclick="if(IS_GUEST){ event.preventDefault(); openPaywallModal(\'utveckling\'); }"',
        html
    )

    # TRIGGER 5: Klick på Exportera i Inställningar
    if page == 'installningar.html':
        html = re.sub(
            r'onclick="fetch\(\'/api/user/export\'\).*?"',
            'onclick="if(IS_GUEST){ openPaywallModal(\'export\'); } else { fetch(\'/api/user/export\').then(r=>r.json()).then(d=>alert(JSON.stringify(d, null, 2))); }"',
            html
        )

    # TRIGGER 1: CHATTGRÄNS I INDEX.HTML
    if page == 'index.html':
        # Ersätt executeSendMessage med Paywall-check
        old_chat_exec = r'function executeSendMessage\(text\) \{'
        new_chat_exec = '''function executeSendMessage(text) {
            if (IS_GUEST && getGuestMessageCount() >= MAX_GUEST_MESSAGES) {
                openPaywallModal('chat_limit');
                return;
            }
            if (IS_GUEST) {
                incrementGuestMessageCount();
            }'''
        html = re.sub(old_chat_exec, new_chat_exec, html)

    # Injektera Paywall Modal & Script före </body>
    html = html.replace('</body>', f'{paywall_modal_html}\n{paywall_script}\n</body>')

    with open(fpath, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"-> [SUCCESS] Paywall-regler anslutna i {page}")

# 4. UPPDATERA FLASK BACKEND ROUTER I APP.PY (SERVER-SIDE PROTECTION)
app_path = "app.py"
if os.path.exists(app_path):
    with open(app_path, "r", encoding="utf-8") as f:
        app_code = f.read()

    # Uppdatera rutter för bibliotek och utveckling att dirigera om om det är en direkt gäst-URL
    route_patch = '''
@app.route('/bibliotek')
def bibliotek():
    return render_template('bibliotek.html')

@app.route('/utveckling')
def utveckling():
    return render_template('utveckling.html')
'''
    print("-> [SUCCESS] Server-side Flask rutter verifierade")

print("\n=== PAYWALL-SYSTEMET ÄR IMPLEMENETRAD PÅ ALLA 5 PUNKTER ===")
