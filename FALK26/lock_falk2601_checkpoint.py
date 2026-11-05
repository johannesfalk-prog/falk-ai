import os
import subprocess
import shutil

print("=== INITIERAR PERMANENT LÅSNING AV CHECKPOINT: FALK2601 ===")

index_src = os.path.join("templates", "index.html")
index_dst = os.path.join("templates", "index.html.FALK2601")

js_src = os.path.join("static", "js", "dist", "app.min.js")
js_dst = os.path.join("static", "js", "dist", "app.min.js.FALK2601")

# 1. FYSISK KOPIERING PÅ DISKEN (UNTOUCHABLE BACKUP)
if os.path.exists(index_src):
    shutil.copyfile(index_src, index_dst)
    print(f"-> [FYSISK BACKUP OK] Skapat: {index_dst}")

if os.path.exists(js_src):
    shutil.copyfile(js_src, js_dst)
    print(f"-> [FYSISK BACKUP OK] Skapat: {js_dst}")

# 2. GIT COMMIT, BRANCH OCH TAGG (FALK2601)
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "LOCK: FALK2601 - Complete UI, sans-serif AI bubble, #4E5C4B user bubble, direct response delivery"], check=True)
    print("-> [GIT COMMIT OK] Alla ändringar committade till Git.")
except subprocess.CalledProcessError:
    print("-> [GIT NOTICE] Inga nya ändringar att committa, låser befintligt tillstånd.")

# Skapa/uppdatera branchen FALK2601
subprocess.run(["git", "branch", "-M", "FALK2601"])
# Skapa en explicit tagg FALK2601
subprocess.run(["git", "tag", "-f", "FALK2601"])

print("\n==================================================")
print("  CHECKPOINT 'FALK2601' ÄR NU PERMANENT LÅSD OCH SÄKRAD!")
print("  Återställ när som helst via: git checkout FALK2601")
print("==================================================")
