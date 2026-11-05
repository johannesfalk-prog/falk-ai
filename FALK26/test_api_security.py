from dotenv import load_dotenv
load_dotenv()
import sys
import json
from app import app

client = app.test_client()

print("="*60)
print("A. NEGATIVA TESTER (Oinloggade/Overifierade anrop)")
print("="*60)

negative_tests = [
    ("GET", "/api/journal", None, 401),
    ("GET", "/api/sessions", None, 401),
    ("POST", "/api/sessions", {"title": "Test Session"}, 401),
    ("GET", "/api/profile", None, 401),
]

passed_neg = True
for method, path, payload, expected in negative_tests:
    res = client.get(path) if method == "GET" else client.post(path, json=payload or {})
    status_ok = (res.status_code == expected)
    icon = "✅" if status_ok else "🚨"
    print(f"{icon} {method:4s} {path:25s} | Forvantat: {expected} | Fick: {res.status_code}")
    if not status_ok:
        passed_neg = False

print("\n" + "="*60)
print("B. POSITIVA TESTER (Gäst-chatt & Input-validering)")
print("="*60)

# 1. Tomt meddelande ska ge 400
res_empty = client.post("/chat", json={"message": "   "})
status_empty_ok = (res_empty.status_code == 400)
print(f"{'✅' if status_empty_ok else '🚨'} POST /chat (Tomt meddelande)      | Forvantat: 400 | Fick: {res_empty.status_code}")

# 2. Giltigt gästmeddelande ska svara utan backend-krasch (200 eller hanterat AI-svar)
res_valid = client.post("/chat", json={"message": "Hej FALK, detta ar ett integrationstest."})
status_valid_ok = (res_valid.status_code in [200, 429, 503]) # 200 OK, eller giltig rate-limit/API-key saknas i testmiljo
print(f"{'✅' if status_valid_ok else '🚨'} POST /chat (Giltigt gästmeddelande)| Forvantat: 200/429/503 | Fick: {res_valid.status_code}")

print("\n" + "="*60)
if passed_neg and status_empty_ok and status_valid_ok:
    print("🎉 FULLSTÄNDIG AUDIT GODKÄND: Gatekeeper skyddar och motorn exekverar.")
    sys.exit(0)
else:
    print("💥 AUDIT MISSLYCKADES: Systemet har funktionella eller säkerhetsmässiga brister.")
    sys.exit(1)
