import os

target_file = os.path.join("templates", "index.html")

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Ursprungligt antal rader: {len(lines)}")

# Behåll alla rader fram till precis innan kraschen (ca rad 2430)
# Vi söker sista giltiga </body> eller rensar bara trasiga slut-skript
clean_lines = []
for line in lines:
    clean_lines.append(line)
    if "</html>" in line.lower():
        break

content = "".join(clean_lines)

# Ta bort eventuella skräp-parenteser eller oanvända skript i slutet
import re
# Ta bort kända trasiga anrop längst ned
content = re.sub(r'<script>[^<]*missing\s*\)[^<]*</script>', '', content, flags=re.IGNORECASE)

# Säkerställ att filen slutar rent
if "</html>" not in content.lower():
    content += "\n</body>\n</html>"

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("-> [SUCCESS] Slutskripten rensade och säkrade!")
