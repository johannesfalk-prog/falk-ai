import sys
import os
import re
from dotenv import load_dotenv
from supabase import create_client

if len(sys.argv) < 3:
    print("❌ FEL: Du måste skicka med båda nycklarna som argument!")
    print("Användning: python3 scripts/set_keys.py \"ANON_KEY\" \"SERVICE_ROLE_KEY\"")
    sys.exit(1)

anon_key = sys.argv[1].strip()
service_key = sys.argv[2].strip()

if not anon_key.startswith("ey") or not service_key.startswith("ey"):
    print("❌ FEL: En eller båda nycklarna har felaktigt format (måste börja på 'ey').")
    sys.exit(1)

if anon_key == service_key:
    print("❌ KRITISKT FEL: Du har matat in exakt samma nyckel för båda!")
    print("   Du MÅSTE hämta två OLIKA nycklar från Supabase Dashboard.")
    sys.exit(1)

env_path = '.env'
with open(env_path, 'r') as f:
    content = f.read()

content = re.sub(r'^SUPABASE_KEY=.*$', f'SUPABASE_KEY={anon_key}', content, flags=re.MULTILINE)
content = re.sub(r'^SUPABASE_SERVICE_ROLE_KEY=.*$', f'SUPABASE_SERVICE_ROLE_KEY={service_key}', content, flags=re.MULTILINE)

with open(env_path, 'w') as f:
    f.write(content)

print("✅ `.env` har skrivits om och sparats med två unika nycklar.")
print("\n------------------------------------------------------------------")
print("🛡️ KÖR OMEDELBAR RLS-SÄKERHETSKONTROLL")
print("------------------------------------------------------------------")

load_dotenv(override=True)
url = os.getenv("SUPABASE_URL", "")

# 1. Test Anon Access
anon_client = create_client(url, anon_key)
try:
    res_anon = anon_client.table("dialogue_messages").select("*").limit(5).execute()
    if len(res_anon.data) > 0:
        print(f"❌ VARNING / SÅRBARHET: Anonym nyckel kunde läsa {len(res_anon.data)} meddelanden!")
        print("   -> RLS spärrar INTE anonym läsning i Supabase!")
    else:
        print("🛡️ PASS: Anonym nyckel fick 0 rader (RLS fungerar!).")
except Exception as e:
    print(f"🛡️ PASS: Anonym läsning nekades av Supabase: {e}")

# 2. Test Service Role Access
service_client = create_client(url, service_key)
try:
    res_service = service_client.table("dialogue_messages").select("count", count="exact").execute()
    print(f"✅ PASS: Service Role (Backend) har full tillgång. Totalt i DB: {res_service.count}")
except Exception as e:
    print(f"❌ FAIL: Service Role kunde inte ansluta: {e}")
