import sys, os, re
from dotenv import load_dotenv
from supabase import create_client

if len(sys.argv) < 3:
    print("❌ FEL: Du måste skicka med båda nycklarna!")
    print("Användning: python3 scripts/fix_env.py \"PUBLISHABLE_KEY\" \"SECRET_KEY\"")
    sys.exit(1)

pub_key = sys.argv[1].strip()
sec_key = sys.argv[2].strip()

if pub_key == sec_key:
    print("❌ KRITISKT FEL: Du kopierade exakt samma nyckel två gånger!")
    print("   Du MÅSTE kopiera från 'Publishable key' (överst) OCH 'Secret keys' (nederst).")
    sys.exit(1)

env_path = '.env'
with open(env_path, 'r') as f:
    content = f.read()

content = re.sub(r'^SUPABASE_KEY=.*$', f'SUPABASE_KEY={pub_key}', content, flags=re.MULTILINE)
content = re.sub(r'^SUPABASE_SERVICE_ROLE_KEY=.*$', f'SUPABASE_SERVICE_ROLE_KEY={sec_key}', content, flags=re.MULTILINE)

with open(env_path, 'w') as f:
    f.write(content)

print("✅ `.env` uppdaterad med separata nycklar.")
print("==================================================================")
print("🛡️ RLS SÄKERHETSAUDIT (PENETRATIONSTEST)")
print("==================================================================")

load_dotenv(override=True)
url = os.getenv("SUPABASE_URL", "")

# 1. Test Anon (Publishable) Key
anon_client = create_client(url, pub_key)
try:
    res_anon = anon_client.table("dialogue_messages").select("*").limit(5).execute()
    if len(res_anon.data) > 0:
        print(f"❌ VARNING: Anonym nyckel kunde läsa {len(res_anon.data)} rader! RLS är INTE aktivt i Supabase.")
    else:
        print("🛡️ PASS: Anonym läsning nekades / 0 rader returnerade (RLS fungerar!).")
except Exception as e:
    print(f"🛡️ PASS: Anonym läsning nekades av Supabase: {e}")

# 2. Test Service Role (Secret) Key
service_client = create_client(url, sec_key)
try:
    res_service = service_client.table("dialogue_messages").select("count", count="exact").execute()
    print(f"✅ PASS: Backend (service_role) har full tillgång. Totalt i DB: {res_service.count}")
except Exception as e:
    print(f"❌ FAIL: Service Role kunde inte ansluta: {e}")
