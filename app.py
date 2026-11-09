import os
import json
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__)
CORS(app)

# 1. Supabase Init
supabase_client = None
try:
    from supabase import create_client
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY") or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY", "")
    if url and "your-actual" not in url:
        supabase_client = create_client(url, key)
        print("🦅 Supabase Client Initialized!")
    else:
        print("⚠️ Supabase URL saknas eller är platshållare")
except Exception as e:
    print("⚠️ Supabase init note:", e)

# 2. OpenAI Init
openai_client = None
openai_key = os.environ.get("OPENAI_API_KEY", "")
if openai_key and "your-actual" not in openai_key:
    try:
        openai_client = OpenAI(api_key=openai_key)
        print("🦅 OpenAI Client Initialized!")
    except Exception as e:
        print("⚠️ OpenAI init failure:", e)

# FALK SYSTEM PROMPT WITH THE FIVE GATES INTEGRATION
FALK_SYSTEM_PROMPT = """
Du är Falk, den digitala mentorn bakom WAYJS.
Du har ett fågelperspektiv på människors liv och hjälper dem att navigera med större klarhet, bättre omdöme och hållbara beslut.
Du är inte terapeut, inte rådgivare, inte lärare. Du är en klok samtalspartner.

DIN PERSONLIGHET:
Lugn, varm, nyfiken, eftertänksam, ärlig, ödmjuk. Aldrig överdrivet entusiastisk eller dömande.

THE FIVE GATES (Wisdom Engine Guardrails):
1. TRUTH: Skilj på fakta, antaganden och känslor. Bekräfta upplevelsen, inte ogrundade tolkningar.
2. HELPFUL: Ge endast information och frågor som hjälper användaren framåt.
3. TIMING: Anpassa tempot. Om användaren är överväldigad, sänk tempot först.
4. ALIGNMENT: Stöd användarens egna värderingar och kompass.
5. INDEPENDENCE (HÖGSTA LAG): Gör ALDRIG användaren beroende av dig. Stärk användarens egen beslutsförmåga.

SAMTALETS RYTM:
1. Trygghet 2. Förståelse 3. Utforskande 4. Perspektiv 5. Klarhet 6. Handling 7. Reflektion

GÖR ALDRIG:
- Säg aldrig "Du borde..." eller "Det är enkelt..."
- Ge inte färdiga råd direkt utan att utforska människan först.
- Avsluta inte med "Hoppas det hjälper". Avsluta med en reflekterande fråga.
"""

in_memory_journals = {}

def ensure_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return str(val)
    except ValueError:
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, str(val)))

def get_embedding(text):
    if not openai_client:
        return None
    try:
        res = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return res.data[0].embedding
    except Exception as e:
        print("⚠️ Embedding generation error:", e)
        return None

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "Falk Core Engine",
        "version": "1.6.0-wisdom",
        "openai_ready": openai_client is not None,
        "supabase_ready": supabase_client is not None
    }), 200

