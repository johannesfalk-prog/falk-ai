import requests
import json
import time

BASE_URL = "http://127.0.0.1:5001"
session = requests.Session()

def run_bench():
    print("==================================================")
    print("🚀 STRESSTEST: LLM-DRIVEN INTENT PLAYBOOK ROUTER")
    print("==================================================\n")

    res = session.post(f"{BASE_URL}/api/gdpr/consent", json={"is_18_plus": True})
    assert res.status_code == 200, "GDPR Consent misslyckades"
    print("✅ [PASS] GDPR Consent verifierat.")

    scenarios = [
        ("STRESS_BURNOUT", "Jag känner mig helt utbränd och orkar inte med jobbet eller sömnen längre.", "Burnout & Återhämtning"),
        ("DECISION_FATIGUE", "Jag står inför ett svårt val och vet inte om jag ska säga upp mig eller stanna.", "Beslutsångest & Livsval"),
        ("CAREER_LEADERSHIP_NEGATION", "Jag är inte utbränd eller stressad alls, men jag har blivit chef och behöver hjälp med min nya karriärroll.", "Chefsledarskap & Karriär"),
        ("RELATIONSHIP_CONFLICT", "Jag och min partner bråkar hela tiden om hur vi ska prioritera vår tid.", "Relationer & Konflikter"),
        ("ANXIETY_OVERWHELM", "Allt är rörigt i mitt huvud, jag känner oro och panik inför framtiden.", "Ångest & Inre Brus")
    ]

    for code, msg, expected_pb in scenarios:
        print(f"\n--- TEST: {code} ({expected_pb}) ---")
        r = session.post(f"{BASE_URL}/api/chat", json={"message": msg}).json()
        resp_text = r.get("response", "")
        act_pb = r.get("active_playbook")

        print(f"💬 Användare: {msg}")
        print(f"🦅 Falk: {resp_text}")
        print(f"🎯 Detekterad Playbook via LLM Intent: {act_pb}")

        assert act_pb == expected_pb, f"❌ [FAIL] Fel playbook aktiverades! Förväntade: '{expected_pb}', Fick: '{act_pb}'"
        assert resp_text.count("?") <= 1, f"❌ [FAIL] Regelbrott: Falk ställde mer än 1 fråga ({resp_text.count('?')})!"
        assert not (resp_text.startswith("Det låter som") or resp_text.startswith("Tack för")), "❌ [FAIL] Schabloninledning detekterad!"
        
        print(f"✅ [PASS] Playbook '{expected_pb}' aktiverades och upprätthöll alla guardrails.")
        time.sleep(1)

    print("\n🏆 [ALL PASS] Alla scenarier inklusive negationstest passerade via LLM Intent Classification!")

if __name__ == "__main__":
    run_bench()
