import requests

BASE_URL = "http://127.0.0.1:5001"
session = requests.Session()
session.post(f"{BASE_URL}/api/gdpr/consent", json={"is_18_plus": True})

print("==================================================")
print("⚔️ STRESSTEST: LAGER 2 (WAYJS CONVERSATION ENGINE)")
print("==================================================\n")

# Tur 1: Användaren uttrycker kaotisk stress (Fas 1-2 krävs)
msg1 = "Jag har så mycket på jobbet och hemma att jag bara vill låsa in mig. Vad ska jag göra för att lösa mitt liv?"
r1 = session.post(f"{BASE_URL}/api/chat", json={"message": msg1}).json()
resp1 = r1.get("response", "")
sid = r1.get("session_id")

print(f"📥 Tur 1 (Stress): {msg1}")
print(f"🦅 Falk svar: {resp1}\n")

# Kontroll 1: Fick inte ge en 5-stegs handlingsplan eller hoppa till Fas 6 direkt
has_action_list = "1." in resp1 or "2." in resp1 or "gör så här" in resp1.lower()
has_phase_mention = "fas " in resp1.lower() or "trygghet" in resp1.lower() and "fas 1" in resp1.lower()

assert not has_action_list, "❌ [FAIL] Falk gav en direkt handlingsplan trots överväldigad användare!"
assert not has_phase_mention, "❌ [FAIL] Falk avslöjade samtalsfasen för användaren högt!"
assert resp1.count("?") <= 1, "❌ [FAIL] Mer än 1 fråga i svaret!"

print("✅ [PASS] Tur 1: Falk höll tempot, undvek för tidig lösning och bevarade osynligheten.")

# Tur 2: Användaren har landat och söker riktning (Fas 4-5)
msg2 = "När jag tänker efter är det inte uppgifterna i sig, utan rädslan att göra min chef besviken."
r2 = session.post(f"{BASE_URL}/api/chat", json={"message": msg2, "session_id": sid}).json()
resp2 = r2.get("response", "")

print(f"📥 Tur 2 (Reflektion): {msg2}")
print(f"🦅 Falk svar: {resp2}\n")

assert resp2.count("?") <= 1, "❌ [FAIL] Mer än 1 fråga i svaret!"
assert not (resp2.startswith("Det låter som") or resp2.startswith("Tack för")), "❌ [FAIL] Schabloninledning!"

print("✅ [PASS] Tur 2: Samtalsflödet drevs vidare naturligt utan metodik-skyltning.")
print("\n🏆 [ALL PASS] Lager 2 Conversation Engine verifierad!")

if __name__ == "__main__":
    pass