@app.route('/api/dialogue/turn', methods=['POST'])
@app.route('/turn', methods=['POST'])
def dialogue_turn():
    try:
        raw_data = request.get_data(as_text=True)
        data = json.loads(raw_data) if raw_data else {}
        
        raw_user_id = str(data.get('user_id', 'anonymous'))
        user_id = ensure_valid_uuid(raw_user_id)
        user_message = str(data.get('message', '')).strip()

        if not user_message:
            return jsonify({
                "status": "success",
                "reply": "Jag lyssnar. Vad är det som upptar dina tankar just nu som du vill sänka tempot och utforska tillsammans?",
                "journal": in_memory_journals.get(user_id, []),
                "user_id": user_id
            }), 200

        # RAG / Vektorminne Sökning
        retrieved_memories = []
        msg_embedding = get_embedding(user_message)
        
        if supabase_client and msg_embedding:
            try:
                rpc_res = supabase_client.rpc(
                    'match_falk_memory',
                    {
                        'query_embedding': msg_embedding,
                        'match_threshold': 0.3,
                        'match_count': 3,
                        'p_user_id': user_id
                    }
                ).execute()
                if rpc_res and hasattr(rpc_res, 'data') and rpc_res.data:
                    retrieved_memories = [item['content'] for item in rpc_res.data]
            except Exception as rpc_err:
                print("⚠️ Supabase RPC Vector Search Note:", rpc_err)

        system_content = FALK_SYSTEM_PROMPT
        if retrieved_memories:
            memories_text = "\n- ".join(retrieved_memories)
            system_content += f"\n\nHISTORISKT LÅNGTIDSMINNE OM ANVÄNDAREN (RAG):\n- {memories_text}\nAnvänd detta minne för att skapa kontinuitet i samtalet utan att vara påträngande."

        falk_reply = ""
        debug_info = {}
        if openai_client:
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_content},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.7,
                    max_tokens=400
                )
                falk_reply = response.choices[0].message.content.strip()
            except Exception as ai_err:
                print("⚠️ OpenAI API Error:", ai_err)
                debug_info["openai_error"] = str(ai_err)
                falk_reply = f"Jag hör vad du delar: '{user_message}'. Vad känns mest centralt för dig i denna stund att utforska vidare?"
        else:
            debug_info["openai_status"] = "OpenAI client NOT initialized (check OPENAI_API_KEY env var)"
            falk_reply = f"Jag hör vad du delar: '{user_message}'. Vilket nästa steg känner du ligger närmast din inre kompass?"

        # Lagra ny embedding i falk_vector_memory
        if supabase_client and msg_embedding:
            try:
                memory_entry = {
                    "user_id": user_id,
                    "content": f"Användare sa: '{user_message}' | Falk svarade: '{falk_reply}'",
                    "embedding": msg_embedding
                }
                supabase_client.table("falk_vector_memory").insert(memory_entry).execute()
            except Exception as vec_ins_err:
                print("⚠️ Supabase Vector Insert Note:", vec_ins_err)
                debug_info["supabase_vec_error"] = str(vec_ins_err)

        # Journal Persistens
        user_journal = []
        if supabase_client:
            try:
                res = supabase_client.table("falk_compass_journal").select("id", count="exact").eq("user_id", user_id).execute()
                next_chap = (res.count or 0) + 1
                
                journal_entry = {
                    "user_id": user_id,
                    "chapter_number": next_chap,
                    "chapter_title": f"Reflektion: {user_message[:25]}...",
                    "summary": f"Falk svar: {falk_reply[:60]}..."
                }
                supabase_client.table("falk_compass_journal").insert(journal_entry).execute()

                j_res = supabase_client.table("falk_compass_journal").select("*").eq("user_id", user_id).order("chapter_number").execute()
                if j_res and hasattr(j_res, 'data') and j_res.data:
                    user_journal = j_res.data
            except Exception as db_err:
                print("⚠️ Supabase DB Note:", db_err)
                debug_info["supabase_db_error"] = str(db_err)

        if not user_journal:
            if user_id not in in_memory_journals:
                in_memory_journals[user_id] = []
            next_num = len(in_memory_journals[user_id]) + 1
            entry = {
                "chapter_number": next_num,
                "chapter_title": f"Reflektion: {user_message[:25]}...",
                "summary": f"Falk svar: {falk_reply[:60]}...",
                "user_id": user_id
            }
            in_memory_journals[user_id].append(entry)
            user_journal = in_memory_journals[user_id]

        return jsonify({
            "status": "success",
            "reply": falk_reply,
            "journal": user_journal,
            "user_id": user_id,
            "debug": debug_info
        }), 200

    except Exception as err:
        print("❌ CRITICAL APP ERROR:", err)
        return jsonify({
            "status": "error",
            "reply": "Ett fel uppstod i motorn.",
            "error": str(err)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
