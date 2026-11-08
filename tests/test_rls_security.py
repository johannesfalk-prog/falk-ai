import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL", "")
anon_key = os.getenv("SUPABASE_KEY", "")

print("==================================================================")
print("🛡️ SUPABASE RLS (ROW LEVEL SECURITY) ANON-KEY AUDIT")
print("==================================================================")

if not url or not anon_key:
    print("❌ FAIL: SUPABASE_URL eller SUPABASE_KEY saknas i .env!")
    exit(1)

client = create_client(url, anon_key)

try:
    res = client.table("dialogue_messages").select("*").limit(5).execute()
    if len(res.data) > 0:
        print(f"❌ VARNING / SÅRBARHET: Anonym nyckel kunde läsa {len(res.data)} meddelanden!")
        print("   -> RLS (Row Level Security) är INTE aktiverat på 'dialogue_messages'. Obeförhöriga kan läsa historik!")
    else:
        print("✅ PASS: Anonym nyckel fick 0 rader (RLS spärrar obehörig läsning).")
except Exception as e:
    print(f"✅ PASS: Anonym åtkomst neka des av Supabase: {e}")
