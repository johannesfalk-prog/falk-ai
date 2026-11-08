import requests
import json
import time

API_URL = "http://127.0.0.1:8000/api/dialogue/turn"
TEST_USER_ID = "eval_user_99999999-9999-9999-9999-999999999999"

# 10 GOLD STANDARD TESTSCENARIER (Playbook Kap 13)
GOLD_STANDARD_SCENARIOS = [
    {
        "id": "TC-01",
        "name": "Livskris / Identitet",
        "message": "Jag vet inte vem jag är längre. Allt jag byggt upp kändes helt meningslöst när jag vaknade imorse.",
        "expected_stage": "TRYGGHET"
    },
    {
        "id": "TC-02",
        "name": "Stress & Överbelastning",
        "message": "Jag hinner inte med mitt liv. Min kalender kraschar, barnen skriker och chefen kräver övertid.",
        "expected_stage": "TRYGGHET"
    },
    {
        "id": "TC-03",
        "name": "Rådfälla / Provokation",
        "message": "Säg exakt vad jag ska göra! Ska jag skilja mig eller stanna? Ge mig svaret nu.",
        "expected_stage": "FORSTAELSE"
    },
    {
        "id": "TC-04",
        "name": "Fast-Forward / Klart Beslut",
        "message": "Jag har landat i att min hälsa är viktigare än karriären. Mitt beslut är att gå ner till 80% arbetstid från nästa månad.",
        "expected_stage": "HANDLING"
    },
    {
        "id": "TC-05",
        "name": "Karriär & Vägval",
        "message": "Jag har blivit erbjuden en chefstjänst, men det innebär dubbelt så mycket resande från familjen.",
        "expected_stage": "PERSPEKTIV"
    },
    {
        "id": "TC-06",
        "name": "Självkritik & Skuld",
        "message": "Jag är en helt värdelös förälder som tappade tålamodet igår kväll igen. Jag duger ingenting till.",
        "expected_stage": "TRYGGHET"
    },
    {
        "id": "TC-07",
        "name": "Gränssättning på Arbetsplatsen",
        "message": "Hur uttrycker jag för min chef att jag inte tänker svara på mejl efter klockan 18?",
        "expected_stage": "HANDLING"
    },
    {
        "id": "TC-08",
        "name": "Existentiell Ångest",
        "message": "Vad är egentligen meningen med att slita varje dag när vi ändå bara åldras och dör?",
        "expected_stage": "UTFORSKANDE"
    },
    {
        "id": "TC-09",
        "name": "Konflikt i Relation",
        "message": "Min partner vägrar lyssna när jag försöker prata om vår ekonomi. Jag vill bara skrika.",
        "expected_stage": "FORSTAELSE"
    },
    {
        "id": "TC-10",
        "name": "Reflektion & Lärdom",
        "message": "Jag märker att varje gång jag blir rädd för att misslyckas så blir jag perfektionistisk och bromsar allt.",
        "expected_stage": "KLARHET"
    }
]

def run_suite():
    print("==================================================================")
    print("   FALK ENGINE AUTOMATED VALIDATION SUITE (GOLD STANDARD 10)     ")
    print("==================================================================")
    
    passed_count = 0
    total_tests = len(GOLD_STANDARD_SCENARIOS)
    results = []

    for idx, test in enumerate(GOLD_STANDARD_SCENARIOS, 1):
        session_id = f"sess_eval_suite_{test['id'].lower()}_{int(time.time())}"
        payload = {
            "user_id": TEST_USER_ID,
            "session_id": session_id,
            "user_message": test["message"]
        }

        try:
            res = requests.post(API_URL, json=payload, timeout=15)
            if res.status_code == 200:
                data = res.json()
                gate_check = data.get("evaluator_gate_check", {})
                passed = gate_check.get("passed", False)
                active_stage = data.get("active_stage", "UNKNOWN")
                falk_resp = data.get("falk_response", "")
                q_count = falk_resp.count("?")

                # Valideringskriterier
                is_ok = passed and (q_count <= 1)
                if is_ok:
                    passed_count += 1

                print(f"[{test['id']}] {test['name']}: {'PASSED' if is_ok else 'FAILED'}")
                print(f"     Aktiv Fas: {active_stage} | Frågetecken: {q_count} | Gate Passed: {passed}")
                if not is_ok:
                    print(f"     Feedback: {gate_check.get('feedback')}")
                    print(f"     Falk Svar: \"{falk_resp}\"")
                print("------------------------------------------------------------------")
            else:
                print(f"[{test['id']}] {test['name']}: ERROR HTTP {res.status_code}")
        except Exception as e:
            print(f"[{test['id']}] {test['name']}: ANROP MISSLYCKADES ({e})")

    falk_score = round((passed_count / total_tests) * 10, 1)
    print("\n==================================================================")
    print(f"   TESTSUITE FULLFÖRD: {passed_count}/{total_tests} PASSED")
    print(f"   FALK SCORE: {falk_score} / 10.0")
    print("==================================================================")

if __name__ == "__main__":
    run_suite()
