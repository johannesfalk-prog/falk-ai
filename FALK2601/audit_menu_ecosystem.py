import os
import re

print("=== AUDITERAR MENY-EKOSYSTEMETS ALLA FILER ===\n")

# 1. Hitta alla HTML- och JS-filer i projektet
project_files = []
for root, dirs, files in os.walk("."):
    # Ignorera venv och git
    if "venv" in root or ".git" in root or "node_modules" in root:
        continue
    for f in files:
        if f.endswith(".html") or f.endswith(".js"):
            project_files.append(os.path.join(root, f))

print(f"-> Hittade {len(project_files)} relevanta källfiler i projektet.\n")

# 2. Sök efter Meny-relaterade ID:n och Funktioner i varje fil
for filepath in sorted(project_files):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    drawer_ids = re.findall(r'id=["\']([^"\']*drawer[^"\']*|[^"\']*menu[^"\']*|[^"\']*sidebar[^"\']*)["\']', content, re.I)
    click_handlers = re.findall(r'onclick=["\']([^"\']+)["\']', content, re.I)
    window_funcs = re.findall(r'window\.([a-zA-Z0-9_]+)\s*=', content)

    if drawer_ids or any("Menu" in c or "Sidebar" in c for c in click_handlers) or any("Menu" in w or "Sidebar" in w for w in window_funcs):
        print(f"==================================================")
        print(f"FIL: {filepath}")
        if drawer_ids:
            print(f"  - Funna ID-namn: {set(drawer_ids)}")
        if click_handlers:
            menu_clicks = [c for c in click_handlers if "menu" in c.lower() or "sidebar" in c.lower() or "falk" in c.lower()]
            if menu_clicks:
                print(f"  - Onclick-anrop i HTML: {set(menu_clicks)}")
        if window_funcs:
            menu_funcs = [w for w in window_funcs if "menu" in w.lower() or "sidebar" in w.lower() or "falk" in w.lower()]
            if menu_funcs:
                print(f"  - Exporterade JS-funktioner: {set(menu_funcs)}")
        print(f"==================================================\n")

print("=== AUDITERING SLUTFÖRD ===")
