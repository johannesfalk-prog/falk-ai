import os
import requests
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# Korrekt Serverless Inference URL för Hugging Face
HF_EMBEDDING_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"

def get_embedding(text: str):
    # 1. Försök med OpenAI (Lägst latens, högst tillförlitlighet)
    if OPENAI_API_KEY:
        try:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "input": text,
                "model": "text-embedding-3-small"
            }
            res = requests.post("https://api.openai.com/v1/embeddings", headers=headers, json=payload, timeout=5.0)
            if res.status_code == 200:
                return res.json()["data"][0]["embedding"]
            else:
                print(f"[OPENAI EMBEDDING ERROR]: {res.status_code} - {res.text}", flush=True)
        except Exception as e:
            print(f"[OPENAI EMBEDDING EXCEPTION]: {e}", flush=True)

    # 2. Fallback till Hugging Face REST API
    if HF_API_TOKEN:
        try:
            headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
            payload = {"inputs": text, "options": {"wait_for_model": True}}
            res = requests.post(HF_EMBEDDING_URL, headers=headers, json=payload, timeout=8.0)
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
                    return data[0]
                return data
            else:
                print(f"[HF EMBEDDING ERROR]: {res.status_code} - {res.text}", flush=True)
        except Exception as e:
            print(f"[HF EMBEDDING EXCEPTION]: {e}", flush=True)

    print("[MEMORY ERROR]: Inget fungerande embedding-API tillgängligt.", flush=True)
    return None

def store_memory(user_id: str, content: str, category: str = "reflection"):
    if not supabase:
        print("[MEMORY ERROR]: Supabase client inte initierad.", flush=True)
        return False
        
    vec = get_embedding(content)
    if not vec:
        print("[MEMORY ERROR]: Kunde inte generera embedding för lagring.", flush=True)
        return False

    try:
        res = supabase.table("user_memories").insert({
            "user_id": user_id,
            "content": content,
            "category": category,
            "embedding": vec
        }).execute()
        print(f"[MEMORY STORE SUCCESS]: Sparade minne för user {user_id}", flush=True)
        return True
    except Exception as e:
        print(f"[SUPABASE STORE ERROR]: {e}", flush=True)
        return False

def get_relevant_memories(user_id: str, query: str, limit: int = 3):
    if not supabase:
        return []
        
    vec = get_embedding(query)
    if not vec:
        print("[MEMORY ERROR]: Kunde inte generera embedding för sökning.", flush=True)
        return []

    try:
        rpc_res = supabase.rpc("match_memories", {
            "query_embedding": vec,
            "match_threshold": 0.3,
            "match_count": limit,
            "p_user_id": user_id
        }).execute()
        
        if rpc_res.data:
            print(f"[MEMORY MATCH SUCCESS]: Hittade {len(rpc_res.data)} minnen", flush=True)
            return [item["content"] for item in rpc_res.data]
    except Exception as e:
        print(f"[SUPABASE MATCH ERROR]: {e}", flush=True)
        
    return []

def should_store_memory(message: str) -> bool:
    indicators = ["känner", "tror", "mår", "rädd", "stressad", "mål", "vill", "problem", "oro", "alltid", "aldrig"]
    return len(message) > 15 and any(word in message.lower() for word in indicators)
