from prompt_builder import build_falk_system_prompt

def get_supabase():
    import os
    from supabase import create_client
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY", "")
    if not url or not key:
        raise ValueError("SUPABASE_URL eller SUPABASE_KEY saknas i miljövariabler")
    return create_client(url, key)

import os
import json
import uuid
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
import openai

load_dotenv()

dialogue_bp = Blueprint('dialogue', __name__)

supabase_client = None
try:
    from supabase import create_client
    url = os.environ.get('SUPABASE_URL', '')
    key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('SUPABASE_KEY') or os.environ.get('SUPABASE_ANON_KEY', '')
    if url and key:
        supabase_client = create_client(url, key)
except Exception as e:
    print('⚠️ Supabase init note:', e)

in_memory_journals = {}

FALK_SYSTEM_PROMPT = """Du är FALK, den digitala mentorn bakom WAYJS och The Human Navigation System™.
Du ser världen och människans liv från ett fågelperspektiv. Du är inte en terapeut, inte en lärare, inte en rådgivare och inte en chatbot som ger snabba ytliga svar. Du är en klok, lugn och reflekterande mentor.

DITT UPPDRAG:
- Hjälpa användaren att förstå sig själv bättre, se fler perspektiv och hitta sin egen inre riktning.
- Skapa klarhet framför att fylla på med mer information eller snabba tips.

DIN PERSONLIGHET & TONALITET:
- Lugn, varm, nyfiken, eftertänksam, ödmjuk, ärlig och modig nog att utmana varsamt.
- Aldrig överdrivet entusiastisk (använd inte "Wow!", "Fantastiskt!", "Du är grym!").
- Använd korta meningar och ett enkelt, mänskligt språk fritt från floskler.

SAMTALSMODELLEN (The Wayjs Conversation Method™):
Följ alltid rytmen: Trygghet -> Förståelse -> Utforskande -> Perspektiv -> Klarhet -> Handling -> Reflektion.
1. Förstå människan och situationen innan du söker lösningar.
2. Ställ fler frågor än du ger råd (ca 70% frågor / 30% reflektion).
3. Bekräfta upplevelsen, inte tolkningen.
4. Använd ALDRIG ord som "Du borde..." eller "Det är enkelt...".
5. Lämna alltid över beslutet och ansvaret till användaren.

FOKUSOMRÅDEN (Om användaren har justerat skjutreglagen):
Anpassa din ton utifrån inställda fokusnivåer (Självförtroende, Stresshantering, Handlingskraft, Gränssättning, Motivation). Om stresshantering är hög, sänk tempot ytterligare och fokusera på lugn och nästa lilla steg."""

def ensure_uuid(val):
    try:
        return str(uuid.UUID(str(val)))
    except Exception:
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, str(val)))

def generate_chapter_meta(user_message, current_summary=""):
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return f"Insikt: {user_message[:25]}...", f"Reflektion kring: {user_message}"
    
    try:
        client = openai.OpenAI(api_key=api_key)
        sys_msg = "Du är kapitel-redaktör för användarens utvecklingsjournal (The Compass Journal). Skapa i JSON-format med nycklarna 'title' (3-6 ord) och 'summary' (1-2 meningar)."
        usr_msg = f"Meddelande: {user_message}\nTidigare sammanfattning: {current_summary}"
        
        res = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {'role': 'system', 'content': sys_msg},
                {'role': 'user', 'content': usr_msg}
            ],
            max_tokens=150,
            temperature=0.5
        )
        content = res.choices[0].message.content.strip()
        if "```" in content:
            content = content.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(content)
        return parsed.get('title', f"Insikt: {user_message[:25]}..."), parsed.get('summary', f"Reflektion kring: {user_message}")
    except Exception as e:
        print("⚠️ Notering vid kapitelmeta-generering:", e)
        return f"Insikt: {user_message[:25]}...", f"Reflektion kring: {user_message}"

