import requests

BASE_URL = "http://127.0.0.1:5001"
session = requests.Session()

print("==================================================")
print("🦅 TESTAR UI & TÄNKANDE TILLSTÅND (PORT 5001)")
print("==================================================\n")

# 1. Verifiera att HTML innehåller "Falk tänker..."
r_index = session.get(f"{BASE_URL}/")
assert "Falk tänker..." in r_index.text, "❌ UI saknar 'Falk tänker...'-indikatorn!"
print("✅ [PASS] Gränssnittet innehåller 'Falk tänker...'")

# 2. Skicka testmeddelande
session.post(f"{BASE_URL}/api/gdpr/consent", json={"is_18_plus": True})
r_chat = session.post(f"{BASE_URL}/api/chat", json={"message": "Jag vet inte vilken riktning jag ska välja i min karriär."}).json()

assert "response" in r_chat, "❌ Inget svar från Falk!"
print(f"🦅 Falks svar efter tänkandet:\n{r_chat['response']}\n")

print("🏆 [ALL PASS] Tänkande-status och UI-integration verifierad!")
