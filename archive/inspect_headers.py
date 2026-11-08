import subprocess
import re

print("=== SKRIVSKYDDAD INSPEKTION AV ALLA HISTORISKA HEADERS ===\n")

try:
    log_output = subprocess.check_output(
        ["git", "log", "--oneline", "-n", "25", "--", "templates/index.html"]
    ).decode("utf-8").strip()

    commits = [line.split()[0] for line in log_output.split("\n") if line]
    seen_headers = {}

    for commit in commits:
        try:
            content = subprocess.check_output(
                ["git", "show", f"{commit}:templates/index.html"]
            ).decode("utf-8", errors="ignore")

            header_match = re.search(r'(<header[\s\S]*?</header>)', content, re.IGNORECASE)
            if header_match:
                header_code = header_match.group(1).strip()
                if header_code not in seen_headers:
                    seen_headers[header_code] = commit

        except Exception:
            continue

    print(f"Hittade {len(seen_headers)} UNIKA header-varianter i projektets historik:\n")

    for idx, (code, commit) in enumerate(seen_headers.items()):
        print(f"==================== VARIANT [{idx}] (Commit: {commit}) ====================")
        print(code[:600] + ("\n... [avhuggen för överskådlighet]" if len(code) > 600 else ""))
        print("========================================================================\n")

except Exception as e:
    print("Fel vid sökning:", e)
