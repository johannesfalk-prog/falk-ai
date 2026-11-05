import os
import subprocess
import shutil

print("=== INITIERAR PERMANENT LÅSNING AV CHECKPOINT: FALK2602 ===")

# 1. FYSISK KOPIERING AV ALLA TEMPLATES OCH APP.PY
backup_dir = "backups_FALK2602"
os.makedirs(backup_dir, exist_ok=True)

files_to_backup = [
    "app.py",
    os.path.join("templates", "index.html"),
    os.path.join("templates", "bibliotek.html"),
    os.path.join("templates", "utveckling.html"),
    os.path.join("templates", "installningar.html")
]

for file_path in files_to_backup:
    if os.path.exists(file_path):
        dest_path = os.path.join(backup_dir, os.path.basename(file_path) + ".FALK2602")
        shutil.copyfile(file_path, dest_path)
        print(f"-> [FYSISK BACKUP OK] {file_path} -> {dest_path}")

# 2. GIT COMMIT, BRANCH OCH TAGG (FALK2602)
try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "LOCK: FALK2602 - Complete solid UI, restore all icons, subpages, dashboard replication & widget filters"], check=True)
    print("-> [GIT COMMIT OK] Alla ändringar committade till Git.")
except subprocess.CalledProcessError:
    print("-> [GIT NOTICE] Inga nya ändringar att committa, låser befintligt tillstånd.")

# Skapa/uppdatera branchen och taggen FALK2602
subprocess.run(["git", "branch", "-M", "FALK2602"])
subprocess.run(["git", "tag", "-f", "FALK2602"])

print("\n==================================================")
print("  CHECKPOINT 'FALK2602' ÄR NU PERMANENT LÅSD OCH SÄKRAD!")
print("  Återställ när som helst via: git checkout FALK2602")
print("==================================================")
