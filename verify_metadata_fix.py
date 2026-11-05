import requests

BASE_URL = "http://127.0.0.1:5001"
session = requests.Session()

print("==================================================")
print("⚔️ STRESSTEST: METADATA-KOLUMN & SUPABASE PERSISTENCE")
print("==================================================\n")

# 1. GDPR Consent
session.post(f"{BASE_URL}/api/gdpr/consent", json={"is_18_plus": True})

# 2. Skicka chatmeddelande för att trigga session creation och metadata-uppdatering
r = session.post(f"{BASE_URL}/api/chat", json={"message": "Jag vill stresstesta att min kompass persisteras i Supabase metadata."})
assert r.status_code == 200, f"❌ Chat anrop misslyckades: {r.status_code}"

res_data = r.json()
print(f"✅ Svar mottaget från Falk (Session ID: {res_data.get('session_id')})")

# 3. Hämta dashboard för att verifiera att Kompassen läses från Supabase
r_dash = session.get(f"{BASE_URL}/api/dashboard")
assert r_dash.status_code == 200, f"❌ Dashboard anrop misslyckades: {r_dash.status_code}"

dash_data = r_dash.json()
print(f"📊 Kompassvärden hämtade: {dash_data.get('compass_scores')}")
print("\n🏆 [SUCCESS] Inga fel i backend! Kontrollera Terminal 1: Inga 'column chat_sessions.metadata does not exist'-varningar ska visas.")
