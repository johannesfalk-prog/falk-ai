import requests

url = "https://falk-backend.onrender.com"
print(f"🔍 Diagnostik mot: {url}\n")

try:
    r = requests.get(url, timeout=10)
    print(f"Statuskod: {r.status_code}")
    print(f"Server Header: {r.headers.get('Server', 'Okänd')}")
    print(f"Content-Type: {r.headers.get('Content-Type', 'Okänd')}")
    print(f"\nSvarsinnehåll (första 300 tecken):\n{r.text[:300]}")
except Exception as e:
    print(f"❌ Nätverksfel: {e}")
