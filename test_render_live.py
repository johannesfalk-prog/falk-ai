import sys, os

def main():
    import sys
    import requests
    import json
    
    print("==================================================================")
    print("🦅 FALK CORE ENGINE - RENDER LIVE PRODUCTION AUDIT")
    print("==================================================================\n")
    
    if len(sys.argv) < 2:
        print("⚠️ Användning: python3 test_render_live.py <DIN_RENDER_URL>")
        print("Exempel: python3 test_render_live.py https://falk-backend.onrender.com\n")
        render_url = input("Klistra in din Render URL (eller tryck Enter för lokal 5001-test): ").strip()
        if not render_url:
            render_url = "http://127.0.0.1:5001"
    else:
        render_url = sys.argv[1].strip()
    
    render_url = render_url.rstrip("/")
    
    print(f"\n📡 Mål-URL: {render_url}")
    print("------------------------------------------------------------------")
    
    # 1. Health check over HTTPS
    print("🔍 1. Testar /health endpoint...")
    try:
        res = requests.get(f"{render_url}/health", timeout=15)
        print(f"   Status: HTTP {res.status_code}")
        print(f"   Respons: {res.json()}")
        if res.status_code == 200:
            print("   ✅ Health Check: PASS!")
        else:
            print("   ❌ Health Check: MISSLYCKADES!")
    except Exception as e:
        print(f"   ❌ Anslutningsfel mot {render_url}: {e}")
        sys.exit(1)
    
    # 2. Skarpt samtalstest
    print("\n💬 2. Testar /api/dialogue/turn endpoint...")
    payload = {
        "user_id": "live-audit-user",
        "session_id": "sess-live-render-audit-v1",
        "user_message": "Jag vill förstå hur jag kan skapa bättre balans i min vardag."
    }
    
    try:
        res = requests.post(f"{render_url}/api/dialogue/turn", json=payload, headers={"Content-Type": "application/json"}, timeout=30)
        print(f"   Status: HTTP {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print(f"   Aktiv Fas: [{data.get('active_stage')}]")
            print(f"   Falk Svar: \"{data.get('falk_response')[:100]}...\"")
            print("   ✅ Live API Check: PASS!")
        else:
            print(f"   ❌ API Check MISSLYCKADES: {res.text}")
    except Exception as e:
        print(f"   ❌ Fel vid anrop till /api/dialogue/turn: {e}")
    
    print("\n==================================================================")

if __name__ == '__main__':
    main()
