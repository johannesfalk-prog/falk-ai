import requests

BASE_URL = "http://127.0.0.1:5001"
session = requests.Session()

print("==================================================")
print("⚔️ STRESSTEST: GÄSTGRÄNS & KONVERTERINGSSPÄRR (MAX 6)")
print("==================================================\n")

# 1. GDPR Consent
session.post(f"{BASE_URL}/api/gdpr/consent", json={"is_18_plus": True})

# 2. Skicka 6 meddelanden i rad som gäst
for i in range(1, 7):
    msg = f"Detta är gästmeddelande nummer {i} om min situation."
    res = session.post(f"{BASE_URL}/api/chat", json={"message": msg})
    data = res.json()
    left = data.get("guest_messages_left", 0)
    print(f"💬 Meddelande {i}/6 skickat. Status: {res.status_code}. Meddelanden kvar: {left}")
    assert res.status_code == 200, f"❌ Meddelande {i} misslyckades oväntat!"

# 3. Försök skicka det 7:e meddelandet (Ska spärras)
msg_7 = "Detta är meddelande 7 som ska stoppas av konverteringsväggen."
res_7 = session.post(f"{BASE_URL}/api/chat", json={"message": msg_7})
data_7 = res_7.json()

print(f"\n🛑 Meddelande 7 skickat. Statuskod: {res_7.status_code}")
print(f"🦅 Falks konverteringssvar:\n{data_7.get('response')}\n")

assert res_7.status_code == 402, f"❌ [FAIL] Meddelande 7 spärrades inte! Status: {res_7.status_code}"
assert data_7.get("limit_reached") == True, "❌ [FAIL] limit_reached flagga saknas i svaret!"

print("🏆 [ALL PASS] Gästgränsen på 6 meddelanden är 100% verifierad och skottsäker!")
