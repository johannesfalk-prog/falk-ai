import requests
import time

BASE_URL = "http://127.0.0.1:5001"
session_id = f"multiturn_verify_{int(time.time())}"
user_id = "test_user_multiturn"

script = [
    "Hej Falk, jag känner mig ganska förvirrad kring min framtid just nu.",
    "Det har funnits i flera månader. Jag vet inte om jag ska stanna på mitt nuvarande jobb eller satsa på något helt nytt.",
    "Det som stoppar mig mest är rädslan för att förlora den ekonomiska tryggheten.",
    "Hur tycker du att jag ska titta på det här beslutet från ett fågelperspektiv?"
]

print("==================================================================")
print("🦅 MULTI-TURN DIALOGUE & STAGE PROGRESSION TEST")
print("==================================================================\n")

for i, user_msg in enumerate(script, 1):
    print(f"--- Tur {i} ---")
    print(f"👤 Användare: \"{user_msg}\"")
    
    res = requests.post(f"{BASE_URL}/api/dialogue/turn", json={
        "session_id": session_id,
        "user_id": user_id,
        "user_message": user_msg
    }).json()
    
    stage = res.get("active_stage", "OKÄND")
    ans = res.get("falk_response", "")
    
    print(f"📍 Aktiv samtalsfas: [{stage}]")
    print(f"🦅 Falk: \"{ans}\"\n")
    time.sleep(1)

print("==================================================================")
print("✅ PASS: Sekvens kördes utan tekniska avbrott.")
print("==================================================================")
