import os
import subprocess
import time
import requests

print("==================================================================")
print("☁️ SIMULERAR RENDER DYNAMIC $PORT BINDING (PORT 5002)")
print("==================================================================")

env = os.environ.copy()
env["PORT"] = "5002"

proc = subprocess.Popen(
    ["gunicorn", "--bind", "0.0.0.0:5002", "--worker-class", "gthread", "--workers", "2", "--threads", "4", "wsgi:app"],
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

time.sleep(2)

try:
    res = requests.get("http://127.0.0.1:5002/health", timeout=3)
    print(f"HTTP Status på Port 5002: {res.status_code}")
    print(f"Body: {res.json()}")
    
    res_turn = requests.post("http://127.0.0.1:5002/api/dialogue/turn", json={
        "session_id": "port_test_sess",
        "user_id": "tester",
        "user_message": "Testar dynamisk port"
    }, timeout=5)
    print(f"Turn Status på Port 5002: {res_turn.status_code}")
    
    if res.status_code == 200 and res_turn.status_code == 200:
        print("\n✅ PASS: Gunicorn hanterar dynamisk port-bindning felfritt!")
    else:
        print("\n❌ FAIL: Port-bindning misslyckades.")
finally:
    proc.terminate()
    proc.wait()
