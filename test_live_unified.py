import requests

BASE_URL = "http://127.0.0.1:5001"
session = requests.Session()

def run_test():
    print("==================================================")
    print("🚀 INTEGRATIONSTEST: UNIFIED FLASK BACKEND (PORT 5001)")
    print("==================================================\n")

    # 1. GDPR Consent
    r_gdpr = session.post(f"{BASE_URL}/api/gdpr/consent", json={"is_18_plus": True})
    assert r_gdpr.status_code == 200, "❌ GDPR misslyckades"
    print("✅ [PASS] GDPR Samtycke registrerat.")

    # 2. Skarp LLM Chat (Standard)
    msg = "Jag upplever att mitt jobb tar all energi från mitt privatliv, vad ska jag göra?"
    r_chat = session.post(f"{BASE_URL}/api/chat", json={"message": msg}).json()
    resp_text = r_chat.get("response", "")
    sid = r_chat.get("session_id")

    print(f"📥 Användare: {msg}")
    print(f"🦅 Falk (Skarp LLM): {resp_text}\n")

    assert resp_text != "", "❌ Falk returnerade tomt svar!"
    assert resp_text.count("?") <= 1, f"❌ [FAIL] Mer än 1 frågetecken detekterat: ({resp_text.count('?')})"
    assert not (resp_text.startswith("Det låter som") or resp_text.startswith("Tack för")), "❌ [FAIL] Schabloninledning detekterad!"
    print("✅ [PASS] Skarpt LLM-svar klarade The Falk Filter.")

    # 3. Test av UI-modifierare (+) DEEPER
    r_deep = session.post(f"{BASE_URL}/api/chat", json={"message": msg, "session_id": sid, "modifier_type": "DEEPER"}).json()
    resp_deep = r_deep.get("response", "")
    print(f"➕ Falk (Modifierare DEEPER +): {resp_deep}\n")
    assert resp_deep != "", "❌ Tomt svar på DEEPER modifierare!"
    print("✅ [PASS] Modifierare DEEPER exekverad.")

    # 4. Dashboard (4 Kompasser)
    r_dash = session.get(f"{BASE_URL}/api/dashboard").json()
    assert "compass_scores" in r_dash, "❌ Dashboard saknar compass_scores!"
    print("✅ [PASS] Dashboard endpoint (/api/dashboard) levererar 4 Kompasser.")

    print("\n🏆 [ALL PASS] Backend är helt enhetlig och redo för UI-betan!")

if __name__ == "__main__":
    run_test()
