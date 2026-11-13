import os
import re
import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple, List

import requests
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from supabase import create_client, Client

from safety_guardrails import evaluate_safety_and_crisis
from state_machine import FalkStateMachine
from prompt_builder import build_falk_system_prompt
from gate_checker import validate_response_against_gates
from exercise_library import FALK_15_EXERCISE_CARDS, get_library_cards
from pdf_exporter import generate_session_pdf_html

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "").strip()
SUPABASE_KEY = SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY

supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logging.info("Supabase ansluten i app.py")
    except Exception as e:
        logging.error(f"Supabase-anslutningsfel: {e}")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

state_machine = FalkStateMachine()

# Fallback in-memory spärr endast om Supabase RPC tillfälligt ej når fram
_FALLBACK_GUEST_STORE: Dict[str, List[float]] = {}

FOCUS_KEY_MAP = {
    "självförtroende": "sjalvfortroende",
    "sjalvfortroende": "sjalvfortroende",
    "stresshantering": "stresshantering",
    "handlingskraft": "handlingskraft",
    "gränssättning": "granssattning",
    "granssattning": "granssattning",
    "motivation": "motivation",
}


def _normalize_focus_sliders(raw_focus: Any) -> Dict[str, int]:
    normalized = {
        "sjalvfortroende": 0,
        "stresshantering": 0,
        "handlingskraft": 0,
        "granssattning": 0,
        "motivation": 0,
    }
    if not isinstance(raw_focus, dict):
        return normalized
    for k, v in raw_focus.items():
        clean_k = FOCUS_KEY_MAP.get(str(k).strip().lower())
        if clean_k:
            try:
                normalized[clean_k] = max(0, min(100, int(float(v))))
            except (ValueError, TypeError):
                normalized[clean_k] = 0
    return normalized


def _resolve_auth_user() -> Tuple[Optional[str], Optional[str], bool]:
    """
    Verifierar Supabase JWT från Authorization: Bearer <token>.
    Returnerar (user_id, email, is_premium). Saknas eller ogiltig token -> (None, None, False).
    """
    auth_header = request.headers.get("Authorization", "").strip()
    if not auth_header.startswith("Bearer ") or not supabase:
        return None, None, False

    token = auth_header.split(" ", 1)[1].strip()
    if not token or token in ("null", "undefined", "guest"):
        return None, None, False

    try:
        user_resp = supabase.auth.get_user(token)
        user_obj = getattr(user_resp, "user", None)
        if not user_obj or not getattr(user_obj, "id", None):
            return None, None, False

        uid = str(user_obj.id)
        email = getattr(user_obj, "email", None)
        is_premium = False

        try:
            prof = supabase.table("user_profiles").select("is_premium").eq("id", uid).limit(1).execute()
            if prof.data and len(prof.data) > 0:
                is_premium = bool(prof.data[0].get("is_premium", False))
        except Exception as pe:
            logging.warning(f"Kunde inte läsa user_profiles för {uid}: {pe}")

        return uid, email, is_premium
    except Exception as e:
        logging.warning(f"JWT-verifiering misslyckades: {e}")
        return None, None, False


def _get_client_ip() -> str:
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown_ip"


def _check_guest_quota(identifier: str, limit: int = 6) -> Tuple[bool, int]:
    """
    Använder Supabase RPC check_and_increment_guest_limit(p_identifier, p_limit)
    för persistent dygnsbegränsning (max 6 meddelanden/dygn).
    Returnerar (allowed, remaining).
    """
    if supabase:
        try:
            res = supabase.rpc(
                "check_and_increment_guest_limit",
                {"p_identifier": identifier, "p_max_count": limit},
            ).execute()
            data = res.data
            if isinstance(data, list) and len(data) > 0:
                row = data[0]
                allowed = bool(row.get("allowed", False))
                if "remaining" in row and row["remaining"] is not None:
                    rem = int(row["remaining"])
                else:
                    rem = max(0, limit - int(row.get("current_count", limit)))
                return allowed, rem
            if isinstance(data, dict):
                allowed = bool(data.get("allowed", False))
                if "remaining" in data and data["remaining"] is not None:
                    rem = int(data["remaining"])
                else:
                    rem = max(0, limit - int(data.get("current_count", limit)))
                return allowed, rem
        except Exception as e:
            logging.error(f"Supabase guest RPC misslyckades, använder fallback: {e}")

    now = time.time()
    timestamps = [t for t in _FALLBACK_GUEST_STORE.get(identifier, []) if now - t < 86400]
    if len(timestamps) >= limit:
        _FALLBACK_GUEST_STORE[identifier] = timestamps
        return False, 0
    timestamps.append(now)
    _FALLBACK_GUEST_STORE[identifier] = timestamps
    return True, max(0, limit - len(timestamps))


def _call_llm(system_prompt: str, messages_payload: List[Dict[str, str]], max_tokens: int = 650) -> str:
    full_messages = [{"role": "system", "content": system_prompt}] + messages_payload

    if GROQ_API_KEY:
        try:
            res = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": full_messages,
                    "temperature": 0.65,
                    "max_tokens": max_tokens,
                },
                timeout=14,
            )
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"].strip()
            logging.warning(f"Groq API status {res.status_code}: {res.text[:200]}")
        except Exception as e:
            logging.error(f"Groq-anrop misslyckades: {e}")

    if OPENAI_API_KEY:
        try:
            import openai
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=full_messages,
                temperature=0.65,
                max_tokens=max_tokens,
            )
            return res.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"OpenAI-anrop misslyckades: {e}")

    last_user = next((m["content"] for m in reversed(messages_payload) if m["role"] == "user"), "")
    return (
        f"Jag hör att du bär på tankar kring \"{last_user[:120]}\". "
        "Om vi lyfter blicken ett ögonblick – vad känns viktigast för dig att få klarhet i just nu?"
    )


