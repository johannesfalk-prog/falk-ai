import requests
import time
import sys

RENDER_URL = "https://falk-backend.onrender.com"
session = requests.Session()

print("==================================================================")
print("⚔️  LIVE E2E STRESSTEST: 3-TURS DB-FALLBACK & FASDETEKTERING")
print(f"🌍 Mål-URL: {RENDER_URL}")
print("==================================================================\n")

# 1. Warmup & GDPR
print("🔄 Steg 1: Värmer upp Render-instansen och sätter GDPR...")
try:
    r_warm = session.get(f"{RENDER_URL}/", timeout=60)
    assert r_warm.status_code == 200, f"Server gav status {r_warm.status_code}"
    r_gdpr = session.post(f"{RENDER_URL}/api/gdpr/consent", json={"is_18_plus": True})
    assert r_gdpr.status_code == 200, "GDPR samtycke misslyckades"
    print("✅ Server redo och GDPR samtyckt.\n")
except Exception as e:
    print(f"❌ KONTROLL MISSLYCKADES: {e}")
    sys.exit(1)

# TUR 1: Initial känsla (Förväntad Fas 1 eller 2)
print("💬 TUR 1: Skickar initialt stressmeddelande...")
msg_1 = "Jag känner stark stress på jobbet och hinner inte med återhämtning."
r1 = session.post(f"{RENDER_URL}/api/chat", json={"message": msg_1})
assert r1.status_code == 200, f"Tur 1 misslyckades: {r1.status_code}"
d1 = r1.json()
session_id = d1.get("session_id")
phase_1 = d1.get("current_phase")
resp_1 = d1.get("response", "")

print(f"  - Session ID: {session_id}")
print(f"  - Detekterad Fas: {phase_1}")
print(f"  - Falk: \"{resp_1[:120]}...\"")
assert session_id is not None, "❌ session_id saknas i Tur 1!"
assert phase_1 is not None, "❌ current_phase saknas i Tur 1!"

print("⏳ Väntar 3 sekunder för att låta async bakgrundsarbetare skriva historik till Supabase...")
time.sleep(3)

# TUR 2: Fördjupning (Ingen 'history' i JSON - tvingar DB-fallback)
print("\n💬 TUR 2: Skickar fördjupningsmeddelande (UTAN history-payload, testar DB-fallback)...")
msg_2 = "Jag har försökt prata med min chef men det känns som om ingen lyssnar på vad jag behöver."
r2 = session.post(f"{RENDER_URL}/api/chat", json={
    "message": msg_2,
    "session_id": session_id
    # Medvetet INGEN 'history' här för att verifiera Supabase-fallback!
})
assert r2.status_code == 200, f"Tur 2 misslyckades: {r2.status_code}"
d2 = r2.json()
phase_2 = d2.get("current_phase")
resp_2 = d2.get("response", "")

print(f"  - Detekterad Fas: {phase_2}")
print(f"  - Falk: \"{resp_2[:120]}...\"")
assert phase_2 is not None, "❌ current_phase saknas i Tur 2!"
assert "Du borde" not in resp_2, "❌ Guardrail överträdd i Tur 2"

print("⏳ Väntar 3 sekunder för att persistera Tur 2 i Supabase...")
time.sleep(3)

# TUR 3: Insikt & Vägval (Ska stegra till högre fas och ej fallbaksnolla till Fas 1)
print("\n💬 TUR 3: Skickar insiktsmeddelande (Tvingar fasskifte till Utforskande/Perspektiv)...")
msg_3 = "När jag tänker efter är det nog min egen rädsla för att misslyckas som hindrar mig från att ta ett beslut."
r3 = session.post(f"{RENDER_URL}/api/chat", json={
    "message": msg_3,
    "session_id": session_id
})
assert r3.status_code == 200, f"Tur 3 misslyckades: {r3.status_code}"
d3 = r3.json()
phase_3 = d3.get("current_phase")
resp_3 = d3.get("response", "")

print(f"  - Detekterad Fas: {phase_3}")
print(f"  - Falk: \"{resp_3[:120]}...\"")
assert phase_3 is not None, "❌ current_phase saknas i Tur 3!"
assert "Du borde" not in resp_3 and "!" not in resp_3 and "?" in resp_3, "❌ Guardrails bröt i Tur 3!"

print("\n==================================================================")
print(f"📊 FAS-UTVECKLING ÖVER 3 TURER: Tur 1 (Fas {phase_1}) ➔ Tur 2 (Fas {phase_2}) ➔ Tur 3 (Fas {phase_3})")
if phase_3 > 1:
    print("🏆 [SUCCESS] DB-fallback fungerar och samtalsrytmen stegras utan att nollställas!")
else:
    print("⚠️ [VARNING] Fasen nollställdes till Fas 1 i Tur 3. Kontrollera Supabase-lagringen.")
print("==================================================================")
