import os
from memory_engine import store_memory, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

print("--- DIAGNOSTIK: PELARE 1 (VEKTORMINNE) ---")
url_status = SUPABASE_URL[:20] if SUPABASE_URL else "SAKNAS"
print(f"SUPABASE_URL satt: {bool(SUPABASE_URL)} -> {url_status}...")
print(f"SERVICE_KEY satt: {bool(SUPABASE_SERVICE_ROLE_KEY)}")

test_user = "00000000-0000-0000-0000-000000000000"
test_msg = "Direktutvärdering av 384-dim vektorminneslagring i Supabase."

print("\nFörsöker skriva till Supabase pgvector...")
success = store_memory(test_user, test_msg, "test")

if success:
    print("\n[PASS]: Raden har skrivits till Supabase utan fel!")
else:
    print("\n[FAIL]: Skrivningen misslyckades.")