FORBIDDEN_FALK_PHRASES = (
    "du borde",
    "du måste",
    "det enda du behöver göra",
    "du är grym",
    "fantastiskt!",
    "wow!",
    "lita på mig",
    "garanterat",
)


def _apply_gate_filter(
    reply: str,
    user_message: str,
    stage: str,
    system_prompt: str,
    is_guest: bool = True,
) -> str:
    """
    Kör svaret genom The Five Gates™ (Falk Bible Kap. 4 & Falk Playbook Kap. 4.19)
    inklusive åldersanpassad trygghetskontroll i gästläge.
    """
    lowered = reply.lower()
    hits = [p for p in FORBIDDEN_FALK_PHRASES if p in lowered]
    if hits:
        logging.info(f"Deterministiskt Gate-filter fångade förbjudna fraser: {hits}")
        age_guard = (
            " Säkerställ även att svaret är tryggt och åldersanpassat för minderåriga i gästläge."
            if is_guest
            else ""
        )
        repair_instruction = (
            f"{system_prompt}\n\n"
            f"[KVALITETSKORRIGERING — THE FIVE GATES]: Ditt utkast innehöll förbjudna mentorformuleringar "
            f"({', '.join(hits)}). Skriv om svaret lugnt, utforskande och utan att styra användaren.{age_guard}"
        )
        reply = _call_llm(
            repair_instruction,
            [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": reply},
                {"role": "user", "content": "Skriv om svaret så att det följer alla FALK-principer."},
            ],
        )

    passed, final_response, meta = validate_response_against_gates(
        proposed_response=reply,
        user_message=user_message,
        active_stage=stage,
        is_guest=is_guest,
    )
    if not passed:
        logging.info(f"Five Gates justerade svar: {meta.get('violated_gates')} - {meta.get('feedback')}")
    return final_response or reply


def _fetch_user_continuity(uid: str) -> Tuple[List[str], Optional[str]]:
    """
    Hämtar sparade insikter och senaste kompasskalibrering för inloggad användare.
    """
    memories: List[str] = []
    compass_summary: Optional[str] = None
    if not supabase:
        return memories, compass_summary

    try:
        ins = (
            supabase.table("user_insights")
            .select("content")
            .eq("user_id", uid)
            .order("created_at", desc=True)
            .limit(4)
            .execute()
        )
        if ins.data:
            memories = [row["content"] for row in ins.data if row.get("content")]
    except Exception as e:
        logging.warning(f"Kunde inte hämta kontinuitetsinsikter: {e}")

    try:
        comp = (
            supabase.table("compass_scores")
            .select("scores, created_at")
            .eq("user_id", uid)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        if comp.data and comp.data[0].get("scores"):
            compass_summary = str(comp.data[0]["scores"])
    except Exception as e:
        logging.warning(f"Kunde inte hämta kompassläge: {e}")

    return memories, compass_summary


# ---------------------------------------------------------------------------
# HEALTH & SYSTEM
# ---------------------------------------------------------------------------
@app.route("/", methods=["GET"])
@app.route("/health", methods=["GET"])
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "FALK Wisdom Engine API",
        "version": "2.0.0",
        "supabase_connected": bool(supabase),
        "groq_available": bool(GROQ_API_KEY),
        "openai_available": bool(OPENAI_API_KEY),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }), 200


