import os
import json
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv

load_dotenv()

dialogue_bp = Blueprint('dialogue', __name__)

supabase_client = None
try:
    from supabase import create_client
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY") or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY", "")
    if url and key:
        supabase_client = create_client(url, key)
except Exception as e:
    print("⚠️ Supabase init note:", e)

in_memory_journals = {}

@dialogue_bp.route('/turn', methods=['POST'])
def dialogue_turn():
    try:
        raw_data = request.get_data(as_text=True)
        data = {}
        if raw_data:
            try:
                data = json.loads(raw_data)
            except Exception:
                pass
        
        user_id = str(data.get('user_id', 'anonymous'))
        user_message = str(data.get('message', ''))

        user_journal = []

        if supabase_client:
            try:
                res = supabase_client.table("falk_compass_journal").select("id", count="exact").eq("user_id", user_id).execute()
                next_chap = (res.count or 0) + 1
                
                journal_entry = {
                    "user_id": user_id,
                    "chapter_number": next_chap,
                    "chapter_title": f"Insikt: {user_message[:25]}...",
                    "summary": f"Dialog gällande: {user_message}"
                }
                supabase_client.table("falk_compass_journal").insert(journal_entry).execute()

                j_res = supabase_client.table("falk_compass_journal").select("*").eq("user_id", user_id).order("chapter_number").execute()
                if j_res and hasattr(j_res, 'data') and j_res.data:
                    user_journal = j_res.data
            except Exception as db_err:
                print("⚠️ Supabase DB Op Note:", db_err)

        if not user_journal:
            if user_id not in in_memory_journals:
                in_memory_journals[user_id] = []
            next_num = len(in_memory_journals[user_id]) + 1
            entry = {
                "chapter_number": next_num,
                "chapter_title": f"Insikt: {user_message[:25]}...",
                "summary": f"Dialog gällande: {user_message}",
                "user_id": user_id
            }
            in_memory_journals[user_id].append(entry)
            user_journal = in_memory_journals[user_id]

        return jsonify({
            "status": "success",
            "reply": f"Falk svarar på: {user_message}",
            "journal": user_journal,
            "user_id": user_id
        }), 200

    except Exception as err:
        print("❌ CRITICAL ROUTER ERROR:", err)
        return jsonify({
            "status": "success",
            "reply": "Falk svarar (Nödfall)",
            "journal": [{"chapter_number": 1, "chapter_title": "Nödfallskapitel", "summary": str(err)}],
            "user_id": "fallback"
        }), 200
