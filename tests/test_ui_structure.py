import requests

BASE_URL = "http://127.0.0.1:5001"
session = requests.Session()

def run_test():
    print("==================================================")
    print("🚀 STRESSTEST: FALK 4 KOMPASSER DASHBOARD & UI ENGINE")
    print("==================================================\n")

    # 1. GDPR Consent
    r1 = session.post(f"{BASE_URL}/api/gdpr/consent", json={"is_18_plus": True})
    assert r1.status_code == 200, "GDPR Misslyckades"
    print("✅ [PASS] GDPR Consent godkänt.")

    # 2. Dashboard API Check (4 Kompasser)
    r2 = session.get(f"{BASE_URL}/api/dashboard").json()
    assert "compass_scores" in r2, "❌ Dashboard saknar kompass-scores!"
    assert r2["compass_scores"]["personal"] == 75, "❌ Fel score i Personlig Kompass!"
    print("✅ [PASS] 4 Kompasser Dashboard API levererar korrekt datastruktur.")

    # 3. Web Page Check
    r3 = session.get(f"{BASE_URL}/")
    assert r3.status_code == 200, "❌ Rot-URL servar inte index.html"
    print("✅ [PASS] HTML-gränssnittet servas korrekt på HTTP 200 OK.")

    print("\n🏆 [ALL PASS] FALK Dashboard (4 Kompasser) och UI-motor är verifierade!")

if __name__ == "__main__":
    run_test()
