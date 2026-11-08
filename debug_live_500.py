import requests
import json

url = "https://falk-backend.onrender.com/api/chat"
payload = {"message": "Jag vet inte vad jag vill med mitt liv längre."}
headers = {"Content-Type": "application/json"}

print(f"🔍 SKICKAR DIAGNOSANROP MOT: {url} (Timeout: 60s)...")
try:
    res = requests.post(url, json=payload, headers=headers, timeout=60)
    print(f"📊 HTTP Status: {res.status_code}")
    print("------------------------------------------------------------------")
    try:
        data = res.json()
        print("📄 Svar från server (JSON):")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception:
        print("📄 Svar från server (Råtext):")
        print(res.text[:1000])
except Exception as e:
    print(f"❌ Nätverksfel vid anrop: {e}")
