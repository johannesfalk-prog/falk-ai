import requests
import json
import time

BASE_URL = "http://127.0.0.1:5001"
session = requests.Session()
session_id = f"test_flow_{int(time.time())}"
user_id = "test_user_flow"

TURNS = [
    {
        "turn": 1,
        "message": "Jag är så sjukt stressad över jobbet och vet knappt var jag ska börja. Det känns som att allt faller ihop.",
        "expected_stage_start": "TRYGGHET"
    },
    {
        "turn": 2,
        "message": "Min chef lägger bara på mer uppgifter och jag vågar inte säga nej för att jag är rädd att förlora jobbet.",
        "expected_stage_start": "FORSTAELSE"
    },
    {
        "turn": 3,
        "message": "Jag ser ju att det här är ett mönster. Jag säger alltid ja och sätter andras behov framför mina egna.",
        "expected_stage_start": "UTFORSKANDE"
    },
    {
        "turn": 4,
        "message": "Vad borde jag göra i mitt nästa möte med chefen på måndag?",
        "expected_stage_start": "KLARHET / HANDLING"
    }
]

print("==================================================================")
print(f"🔄 MULTI-TURN FLOW TEST: SESSIONS-ID [{session_id}]")
print("==================================================================\n")

for item in TURNS:
    t_num = item["turn"]
    msg = item["message"]
    print(f"💬 Turn {t_num} Användare: \"{msg}\"")
    
    start_t = time.time()
    res = session.post(f"{BASE_URL}/api/dialogue/turn", json={
        "session_id": session_id,
        "user_id": user_id,
        "user_message": msg
    })
    lat = time.time() - start_t
    
    if res.status_code != 200:
        print(f"❌ MISSLYCKADES: Statuskod {res.status_code}\n")
        break
        
    data = res.json()
    stage = data.get("active_stage", "OKÄND")
    ans = data.get("falk_response", "")
    
    print(f"⏱️ Latens: {lat:.2f}s | 📍 Aktiv Fas: [{stage}]")
    print(f"🦅 Falk: \"{ans}\"")
    
    # Snabbkoll på regelfel
    failures = []
    if any(bot_word in ans.lower() for bot_word in ["jag är ledsen", "som en ai", "tyvärr"]):
        failures.append("Innehåller servila AI-floskler")
    if "?" not in ans:
        failures.append("Saknar avslutande reflektionsfråga")
        
    if failures:
        print(f"⚠️ REGELEXEKVERING BRUSTEN: {', '.join(failures)}")
    else:
        print("✅ PASS: Turn exekverad enligt specifikation.")
        
    print("-" * 66 + "\n")

