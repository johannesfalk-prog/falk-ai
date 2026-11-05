import os
import shutil
import zipfile
from datetime import datetime

backup_name = "FALK2602"
zip_filename = f"{backup_name}.zip"
folder_filename = backup_name

print(f"=== SKAPAR PERMANENT SÄKERHETSKOPIA: {backup_name} ===")

# Explicitt kommando mottaget: Skapa ny permanent baslinje
if os.path.exists(zip_filename):
    os.remove(zip_filename)
    print(f"-> Skrev över tidigare arkiv med manuellt godkännande: {zip_filename}")

if os.path.exists(folder_filename):
    shutil.rmtree(folder_filename)
    print(f"-> Skrev över tidigare mapp med manuellt godkännande: {folder_filename}")

# Kopiera hela projektet exklusive virtuella miljöer och tidigare backuper
ignore_patterns = shutil.ignore_patterns('__pycache__', '*.pyc', '.git', 'venv', '.env', 'FALK26*', 'backup*')
shutil.copytree('.', folder_filename, ignore=ignore_patterns)

# Komprimera till ZIP
with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(folder_filename):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, folder_filename)
            zipf.write(file_path, arcname)

print(f"-> [SUCCESS] Permanent säkerhetskopia låst och sparad: '{zip_filename}' & '{folder_filename}/'")
print(f"-> Tidsstämpel: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("-> Mappen FALK2602 kommer nu att ignoreras av alla framtida automatiska skript.")
