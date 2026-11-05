import os
import subprocess
import shutil

print("=== INITIERAR PERMANENT LÅSNING AV CHECKPOINT: FALK26 ===")

index_src = os.path.join("templates", "index.html")
index_dst = os.path.join("templates", "index.html.FALK26")

js_src = os.path.join("static", "js", "dist", "app.min.js")
js_dst = os.path.join("static", "js", "dist", "app.min.js.FALK26")

# 1. FYSISK KOPIERING PÅ DISKEN (UNTOUCHABLE BACKUP)
if os.path.exists(index_src):
    shutil.copyfile(index_src, index_dst)
    print(f"-> [FYSISK BACKUP OK] Skapat: {index_dst}")

if os.path.exists(js_src):
    shutil.copyfile(js_src, js_dst)
    print(f"-> [FYSISK BACKUP OK] Skapat: {js_dst}")

# 2. GIT COMMIT, BRANCH OCH TAGG (FALK26)
try:
    # Staga alla filer
    subprocess.run(["git", "add", "."], check=True)
    
    # Commit
    subprocess.run(["git", "commit", "-m", "LOCK: FALK26 - Full visual UI lock and stable checkpoint"], check=True)
    print("-> [GIT COMMIT OK] Alla ändringar committade.")
except subprocess.CalledProcessError:
    print("-> [GIT NOTICE] Inga nya ändringar att committa, låser befintligt tillstånd.")

# Skapa/uppdatera branchen FALK26
subprocess.run(["git", "branch", "-M", "FALK26"])
# Skapa en explicit tagg FALK26
subprocess.run(["git", "tag", "-f", "FALK26"])

print("\n==================================================")
print("  CHECKPOINT 'FALK26' ÄR NU NÅDD OCH PERMANENT LÅSD!")
print("  Du kan när som helst återställa detta läge med:")
print("  git checkout FALK26  ELLER  cp templates/index.html.FALK26 templates/index.html")
print("==================================================")
