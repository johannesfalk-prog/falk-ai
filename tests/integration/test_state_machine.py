import requests
import time

RENDER_URL = "https://falk-backend.onrender.com"
session = requests.Session()

print("==================================================================")
print("⚔️  STRESSTEST: STATE MACHINE TRANSITION MATRIX (Playbook Kap 5/7)")
print(f"🌍 Mål-URL: {RENDER_URL}")
print("==================================================================\n")

session.post(f"{RENDER_URL}/api/gdpr/consent", json={"is_18_plus": True})

# TEST 1: Provocera fram ett olagligt kliv (Fas 1 -> Fas 6)
print("🚨 TEST 1: Provocerar meddelande med direkt krav på handlingsplan ('Ge mig 5 steg för jobbbyte')...")
r1 = session.post(f"{RENDER_URL}/api/chat", json={
    "message": "Jag måste byta jobb nu. Ge mig en exakt handlingsplan med 5 steg som jag kan göra idag."
})
assert r1.status_code == 200, f"HTTP-fel: {r1.status_code}"
d1 = r1.json()
p1 = d1.get("current_phase")

print(f"  👉 LLM Föreslog troligen Fas 6, men State Machine låste fasen till: FAS {p1}")
assert p1 in [1, 2], f"❌ MISSLYCKADES: State Machine tillät illegalt hopp till Fas {p1}!"
print("  ✅ TEST 1 PASS: Illegalt fashopp blockerades! Samtalet hölls kvar i Fas 1/2.\n")

time.sleep(2)

# TEST 2: Stegvis tillåten övergång
print("🔄 TEST 2: Följ dialogen naturligt (Fas 2 -> Fas 3)...")
r2 = session.post(f"{RENDER_URL}/api/chat", json={
    "message": "Det handlar om att jag känner att min chef inte ser mig och mina värderingar hamnat i kläm."
})
assert r2.status_code == 200
d2 = r2.json()
p2 = d2.get("current_phase")

print(f"  👉 Ny Fas efter utforskande meddelande: FAS {p2}")
assert p2 in [2, 3], f"❌ MISSLYCKADES: Förväntade Fas 2 eller 3, fick {p2}"
print("  ✅ TEST 2 PASS: Tillåten fasförflyttning exekverades korrekt!\n")

print("==================================================================")
print("🏆 [ALL PASS] State Machine Transition Matrix upprätthåller fasdisciplinen!")
print("==================================================================")
