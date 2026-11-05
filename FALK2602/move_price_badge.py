import os
import re

print("=== FLYTTAR PRIS-BADGE TILL VÄRDELISTAN OCH RENSAR CTA-KNAPPEN ===")

pages = ['index.html', 'bibliotek.html', 'utveckling.html', 'installningar.html']
templates_dir = "templates"

# EXAKT NY PAYWALL-MODAL MED PRIS-BADGEN INNE I KORTET
new_paywall_modal = '''    <!-- UNIVERSAL PAYWALL MODAL -->
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

        <!-- 4 EXAKTA PUNKTER MED PRIS-BADGE ÖVERST I LISTKORTET -->
        <div class="bg-white/80 border border-[#DDD0B8] rounded-2xl p-4 text-left space-y-3 text-xs text-stone-800">
            <!-- PRIS BADGE FRAMHÄVD INNE I KORTET -->
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

        <!-- ACTION KNAPPAR (REN & STARK CTA) -->
        <div class="space-y-2.5 pt-1">
            <button onclick="alert('Omdirigerar till kassan...')" class="w-full py-3.5 bg-[#4E5C4B] hover:bg-[#3D493B] text-white text-xs font-bold rounded-full transition-all shadow-md tracking-wider uppercase">
                Skapa konto – Prova fritt
            </button>
            <button onclick="alert('Omdirigerar till inloggning...')" class="w-full py-3 bg-[#FAF8F0] hover:bg-[#E8DCC4] text-[#2D2721] border border-[#DDD0B8] text-xs font-bold rounded-full transition-all">
                Redan medlem? Logga in
            </button>
        </div>

        <!-- CLOSE LINK -->
        <button onclick="closePaywallModal()" class="text-xs font-semibold text-stone-500 hover:text-black transition-all block mx-auto pt-1">
            Fortsätt titta runt som gäst
        </button>
    </div>'''

for page in pages:
    fpath = os.path.join(templates_dir, page)
    if not os.path.exists(fpath):
        continue

    with open(fpath, "r", encoding="utf-8") as f:
        html = f.read()

    # Ersätt existerande Paywall Modal-block
    pattern = r'<!-- UNIVERSAL PAYWALL MODAL -->.*?<\/div>\s*<\/div>'
    if re.search(pattern, html, flags=re.DOTALL):
        html = re.sub(pattern, new_paywall_modal, html, flags=re.DOTALL)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"-> [BADGE MOVED] Uppdaterade Paywall i {page}")
    else:
        print(f"-> [WARNING] Hittade inte modal-mönstret i {page}")

print("\n=== SKRIPTET FULLBORDAT: BADGEN LIGGER NU INNE I VÄRDELISTAN ===")
