import os
import re

print("=== VERKSTÄLLER RENSNING AV INLINE PAYWALLS OCH ALERTS ===")

index_path = os.path.join("templates", "index.html")
if not os.path.exists(index_path):
    print("Error: index.html hittades inte!")
    exit(1)

with open(index_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. TA BORT SKRÄP-HTML SOM HAMNAT NEDANFÖR FOOTERN (BILD 2 CLEANUP)
# Vi klipper bort allt mellan </footer> och <script> som inte hör hemma i flödet
html = re.sub(r'</footer>\s*<div id="falk-paywall-backdrop".*?<!-- FOKUS MODAL -->', '</footer>\n\n    <!-- UNIVERSAL POPUP PAYWALL MODAL -->', html, flags=re.DOTALL)
html = re.sub(r'(SKAPA KONTO – PROVA FRITT.*?Fortsätt titta runt som gäst)', '', html, flags=re.DOTALL)

# 2. DEFINIERA RENA DÖLJBARA OVERLAY-MODALER (FIXED POSITIONING ENBART)
paywall_overlay = '''
    <!-- UNIVERSAL POPUP PAYWALL MODAL (KORREKT DÖLJS MED HIDDEN) -->
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
            <button onclick="triggerStripeCheckout()" class="w-full py-3.5 bg-[#4E5C4B] hover:bg-[#3D493B] text-white text-xs font-bold rounded-full transition-all shadow-md tracking-wider uppercase">
                Skapa konto
            </button>
            <button onclick="openAuthModal()" class="w-full py-3 bg-[#FAF8F0] hover:bg-[#E8DCC4] text-[#2D2721] border border-[#DDD0B8] text-xs font-bold rounded-full transition-all">
                Redan medlem? Logga in
            </button>
        </div>
        <button onclick="closePaywallModal()" class="text-xs font-semibold text-stone-500 hover:text-black transition-all block mx-auto pt-1">
            Fortsätt titta runt som gäst
        </button>
    </div>
'''

# 3. TA BORT ALERT() I JAVASCRIPT
html = re.sub(r'alert\(\'Välkommen tillbaka!.*?\);', '', html)
html = re.sub(r'alert\(\'Du har loggat ut.*?\);', '', html)

# 4. SKRIV TILLBAKA RENSAD OCH KORREKT STRUKTUR
# Hitta rätt plats före </body>
main_parts = html.split('</body>')
clean_body = main_parts[0]

# Rensa dubblerade modal-block om de finns i slutet
clean_body = re.sub(r'<!-- UNIVERSAL POPUP PAYWALL MODAL -->.*', '', clean_body, flags=re.DOTALL)

new_html = clean_body + paywall_overlay + '\n</body>' + main_parts[1]

with open(index_path, "w", encoding="utf-8") as f:
    f.write(new_html)

print("-> [SUCCESS] index.html rensad från inline paywall-skräp och alerts!")