# ---------------------------------------------------------------------------
# CHAT & DIALOGUE ENGINE (7 FASER + 5 FOKUSREGLAGE + GÄSTSPÄRR + GATE CHECKER)
# ---------------------------------------------------------------------------
@app.route("/api/chat", methods=["POST", "OPTIONS"])
def handle_chat():
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()
    if not message:
        return jsonify({"status": "error", "message": "Meddelandet kan inte vara tomt."}), 400

    auth_uid, _, is_premium = _resolve_auth_user()
    is_guest = auth_uid is None
    user_tier = "guest" if is_guest else ("premium" if is_premium else "free")

    guest_remaining = None
    if is_guest:
        client_ip = _get_client_ip()
        if client_ip == "unknown_ip":
            ua = request.headers.get("User-Agent", "")
            identifier = f"unknown_ip_{abs(hash(ua)) % 10**10}"
        else:
            identifier = client_ip
        allowed, guest_remaining = _check_guest_quota(identifier, limit=6)
        if not allowed:
            return jsonify({
                "status": "error",
                "code": "GUEST_LIMIT_REACHED",
                "remaining": 0,
                "message": "Du har använt dina 6 kostnadsfria meddelanden för idag. Skapa ett konto (18+) för att fortsätta utforska med FALK.",
            }), 403

    # Steg 1 i Beslutspyramiden: Säkerhet & Akut kris (inkl. gästskydd)
    is_safe, refusal_text, flag_data = evaluate_safety_and_crisis(message, is_guest=is_guest)
    if not is_safe:
        return jsonify({
            "status": "success",
            "reply": refusal_text,
            "stage": "KRIS_OVERRIDE",
            "flagged": True,
            "flag_data": flag_data,
            "guest_remaining": guest_remaining,
        }), 200

    # Samtalsfas via FalkStateMachine
    raw_history = data.get("history") if isinstance(data.get("history"), list) else []
    clean_history: List[Dict[str, str]] = []
    for item in raw_history[-8:]:
        if isinstance(item, dict) and item.get("role") in ("user", "assistant") and item.get("content"):
            clean_history.append({"role": item["role"], "content": str(item["content"])[:2000]})

    curr_num, _ = state_machine.normalize_stage(data.get("stage", "TRYGGHET"))
    user_turns = sum(1 for m in clean_history if m.get("role") == "user") + 1
    proposed_num = min(7, max(1, user_turns))
    next_num = state_machine.resolve_next_phase(
        current_phase=curr_num,
        proposed_phase=proposed_num,
        turns_in_current_phase=user_turns,
        crisis_status="NONE",
    )
    _, next_stage = state_machine.normalize_stage(next_num)

    focus_sliders = _normalize_focus_sliders(data.get("focus"))
    mode = str(data.get("mode", "normal")).lower()
    variant_map = {
        "normal": "default",
        "default": "default",
        "regenerate": "alternative",
        "new_response": "alternative",
        "alternative": "alternative",
        "longer": "deeper",
        "deeper": "deeper",
        "shorter": "concise",
        "concise": "concise",
    }
    response_variant = variant_map.get(mode, "default")
    if response_variant in ("deeper", "concise") and (is_guest or user_tier != "premium"):
        return jsonify({
            "status": "error",
            "code": "PREMIUM_REQUIRED",
            "message": "Fördjupning (+) och komprimering (-) kräver FALK Premium.",
        }), 403

    memories, compass_summary = ([], None)
    if not is_guest and auth_uid:
        memories, compass_summary = _fetch_user_continuity(auth_uid)

    system_prompt = build_falk_system_prompt(
        user_message=message,
        current_stage=next_stage,
        is_guest=is_guest,
        focus_sliders=focus_sliders,
        user_context_memories=memories,
        compass_summary=compass_summary,
        response_variant=response_variant,
    )

    convo_messages = clean_history + [{"role": "user", "content": message}]
    raw_reply = _call_llm(system_prompt, convo_messages)
    final_reply = _apply_gate_filter(
        raw_reply,
        message,
        next_stage,
        system_prompt,
        is_guest=is_guest,
    )

    conversation_id = data.get("conversation_id")
    if supabase and not is_guest and auth_uid:
        try:
            if not conversation_id:
                conv_res = supabase.table("conversations").insert({
                    "user_id": auth_uid,
                    "title": message[:60],
                }).execute()
                if conv_res.data:
                    conversation_id = conv_res.data[0].get("id")

            msg_rows = [
                {"user_id": auth_uid, "role": "user", "content": message},
                {"user_id": auth_uid, "role": "assistant", "content": final_reply},
            ]
            if conversation_id:
                msg_rows[0]["conversation_id"] = conversation_id
                msg_rows[1]["conversation_id"] = conversation_id

            supabase.table("messages").insert(msg_rows).execute()
        except Exception as e:
            logging.error(f"Kunde inte spara meddelanden i Supabase: {e}")

    return jsonify({
        "status": "success",
        "reply": final_reply,
        "stage": next_stage,
        "variant": response_variant,
        "user_tier": user_tier,
        "conversation_id": conversation_id,
        "guest_remaining": guest_remaining,
    }), 200


@app.route("/api/message/variation", methods=["POST", "OPTIONS"])
def handle_message_variation():
    """
    Hanterar svarskarusellen i samma bubbla:
    - 'new_response' / 'regenerate' (Tillgänglig för Gäst + Premium)
    - 'longer' (Plus - Enbart Premium)
    - 'shorter' (Minus - Enbart Premium)
    """
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json(silent=True) or {}
    action = str(data.get("action", "regenerate")).lower()
    original_reply = str(data.get("message", "")).strip()
    user_prompt = str(data.get("user_message", "")).strip()

    auth_uid, _, is_premium = _resolve_auth_user()
    is_guest = auth_uid is None

    if action in ("longer", "deeper", "shorter", "concise") and (is_guest or not is_premium):
        return jsonify({
            "status": "error",
            "code": "PREMIUM_REQUIRED",
            "message": "Fördjupning (+) och komprimering (-) kräver FALK Premium.",
        }), 403

    check_target = user_prompt or original_reply
    if not check_target:
        return jsonify({"status": "error", "message": "Underlag för svarsvariation saknas."}), 400

    is_safe, refusal_text, flag_data = evaluate_safety_and_crisis(check_target, is_guest=is_guest)
    if not is_safe:
        return jsonify({
            "status": "success",
            "action": action,
            "variant": "safety_override",
            "reply": refusal_text,
            "flagged": True,
            "flag_data": flag_data,
        }), 200

    variant_map = {
        "new_response": "alternative",
        "regenerate": "alternative",
        "alternative": "alternative",
        "longer": "deeper",
        "deeper": "deeper",
        "shorter": "concise",
        "concise": "concise",
    }
    response_variant = variant_map.get(action, "alternative")
    focus_sliders = _normalize_focus_sliders(data.get("focus"))
    _, active_stage = state_machine.normalize_stage(data.get("stage", "PERSPEKTIV"))

    memories, compass_summary = ([], None)
    if not is_guest and auth_uid:
        memories, compass_summary = _fetch_user_continuity(auth_uid)

    system_prompt = build_falk_system_prompt(
        user_message=check_target,
        current_stage=active_stage,
        is_guest=is_guest,
        focus_sliders=focus_sliders,
        user_context_memories=memories,
        compass_summary=compass_summary,
        response_variant=response_variant,
    )

    context_input = (
        f"Användarens ursprungliga fråga: {user_prompt}\n"
        f"Tidigare FALK-svar att omformulera/justera: {original_reply}"
        if user_prompt
        else original_reply
    )
    raw_reply = _call_llm(system_prompt, [{"role": "user", "content": context_input}])
    final_reply = _apply_gate_filter(
        raw_reply,
        check_target,
        active_stage,
        system_prompt,
        is_guest=is_guest,
    )

    return jsonify({
        "status": "success",
        "action": action,
        "variant": response_variant,
        "reply": final_reply,
    }), 200


