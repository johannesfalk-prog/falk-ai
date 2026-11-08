import requests

BASE_URL = "http://127.0.0.1:5001"

print("==================================================================")
print("🔍 TESTING CORS PREFLIGHT (OPTIONS) FOR FRONTEND INTEGRATION")
print("==================================================================")

headers = {
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "Content-Type",
    "Origin": "http://localhost:3000"
}

res = requests.options(f"{BASE_URL}/api/dialogue/turn", headers=headers)

print(f"HTTP Status: {res.status_code}")
print(f"Access-Control-Allow-Origin: {res.headers.get('Access-Control-Allow-Origin')}")
print(f"Access-Control-Allow-Methods: {res.headers.get('Access-Control-Allow-Methods')}")

if res.status_code in [200, 204] and res.headers.get('Access-Control-Allow-Origin'):
    print("✅ PASS: CORS Preflight godkänd. Frontend-integrering redo!")
else:
    print("❌ FAIL: CORS Preflight blockerad!")
