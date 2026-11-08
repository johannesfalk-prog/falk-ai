import requests

BASE_URL = "http://127.0.0.1:5001"

print("==================================================================")
print("🔥 TESTING SYSTEM FALLBACK & RESILIENCE UNDER EXCEPTION")
print("==================================================================")

# 1. Tom payload
res_bad = requests.post(f"{BASE_URL}/api/dialogue/turn", json={})
print(f"1. Tom Payload Status: {res_bad.status_code} (Förväntat 400)")

# 2. Extremt stort meddelande (10 000 tecken)
long_text = "Jag känner mig så stressad. " * 400
res_long = requests.post(f"{BASE_URL}/api/dialogue/turn", json={
    "session_id": "resilience_long_01",
    "user_id": "tester_long",
    "user_message": long_text
})
print(f"2. Lång Payload Status: {res_long.status_code} (Förväntat 200)")

# 3. Normal anrop
res_ok = requests.post(f"{BASE_URL}/api/dialogue/turn", json={
    "session_id": "resilience_check_01",
    "user_id": "tester",
    "user_message": "Hur går vi vidare härifrån?"
})
print(f"3. Normal Payload Status: {res_ok.status_code} (Förväntat 200)")

if res_bad.status_code == 400 and res_long.status_code == 200 and res_ok.status_code == 200:
    print("\n✅ PASS: Backend-gränssnittet hanterar alla belastnings- och feltyper säkert!")
else:
    print("\n❌ FAIL: Oväntad statuskod vid resiliensprov.")
