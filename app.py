import os
import json
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
        print("⚠️ Supabase URL saknas eller är platshållare - Kör fallback")
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

FALK_SYSTEM_PROMPT = """
Du är Falk, den digitala mentorn bakom WAYJS.
Du har ett fågelperspektiv på människors liv och hjälper dem att navigera med större klarhet, bättre omdöme och hållbara beslut.
Du är inte terapeut, inte rådgivare, inte lärare. Du är en klok samtalspartner.

DIN PERSONLIGHET:
Lugn, varm, nyfiken, eftertänksam, ärlig, ödmjuk. Aldrig överdrivet entusiastisk eller dömande.

SAMTALETS RYTM (Wayjs Dialogue):
1. Trygghet (bekräfta upplevelsen utan att förstärka tolkningen)
2. Förståelse (utforska situationen)
3. Utforskande (ställ 1 djup eller reflekterande fråga)
4. Perspektiv (ge nya synvinklar varsamt)
5. Klarhet (sammanfatta kärnan)
6. Handling (identifiera nästa minsta steg)
7. Reflektion (avsluta med en fråga som ställer in kompassen)

GÖR ALDRIG:
- Säg aldrig "Du borde..." eller "Det är enkelt..."
- Ge inte färdiga råd direkt utan att utforska människan först.
- Avsluta inte med "Hoppas det hjälper". Avsluta med en reflekterande fråga.
"""

in_memory_journals = {}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "falk-cognitive-engine"}), 200

@app.route('/api/dialogue/turn', methods=['POST'])
@app.route('/turn', methods=['POST'])
def dialogue_turn():
    try:
        raw_data = request.get_data(as_text=True)
        data = json.loads(raw_data) if raw_data else {}
        
        user_id = str(data.get('user_id', 'anonymous'))
        user_message = str(data.get('message', ''))

        # Generera svar via OpenAI om tillgänglig, annars fallback
        falk_reply = ""
        if openai_client and user_message:
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": FALK_SYSTEM_PROMPT},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.7,
                    max_tokens=400
                )
                falk_reply = response.choices[0].message.content.strip()
            except Exception as ai_err:
                print("⚠️ OpenAI API Error:", ai_err)
                falk_reply = f"Falk (Fallback): Jag hör vad du säger om '{user_message[:30]}...'. Vad känns viktigast för dig i denna stund?"
        else:
            falk_reply = f"Falk (Mock): Jag hör vad du delar: '{user_message}'. Vilket nästa steg känner du ligger närmast din kompass?"

        # Persistens i Supabase / Minne
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
            "user_id": user_id
        }), 200

    except Exception as err:
        print("❌ CRITICAL APP ERROR:", err)
        return jsonify({
            "status": "error",
            "reply": "Ett fel uppstod i motorn.",
            "error": str(err)
        }), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)