# ---------------------------------------------------------------------------
# BIBLIOTEK (15 ÖVNINGSKORT) & PDF-EXPORT
# ---------------------------------------------------------------------------
@app.route("/api/library", methods=["GET", "OPTIONS"])
def api_get_library_cards():
    if request.method == "OPTIONS":
        return "", 200
    auth_uid, _, is_premium = _resolve_auth_user()
    if not auth_uid or not is_premium:
        return jsonify({
            "status": "error",
            "code": "PREMIUM_REQUIRED",
            "message": "Biblioteket kräver FALK Premium.",
        }), 403
    category = request.args.get("category")
    cards = get_library_cards(category) if category else FALK_15_EXERCISE_CARDS
    return jsonify({"status": "success", "count": len(cards), "cards": cards}), 200


@app.route("/api/export/pdf", methods=["POST", "OPTIONS"])
def export_session_pdf():
    if request.method == "OPTIONS":
        return "", 200

    import html as _html
    auth_uid, _, _ = _resolve_auth_user()
    data = request.get_json(silent=True) or {}
    conv_id = str(data.get("conversation_id") or data.get("session_id") or "").strip()
    raw_messages = data.get("messages") if isinstance(data.get("messages"), list) else []
    session_label = str(data.get("title") or conv_id or "Kompasssamtal med FALK").strip()

    if conv_id and not raw_messages:
        if not auth_uid or not supabase:
            return jsonify({"status": "error", "code": "AUTH_REQUIRED", "message": "Inloggning krävs för att exportera sparad session."}), 401
        conv_res = (
            supabase.table("conversations")
            .select("id,title")
            .eq("id", conv_id)
            .eq("user_id", auth_uid)
            .execute()
        )
        if not conv_res.data:
            return jsonify({"status": "error", "code": "NOT_FOUND", "message": "Sessionen hittades inte."}), 404
        db_title = conv_res.data[0].get("title")
        if db_title:
            session_label = str(db_title).strip()
        msg_res = (
            supabase.table("messages")
            .select("role,content")
            .eq("conversation_id", conv_id)
            .eq("user_id", auth_uid)
            .order("id", desc=False)
            .execute()
        )
        raw_messages = msg_res.data or []

    if not raw_messages:
        return jsonify({"status": "error", "code": "BAD_REQUEST", "message": "Inga meddelanden att exportera."}), 400

    sanitized_messages = [
        {
            "role": "assistant" if m.get("role") == "assistant" else "user",
            "content": _html.escape(str(m.get("content", ""))),
        }
        for m in raw_messages
        if isinstance(m, dict) and str(m.get("content", "")).strip()
    ]
    if not sanitized_messages:
        return jsonify({"status": "error", "code": "BAD_REQUEST", "message": "Inga giltiga meddelanden att exportera."}), 400

    html_doc = generate_session_pdf_html(
        session_id=_html.escape(session_label),
        messages=sanitized_messages,
    )
    return Response(html_doc, mimetype="text/html; charset=utf-8")


# ---------------------------------------------------------------------------
# INSIKTER, MÅL, PÅMINNELSER, KOMPASSKALIBRERING & FEEDBACK
# ---------------------------------------------------------------------------
@app.route("/api/insights", methods=["GET", "POST", "DELETE", "OPTIONS"])
def handle_insights():
    if request.method == "OPTIONS":
        return "", 200

    auth_uid, _, is_premium = _resolve_auth_user()
    if not auth_uid or not supabase:
        return jsonify({"status": "error", "code": "AUTH_REQUIRED", "message": "Inloggning krävs."}), 401
    if not is_premium:
        return jsonify({"status": "error", "code": "PREMIUM_REQUIRED", "message": "Insikter kräver FALK Premium."}), 403

    if request.method == "GET":
        res = (
            supabase.table("user_insights")
            .select("*")
            .eq("user_id", auth_uid)
            .order("created_at", desc=True)
            .execute()
        )
        return jsonify({"status": "success", "insights": res.data or []}), 200

    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        text = str(data.get("content") or data.get("text", "")).strip()
        insight_type = str(data.get("type", "insikt")).strip()
        source_context = str(data.get("source_context", "")).strip()
        if not text:
            return jsonify({"status": "error", "message": "Insiktstext saknas."}), 400

        payload = {"user_id": auth_uid, "content": text, "type": insight_type}
        if source_context:
            payload["source_context"] = source_context
        res = supabase.table("user_insights").insert(payload).execute()
        return jsonify({"status": "success", "insight": res.data[0] if res.data else payload}), 201

    if request.method == "DELETE":
        insight_id = request.args.get("id") or (request.get_json(silent=True) or {}).get("id")
        if not insight_id:
            return jsonify({"status": "error", "message": "id saknas."}), 400
        supabase.table("user_insights").delete().eq("id", insight_id).eq("user_id", auth_uid).execute()
        return jsonify({"status": "success"}), 200


