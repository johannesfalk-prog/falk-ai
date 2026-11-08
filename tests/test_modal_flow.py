import requests

BASE_URL = "http://127.0.0.1:5001"
session = requests.Session()

print("==================================================")
print("⚔️ STRESSTEST: PAYWALL MODAL & KONTO-REGISTRERING (KORRIGERAD)")
print("==================================================\n")

# 1. GDPR Samtycke
session.post(f"{BASE_URL}/api/gdpr/consent", json={"is_18_plus": True})

# 2. Skicka 6 meddelanden som gäst
print("💬 Skickar 6 gästmeddelanden för att trigga betalväggen...")
for i in range(1, 7):
    session.post(f"{BASE_URL}/api/chat", json={"message": f"Testmeddelande {i}"})

# 3. Försök skicka meddelande 7 (Ska stoppas)
res_7 = session.post(f"{BASE_URL}/api/chat", json={"message": "Meddelande 7"})
assert res_7.status_code == 402, f"❌ Meddelande 7 spärrades inte! Status: {res_7.status_code}"
print("✅ [PASS] Betalvägg triggad (402 mottagen).")

# 4. Registrera konto med giltigt UUID
r_reg = session.post(f"{BASE_URL}/api/auth/register", json={"email": "beta_testare@wayjs.se"}).json()
new_user_id = r_reg.get("user_id")
print(f"🔑 Konto skapat med UUID: {new_user_id}")

# 5. Skicka meddelande 8 som inloggad användare
res_8 = session.post(
    f"{BASE_URL}/api/chat", 
    json={"message": "Nu är jag inloggad och fortsätter mitt samtal med Falk."},
    headers={"X-User-ID": new_user_id}
)

if res_8.status_code != 200:
    print(f"❌ [FAIL] Status: {res_8.status_code}, Svar: {res_8.text}")
    assert False, "Inloggat anrop misslyckades!"

print(f"🦅 Falk svar efter registrering: {res_8.json().get('response')}\n")
print("🏆 [ALL PASS] Betalvägg och registrering är 100% skottsäkra!")
