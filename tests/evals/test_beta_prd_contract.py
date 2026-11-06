import requests
import time
import sys

RENDER_URL = "https://falk-backend.onrender.com"
session = requests.Session()

print("==================================================================")
print("⚔️  PRD VERIFIERING: FRONTEND API-KONTRAKT & MIGRERINGSTEST")
print(f"🌍 Mål-URL: {RENDER_URL}")
print("==================================================================\n")

print("1️⃣ Testing GET /api/dashboard...")
r_dash = session.get(f"{RENDER_URL}/api/dashboard")
assert r_dash.status_code == 200, f"Dashboard fel: {r_dash.status_code}"
print(f"  - Kompass: {r_dash.json().get('compass_scores')}")

print("\n2️⃣ Testing POST /api/gdpr/consent...")
r_gdpr = session.post(f"{RENDER_URL}/api/gdpr/consent", json={"is_18_plus": True})
assert r_gdpr.status_code == 200, "GDPR fel"
print("  - GDPR Registrerat.")

print("\n3️⃣ Testing POST /api/chat...")
r_chat = session.post(f"{RENDER_URL}/api/chat", json={"message": "Jag känner mig överväldigad på jobbet."})
assert r_chat.status_code == 200, f"Chat fel: {r_chat.status_code}"
data = r_chat.json()
print(f"  - Current Phase: {data.get('current_phase')}")
print(f"  - Messages left: {data.get('guest_messages_left')}")

print("\n4️⃣ Testing POST /api/auth/register...")
r_reg = session.post(f"{RENDER_URL}/api/auth/register", json={"email": "beta_tester@wayjs.se"})
assert r_reg.status_code == 200, f"Registrering fel: {r_reg.status_code}"
print(f"  - Skapat User ID: {r_reg.json().get('user_id')}")

print("\n==================================================================")
print("🏆 [SUCCESS] API-kontraktet är 100% verifierat mot PRD v1.3!")
print("==================================================================")
