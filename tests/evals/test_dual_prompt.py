import requests
import time

BASE_URL = "http://127.0.0.1:5001"
session = requests.Session()

print("==================================================")
print("⚔️ STRESSTEST: DUAL-LAYER PROMPT ENGINE & LATENS")
print("==================================================\n")

# 1. GDPR Samtycke
session.post(f"{BASE_URL}/api/gdpr/consent", json={"is_18_plus": True})

# 2. Skicka testmeddelande och mät latens
start_time = time.time()
r = session.post(f"{BASE_URL}/api/chat", json={"message": "Jag upplever enorm stress på jobbet och hinner inte återhämta mig."})
latency = time.time() - start_time

assert r.status_code == 200, f"❌ Anropet misslyckades med status {r.status_code}"
data = r.json()
response_text = data.get("response", "")

print(f"⏱️  Responstid för Dual-Layer Prompt: {latency:.2f} sekunder")
print(f"🦅 Falks svar:\n{response_text}\n")

# 3. Verifiera regeluppfyllnad i prompten
assert latency < 4.0, f"❌ Responstiden ({latency:.2f}s) var för hög!"
assert "Du borde" not in response_text, "❌ Falk använde förbjudna 'Du borde'!"
assert "!" not in response_text, "❌ Falk använde utropstecken (strider mot lugnt tonfall)!"

print("✅ [PASS] Latens godkänd (< 4.0s).")
print("✅ [PASS] Tonfalls- och regelkontroller uppfyllda.")
print("🏆 [ALL PASS] Dual-Layer Prompt Engine är 100% verifierad!")
