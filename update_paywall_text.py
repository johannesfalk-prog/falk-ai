import os
import re

print("=== UPPDATERAR PAYWALL-TEXTER OCH PRIS-BADGE ÖVER ALLA MALLAR ===")

pages = ['index.html', 'bibliotek.html', 'utveckling.html', 'installningar.html']
templates_dir = "templates"

# NY UTFORMNING FÖR PUNKTLESTA OCH PRIS-BADGE KNAPP
new_paywall_body = '''
        <!-- VALUE PROPOSITION LISTA (RENOVLAD & SKARP) -->
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

        <!-- ACTION KNAPPAR (MED PRIS-BADGE: 199kr/mån, ord. 249kr/mån) -->
        <div class="space-y-3 pt-2">
            <button onclick="alert('Omdirigerar till registrering och kassa...')" class="w-full py-3.5 bg-[#4E5C4B] hover:bg-[#3D493B] text-white text-xs font-bold rounded-full transition-all shadow-md flex items-center justify-center gap-2 flex-wrap">
                <span class="uppercase tracking-wide">Skapa konto</span>
                <span class="normal-case bg-[#C57B57] text-white px-2.5 py-0.5 rounded-full text-[10px] font-bold shadow-xs">
                    199 kr/mån <span class="line-through opacity-75">ord. 249 kr/mån</span>
                </span>
            </button>
            <button onclick="alert('Omdirigerar till inloggning...')" class="w-full py-3 bg-[#FAF8F0] hover:bg-[#E8DCC4] text-[#2D2721] border border-[#DDD0B8] text-xs font-bold rounded-full transition-all">
                Redan medlem? Logga in
            </button>
        </div>
'''

for page in pages:
    fpath = os.path.join(templates_dir, page)
    if not os.path.exists(fpath):
        continue

    with open(fpath, "r", encoding="utf-8") as f:
        html = f.read()

    # Matcha och ersätt hela blocket från VALUE PROPOSITION LISTA till slutet på ACTION KNAPPAR
    pattern = r'<!-- VALUE PROPOSITION LISTA.*?<\/div>\s*<\/div>\s*<!-- ACTION KNAPPAR.*?<\/div>\s*<\/div>'
    
    if re.search(pattern, html, flags=re.DOTALL):
        html = re.sub(pattern, new_paywall_body.strip(), html, flags=re.DOTALL)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"-> [SUCCESS] Uppdaterade Paywall i {page}")
    else:
        print(f"-> [WARNING] Kunde inte matcha mönstret i {page}")

print("\n=== UPPDATERINGEN ÄR SLUTFÖRD UTAN FEL ===")
