import os
import requests

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

def get_embedding(text):
    if not OPENAI_API_KEY:
        print("[MEMORY ENGINE WARNING]: OPENAI_API_KEY saknas i Environment.", flush=True)
        return None
    try:
        res = requests.post(
            "https://api.openai.com/v1/embeddings",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "text-embedding-3-small",
                "input": text
            },
            timeout=5.0
        )
        if res.status_code == 200:
            return res.json()["data"][0]["embedding"]
        else:
            print(f"[OPENAI EMBEDDING ERROR]: {res.status_code} - {res.text}", flush=True)
            return None
    except Exception as e:
        print(f"[OPENAI EMBEDDING EXCEPTION]: {e}", flush=True)
        return None

def store_memory(user_id, text, category="general"):
    embedding = get_embedding(text)
    if not embedding or not SUPABASE_URL or not SUPABASE_ANON_KEY:
        print("[STORE MEMORY SKIPPED]: Saknar embedding eller Supabase-konfig.", flush=True)
        return False

    try:
        res = requests.post(
            f"{SUPABASE_URL}/rest/v1/user_memories",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            },
            json={
                "user_id": user_id,
                "content": text,
                "category": category,
                "embedding": embedding
            },
            timeout=5.0
        )
        return res.status_code in [200, 201]
    except Exception as e:
        print(f"[STORE MEMORY EXCEPTION]: {e}", flush=True)
        return False

def get_relevant_memories(user_id, query, threshold=0.3, limit=3):
    embedding = get_embedding(query)
    if not embedding or not SUPABASE_URL or not SUPABASE_ANON_KEY:
        return []

    try:
        res = requests.post(
            f"{SUPABASE_URL}/rest/v1/rpc/match_memories",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "query_embedding": embedding,
                "match_threshold": threshold,
                "match_count": limit,
                "p_user_id": user_id
            },
            timeout=5.0
        )
        if res.status_code == 200:
            data = res.json()
            return [m["content"] for m in data if "content" in m]
        else:
            print(f"[RPC MATCH ERROR]: {res.status_code} - {res.text}", flush=True)
            return []
    except Exception as e:
        print(f"[RPC MATCH EXCEPTION]: {e}", flush=True)
        return []

def should_store_memory(text):
    text_lower = text.lower()
    triggers = ["mål", "namn", "heter", "jobbar", "känner", "problem", "ångest", "vision", "vill", "min"]
    return any(t in text_lower for t in triggers)