@app.route("/api/goals", methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"])
def handle_goals():
    if request.method == "OPTIONS":
        return "", 200

    auth_uid, _, is_premium = _resolve_auth_user()
    if not auth_uid or not supabase:
        return jsonify({"status": "error", "code": "AUTH_REQUIRED", "message": "Inloggning krävs."}), 401
    if not is_premium:
        return jsonify({"status": "error", "code": "PREMIUM_REQUIRED", "message": "Mål kräver FALK Premium."}), 403

    if request.method == "GET":
        res = (
            supabase.table("user_goals")
            .select("*")
            .eq("user_id", auth_uid)
            .order("created_at", desc=True)
            .execute()
        )
        return jsonify({"status": "success", "goals": res.data or []}), 200

    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        title = str(data.get("title", "Nytt mål")).strip()
        area = str(data.get("area", "Personlig utveckling")).strip()
        progress = max(0, min(100, int(data.get("progress", 0))))
        res = supabase.table("user_goals").insert({
            "user_id": auth_uid,
            "title": title,
            "area": area,
            "progress": progress,
        }).execute()
        return jsonify({"status": "success", "goal": res.data[0] if res.data else {}}), 201

    if request.method == "PATCH":
        data = request.get_json(silent=True) or {}
        goal_id = data.get("id")
        if not goal_id:
            return jsonify({"status": "error", "message": "id saknas."}), 400
        updates: Dict[str, Any] = {}
        if "progress" in data:
            updates["progress"] = max(0, min(100, int(data["progress"])))
        if "title" in data:
            updates["title"] = str(data["title"]).strip()
        res = supabase.table("user_goals").update(updates).eq("id", goal_id).eq("user_id", auth_uid).execute()
        return jsonify({"status": "success", "goal": res.data[0] if res.data else {}}), 200

    if request.method == "DELETE":
        goal_id = request.args.get("id") or (request.get_json(silent=True) or {}).get("id")
        if not goal_id:
            return jsonify({"status": "error", "message": "id saknas."}), 400
        supabase.table("user_goals").delete().eq("id", goal_id).eq("user_id", auth_uid).execute()
        return jsonify({"status": "success"}), 200


@app.route("/api/reminders", methods=["GET", "POST", "DELETE", "OPTIONS"])
def handle_reminders():
    if request.method == "OPTIONS":
        return "", 200

    auth_uid, _, is_premium = _resolve_auth_user()
    if not auth_uid or not supabase:
        return jsonify({"status": "error", "code": "AUTH_REQUIRED", "message": "Inloggning krävs."}), 401
    if not is_premium:
        return jsonify({"status": "error", "code": "PREMIUM_REQUIRED", "message": "Påminnelser kräver FALK Premium."}), 403

    if request.method == "GET":
        res = (
            supabase.table("user_reminders")
            .select("*")
            .eq("user_id", auth_uid)
            .order("created_at", desc=True)
            .execute()
        )
        return jsonify({"status": "success", "reminders": res.data or []}), 200

    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        content = str(data.get("content", "")).strip()
        freq = str(data.get("frequency", "daily")).strip()
        remind_at = data.get("remind_at")
        if not content:
            return jsonify({"status": "error", "message": "Påminnelsetext saknas."}), 400

        payload: Dict[str, Any] = {"user_id": auth_uid, "content": content, "frequency": freq}
        if remind_at:
            payload["remind_at"] = remind_at
        res = supabase.table("user_reminders").insert(payload).execute()
        return jsonify({"status": "success", "reminder": res.data[0] if res.data else payload}), 201

    if request.method == "DELETE":
        rem_id = request.args.get("id") or (request.get_json(silent=True) or {}).get("id")
        if not rem_id:
            return jsonify({"status": "error", "message": "id saknas."}), 400
        supabase.table("user_reminders").delete().eq("id", rem_id).eq("user_id", auth_uid).execute()
        return jsonify({"status": "success"}), 200


@app.route("/api/calibration", methods=["GET", "POST", "OPTIONS"])
def handle_calibration():
    if request.method == "OPTIONS":
        return "", 200

    auth_uid, _, is_premium = _resolve_auth_user()
    if request.method == "GET":
        if not auth_uid or not supabase:
            return jsonify({"status": "success", "calibrations": []}), 200
        if not is_premium:
            return jsonify({"status": "error", "code": "PREMIUM_REQUIRED", "message": "Min utveckling kräver FALK Premium."}), 403
        res = (
            supabase.table("compass_scores")
            .select("*")
            .eq("user_id", auth_uid)
            .order("created_at", desc=True)
            .limit(30)
            .execute()
        )
        return jsonify({"status": "success", "calibrations": res.data or []}), 200

    data = request.get_json(silent=True) or {}
    scores = data.get("scores", {})
    if auth_uid and supabase:
        try:
            res = supabase.table("compass_scores").insert({
                "user_id": auth_uid,
                "scores": scores,
            }).execute()
            return jsonify({"status": "success", "data": res.data}), 200
        except Exception as e:
            logging.error(f"Kunde inte spara kompasskalibrering: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    return jsonify({"status": "success", "message": "Gästkalibrering mottagen lokalt.", "data": scores}), 200


@app.route("/api/feedback", methods=["POST", "OPTIONS"])
def handle_feedback():
    if request.method == "OPTIONS":
        return "", 200

    auth_uid, _, _ = _resolve_auth_user()
    data = request.get_json(silent=True) or {}
    rating = data.get("rating")
    msg_id = data.get("message_id")
    text = str(data.get("feedback_text", "")).strip()

    if supabase:
        try:
            supabase.table("falk_system_logs").insert({
                "event_type": "user_feedback",
                "user_id": auth_uid,
                "details": {
                    "message_id": msg_id,
                    "rating": rating,
                    "feedback_text": text,
                },
            }).execute()
        except Exception as e:
            logging.error(f"Kunde inte logga feedback i falk_system_logs: {e}")

    return jsonify({"status": "success", "message": "Feedback mottagen."}), 200


# ---------------------------------------------------------------------------
# GDPR: KOMPLETT DATAEXPORT & PERMANENT RADERING AV KONTO + ALL DATA
# ---------------------------------------------------------------------------
@app.route("/api/user/export", methods=["GET"])
def export_user_data():
    auth_uid, email, _ = _resolve_auth_user()
    if not auth_uid or not supabase:
        return jsonify({"status": "error", "code": "AUTH_REQUIRED", "message": "Inloggning krävs för GDPR-export."}), 401

    export_payload: Dict[str, Any] = {
        "user_id": auth_uid,
        "email": email,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "profile": {},
        "compass_scores": [],
        "compass_calibrations": [],
        "compass_state": {},
        "conversations": [],
        "messages": [],
        "message_feedback": [],
        "insights": [],
        "goals": [],
        "reminders": [],
        "promo_redemptions": [],
    }
    try:
        prof = supabase.table("user_profiles").select("*").eq("id", auth_uid).execute()
        if not prof.data:
            prof = supabase.table("user_profiles").select("*").eq("user_id", auth_uid).execute()
        comp = supabase.table("compass_scores").select("*").eq("user_id", auth_uid).execute()
        cals = supabase.table("compass_calibrations").select("*").eq("user_id", auth_uid).execute()
        cstate = supabase.table("user_compass_states").select("*").eq("user_id", auth_uid).execute()
        convs = supabase.table("conversations").select("*").eq("user_id", auth_uid).execute()
        msgs = supabase.table("messages").select("*").eq("user_id", auth_uid).execute()
        fb = supabase.table("message_feedback").select("*").eq("user_id", auth_uid).execute()
        ins = supabase.table("user_insights").select("*").eq("user_id", auth_uid).execute()
        goals = supabase.table("user_goals").select("*").eq("user_id", auth_uid).execute()
        rems = supabase.table("user_reminders").select("*").eq("user_id", auth_uid).execute()
        promos = supabase.table("promo_redemptions").select("*").eq("user_id", auth_uid).execute()

        export_payload["profile"] = prof.data[0] if prof.data else {}
        export_payload["compass_scores"] = comp.data or []
        export_payload["compass_calibrations"] = cals.data or []
        export_payload["compass_state"] = cstate.data[0] if cstate.data else {}
        export_payload["conversations"] = convs.data or []
        export_payload["messages"] = msgs.data or []
        export_payload["message_feedback"] = fb.data or []
        export_payload["insights"] = ins.data or []
        export_payload["goals"] = goals.data or []
        export_payload["reminders"] = rems.data or []
        export_payload["promo_redemptions"] = promos.data or []
    except Exception as e:
        logging.error(f"GDPR-exportfel för {auth_uid}: {e}")
        return jsonify({"status": "error", "message": f"Exportfel: {e}"}), 500

    return jsonify({"status": "success", "export": export_payload}), 200


@app.route("/api/user/delete", methods=["DELETE", "POST", "OPTIONS"])
def delete_user_account():
    if request.method == "OPTIONS":
        return "", 200

    auth_uid, _, _ = _resolve_auth_user()
    if not auth_uid or not supabase:
        return jsonify({"status": "error", "code": "AUTH_REQUIRED", "message": "Inloggning krävs för radering."}), 401

    if not SUPABASE_SERVICE_ROLE_KEY:
        return jsonify({"status": "error", "message": "Servern saknar behörighet för permanent kontoradering."}), 500

    try:
        # 1. Hämta eventuell Stripe-koppling och avsluta aktiv prenumeration innan profilen raderas
        prof_rows = []
        p1 = supabase.table("user_profiles").select("id,user_id,stripe_customer_id,stripe_subscription_id").eq("id", auth_uid).execute()
        if p1.data:
            prof_rows.extend(p1.data)
        p2 = supabase.table("user_profiles").select("id,user_id,stripe_customer_id,stripe_subscription_id").eq("user_id", auth_uid).execute()
        if p2.data:
            prof_rows.extend(p2.data)

        stripe_key = os.getenv("STRIPE_SECRET_KEY", "").strip()
        if stripe_key and prof_rows:
            import stripe as _stripe
            _stripe.api_key = stripe_key
            cancel_fn = getattr(_stripe.Subscription, "cancel", _stripe.Subscription.delete)
            seen_subs = set()
            seen_custs = set()
            for row in prof_rows:
                sub_id = (row.get("stripe_subscription_id") or "").strip()
                cust_id = (row.get("stripe_customer_id") or "").strip()
                if sub_id and sub_id not in seen_subs:
                    seen_subs.add(sub_id)
                    try:
                        cancel_fn(sub_id)
                    except Exception as sub_err:
                        if "no such subscription" not in str(sub_err).lower() and "canceled" not in str(sub_err).lower():
                            raise
                if cust_id and cust_id not in seen_custs:
                    seen_custs.add(cust_id)
                    try:
                        active_subs = _stripe.Subscription.list(customer=cust_id, status="active")
                        for s in getattr(active_subs, "data", []) or []:
                            sid = getattr(s, "id", None) or (s.get("id") if isinstance(s, dict) else None)
                            if sid and sid not in seen_subs:
                                seen_subs.add(sid)
                                cancel_fn(sid)
                    except Exception as cust_err:
                        if "no such customer" not in str(cust_err).lower():
                            raise

        # 2. Radera all associerad användardata i samtliga tabeller
        for table_name in (
            "message_feedback",
            "messages",
            "conversations",
            "user_insights",
            "user_goals",
            "user_reminders",
            "compass_calibrations",
            "compass_scores",
            "user_compass_states",
            "promo_redemptions",
        ):
            supabase.table(table_name).delete().eq("user_id", auth_uid).execute()

        supabase.table("user_profiles").delete().eq("id", auth_uid).execute()
        supabase.table("user_profiles").delete().eq("user_id", auth_uid).execute()

        # 3. Radera inloggningskontot i Supabase Auth
        try:
            supabase.auth.admin.delete_user(auth_uid)
        except Exception as auth_del_err:
            if "not found" not in str(auth_del_err).lower():
                raise

        return jsonify({
            "status": "success",
            "message": "Ditt konto, eventuell prenumeration och all associerad data har raderats permanent enligt GDPR.",
        }), 200
    except Exception as e:
        logging.error(f"GDPR-raderingsfel för {auth_uid}: {e}")
        return jsonify({"status": "error", "message": f"Radering misslyckades: {e}"}), 500


# ---------------------------------------------------------------------------
# STRIPE CHECKOUT, CUSTOMER PORTAL & WEBHOOK
# ---------------------------------------------------------------------------
def _sanitize_redirect_url(candidate: Any, fallback: str) -> str:
    url = str(candidate or "").strip()
    if not url:
        return fallback
    allowed_prefixes = [
        "https://falk-frontend.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    custom_frontend = os.getenv("FRONTEND_URL", "").strip().rstrip("/")
    if custom_frontend:
        allowed_prefixes.append(custom_frontend)
    if any(url == prefix or url.startswith(prefix + "/") or url.startswith(prefix + "?") for prefix in allowed_prefixes):
        return url
    return fallback


def _verify_adult_and_terms(auth_uid: str) -> bool:
    if not supabase or not auth_uid:
        return False
    try:
        prof = supabase.table("user_profiles").select("age_verified_18_plus,terms_accepted").eq("id", auth_uid).limit(1).execute()
        if prof.data:
            row = prof.data[0]
            if row.get("age_verified_18_plus") and row.get("terms_accepted"):
                return True
    except Exception as e:
        logging.warning(f"Kunde inte läsa 18+/villkor från user_profiles för {auth_uid}: {e}")

    if SUPABASE_SERVICE_ROLE_KEY:
        try:
            user_resp = supabase.auth.admin.get_user_by_id(auth_uid)
            user_obj = getattr(user_resp, "user", None)
            meta = getattr(user_obj, "user_metadata", None) or {}
            if meta.get("age_verified_18_plus") and meta.get("terms_accepted"):
                try:
                    supabase.table("user_profiles").upsert({
                        "id": auth_uid,
                        "age_verified_18_plus": True,
                        "terms_accepted": True,
                    }).execute()
                except Exception:
                    pass
                return True
        except Exception as e:
            logging.warning(f"Kunde inte läsa user_metadata för {auth_uid}: {e}")
    return False


@app.route("/api/checkout", methods=["POST", "OPTIONS"])
def create_stripe_checkout():
    if request.method == "OPTIONS":
        return "", 200

    auth_uid, auth_email, _ = _resolve_auth_user()
    if not auth_uid:
        return jsonify({
            "status": "error",
            "code": "AUTH_REQUIRED",
            "message": "Du måste vara inloggad och ha bekräftat 18+ innan du uppgraderar till Premium.",
        }), 401

    if not _verify_adult_and_terms(auth_uid):
        return jsonify({
            "status": "error",
            "code": "AGE_AND_TERMS_REQUIRED",
            "message": "Bekräftelse av 18+ och godkända villkor krävs före köp av FALK Premium.",
        }), 403

    data = request.get_json(silent=True) or {}
    email = auth_email or str(data.get("email", "")).strip()
    success_url = _sanitize_redirect_url(data.get("success_url"), "https://falk-frontend.vercel.app/?upgrade=success")
    cancel_url = _sanitize_redirect_url(data.get("cancel_url"), "https://falk-frontend.vercel.app/?upgrade=cancel")

    stripe_key = os.getenv("STRIPE_SECRET_KEY", "").strip()
    price_id = os.getenv("STRIPE_PRICE_ID", "").strip()
    if not stripe_key or not price_id:
        return jsonify({"status": "error", "message": "Stripe är inte konfigurerat på servern."}), 500

    try:
        import stripe
        stripe.api_key = stripe_key
        session = stripe.checkout.Session.create(
            mode="subscription",
            payment_method_types=["card"],
            customer_email=email if email else None,
            client_reference_id=auth_uid,
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"user_id": auth_uid, "age_verified_18_plus": "true"},
            subscription_data={"metadata": {"user_id": auth_uid, "age_verified_18_plus": "true"}},
        )
        return jsonify({"status": "success", "checkout_url": session.url}), 200
    except Exception as e:
        logging.error(f"Stripe checkout-fel: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/billing/portal", methods=["POST", "OPTIONS"])
def create_stripe_portal():
    if request.method == "OPTIONS":
        return "", 200

    auth_uid, auth_email, _ = _resolve_auth_user()
    if not auth_uid:
        return jsonify({"status": "error", "code": "AUTH_REQUIRED", "message": "Inloggning krävs."}), 401

    stripe_key = os.getenv("STRIPE_SECRET_KEY", "").strip()
    if not stripe_key:
        return jsonify({"status": "error", "message": "Stripe är inte konfigurerat."}), 500

    data = request.get_json(silent=True) or {}
    return_url = _sanitize_redirect_url(data.get("return_url"), "https://falk-frontend.vercel.app/")

    try:
        import stripe
        stripe.api_key = stripe_key
        customer_id = None
        if auth_email:
            customers = stripe.Customer.list(email=auth_email, limit=1)
            if customers and customers.data:
                customer_id = customers.data[0].id
        if not customer_id:
            try:
                subs = stripe.Subscription.search(query=f"metadata['user_id']:'{auth_uid}'", limit=1)
                if subs and subs.data:
                    customer_id = subs.data[0].customer
            except Exception:
                pass
        if not customer_id:
            return jsonify({"status": "error", "message": "Ingen aktiv Stripe-kund hittades för kontot."}), 404

        portal = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
        return jsonify({"status": "success", "portal_url": portal.url}), 200
    except Exception as e:
        logging.error(f"Stripe portal-fel: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature", "")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "").strip()
    stripe_key = os.getenv("STRIPE_SECRET_KEY", "").strip()
    if not webhook_secret:
        logging.error("STRIPE_WEBHOOK_SECRET saknas - avvisar webhook (fail-closed).")
        return jsonify({"status": "error", "message": "Webhook-signatur ej konfigurerad."}), 500

    try:
        import stripe
        stripe.api_key = stripe_key
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        if not event:
            return jsonify({"status": "ignored"}), 200

        event_type = event.get("type", "")
        obj = event.get("data", {}).get("object", {})

        if event_type == "checkout.session.completed":
            uid = obj.get("client_reference_id") or (obj.get("metadata") or {}).get("user_id")
            if supabase and uid and uid != "guest":
                supabase.table("user_profiles").upsert({"id": uid, "is_premium": True}).execute()

        elif event_type == "customer.subscription.updated":
            uid = (obj.get("metadata") or {}).get("user_id")
            sub_status = str(obj.get("status", "")).lower()
            if supabase and uid and uid != "guest":
                if sub_status in ("active", "trialing"):
                    supabase.table("user_profiles").upsert({"id": uid, "is_premium": True}).execute()
                elif sub_status in ("canceled", "unpaid", "incomplete_expired"):
                    supabase.table("user_profiles").upsert({"id": uid, "is_premium": False}).execute()

        elif event_type == "customer.subscription.deleted":
            uid = (obj.get("metadata") or {}).get("user_id")
            if supabase and uid and uid != "guest":
                supabase.table("user_profiles").upsert({"id": uid, "is_premium": False}).execute()

        return jsonify({"status": "received"}), 200
    except Exception as e:
        logging.error(f"Stripe webhook-fel: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400



_PROMO_REDEEM_ATTEMPTS: dict[str, list[float]] = {}


@app.route("/api/billing/redeem-promo", methods=["POST", "OPTIONS"])
def redeem_promo_code_route():
    if request.method == "OPTIONS":
        return "", 200

    auth_uid, _, _ = _resolve_auth_user()
    if not auth_uid:
        return jsonify({
            "status": "error",
            "code": "AUTH_REQUIRED",
            "message": "Du måste vara inloggad och ha bekräftat 18+ innan du aktiverar en rabattkod.",
        }), 401

    if not _verify_adult_and_terms(auth_uid):
        return jsonify({
            "status": "error",
            "code": "AGE_AND_TERMS_REQUIRED",
            "message": "Bekräftelse av 18+ och godkända villkor krävs före aktivering av FALK Premium.",
        }), 403

    if not supabase:
        return jsonify({"status": "error", "message": "Databasanslutning saknas."}), 500

    # Brute-force-skydd: max 5 försök per 10 minuter och användare
    import time as _time
    now_ts = _time.time()
    recent = [ts for ts in _PROMO_REDEEM_ATTEMPTS.get(auth_uid, []) if now_ts - ts < 600]
    if len(recent) >= 5:
        _PROMO_REDEEM_ATTEMPTS[auth_uid] = recent
        return jsonify({
            "status": "error",
            "code": "RATE_LIMITED",
            "message": "För många försök. Vänta en stund och försök igen.",
        }), 429
    recent.append(now_ts)
    _PROMO_REDEEM_ATTEMPTS[auth_uid] = recent

    data = request.get_json(silent=True) or {}
    raw_code = str(data.get("code", "")).strip()
    if not raw_code or len(raw_code) > 64:
        return jsonify({
            "status": "error",
            "code": "INVALID_CODE",
            "message": "Ange en giltig rabattkod.",
        }), 400

    try:
        rpc_res = supabase.rpc(
            "redeem_promo_code",
            {"p_user_id": auth_uid, "p_code": raw_code},
        ).execute()
        payload = rpc_res.data
        if isinstance(payload, list):
            payload = payload[0] if payload else {}
        if not isinstance(payload, dict):
            payload = {}

        if payload.get("ok") is True:
            return jsonify({
                "status": "success",
                "code": payload.get("code", "REDEEMED"),
                "message": payload.get("message", "Premium har aktiverats!"),
                "is_premium": True,
            }), 200

        err_code = str(payload.get("code") or "INVALID_CODE")
        err_msg = str(payload.get("message") or "Ogiltig eller inaktiv rabattkod.")
        http_status = 409 if err_code == "ALREADY_REDEEMED" else 400
        return jsonify({
            "status": "error",
            "code": err_code,
            "message": err_msg,
        }), http_status
    except Exception as e:
        logging.error(f"Promo-inlösenfel för {auth_uid}: {e}")
        return jsonify({
            "status": "error",
            "message": "Kunde inte verifiera rabattkoden just nu. Försök igen.",
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)
