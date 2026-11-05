import subprocess
import re

print("=== APPLICERAR ENBART HEADER VARIANT 0 ===")

target_file = "templates/index.html"

# 1. Hämta första historiska headern (Variant 0) ur Git
try:
    log_output = subprocess.check_output(
        ["git", "log", "--oneline", "-n", "25", "--", "templates/index.html"]
    ).decode("utf-8").strip()

    commits = [line.split()[0] for line in log_output.split("\n") if line]
    variant_0_header = None
    variant_0_commit = None

    for commit in commits:
        try:
            content = subprocess.check_output(
                ["git", "show", f"{commit}:templates/index.html"]
            ).decode("utf-8", errors="ignore")
            
            header_match = re.search(r'(<header[\s\S]*?</header>)', content, re.IGNORECASE)
            if header_match:
                variant_0_header = header_match.group(1)
                variant_0_commit = commit
                break
        except Exception:
            continue

    if not variant_0_header:
        print("[ERROR] Kunde inte hitta någon giltig header i Git-historiken.")
        exit(1)

    print(f"Hittade Variant 0 i commit {variant_0_commit}.")

    # 2. Läs in nuvarande fil på disken
    with open(target_file, "r", encoding="utf-8") as f:
        current_html = f.read()

    # 3. Ersätt ENBART <header>...</header>
    if re.search(r'<header[\s\S]*?</header>', current_html, re.IGNORECASE):
        new_html = re.sub(r'<header[\s\S]*?</header>', variant_0_header, current_html, count=1, flags=re.IGNORECASE)
    else:
        # Fallback om <header> saknades helt i målfilen
        new_html = re.sub(r'(<body[^>]*>)', r'\1\n' + variant_0_header, current_html, count=1, flags=re.IGNORECASE)

    # 4. Spara filen
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(new_html)

    print(f"-> [SUCCESS] Enbart <header> har ersatts med Variant 0 ({variant_0_commit}). Övrig kod orörd!")

except Exception as e:
    print(f"[CRITICAL ERROR] Åtgärden misslyckades: {e}")
