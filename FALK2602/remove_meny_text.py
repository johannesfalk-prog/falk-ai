import re

filepath = "templates/index.html"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Sök upp <header>...</header> och ta bort ordet "Meny" ur textnoder
def strip_meny(match):
    header_html = match.group(0)
    # Ta bort ordet Meny (skiftlägesokänsligt) inne i headern
    return re.sub(r'\bMeny\b', '', header_html, flags=re.IGNORECASE)

if re.search(r'<header[\s\S]*?</header>', content, re.IGNORECASE):
    new_content = re.sub(r'<header[\s\S]*?</header>', strip_meny, content, count=1, flags=re.IGNORECASE)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("-> [SUCCESS] Texten 'Meny' har raderats ur <header> i templates/index.html!")
else:
    print("[ERROR] Ingen <header>-tagg hittades i templates/index.html")
