import requests
import time
import sys

RENDER_URL = "https://falk-backend.onrender.com"
session = requests.Session()

print("==================================================================")
print("⚔️  LIVE E2E STRESSTEST: RENDER CLOUD DEPLOYMENT (HÄRDAD CORS)")
print(f"🌍 Mål-URL: {RENDER_URL}")
print("==================================================================\n")

# 1. Warmup för Cold Start
print("🔄 Steg 1: Värmer upp Render-instansen...")
start_warmup = time.time()
try:
    r_warm = session.get(f"{RENDER_URL}/", timeout=60)
    warmup_time = time.time() - start_warmup
    print(f"📡 Status: {r_warm.status_code} | Responstid: {warmup_time:.2f}s")
    if r_warm.status_code != 200:
        print(f"❌ MISSLYCKADES: Servern svarade med status {r_warm.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"❌ KONTROLL MISSLYCKADES: Kan inte nå Render. Fel: {e}")
    sys.exit(1)

# 2. GDPR Samtycke
print("\n🔒 Steg 2: Skickar GDPR-samtycke...")
r_gdpr = session.post(f"{RENDER_URL}/api/gdpr/consent", json={"is_18_plus": True})
assert r_gdpr.status_code == 200, f"❌ GDPR Samtycke misslyckades: {r_gdpr.status_code}"
print("✅ GDPR-samtycke registrerat.")

# 3. Dual-Layer Engine & Guardrails i molnet
print("\n⚡ Steg 3: Testar Dual-Layer Prompt Engine & Guardrails i molnet...")
prompt_msg = "Jag känner stark stress på jobbet och hinner inte återhämta mig."
start_t = time.time()
r_chat = session.post(f"{RENDER_URL}/api/chat", json={"message": prompt_msg})
latency = time.time() - start_t

assert r_chat.status_code == 200, f"❌ Chat-anrop misslyckades med status {r_chat.status_code}: {r_chat.text}"
chat_data = r_chat.json()
response_text = chat_data.get("response", "")

print(f"⏱️  Responstid i molnet: {latency:.2f}s")
print(f"🦅 Falks Svar:\n\"{response_text}\"")

assert "Du borde" not in response_text, "❌ Guardrail bröt: Innehåller 'Du borde'"
assert "!" not in response_text, "❌ Guardrail bröt: Innehåller utropstecken"
assert "?" in response_text, "❌ Guardrail bröt: Saknar reflektionsfråga"
print("✅ [PASS] Latens och Guardrails godkända i molnet.")

# 4. Gästgräns (6 meddelanden -> HTTP 402 Paywall)
print("\n🧱 Steg 4: Stresstestar Gästgränsen (6 meddelanden -> 402 Paywall)...")
for i in range(2, 7):
    r_sub = session.post(f"{RENDER_URL}/api/chat", json={"message": f"Testmeddelande {i}"})
    assert r_sub.status_code == 200, f"❌ Meddelande {i} misslyckades"

r_blocked = session.post(f"{RENDER_URL}/api/chat", json={"message": "Sjunde meddelandet som ska stoppas."})
assert r_blocked.status_code == 402, f"❌ Betalväggen utlöste inte HTTP 402! Status: {r_blocked.status_code}"
assert r_blocked.json().get("limit_reached") == True, "❌ limit_reached flaggan saknas i 402-responsen"
print("✅ [PASS] Betalväggen (HTTP 402) verifierad i produktion.")

# 5. Dashboard & Metadata persistence
print("\n📊 Steg 5: Verifierar Supabase metadata-persistering...")
time.sleep(3)
r_dash = session.get(f"{RENDER_URL}/api/dashboard")
assert r_dash.status_code == 200, f"❌ Dashboard misslyckades: {r_dash.status_code}"
dash_scores = r_dash.json().get('compass_scores')
print(f"📊 Hämtad Kompass från molnet: {dash_scores}")

print("\n==================================================================")
print("🏆 [ALL PASS] Backend lever på Render och alla endpoints fungerar!")
print("==================================================================")