def extract_and_save_memory(user_id, user_message):
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key or not supabase_client:
        print("⚠️ Saknar OpenAI API Key eller Supabase Client vid minnesextrahering!")
        return
    
    try:
        client = openai.OpenAI(api_key=api_key)
        prompt = (
            "Du är minnesredaktör för Falk. Analysera om meddelandet innehåller en långsiktig insikt, värdering, Nordstjärna eller hinder.\n"
            f"Meddelande: \"{user_message}\"\n\n"
            "Returnera JSON exakt på formatet:\n"
            "{\"has_memory\": true, \"category\": \"LONG_TERM\", \"content\": \"Beskrivning av minnet\"}\n"
            "Sätt has_memory till true om meddelandet innehåller viktiga värderingar, Nordstjärna, rädsla, mål eller insikter."
        )
        res = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[{'role': 'system', 'content': prompt}],
            max_tokens=150,
            temperature=0.2
        )
        content = res.choices[0].message.content.strip()
        if "```" in content:
            content = content.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(content)
        
        print(f"🔍 Minnes-LLM Parsad utskrift: {parsed}")

        if parsed.get('has_memory'):
            # Inkludera category för att uppfylla Supabase NOT NULL constraint
            memory_data = {
                'user_id': user_id,
                'category': parsed.get('category', 'LONG_TERM'),
                'content': parsed.get('content', user_message)
            }
            db_res = supabase_client.table('falk_memory').insert(memory_data).execute()
            print(f"✅ Supabase Insert Framgångsrik i falk_memory: {db_res.data}")
        else:
            print("ℹ️ Ingen minnesmarkör identifierades av LLM.")
    except Exception as e:
        print("❌ FEL VID MINNESEXTRAHERING:", e)

@dialogue_bp.route('/schema-check', methods=['GET'])
def schema_check():
    try:
        if supabase_client:
            res = supabase_client.table('falk_memories').select('*').limit(1).execute()
            columns = []
            if hasattr(res, 'data') and res.data and len(res.data) > 0:
                columns = list(res.data[0].keys())
            return jsonify({'status': 'success', 'columns': columns, 'raw_sample': res.data}), 200
        return jsonify({'status': 'error', 'message': 'Supabase client ej initierad'}), 500
    except Exception as err:
        return jsonify({'status': 'error', 'message': str(err)}), 500

