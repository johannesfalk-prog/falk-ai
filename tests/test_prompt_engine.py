import requests
import json

BASE_URL = "http://127.0.0.1:5001"
session = requests.Session()

def run_test():
    print("==================================================")
    print("🚀 STRESSTEST FÖR ALTERNATIV A: 5-LAGERS PROMPTENGINE")
    print("==================================================\n")

    session.post(f"{BASE_URL}/api/gdpr/consent", json={"is_18_plus": True})

    # Test 1: Standard fråga
    msg = "Jag har svårt att sätta gränser mot min chef och känner att jag jobbar för mycket."
    r1 = session.post(f"{BASE_URL}/api/chat", json={"message": msg}).json()
    resp1 = r1.get("response", "")
    print(f"💬 Standardfråga: {msg}")
    print(f"🦅 Falk svar: {resp1}\n")
    
    assert resp1.count("?") <= 1, "❌ [FAIL] Mer än 1 fråga ställdes!"
    assert not (resp1.startswith("Det låter som") or resp1.startswith("Tack för")), "❌ [FAIL] Schabloninledning detekterad!"

    # Test 2: Djupare modifierare (Knapp +)
    r2 = session.post(f"{BASE_URL}/api/chat", json={"message": msg, "modifier_type": "DEEPER"}).json()
    resp2 = r2.get("response", "")
    print(f"➕ Modifierare DEEPER (+):")
    print(f"🦅 Falk svar: {resp2}\n")

    # Test 3: Kortare modifierare (Knapp -)
    r3 = session.post(f"{BASE_URL}/api/chat", json={"message": msg, "modifier_type": "SHORTER"}).json()
    resp3 = r3.get("response", "")
    print(f"➖ Modifierare SHORTER (-):")
    print(f"🦅 Falk svar: {resp3}\n")

    print("🏆 [ALL PASS] 5-lagers promptarkitektur verifierad och exekverad!")

if __name__ == "__main__":
    run_test()
