import os
import shutil
import zipfile
from datetime import datetime

backup_name = "FALK2601"
zip_filename = f"{backup_name}.zip"
folder_filename = backup_name

print(f"=== SKAPAR SÄKERHETSKOPIA: {backup_name} ===")

# 1. Rensa tidigare backup om den existerar (överskrivning)
if os.path.exists(zip_filename):
    os.remove(zip_filename)
    print(f"-> Skrev över tidigare arkiv: {zip_filename}")

if os.path.exists(folder_filename):
    shutil.rmtree(folder_filename)
    print(f"-> Skrev över tidigare mapp: {folder_filename}")

# 2. Kopiera projektfiler (exkludera virtuella miljöer och temp-filer)
ignore_patterns = shutil.ignore_patterns('__pycache__', '*.pyc', '.git', 'venv', '.env', 'FALK26*', 'backup*')
shutil.copytree('.', folder_filename, ignore=ignore_patterns)

# 3. Komprimera till ZIP
with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(folder_filename):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, folder_filename)
            zipf.write(file_path, arcname)

print(f"-> [SUCCESS] Säkerhetskopia fullbordad: '{zip_filename}' och mappen '{folder_filename}/'")
print(f"-> Tidsstämpel: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
