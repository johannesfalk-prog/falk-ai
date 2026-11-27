from prompt_builder import build_falk_system_prompt
from safety_guardrails import evaluate_safety_and_crisis
from gate_checker import validate_response_against_gates
from state_machine import FalkStateMachine

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

def _verify_bearer_uid():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ', 1)[1].strip()
    if not token:
        return None
    if supabase_client:
        try:
            u_res = supabase_client.auth.get_user(token)
            user_obj = getattr(u_res, 'user', None) or (u_res.get('user') if isinstance(u_res, dict) else None)
            uid = getattr(user_obj, 'id', None) or (user_obj.get('id') if isinstance(user_obj, dict) else None)
            if uid:
                return str(uid)
        except Exception:
            pass
    jwt_secret = os.environ.get('SUPABASE_JWT_SECRET', '')
    if jwt_secret:
        try:
            import jwt
            payload = jwt.decode(token, jwt_secret, algorithms=['HS256'], options={'verify_aud': False})
            sub = payload.get('sub')
            if sub:
                return str(sub)
        except Exception:
            pass
    return None

def _authorize_user(raw_user_id):
    auth_uid = _verify_bearer_uid()
    if not auth_uid:
        return None, (jsonify({'status': 'error', 'message': 'Autentisering krävs.'}), 401)
    user_id = ensure_uuid(raw_user_id)
    if ensure_uuid(auth_uid) != user_id:
        return None, (jsonify({'status': 'error', 'message': 'Åtkomst nekad.'}), 403)
    if not supabase_client:
        return None, (jsonify({'status': 'error', 'message': 'Databas ej tillgänglig.'}), 503)
    return user_id, None

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
            res = supabase_client.table('falk_memory').select('*').limit(1).execute()
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
        raw_conversation_id = data.get('conversation_id') or data.get('session_id')
        conversation_id = None
        if raw_conversation_id:
            try:
                conversation_id = str(uuid.UUID(str(raw_conversation_id)))
            except Exception:
                conversation_id = None
        
        is_guest = data.get('is_guest', False) or data.get('guest_uuid') is not None
        guest_uuid = data.get('guest_uuid') or (user_id if is_guest else None)

        if is_guest:
            if not guest_uuid or not supabase_client:
                return jsonify({
                    'status': 'error',
                    'message': 'Gästkontroll tillfälligt otillgänglig. Försök igen eller logga in.'
                }), 503
            try:
                rpc_res = supabase_client.rpc('check_guest_message_limit', {'p_guest_uuid': guest_uuid}).execute()
                if rpc_res and hasattr(rpc_res, 'data') and rpc_res.data is False:
                    return jsonify({
                        'status': 'paywall',
                        'paywall': True,
                        'message': 'Du har nått din dagsgräns på 6 meddelanden som gäst. Skapa ett konto för obegränsad tillgång till FALK.'
                    }), 402
            except Exception as limit_err:
                print('⚠️ Guest limit fail-closed block:', limit_err)
                return jsonify({
                    'status': 'error',
                    'message': 'Kunde inte verifiera gästgräns just nu. Försök igen om en stund.'
                }), 503

        safety_flags = {}
        if user_message:
            is_safe, crisis_reply, safety_flags = evaluate_safety_and_crisis(user_message, is_guest=bool(is_guest))
            if not is_safe:
                return jsonify({
                    'status': 'success',
                    'reply': crisis_reply,
                    'response': crisis_reply,
                    'message': crisis_reply,
                    'journal': [],
                    'user_id': raw_user_id,
                    'safety_triggered': True
                }), 200

        user_journal = []
        history_context = ""

        if supabase_client and user_message and not is_guest:
            try:
                extract_and_save_memory(user_id, user_message)

                j_res = supabase_client.table('falk_compass_journal').select('*').eq('user_id', user_id).order('chapter_number').execute()
                if j_res and hasattr(j_res, 'data') and j_res.data:
                    user_journal = j_res.data
                    past_summaries = [f"Kapitel {j['chapter_number']} ({j['chapter_title']}): {j['summary']}" for j in user_journal[-5:]]
                    if past_summaries:
                        history_context = "\n\nTIDIGARE DIALOGER OCH KAPITEL I ANVÄNDARENS RESA:\n" + "\n".join(past_summaries)

                mem_res = supabase_client.table('falk_memory').select('*').eq('user_id', user_id).execute()
                if mem_res and hasattr(mem_res, 'data') and mem_res.data:
                    mem_list = [f"- Minne: {m.get('content', '')}" for m in mem_res.data[-5:]]
                    if mem_list:
                        history_context += "\n\nANVÄNDARENS LÅNGSIKTIGA MINNEN OCH NORDSTJÄRNA:\n" + "\n".join(mem_list)

                should_update_existing = False
                latest_entry = None
                if user_journal:
                    latest_entry = user_journal[-1]
                    same_session = (
                        not conversation_id
                        or latest_entry.get('conversation_id') in (None, conversation_id)
                    )
                    created_str = latest_entry.get('created_at')
                    if same_session and created_str:
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
                    update_payload = {
                        'chapter_title': c_title,
                        'summary': c_summary
                    }
                    if conversation_id and not latest_entry.get('conversation_id'):
                        update_payload['conversation_id'] = conversation_id
                    supabase_client.table('falk_compass_journal').update(update_payload).eq('id', entry_id).execute()
                else:
                    next_chap = len(user_journal) + 1
                    c_title, c_summary = generate_chapter_meta(user_message)
                    journal_entry = {
                        'user_id': user_id,
                        'chapter_number': next_chap,
                        'chapter_title': c_title,
                        'summary': c_summary
                    }
                    if conversation_id:
                        journal_entry['conversation_id'] = conversation_id
                    supabase_client.table('falk_compass_journal').insert(journal_entry).execute()

                j_res_updated = supabase_client.table('falk_compass_journal').select('*').eq('user_id', user_id).order('chapter_number').execute()
                if j_res_updated and hasattr(j_res_updated, 'data') and j_res_updated.data:
                    user_journal = j_res_updated.data
            except Exception as db_err:
                print('⚠️ Supabase DB Op Note:', db_err)

        api_key = os.environ.get('OPENAI_API_KEY')
        falk_reply = ''
        active_stage = 'TRYGGHET'
        resolved_num = 1
        max_questions = 2
        if api_key and user_message:
            try:
                import inspect
                client = openai.OpenAI(api_key=api_key)
                if not data:
                    data = request.get_json(silent=True) or {}
                focus_scores = data.get('focus', {}) if isinstance(data.get('focus'), dict) else {}

                hist = data.get('history') if isinstance(data.get('history'), list) else []
                turn_count = (len(hist) // 2) + 1 if hist else 1
                raw_stage = data.get('stage') or data.get('current_stage')
                if raw_stage:
                    curr_num, _ = FalkStateMachine.normalize_stage(raw_stage)
                    raw_phase_turns = data.get('turns_in_current_phase')
                    if raw_phase_turns is not None:
                        turns_in_phase = max(1, int(raw_phase_turns))
                    else:
                        turns_in_phase = turn_count if curr_num == 1 else 1
                else:
                    curr_num = min(turn_count, 7)
                    turns_in_phase = 1

                prop_num = min(curr_num + 1, 7) if turn_count > 1 else curr_num

                has_caution_signal = (
                    bool(safety_flags.get('is_crisis'))
                    or safety_flags.get('risk_level') == 'high'
                    or ('PROFESSIONELL GRÄNSDRAGNING' in (safety_flags.get('safety_instructions') or ''))
                )
                stress_val = 0
                for k, v in focus_scores.items():
                    if 'stress' in str(k).lower():
                        try:
                            stress_val = max(stress_val, float(v))
                        except (ValueError, TypeError):
                            pass
                msg_lower = user_message.lower()
                stress_markers = (
                    'stressad', 'överväldigad', 'hinner inte', 'allt snurrar',
                    'orkar inte', 'panik', 'utmattad', 'för mycket', 'hjärtklappning', 'inre brus'
                )
                is_stressed = has_caution_signal or stress_val >= 60 or any(m in msg_lower for m in stress_markers)
                max_questions = 1 if is_stressed else 2

                crisis_st = 'FAIL_SAFE_CAUTION' if has_caution_signal else 'SAFE'
                resolved_num = FalkStateMachine.resolve_next_phase(
                    curr_num,
                    prop_num,
                    turns_in_phase,
                    crisis_st,
                    is_stressed=is_stressed,
                )
                _, active_stage = FalkStateMachine.normalize_stage(resolved_num)

                recent_assistant_messages = [
                    str(h_item.get('content', '')).strip()
                    for h_item in hist
                    if isinstance(h_item, dict)
                    and h_item.get('role') == 'assistant'
                    and str(h_item.get('content', '')).strip()
                ][-6:]

                user_hist_items = [
                    " ".join(str(h_item.get('content', '')).split())
                    for h_item in hist
                    if isinstance(h_item, dict)
                    and h_item.get('role') == 'user'
                    and str(h_item.get('content', '')).strip()
                ]
                summary_lines = []
                if user_hist_items:
                    summary_lines.append(f"Ursprungligt startfokus: \"{user_hist_items[0][:160]}\"")
                if len(hist) > 20:
                    older_user_items = [
                        " ".join(str(h_item.get('content', '')).split())
                        for h_item in hist[:-20]
                        if isinstance(h_item, dict)
                        and h_item.get('role') == 'user'
                        and str(h_item.get('content', '')).strip()
                    ]
                    if older_user_items:
                        older_joined = " | ".join(f'"{u[:110]}"' for u in older_user_items[-4:])
                        summary_lines.append(f"Tidigare spår före senaste 20 meddelanden: {older_joined}")
                summary_lines.append(f"Aktiv fas: {active_stage} (turer i fas: {turns_in_phase})")
                if len(user_hist_items) >= 2:
                    recent_trail = " -> ".join(f'"{u[:90]}"' for u in user_hist_items[-4:])
                    summary_lines.append(f"Senaste användarspår i sessionen: {recent_trail}")
                if focus_scores:
                    active_focus = [
                        f"{k}:{v}%" for k, v in focus_scores.items()
                        if isinstance(v, (int, float)) and v > 0
                    ]
                    if active_focus:
                        summary_lines.append(f"Fokusreglage: {', '.join(active_focus[:3])}")
                summary_lines.append("Samtalsmål: ömsesidig förståelse — översätt positioner till behov, pröva motpartens perspektiv utan att döma och bygg gemensam förståelse.")
                if safety_flags.get("circle_warning") or safety_flags.get("loop_warning") or safety_flags.get("stuck_pattern"):
                    summary_lines.append("Cirkelvarning: möjligen återkommande spår; sänk tempot och pröva perspektiv eller minsta steg.")
                if safety_flags.get("needs_analysis") or safety_flags.get("core_need"):
                    need_val = safety_flags.get("core_need") or safety_flags.get("needs_analysis")
                    summary_lines.append(f"Behovshypotes (ej fastställd): {str(need_val)[:80]}")
                session_working_summary = "\n".join(summary_lines)[:750]

                raw_session_mode = data.get('session_mode')
                if isinstance(raw_session_mode, str) and raw_session_mode.strip():
                    resolved_session_mode = {'track': raw_session_mode.strip()}
                elif isinstance(raw_session_mode, dict):
                    resolved_session_mode = raw_session_mode
                else:
                    resolved_session_mode = None

                raw_card_ctx = data.get('card_context')
                resolved_card_context = raw_card_ctx if isinstance(raw_card_ctx, dict) else None

                pb_kwargs = dict(
                    user_id=raw_user_id,
                    current_dialogue_stage=active_stage,
                    is_guest=bool(is_guest),
                    user_message=user_message,
                    focus_sliders=focus_scores,
                    user_context=history_context,
                    safety_instructions=safety_flags.get('safety_instructions'),
                    recent_assistant_messages=recent_assistant_messages,
                    is_new_session=(len(hist) == 0),
                    turns_in_current_phase=turns_in_phase,
                    is_stressed=is_stressed,
                    max_questions=max_questions,
                    session_working_summary=session_working_summary,
                    session_mode=resolved_session_mode,
                    card_context=resolved_card_context,
                )
                pb_params = inspect.signature(build_falk_system_prompt).parameters
                if not any(p.kind == inspect.Parameter.VAR_KEYWORD for p in pb_params.values()):
                    pb_kwargs = {k: v for k, v in pb_kwargs.items() if k in pb_params}
                full_system_prompt = build_falk_system_prompt(**pb_kwargs)

                llm_messages = [{'role': 'system', 'content': full_system_prompt}]
                for h_item in hist[-20:]:
                    if isinstance(h_item, dict):
                        h_role = h_item.get('role')
                        h_content = str(h_item.get('content', '')).strip()
                        if h_role in ('user', 'assistant') and h_content:
                            llm_messages.append({'role': h_role, 'content': h_content})
                if not llm_messages or llm_messages[-1].get('role') != 'user' or llm_messages[-1].get('content') != user_message.strip():
                    llm_messages.append({'role': 'user', 'content': user_message})

                comp = client.chat.completions.create(
                    model='gpt-4o-mini',
                    messages=llm_messages,
                    max_tokens=500,
                    temperature=0.7
                )
                raw_reply = comp.choices[0].message.content
                try:
                    gc_kwargs = dict(
                        proposed_response=raw_reply,
                        user_message=user_message,
                        active_stage=active_stage,
                        is_guest=bool(is_guest),
                        max_questions=max_questions,
                        is_stressed=is_stressed,
                    )
                    gc_params = inspect.signature(validate_response_against_gates).parameters
                    if not any(p.kind == inspect.Parameter.VAR_KEYWORD for p in gc_params.values()):
                        gc_kwargs = {k: v for k, v in gc_kwargs.items() if k in gc_params}
                    _, falk_reply, _ = validate_response_against_gates(**gc_kwargs)
                except Exception as gate_err:
                    print('⚠️ Gate checker fallback:', gate_err)
                    falk_reply = raw_reply
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
            'user_id': raw_user_id,
            'stage': active_stage,
            'stage_num': resolved_num,
            'max_questions': max_questions
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
        user_id, auth_err = _authorize_user(raw_user_id)
        if auth_err:
            return auth_err
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
    except Exception as err:
        return jsonify({'status': 'error', 'message': str(err)}), 500

@dialogue_bp.route('/memories/<raw_user_id>', methods=['GET'])
def get_user_memories(raw_user_id):
    try:
        user_id, auth_err = _authorize_user(raw_user_id)
        if auth_err:
            return auth_err
        res = supabase_client.table('falk_memory').select('*').eq('user_id', user_id).execute()
        raw_data = res.data if hasattr(res, 'data') and res.data is not None else []
        return jsonify({
            'status': 'success',
            'memories': raw_data,
            'user_id': raw_user_id
        }), 200
    except Exception as err:
        return jsonify({'status': 'error', 'message': str(err)}), 500

@dialogue_bp.route('/reset/<raw_user_id>', methods=['POST', 'DELETE'])
def reset_user_journal(raw_user_id):
    try:
        user_id, auth_err = _authorize_user(raw_user_id)
        if auth_err:
            return auth_err
        supabase_client.table('falk_compass_journal').delete().eq('user_id', user_id).execute()
        supabase_client.table('falk_memory').delete().eq('user_id', user_id).execute()
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
        payload['user_id'] = ensure_uuid(raw_user_id)
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
        user_id = ensure_uuid(request.args.get('user_id', '00000000-0000-0000-0000-000000000000'))
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
        user_id = ensure_uuid(request.args.get('user_id', '00000000-0000-0000-0000-000000000000'))
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
        user_id = ensure_uuid(request.args.get('user_id', '00000000-0000-0000-0000-000000000000'))
        res = supabase.table('user_insights').select('*').or_(f"user_id.eq.{user_id},guest_uuid.eq.{user_id}").eq('type', 'mål').execute()
        return jsonify({'goals': res.data}), 200
