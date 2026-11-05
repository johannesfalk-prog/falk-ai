import subprocess
import re

print("=== APPLICERAR ENBART HEADER VARIANT 1 ===")

target_file = "templates/index.html"

try:
    # 1. Hämta historik över templates/index.html
    log_output = subprocess.check_output(
        ["git", "log", "--oneline", "-n", "25", "--", "templates/index.html"]
    ).decode("utf-8").strip()

    commits = [line.split()[0] for line in log_output.split("\n") if line]
    seen_headers = []

    for commit in commits:
        try:
            content = subprocess.check_output(
                ["git", "show", f"{commit}:templates/index.html"]
            ).decode("utf-8", errors="ignore")
            
            header_match = re.search(r'(<header[\s\S]*?</header>)', content, re.IGNORECASE)
            if header_match:
                h_code = header_match.group(1).strip()
                # Lägg bara till om det är en ny unik header-kod
                if h_code not in [h[0] for h in seen_headers]:
                    seen_headers.append((h_code, commit))
        except Exception:
            continue

    if len(seen_headers) < 2:
        print("[WARN] Mindre än 2 unika headervarianter hittades i historiken. Använder den som finns.")
        variant_1_header, variant_1_commit = seen_headers[0]
    else:
        variant_1_header, variant_1_commit = seen_headers[1]

    print(f"Hittade Variant 1 i commit {variant_1_commit}.")

    # 2. Läs in nuvarande fil på disken
    with open(target_file, "r", encoding="utf-8") as f:
        current_html = f.read()

    # 3. Ersätt ENBART <header>...</header>
    if re.search(r'<header[\s\S]*?</header>', current_html, re.IGNORECASE):
        new_html = re.sub(r'<header[\s\S]*?</header>', variant_1_header, current_html, count=1, flags=re.IGNORECASE)
    else:
        new_html = re.sub(r'(<body[^>]*>)', r'\1\n' + variant_1_header, current_html, count=1, flags=re.IGNORECASE)

    # 4. Spara filen
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(new_html)

    print(f"-> [SUCCESS] Enbart <header> har ersatts med Variant 1 (Commit: {variant_1_commit}). Övrig kod helt orörd!")

except Exception as e:
    print(f"[CRITICAL ERROR] Åtgärden misslyckades: {e}")
