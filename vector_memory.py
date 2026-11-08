import os
from typing import List, Dict, Any, Optional
from openai import OpenAI
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
supabase_url = os.getenv("SUPABASE_URL", "")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

supabase = None
if supabase_url.startswith("http") and supabase_key:
    try:
        supabase = create_client(supabase_url, supabase_key)
    except Exception as e:
        print(f"[Varning] Supabase vector client kunde inte starta: {e}")

def generate_embedding(text: str) -> List[float]:
    res = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return res.data[0].embedding

def store_memory_vector(user_id: str, session_id: str, content: str, memory_layer: str = "LONG_TERM"):
    if not supabase or user_id.startswith("beta_guest") or user_id == "11111111-1111-1111-1111-111111111111":
        return
    try:
        embedding = generate_embedding(content)
        supabase.table("user_memory_vectors").insert({
            "user_id": user_id,
            "session_id": session_id,
            "memory_layer": memory_layer,
            "content": content,
            "embedding": embedding,
            "metadata": {"source": "falk_hybrid_calibration"}
        }).execute()
    except Exception as e:
        print(f"[Varning] Kunde inte spara minnesvektor: {e}")

def retrieve_rag_memories(user_id: str, query_text: str, limit: int = 3) -> str:
    if not supabase or user_id.startswith("beta_guest"):
        return ""
    try:
        query_embedding = generate_embedding(query_text)
        res = supabase.rpc(
            "match_user_memories_hybrid",
            {
                "query_embedding": query_embedding,
                "match_threshold": 0.30,
                "match_count": limit,
                "p_user_id": user_id
            }
        ).execute()

        if res.data and len(res.data) > 0:
            memories = [f"• [{m['memory_layer']}] {m['content']}" for m in res.data]
            return "\nRELEVANTA HISTORISKA MINNEN (HYBRID RAG):\n" + "\n".join(memories)
    except Exception as e:
        print(f"[Varning] Hybrid RAG-sökning misslyckades: {e}")
    return ""
