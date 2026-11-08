import os
import re

print("=== VERKSTÄLLER SKARP PAYWALL MED PRIS-BADGE OCH 5 TRIGGERS ===")

# 1. EXAKT PAYWALL HTML (BILD-PARITET + EXAKTA PUNKTLESTER + PRIS-BADGE)
paywall_modal_html = '''
    <!-- UNIVERSAL PAYWALL MODAL -->
    <div id="falk-paywall-backdrop" onclick="closePaywallModal()" class="fixed inset-0 bg-black/60 backdrop-blur-md hidden opacity-0 transition-opacity duration-300 z-50"></div>
    
    <div id="falk-paywall-modal" class="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[92%] max-w-md bg-[#FAF8F0] border border-[#DDD0B8] rounded-3xl shadow-2xl hidden opacity-0 transition-all duration-300 z-50 p-6 sm:p-8 text-center space-y-5">
        
        <!-- LOCK ICON -->
        <div class="mx-auto w-12 h-12 rounded-2xl bg-[#E8DCC4] border border-[#DDD0B8] flex items-center justify-center text-xl shadow-xs">
            🔒
        </div>

        <!-- HEADER -->
        <div class="space-y-1.5">
            <span class="text-[11px] font-bold tracking-widest text-[#8C5D37] uppercase">FALK PREMIUM</span>
            <h2 id="paywall-title" class="text-2xl font-black text-[#2D2721] leading-tight">Lås upp hela din kompass</h2>
            <p id="paywall-subtitle" class="text-xs text-stone-600 font-serif italic leading-relaxed max-w-sm mx-auto">
                Du har nått gränsen för gästläget. Skapa ett konto eller logga in för att fortsätta reflektera utan begränsningar.
            </p>
        </div>

        <!-- 4 EXAKTA PUNKTER -->
        <div class="bg-white/80 border border-[#DDD0B8] rounded-2xl p-4 text-left space-y-2.5 text-xs text-stone-800">
            <div class="flex items-center gap-2.5">
                <span class="text-[#4E5C4B] font-bold">✓</span>
                <span>Obegränsad chatt, fördjupade perspektiv</span>
            </div>
            <div class="flex items-center gap-2.5">
                <span class="text-[#4E5C4B] font-bold">✓</span>
                <span>Spara insikter & påminnelser</span>
            </div>
            <div class="flex items-center gap-2.5">
                <span class="text-[#4E5C4B] font-bold">✓</span>
                <span>Full tillgång till Biblioteket</span>
            </div>
            <div class="flex items-center gap-2.5">
                <span class="text-[#4E5C4B] font-bold">✓</span>
                <span>Min utveckling och fler funktioner</span>
            </div>
        </div>

        <!-- ACTION KNAPPAR MED PRIS-BADGE -->
        <div class="space-y-2.5 pt-1">
            <button onclick="alert('Omdirigerar till kassan...')" class="w-full py-3.5 bg-[#4E5C4B] hover:bg-[#3D493B] text-white text-xs font-bold rounded-full transition-all shadow-md flex items-center justify-center gap-2 flex-wrap">
                <span class="uppercase tracking-wider">Skapa konto</span>
                <span class="normal-case bg-[#C57B57] text-white px-2.5 py-0.5 rounded-full text-[10px] font-bold shadow-xs">
                    199 kr/mån <span class="line-through opacity-75">ord. 249 kr/mån</span>
                </span>
            </button>
            <button onclick="alert('Omdirigerar till inloggning...')" class="w-full py-3 bg-[#FAF8F0] hover:bg-[#E8DCC4] text-[#2D2721] border border-[#DDD0B8] text-xs font-bold rounded-full transition-all">
                Redan medlem? Logga in
            </button>
        </div>

        <!-- CLOSE LINK -->
        <button onclick="closePaywallModal()" class="text-xs font-semibold text-stone-500 hover:text-black transition-all block mx-auto pt-1">
            Fortsätt titta runt som gäst
        </button>
    </div>
'''

# 2. PAYWALL CONTROL SCRIPT
paywall_script = '''
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
    </script>
'''

# 3. VERKSTÄLL PÅ DISKEN
pages = ['index.html', 'bibliotek.html', 'utveckling.html', 'installningar.html']
templates_dir = "templates"

for page in pages:
    fpath = os.path.join(templates_dir, page)
    if not os.path.exists(fpath):
        continue

    with open(fpath, "r", encoding="utf-8") as f:
        html = f.read()

    # Rensa gamla paywall-block helt
    html = re.sub(r'<!-- UNIVERSAL PAYWALL MODAL -->.*?<\/div>\s*<\/div>', '', html, flags=re.DOTALL)
    html = re.sub(r'<script>\s*const IS_GUEST = true;.*?<\/script>', '', html, flags=re.DOTALL)

    # TRIGGER 2: Glödlampa (Högermeny) i Header
    html = re.sub(
        r'onclick="openRightMenu\(\)"',
        'onclick="if(typeof IS_GUEST !== \'undefined\' && IS_GUEST){ openPaywallModal(\'right_menu\'); } else { openRightMenu(); }"',
        html
    )

    # TRIGGER 3: Bibliotek i Vänstermeny
    html = re.sub(
        r'<a href="/bibliotek"',
        '<a href="/bibliotek" onclick="if(typeof IS_GUEST !== \'undefined\' && IS_GUEST){ event.preventDefault(); openPaywallModal(\'bibliotek\'); }"',
        html
    )

    # TRIGGER 4: Min utveckling i Vänstermeny
    html = re.sub(
        r'<a href="/utveckling"',
        '<a href="/utveckling" onclick="if(typeof IS_GUEST !== \'undefined\' && IS_GUEST){ event.preventDefault(); openPaywallModal(\'utveckling\'); }"',
        html
    )

    # TRIGGER 5: Exportera i Inställningar
    if page == 'installningar.html':
        html = re.sub(
            r'onclick="fetch\(\'/api/user/export\'\).*?"',
            'onclick="if(typeof IS_GUEST !== \'undefined\' && IS_GUEST){ openPaywallModal(\'export\'); } else { fetch(\'/api/user/export\').then(r=>r.json()).then(d=>alert(JSON.stringify(d, null, 2))); }"',
            html
        )

    # TRIGGER 1: CHATTGRÄNS (6 MEDDELANDEN) I INDEX.HTML
    if page == 'index.html':
        if 'if (IS_GUEST && getGuestMessageCount() >= MAX_GUEST_MESSAGES)' not in html:
            old_chat_exec = r'function executeSendMessage\(text\) \{'
            new_chat_exec = '''function executeSendMessage(text) {
            if (typeof IS_GUEST !== 'undefined' && IS_GUEST && getGuestMessageCount() >= MAX_GUEST_MESSAGES) {
                openPaywallModal('chat_limit');
                return;
            }
            if (typeof IS_GUEST !== 'undefined' && IS_GUEST) {
                incrementGuestMessageCount();
            }'''
            html = re.sub(old_chat_exec, new_chat_exec, html)

    # Injektera före </body>
    html = html.replace('</body>', f'{paywall_modal_html}\n{paywall_script}\n</body>')

    with open(fpath, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"-> [EXAKT UPPDATERING OK] {page}")

print("\n=== PAYWALL-UPPDATERINGEN ÄR NUPPVERKSTÄLLD ===")
