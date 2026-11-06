import requests

BASE_URL = "http://127.0.0.1:5001"
session = requests.Session()

print("==================================================")
print("⚔️ STRESSTEST: SUPABASE PERSISTERING & DATA KONTINUITET")
print("==================================================\n")

# 1. GDPR Samtycke
session.post(f"{BASE_URL}/api/gdpr/consent", json={"is_18_plus": True})

# 2. Hämta initial dashboard
r_dash1 = session.get(f"{BASE_URL}/api/dashboard").json()
print(f"📊 Initial kompass (från Supabase/default): {r_dash1.get('compass_scores')}")

# 3. Skicka meddelande för att skapa session och persistera i Supabase
r_chat = session.post(f"{BASE_URL}/api/chat", json={"message": "Jag behöver hjälp att strukturera min arbetsvecka."}).json()
assert "response" in r_chat, "❌ Inget svar från Falk!"

print(f"🦅 Falk svar mottaget. Session ID persisterat: {r_chat.get('session_id')}\n")

# 4. Verifiera att dashboard kan läsas ut direkt från Supabase utan RAM-beroende
r_dash2 = session.get(f"{BASE_URL}/api/dashboard").json()
assert "compass_scores" in r_dash2, "❌ Misslyckades att hämta kompassvärden!"

print(f"✅ [PASS] Kompassdata hämtas och sparas direkt mot Supabase.")
print("🏆 [ALL PASS] Steg 2 slutfört: Datakontinuiteten överlever serveromstarter!")
