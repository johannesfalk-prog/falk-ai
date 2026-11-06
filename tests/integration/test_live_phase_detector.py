import requests
import time
import sys

RENDER_URL = "https://falk-backend.onrender.com"
session = requests.Session()

print("==================================================================")
print("⚔️  LIVE E2E STRESSTEST: AUTOMATISK 7-FASDETEKTOR")
print(f"🌍 Mål-URL: {RENDER_URL}")
print("==================================================================\n")

# 1. Warmup för Cold Start
print("🔄 Steg 1: Värmer upp Render-instansen...")
try:
    r_warm = session.get(f"{RENDER_URL}/", timeout=60)
    assert r_warm.status_code == 200, f"Server gav status {r_warm.status_code}"
    print("✅ Server online.")
except Exception as e:
    print(f"❌ KONTROLL MISSLYCKADES: Kan inte nå Render. Fel: {e}")
    sys.exit(1)

# 2. GDPR Samtycke
print("\n🔒 Steg 2: Registrerar GDPR-samtycke...")
r_gdpr = session.post(f"{RENDER_URL}/api/gdpr/consent", json={"is_18_plus": True})
assert r_gdpr.status_code == 200, "GDPR misslyckades"

# 3. Test av Fas-detektion i ett stressat ingångsmeddelande (Förväntad Fas 1: Trygghet)
print("\n⚡ Steg 3: Skickar initialt stress-meddelande (Förväntad Fas 1 eller 2)...")
msg_1 = "Jag känner mig helt överväldigad av jobb och beslut. Vet inte var jag ska börja."
r_chat1 = session.post(f"{RENDER_URL}/api/chat", json={"message": msg_1})

assert r_chat1.status_code == 200, f"Chat-anrop misslyckades: {r_chat1.status_code}"
data1 = r_chat1.json()

phase1 = data1.get("current_phase")
resp1 = data1.get("response", "")

print(f"📡 Detekterad Fas: {phase1}")
print(f"🦅 Falks Svar:\n\"{resp1}\"\n")

assert phase1 is not None, "❌ 'current_phase' saknas i JSON-responsen!"
assert "Du borde" not in resp1, "❌ Guardrail-överträdelse: Innehåller 'Du borde'"
assert "!" not in resp1, "❌ Guardrail-överträdelse: Innehåller utropstecken"
assert "?" in resp1, "❌ Guardrail-överträdelse: Saknar reflektionsfråga"
print("✅ [PASS] Meddelande 1 detekterat och guardrails verifierade.")

# 4. Test av Fas-detektion vid reflektionsmeddelande (Förväntad Fas 3/4/5)
print("\n⚡ Steg 4: Skickar reflektivt meddelande för att testa fasskifte...")
msg_2 = "När jag tänker efter handlar det om att jag har svårt att sätta gränser och säga nej till min chef."
r_chat2 = session.post(f"{RENDER_URL}/api/chat", json={"message": msg_2, "session_id": data1.get("session_id")})

assert r_chat2.status_code == 200, f"Chat-anrop 2 misslyckades: {r_chat2.status_code}"
data2 = r_chat2.json()

phase2 = data2.get("current_phase")
resp2 = data2.get("response", "")

print(f"📡 Detekterad Fas: {phase2}")
print(f"🦅 Falks Svar:\n\"{resp2}\"\n")

assert phase2 is not None, "❌ 'current_phase' saknas i JSON-responsen för meddelande 2!"
assert "Du borde" not in resp2, "❌ Guardrail-överträdelse i meddelande 2"
assert "!" not in resp2, "❌ Guardrail-överträdelse i meddelande 2"
assert "?" in resp2, "❌ Guardrail-överträdelse i meddelande 2"
print("✅ [PASS] Meddelande 2 genomfört med aktiv fasdetektion.")

print("\n==================================================================")
print("🏆 [ALL PASS] Den automatiska Fas-detektorn lever på Render!")
print("==================================================================")
