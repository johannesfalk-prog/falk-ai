import re
import os

target_file = os.path.join("templates", "index.html")

if os.path.exists(target_file):
    with open(target_file, "r", encoding="utf-8") as f:
        html = f.read()

    # Lägg till en synlig knallröd test-banner överst i <header>
    watermark = '<div id="falk-pipeline-test" style="background: #FF0000 !important; color: #FFFFFF !important; padding: 10px !important; text-align: center !important; font-weight: bold !important; font-size: 16px !important; z-index: 999999 !important;">=== PIPELINE-TEST: UPPDATERINGAR GÅR IGENOM ===</div>'
    
    # Ta bort eventuell gammal test-banner
    html = re.sub(r'<div id="falk-pipeline-test"[\s\S]*?</div>', '', html)
    
    # Injektera precis efter <header...>
    if "<header" in html:
        html = re.sub(r'(<header[^>]*>)', r'\1\n' + watermark, html, count=1, flags=re.IGNORECASE)
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(html)
        print("-> [SUCCESS] Vattenstämpel injekterad i templates/index.html!")
    else:
        print("[ERROR] Hittade ingen <header>-tagg i templates/index.html")