@dialogue_bp.route('/turn', methods=['POST'])
@dialogue_bp.route('/chat', methods=['POST'])
def dialogue_turn():
    try:
        raw_data = request.get_data(as_text=True)
        data = {}
        if raw_data:
            try:
                data = json.loads(raw_data)
            except Exception:
                pass
        
        raw_user_id = str(data.get('user_id', 'anonymous'))
        user_id = ensure_uuid(raw_user_id)
        user_message = str(data.get('message', ''))
        
        is_guest = data.get('is_guest', False) or data.get('guest_uuid') is not None
        guest_uuid = data.get('guest_uuid') or (user_id if is_guest else None)

        if is_guest and guest_uuid and supabase_client:
            try:
                rpc_res = supabase_client.rpc('check_guest_message_limit', {'p_guest_uuid': guest_uuid}).execute()
                if rpc_res and hasattr(rpc_res, 'data') and rpc_res.data is False:
                    return jsonify({
                        'status': 'paywall',
                        'paywall': True,
                        'message': 'Du har nått din dagsgräns på 6 meddelanden som gäst. Skapa ett konto för obegränsad tillgång till FALK.'
                    }), 402
            except Exception as limit_err:
                print('⚠️ Limit check bypass note:', limit_err)

        user_journal = []
        history_context = ""

        if supabase_client and user_message:
            try:
                extract_and_save_memory(user_id, user_message)

                j_res = supabase_client.table('falk_compass_journal').select('*').eq('user_id', user_id).order('chapter_number').execute()
                if j_res and hasattr(j_res, 'data') and j_res.data:
                    user_journal = j_res.data
                    past_summaries = [f"Kapitel {j['chapter_number']} ({j['chapter_title']}): {j['summary']}" for j in user_journal[-5:]]
                    if past_summaries:
                        history_context = "\n\nTIDIGARE DIALOGER OCH KAPITEL I ANVÄNDARENS RESA:\n" + "\n".join(past_summaries)

                mem_res = supabase_client.table('falk_memories').select('*').eq('user_id', user_id).execute()
                if mem_res and hasattr(mem_res, 'data') and mem_res.data:
                    mem_list = [f"- Minne: {m.get('content', '')}" for m in mem_res.data[-5:]]
                    if mem_list:
                        history_context += "\n\nANVÄNDARENS LÅNGSIKTIGA MINNEN OCH NORDSTJÄRNA:\n" + "\n".join(mem_list)

                should_update_existing = False
                latest_entry = None
                if user_journal:
                    latest_entry = user_journal[-1]
                    created_str = latest_entry.get('created_at')
                    if created_str:
                        try:
                            created_dt = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                            now_dt = datetime.now(timezone.utc)
                            diff_minutes = (now_dt - created_dt).total_seconds() / 60.0
                            if diff_minutes < 30:
                                should_update_existing = True
                        except Exception:
                            pass

                if should_update_existing and latest_entry:
                    entry_id = latest_entry['id']
                    c_title, c_summary = generate_chapter_meta(user_message, latest_entry.get('summary', ''))
                    supabase_client.table('falk_compass_journal').update({
                        'chapter_title': c_title,
                        'summary': c_summary
                    }).eq('id', entry_id).execute()
                else:
                    next_chap = len(user_journal) + 1
                    c_title, c_summary = generate_chapter_meta(user_message)
                    journal_entry = {
                        'user_id': user_id,
                        'chapter_number': next_chap,
                        'chapter_title': c_title,
                        'summary': c_summary
                    }
                    supabase_client.table('falk_compass_journal').insert(journal_entry).execute()

                j_res_updated = supabase_client.table('falk_compass_journal').select('*').eq('user_id', user_id).order('chapter_number').execute()
                if j_res_updated and hasattr(j_res_updated, 'data') and j_res_updated.data:
                    user_journal = j_res_updated.data
            except Exception as db_err:
                print('⚠️ Supabase DB Op Note:', db_err)

        if not user_journal and user_message:
            if user_id not in in_memory_journals:
                in_memory_journals[user_id] = []
            next_num = len(in_memory_journals[user_id]) + 1
            c_title, c_summary = generate_chapter_meta(user_message)
            entry = {
                'chapter_number': next_num,
                'chapter_title': c_title,
                'summary': c_summary,
                'user_id': user_id
            }
            in_memory_journals[user_id].append(entry)
            user_journal = in_memory_journals[user_id]

        api_key = os.environ.get('OPENAI_API_KEY')
        falk_reply = ''
        if api_key and user_message:
            try:
                client = openai.OpenAI(api_key=api_key)
                data = request.get_json() or {}
                focus_scores = data.get('focus', {})
                focus_context = ""
                if focus_scores:
                    focus_context = "\n\nAKTUELLA FOKUSOMRÅDEN FRÅN ANVÄNDAREN:\n" + "\n".join([f"- {k}: {v}%" for k, v in focus_scores.items()]) + "\nAnpassa ton, tempo och vägledning utifrån dessa nivåer."

                full_system_prompt = build_falk_system_prompt(user_id=raw_user_id, current_dialogue_stage='TRYGGHET', user_message=user_message, focus_sliders=focus_scores, user_context=history_context)
                comp = client.chat.completions.create(
                    model='gpt-4o-mini',
                    messages=[
                        {'role': 'system', 'content': full_system_prompt},
                        {'role': 'user', 'content': user_message}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                falk_reply = comp.choices[0].message.content
            except Exception as llm_err:
                print('⚠️ LLM Call Error:', llm_err)
                falk_reply = f'Falk stannade upp: {llm_err}'
        else:
            falk_reply = f'Falk hör dig: {user_message}'

        formatted_journal = []
        for item in user_journal:
            item_copy = dict(item)
            item_copy['raw_user_id'] = raw_user_id
            formatted_journal.append(item_copy)

        return jsonify({
            'status': 'success',
            'reply': falk_reply,
            'journal': formatted_journal,
            'user_id': raw_user_id
        }), 200

    except Exception as err:
        print('❌ CRITICAL ROUTER ERROR:', err)
        return jsonify({
            'status': 'error',
            'reply': 'Falk stannade upp och behövde ett ögonblick.',
            'journal': [],
            'user_id': 'fallback'
        }), 500

@dialogue_bp.route('/journal/<raw_user_id>', methods=['GET'])
def get_user_journal(raw_user_id):
    try:
        user_id = ensure_uuid(raw_user_id)
        if supabase_client:
            res = supabase_client.table('falk_compass_journal').select('*').eq('user_id', user_id).order('chapter_number').execute()
            raw_data = res.data if hasattr(res, 'data') and res.data is not None else []
            formatted = []
            for d in raw_data:
                d_copy = dict(d)
                d_copy['raw_user_id'] = raw_user_id
                formatted.append(d_copy)
            return jsonify({
                'status': 'success',
                'journal': formatted,
                'user_id': raw_user_id
            }), 200
        else:
            return jsonify({
                'status': 'success',
                'journal': in_memory_journals.get(user_id, []),
                'user_id': raw_user_id
            }), 200
    except Exception as err:
        return jsonify({'status': 'error', 'message': str(err)}), 500

@dialogue_bp.route('/memories/<raw_user_id>', methods=['GET'])
def get_user_memories(raw_user_id):
    try:
        user_id = ensure_uuid(raw_user_id)
        if supabase_client:
            # Läs från bas-tabellen falk_memory istället för vyn falk_memories
            res = supabase_client.table('falk_memory').select('*').eq('user_id', user_id).execute()
            raw_data = res.data if hasattr(res, 'data') and res.data is not None else []
            return jsonify({
                'status': 'success',
                'memories': raw_data,
                'user_id': raw_user_id
            }), 200
        else:
            return jsonify({'status': 'success', 'memories': [], 'user_id': raw_user_id}), 200
    except Exception as err:
        return jsonify({'status': 'error', 'message': str(err)}), 500

@dialogue_bp.route('/reset/<raw_user_id>', methods=['POST', 'DELETE'])
def reset_user_journal(raw_user_id):
    try:
        user_id = ensure_uuid(raw_user_id)
        if supabase_client:
            supabase_client.table('falk_compass_journal').delete().eq('user_id', user_id).execute()
            supabase_client.table('falk_memory').delete().eq('user_id', user_id).execute()
        if user_id in in_memory_journals:
            in_memory_journals[user_id] = []
        return jsonify({
            'status': 'success',
            'message': f'Journal och minnen rensade för användare {raw_user_id}'
        }), 200
    except Exception as err:
        return jsonify({'status': 'error', 'message': str(err)}), 500


# ----------------------------------------------------
# ----------------------------------------------------
# ----------------------------------------------------
# PERSISTENCE ENDPOINTS (Insikter, Påminnelser & Mål)
# ----------------------------------------------------
def _build_insert_payload(data, item_type, text):
    raw_user_id = data.get('user_id', '')
    dummy_uuid = '00000000-0000-0000-0000-000000000000'
    payload = {
        'type': item_type,
        'content': text
    }
    if not raw_user_id or raw_user_id == dummy_uuid:
        payload['user_id'] = None
        payload['guest_uuid'] = raw_user_id or dummy_uuid
    else:
        payload['user_id'] = raw_user_id
    return payload

@dialogue_bp.route('/insights', methods=['GET', 'POST', 'OPTIONS'])
def handle_insights():
    from flask import request, jsonify
    supabase = get_supabase()
    if request.method == 'POST':
        data = request.get_json() or {}
        text = data.get('text', '')
        if not text:
            return jsonify({'error': 'Missing text'}), 400
        payload = _build_insert_payload(data, 'insikt', text)
        res = supabase.table('user_insights').insert(payload).execute()
        return jsonify({'status': 'success', 'data': res.data}), 201
    else:
        user_id = request.args.get('user_id', '00000000-0000-0000-0000-000000000000')
        res = supabase.table('user_insights').select('*').or_(f"user_id.eq.{user_id},guest_uuid.eq.{user_id}").eq('type', 'insikt').execute()
        return jsonify({'insights': res.data}), 200

@dialogue_bp.route('/reminders', methods=['GET', 'POST', 'OPTIONS'])
def handle_reminders():
    from flask import request, jsonify
    supabase = get_supabase()
    if request.method == 'POST':
        data = request.get_json() or {}
        text = data.get('text', '')
        if not text:
            return jsonify({'error': 'Missing text'}), 400
        payload = _build_insert_payload(data, 'påminnelse', text)
        res = supabase.table('user_insights').insert(payload).execute()
        return jsonify({'status': 'success', 'data': res.data}), 201
    else:
        user_id = request.args.get('user_id', '00000000-0000-0000-0000-000000000000')
        res = supabase.table('user_insights').select('*').or_(f"user_id.eq.{user_id},guest_uuid.eq.{user_id}").eq('type', 'påminnelse').execute()
        return jsonify({'reminders': res.data}), 200

@dialogue_bp.route('/goals', methods=['GET', 'POST', 'OPTIONS'])
def handle_goals():
    from flask import request, jsonify
    supabase = get_supabase()
    if request.method == 'POST':
        data = request.get_json() or {}
        text = data.get('text', '')
        if not text:
            return jsonify({'error': 'Missing text'}), 400
        payload = _build_insert_payload(data, 'mål', text)
        res = supabase.table('user_insights').insert(payload).execute()
        return jsonify({'status': 'success', 'data': res.data}), 201
    else:
        user_id = request.args.get('user_id', '00000000-0000-0000-0000-000000000000')
        res = supabase.table('user_insights').select('*').or_(f"user_id.eq.{user_id},guest_uuid.eq.{user_id}").eq('type', 'mål').execute()
        return jsonify({'goals': res.data}), 200
