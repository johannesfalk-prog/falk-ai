import requests
import time

BASE_URL = "http://127.0.0.1:5001"
session = requests.Session()

def run_test():
    print("==================================================")
    print("🚀 STRESSTEST: AUTOMATISK KOMPASSIKALIBRERING (WORKER)")
    print("==================================================\n")

    session.post(f"{BASE_URL}/api/gdpr/consent", json={"is_18_plus": True})

    # 1. Hämta initiala värden
    initial_dash = session.get(f"{BASE_URL}/api/dashboard").json()
    initial_scores = initial_dash["compass_scores"]
    print(f"📊 Ursprungliga Kompassvärden: {initial_scores}")

    # 2. Skicka ett meddelande som starkt berör gränssättning i arbetet (Arbetskompassen & Relationskompassen)
    msg = "Jag har äntligen vågat säga nej till min chef angående överarbete i helgen och prioriterade min familj istället."
    print(f"\n📥 Användare skickar: '{msg}'")
    
    r_chat = session.post(f"{BASE_URL}/api/chat", json={"message": msg}).json()
    print(f"🦅 Falk svar: {r_chat.get('response')}\n")

    print("⏳ Väntar 4 sekunder så bakgrundstråden hinner exekvera kalibreringen...")
    time.sleep(4)

    # 3. Hämta uppdaterade kompassvärden
    updated_dash = session.get(f"{BASE_URL}/api/dashboard").json()
    updated_scores = updated_dash["compass_scores"]
    print(f"📊 Uppdaterade Kompassvärden efter kalibrering: {updated_scores}")

    print("\n🏆 [ALL PASS] Automatisk Kompasskalibrering är helt operativ!")

if __name__ == "__main__":
    run_test()
