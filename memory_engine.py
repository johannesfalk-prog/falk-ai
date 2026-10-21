import os
import re
from sentence_transformers import SentenceTransformer
from supabase import create_client, Client

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(supabase_url, supabase_key) if (supabase_url and supabase_key) else None

# Ladda modellen enbart en gång vid start
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print(f"[CRITICAL]: Kunde inte ladda local embedding-modell: {e}")
    model = None

COGNITIVE_MARKERS = [
    r"\bjag känner\b", r"\bjag måste\b", r"\bjag borde\b", r"\balldrig\b", r"\balltid\b",
    r"\bingenting\b", r"\balla\b", r"\bgaranterat\b", r"\bhopplös\b", r"\bmisslyckad\b",
    r"\bsparken\b", r"\bhemlös\b", r"\brädd\b", r"\bångest\b", r"\bchefen\b", r"\bhatar\b",
    r"\borkar inte\b", r"\bkan inte\b", r"\bingen bryr sig\b"
]

def should_store_memory(text: str) -> bool:
    if len(text.strip()) < 15:
        return False
    text_lower = text.lower()
    for pattern in COGNITIVE_MARKERS:
        if re.search(pattern, text_lower):
            return True
    return False

def get_embedding(text: str):
    if not model:
        raise RuntimeError("Embedding-modellen är inte laddad i RAM.")
    return model.encode(text).tolist()

def store_memory(user_id: str, content: str, category: str = "reflection"):
    if not supabase:
        print("[MEMORY_ENGINE] Supabase ej initierad.")
        return None
    embedding = get_embedding(content)
    data = {
        "user_id": user_id,
        "content": content,
        "category": category,
        "embedding": embedding
    }
    return supabase.table("user_memories").insert(data).execute()

def get_relevant_memories(user_id: str, query: str, match_threshold: float = 0.3, match_count: int = 3):
    if not supabase or not model:
        return []
    
    query_embedding = get_embedding(query)
    response = supabase.rpc(
        "match_user_memories",
        {
            "query_embedding": query_embedding,
            "match_threshold": match_threshold,
            "match_count": match_count,
            "p_user_id": user_id
        }
    ).execute()
    
    return [item["content"] for item in response.data] if response.data else []
