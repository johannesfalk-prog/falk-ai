import os
import shutil
import zipfile
from datetime import datetime

backup_name = "FALK26"
zip_filename = f"{backup_name}.zip"
folder_filename = backup_name

print(f"=== SKAPAR NULÄGESBACKUP: {backup_name} ===")

# 1. Om mappen eller zip-filen finns sedan tidigare, ta bort och skriv över
if os.path.exists(zip_filename):
    os.remove(zip_filename)
    print(f"-> Raderade tidigare arkiv: {zip_filename}")

if os.path.exists(folder_filename):
    shutil.rmtree(folder_filename)
    print(f"-> Raderade tidigare backup-mapp: {folder_filename}")

# 2. Skapa ny backup-mapp och kopiera relevanta projektfiler
ignore_patterns = shutil.ignore_patterns('__pycache__', '*.pyc', '.git', 'venv', '.env', 'FALK26*', 'backup*')
shutil.copytree('.', folder_filename, ignore=ignore_patterns)

# 3. Komprimera mappen till FALK26.zip
with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(folder_filename):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, folder_filename)
            zipf.write(file_path, arcname)

print(f"-> [SUCCESS] Backup skapad: Mapp '{folder_filename}/' samt arkiv '{zip_filename}'")
print(f"-> Tidsstämpel: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
