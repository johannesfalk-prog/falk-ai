import os
import subprocess
import shutil

print("=== SKRIVER ÖVER OCH LÅSER CHECKPOINT: FALK2601 ===")

backup_dir = "backups_FALK2601"
if os.path.exists(backup_dir):
    shutil.rmtree(backup_dir)
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
        dest_path = os.path.join(backup_dir, os.path.basename(file_path))
        shutil.copyfile(file_path, dest_path)
        print(f"-> [FYSISK BACKUP OVERWRITTEN] {file_path} -> {dest_path}")

try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "OVERWRITE BACKUP: FALK2601 - Complete 15 exercise cards with category filtering and locked UI"], check=True)
except Exception:
    print("-> [GIT NOTICE] Ändringar finns redan registrerade i commit-historiken.")

# Tvinga överskrivning av gren och tagg FALK2601
subprocess.run(["git", "branch", "-M", "FALK2601"], check=True)
subprocess.run(["git", "tag", "-f", "FALK2601"], check=True)

print("\n==================================================")
print("  CHECKPOINT 'FALK2601' ÄR NU SKRIVEN ÖVER OCH LÅSD!")
print("==================================================")
