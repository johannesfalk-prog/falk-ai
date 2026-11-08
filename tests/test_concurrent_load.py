import concurrent.futures
import requests
import time

BASE_URL = "http://127.0.0.1:5001"

def send_request(i):
    session_id = f"concurrent_test_sess_{i}"
    start = time.time()
    try:
        res = requests.post(f"{BASE_URL}/api/dialogue/turn", json={
            "session_id": session_id,
            "user_id": f"user_{i}",
            "user_message": "Jag känner mig sjukt stressad och har svårt att sortera mina tankar."
        }, timeout=20)
        elapsed = time.time() - start
        return i, res.status_code, res.json().get("active_stage"), elapsed, None
    except Exception as e:
        return i, None, None, time.time() - start, str(e)

print("==================================================================")
print("🔥 WSGI CONCURRENCY STRESS TEST (5 Samtidiga Anrop mot Gunicorn)")
print("==================================================================")

start_total = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(send_request, range(1, 6)))
total_time = time.time() - start_total

all_passed = True
for req_id, status, stage, elapsed, err in results:
    if err:
        print(f"❌ Worker {req_id}: FEL - {err} ({elapsed:.2f}s)")
        all_passed = False
    elif status == 200:
        print(f"✅ Worker {req_id}: HTTP 200 OK | Fas: [{stage}] | Latens: {elapsed:.2f}s")
    else:
        print(f"⚠️ Worker {req_id}: HTTP {status} | Latens: {elapsed:.2f}s")
        all_passed = False

print("-" * 66)
print(f"⏱️ Totalsamlingstid för 5 samtidiga anrop: {total_time:.2f}s")
if all_passed:
    print("🏆 PASS: Gunicorn WSGI hanterade samtidiga anrop utan krascher eller timeouts!")
else:
    print("❌ FAIL: Samtidighetstestet identifierade flaskhalsar!")
