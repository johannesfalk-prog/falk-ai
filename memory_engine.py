import os
from openai import OpenAI
from supabase import create_client, Client

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip().strip('"').strip("'")
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "").strip()

openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY) if SUPABASE_URL and SUPABASE_ANON_KEY else None

def get_embedding(text: str):
    if not openai_client:
        raise ValueError("OpenAI API key saknas för embeddings.")
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def should_store_memory(text: str) -> bool:
    # Tvinga lagring för alla meddelanden som är längre än 10 tecken under testfasen
    return len(text.strip()) > 10

def store_memory(user_id: str, content: str):
    if not supabase_client:
        raise ValueError("Supabase-klient inte initierad.")
    
    embedding = get_embedding(content)
    data = {
        "user_id": user_id,
        "content": content,
        "embedding": embedding
    }
    res = supabase_client.table("memories").insert(data).execute()
    print(f"[RAG STORE SUCCESS]: Minne sparat för user {user_id}", flush=True)
    return res

def get_relevant_memories(user_id: str, query: str, threshold: float = 0.3, limit: int = 3):
    if not supabase_client:
        raise ValueError("Supabase-klient inte initierad.")
    
    query_embedding = get_embedding(query)
    
    params = {
        "query_embedding": query_embedding,
        "match_threshold": threshold,
        "match_count": limit,
        "p_user_id": user_id
    }
    
    res = supabase_client.rpc("match_memories", params).execute()
    memories = [item["content"] for item in res.data] if res.data else []
    print(f"[RAG RETRIEVE SUCCESS]: Hittade {len(memories)} minnen för query '{query}'", flush=True)
    return memories
