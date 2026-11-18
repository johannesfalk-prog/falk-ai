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
from dotenv import load_dotenv
from pdf_exporter import generate_session_pdf_html

load_dotenv()
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                "https://falk-frontend.vercel.app",
                r"^https://falk-frontend-[a-zA-Z0-9-]+\.vercel\.app$",
                "http://localhost:3000",
                "http://127.0.0.1:3000",
            ]
        }
    },
    supports_credentials=True,
)

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

    uid = None
    email = None
    try:
        user_resp = supabase.auth.get_user(token)
        user_obj = getattr(user_resp, "user", None)
        if user_obj and getattr(user_obj, "id", None):
            uid = str(user_obj.id)
            email = getattr(user_obj, "email", None)
    except Exception as e:
        logging.warning(f"supabase.auth.get_user misslyckades, testar lokal JWT: {e}")

    if not uid:
        jwt_secret = os.getenv("SUPABASE_JWT_SECRET", "").strip()
        if jwt_secret:
            try:
                import jwt as pyjwt
                decoded = pyjwt.decode(
                    token,
                    jwt_secret,
                    algorithms=["HS256"],
                    options={"verify_aud": False},
                )
                uid = str(decoded.get("sub") or "").strip() or None
                email = decoded.get("email")
            except Exception as je:
                logging.warning(f"Lokal JWT-verifiering misslyckades: {je}")

    if not uid:
        return None, None, False

    is_premium = False
    try:
        prof = supabase.table("user_profiles").select("is_premium").eq("id", uid).limit(1).execute()
        if prof.data and len(prof.data) > 0:
            is_premium = bool(prof.data[0].get("is_premium", False))
    except Exception as pe:
        logging.warning(f"Kunde inte läsa user_profiles för {uid}: {pe}")

    if not is_premium:
        try:
            b2b_rpc = supabase.rpc("user_has_active_b2b_seat", {"p_user_id": uid}).execute()
            if b2b_rpc.data is True or (isinstance(b2b_rpc.data, list) and len(b2b_rpc.data) > 0 and b2b_rpc.data[0] is True):
                is_premium = True
        except Exception as b2b_err:
            logging.warning(f"Kunde inte kontrollera B2B-säte för {uid}: {b2b_err}")

    return uid, email, is_premium


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
    "det är enkelt",
    "jag vet exakt hur du känner",
    "så här måste du göra",
    "det finns bara ett rätt svar",
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
    Hämtar sparade insikter, aktiva mål, påminnelser och senaste kompasskalibrering
    för inloggad användare (The Wayjs Continuity System™).
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
            memories.extend([f"Insikt: {row['content']}" for row in ins.data if row.get("content")])
    except Exception as e:
        logging.warning(f"Kunde inte hämta kontinuitetsinsikter: {e}")

    try:
        goals = (
            supabase.table("user_goals")
            .select("title, status")
            .eq("user_id", uid)
            .order("created_at", desc=True)
            .limit(3)
            .execute()
        )
        if goals.data:
            for g in goals.data:
                if g.get("title") and g.get("status") != "completed":
                    memories.append(f"Aktivt mål: {g['title']}")
    except Exception as e:
        logging.warning(f"Kunde inte hämta kontinuitetsmål: {e}")

    try:
        rems = (
            supabase.table("user_reminders")
            .select("content, remind_at")
            .eq("user_id", uid)
            .eq("is_active", True)
            .order("created_at", desc=True)
            .limit(3)
            .execute()
        )
        if rems.data:
            for r in rems.data:
                if r.get("content"):
                    memories.append(f"Påminnelse: {r['content']}")
    except Exception as e:
        logging.warning(f"Kunde inte hämta kontinuitetspåminnelser: {e}")

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
            raw_scores = comp.data[0]["scores"]
            if isinstance(raw_scores, dict):
                compass_summary = ", ".join(f"{k}: {v}" for k, v in raw_scores.items())
            else:
                compass_summary = str(raw_scores)
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
                {"user_id": auth_uid, "sender": "user", "content": message},
                {"user_id": auth_uid, "sender": "falk", "content": final_reply},
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


@app.route("/api/conversations/<conv_id>/messages", methods=["GET", "OPTIONS"])
def get_conversation_messages(conv_id):
    if request.method == "OPTIONS":
        return "", 200
    auth_uid, _, _ = _resolve_auth_user()
    if not auth_uid:
        return jsonify({"status": "error", "message": "Inloggning krävs."}), 401
    if not supabase:
        return jsonify({"status": "error", "message": "Databasanslutning saknas."}), 500
    try:
        res = (
            supabase.table("messages")
            .select("id, sender, content, created_at")
            .eq("conversation_id", str(conv_id).strip())
            .eq("user_id", auth_uid)
            .order("created_at", desc=False)
            .execute()
        )
        rows = sorted(
            res.data or [],
            key=lambda m: (
                m.get("created_at") or "",
                0 if m.get("sender") == "user" else 1,
                str(m.get("id") or ""),
            ),
        )
        return jsonify({"status": "success", "messages": rows}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


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
            .select("sender,content")
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
            "role": "assistant" if (m.get("sender") or m.get("role")) in ("falk", "assistant") else "user",
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
@app.route("/api/insights/<item_id>", methods=["DELETE", "OPTIONS"])
def handle_insights(item_id=None):
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

    try:
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            text = str(data.get("content") or data.get("text") or data.get("title", "")).strip()
            raw_type = str(data.get("type") or "insight").strip().lower()
            type_map = {"insikt": "insight", "reflektion": "reflection", "mönster": "pattern", "milstolpe": "milestone"}
            insight_type = type_map.get(raw_type, raw_type or "insight")
            source_context = str(data.get("source_context") or "").strip()
            session_id = str(data.get("session_id") or "").strip()
            if not text:
                return jsonify({"status": "error", "message": "Insiktstext saknas."}), 400

            recent = (
                supabase.table("user_insights")
                .select("*")
                .eq("user_id", auth_uid)
                .eq("content", text)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            if recent.data:
                try:
                    created_dt = datetime.fromisoformat(recent.data[0]["created_at"].replace("Z", "+00:00"))
                    if (datetime.now(timezone.utc) - created_dt).total_seconds() < 5:
                        return jsonify({"status": "success", "insight": recent.data[0]}), 200
                except Exception:
                    pass

            payload = {"user_id": auth_uid, "content": text, "type": insight_type}
            if source_context:
                payload["source_context"] = source_context
            if session_id:
                payload["session_id"] = session_id
            try:
                res = supabase.table("user_insights").insert(payload).execute()
                return jsonify({"status": "success", "insight": res.data[0] if res.data else payload}), 201
            except Exception as e:
                logging.warning(f"Första insert i user_insights misslyckades ({e}), testar fallback type='insight'")
                payload["type"] = "insight"
                payload.pop("session_id", None)
                res = supabase.table("user_insights").insert(payload).execute()
                return jsonify({"status": "success", "insight": res.data[0] if res.data else payload}), 201
    except Exception as e:
        print(f"[ERROR] /api/insights insert misslyckades: {e}", flush=True)
        return jsonify({"status": "error", "message": f"Kunde inte spara insikt: {str(e)}"}), 500

    if request.method == "DELETE":
        insight_id = item_id or request.args.get("id") or (request.get_json(silent=True) or {}).get("id")
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
        clean_goals = []
        for g in (res.data or []):
            raw_prog = g.get("progress")
            try:
                prog = max(0, min(100, int(raw_prog))) if raw_prog is not None else 0
            except (ValueError, TypeError):
                prog = 0
            title_val = str(g.get("title") or g.get("content") or "Namnlöst mål").strip()
            status_val = g.get("status") or ("completed" if prog >= 100 else "active")
            clean_goals.append({
                **g,
                "title": title_val,
                "area": str(g.get("area") or "Personlig utveckling").strip(),
                "progress": prog,
                "status": status_val,
            })
        return jsonify({"status": "success", "goals": clean_goals}), 200

    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        title = str(data.get("title") or "Nytt mål").strip()
        area = str(data.get("area") or "Personlig utveckling").strip()
        try:
            progress = max(0, min(100, int(data.get("progress", 0))))
        except (ValueError, TypeError):
            progress = 0
        status = str(data.get("status") or ("completed" if progress >= 100 else "active")).strip()
        res = supabase.table("user_goals").insert({
            "user_id": auth_uid,
            "title": title,
            "area": area,
            "progress": progress,
            "status": status,
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
@app.route("/api/reminders/<item_id>", methods=["DELETE", "OPTIONS"])
def handle_reminders(item_id=None):
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
        try:
            data = request.get_json(silent=True) or {}
            content = str(data.get("content") or data.get("text") or data.get("title", "")).strip()
            freq = str(data.get("frequency") or "daily").strip() or "daily"
            raw_remind = data.get("remind_at") or data.get("reminder_at")
            remind_at = str(raw_remind).strip() if raw_remind not in (None, "", "null", "None") else None
            if not content:
                return jsonify({"status": "error", "message": "Påminnelsetext saknas."}), 400

            recent = (
                supabase.table("user_reminders")
                .select("*")
                .eq("user_id", auth_uid)
                .eq("content", content)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            if recent.data:
                try:
                    created_dt = datetime.fromisoformat(recent.data[0]["created_at"].replace("Z", "+00:00"))
                    if (datetime.now(timezone.utc) - created_dt).total_seconds() < 5:
                        return jsonify({"status": "success", "reminder": recent.data[0]}), 200
                except Exception:
                    pass

            payload: Dict[str, Any] = {"user_id": auth_uid, "content": content, "frequency": freq}
            if remind_at:
                payload["remind_at"] = remind_at
                payload["reminder_at"] = remind_at
            try:
                res = supabase.table("user_reminders").insert(payload).execute()
                return jsonify({"status": "success", "reminder": res.data[0] if res.data else payload}), 201
            except Exception as e:
                logging.warning(f"Första insert i user_reminders misslyckades ({e}), testar minimal payload")
                minimal_payload: Dict[str, Any] = {"user_id": auth_uid, "content": content, "frequency": freq}
                res = supabase.table("user_reminders").insert(minimal_payload).execute()
                return jsonify({"status": "success", "reminder": res.data[0] if res.data else minimal_payload}), 201
        except Exception as e:
            print(f"[ERROR] /api/reminders insert misslyckades: {e}", flush=True)
            return jsonify({"status": "error", "message": f"Kunde inte spara påminnelse: {str(e)}"}), 500

    if request.method == "DELETE":
        rem_id = item_id or request.args.get("id") or (request.get_json(silent=True) or {}).get("id")
        if not rem_id:
            return jsonify({"status": "error", "message": "id saknas."}), 400
        supabase.table("user_reminders").delete().eq("id", rem_id).eq("user_id", auth_uid).execute()
        return jsonify({"status": "success"}), 200


@app.route("/api/calibration", methods=["GET", "POST", "OPTIONS"])
def handle_calibration():
    if request.method == "OPTIONS":
        return "", 200

    auth_uid, _, is_premium = _resolve_auth_user()
    def _sanitize_scores(raw_scores):
        if not isinstance(raw_scores, dict):
            return {}
        cleaned = {}
        for k, v in raw_scores.items():
            try:
                num = float(v)
                if num == num:  # ej NaN
                    cleaned[str(k)] = max(0, min(100, round(num)))
            except (ValueError, TypeError):
                continue
        return cleaned

    if request.method == "GET":
        if not auth_uid or not supabase:
            return jsonify({"status": "success", "calibrations": []}), 200
        if not is_premium:
            return jsonify({"status": "error", "code": "PREMIUM_REQUIRED", "message": "Min utveckling kräver FALK Premium."}), 403
        rows = []
        for tbl in ("compass_scores", "compass_calibrations"):
            try:
                r = (
                    supabase.table(tbl)
                    .select("*")
                    .eq("user_id", auth_uid)
                    .order("created_at", desc=True)
                    .limit(30)
                    .execute()
                )
                for item in (r.data or []):
                    clean_s = _sanitize_scores(item.get("scores"))
                    if clean_s:
                        rows.append({**item, "scores": clean_s})
            except Exception as e:
                logging.warning(f"Kunde inte läsa {tbl} för {auth_uid}: {e}")
        rows.sort(key=lambda x: str(x.get("created_at") or ""), reverse=True)
        return jsonify({"status": "success", "calibrations": rows[:30]}), 200

    data = request.get_json(silent=True) or {}
    scores = _sanitize_scores(data.get("scores", {}))
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
        "organization_members": [],
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
        org_members = supabase.table("organization_members").select("*").eq("user_id", auth_uid).execute()

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
        export_payload["organization_members"] = org_members.data or []
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
                        all_subs = _stripe.Subscription.list(customer=cust_id, status="all")
                        for s in getattr(all_subs, "data", []) or []:
                            sid = getattr(s, "id", None) or (s.get("id") if isinstance(s, dict) else None)
                            st = str(getattr(s, "status", None) or (s.get("status") if isinstance(s, dict) else "")).lower()
                            if sid and sid not in seen_subs and st not in ("canceled", "incomplete_expired"):
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

        supabase.table("organization_members").delete().eq("user_id", auth_uid).execute()
        supabase.table("organization_invites").update({"created_by": None}).eq("created_by", auth_uid).execute()
        supabase.table("organization_invites").update({"redeemed_by": None}).eq("redeemed_by", auth_uid).execute()

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
        prof = (
            supabase.table("user_profiles")
            .select("is_adult_confirmed,terms_accepted_at,privacy_accepted_at")
            .eq("id", auth_uid)
            .limit(1)
            .execute()
        )
        if prof.data:
            row = prof.data[0]
            if row.get("is_adult_confirmed") and row.get("terms_accepted_at"):
                return True
    except Exception as e:
        logging.warning(f"Kunde inte läsa 18+/villkor från user_profiles för {auth_uid}: {e}")

    if SUPABASE_SERVICE_ROLE_KEY:
        try:
            from datetime import datetime, timezone
            user_resp = supabase.auth.admin.get_user_by_id(auth_uid)
            user_obj = getattr(user_resp, "user", None)
            meta = getattr(user_obj, "user_metadata", None) or {}
            adult_ok = bool(meta.get("age_verified_18_plus") or meta.get("is_adult_confirmed"))
            terms_ok = bool(meta.get("terms_accepted") or meta.get("terms_accepted_at"))
            if adult_ok and terms_ok:
                now_iso = datetime.now(timezone.utc).isoformat()
                payload = {
                    "id": auth_uid,
                    "user_id": str(auth_uid),
                    "is_adult_confirmed": True,
                    "terms_accepted_at": meta.get("terms_accepted_at") or now_iso,
                    "privacy_accepted_at": meta.get("privacy_accepted_at") or now_iso,
                }
                user_email = getattr(user_obj, "email", None)
                if user_email:
                    payload["email"] = user_email
                try:
                    supabase.table("user_profiles").upsert(payload, on_conflict="id").execute()
                except Exception as upsert_err:
                    logging.warning(f"Kunde inte synka user_profiles för {auth_uid}: {upsert_err}")
                return True
        except Exception as e:
            logging.warning(f"Kunde inte läsa user_metadata för {auth_uid}: {e}")
    return False


def _extract_stripe_id(val: Any) -> Optional[str]:
    if isinstance(val, dict):
        val = val.get("id")
    s = str(val or "").strip()
    return s or None


def _get_user_stripe_ids(uid: str) -> Tuple[Optional[str], Optional[str]]:
    if not supabase or not uid:
        return None, None
    try:
        res = supabase.table("user_profiles").select("stripe_customer_id,stripe_subscription_id").eq("id", uid).limit(1).execute()
        if not res.data:
            res = supabase.table("user_profiles").select("stripe_customer_id,stripe_subscription_id").eq("user_id", uid).limit(1).execute()
        if res.data:
            row = res.data[0]
            cust_id = (row.get("stripe_customer_id") or "").strip() or None
            sub_id = (row.get("stripe_subscription_id") or "").strip() or None
            return cust_id, sub_id
    except Exception as e:
        logging.warning(f"Kunde inte läsa Stripe-ID:n för {uid}: {e}")
    return None, None


def _resolve_uid_from_stripe(uid: Optional[str], customer_id: Optional[str], subscription_id: Optional[str]) -> Optional[str]:
    clean_uid = str(uid or "").strip()
    if clean_uid and clean_uid != "guest":
        return clean_uid
    if not supabase:
        return None
    if customer_id:
        res = supabase.table("user_profiles").select("id,user_id").eq("stripe_customer_id", customer_id).limit(1).execute()
        if res.data:
            return str(res.data[0].get("user_id") or res.data[0].get("id") or "").strip() or None
    if subscription_id:
        res = supabase.table("user_profiles").select("id,user_id").eq("stripe_subscription_id", subscription_id).limit(1).execute()
        if res.data:
            return str(res.data[0].get("user_id") or res.data[0].get("id") or "").strip() or None
    return None


def _sync_stripe_profile(
    uid: Optional[str],
    customer_id: Optional[str],
    subscription_id: Optional[str],
    is_premium: Optional[bool],
    clear_subscription: bool = False,
) -> None:
    if not supabase:
        return
    resolved_uid = _resolve_uid_from_stripe(uid, customer_id, subscription_id)
    if not resolved_uid or resolved_uid == "guest":
        logging.warning(f"Stripe-synk ignorerad: kunde inte koppla till användare (cust={customer_id}, sub={subscription_id})")
        return

    updates: Dict[str, Any] = {}
    if is_premium is not None:
        updates["is_premium"] = bool(is_premium)
    if customer_id:
        updates["stripe_customer_id"] = customer_id
    if clear_subscription:
        updates["stripe_subscription_id"] = None
    elif subscription_id:
        updates["stripe_subscription_id"] = subscription_id

    if not updates:
        return

    existing_by_id = supabase.table("user_profiles").select("id").eq("id", resolved_uid).execute()
    existing_by_uid = supabase.table("user_profiles").select("id").eq("user_id", resolved_uid).execute()

    if existing_by_id.data or existing_by_uid.data:
        if existing_by_id.data:
            supabase.table("user_profiles").update(updates).eq("id", resolved_uid).execute()
        if existing_by_uid.data:
            supabase.table("user_profiles").update(updates).eq("user_id", resolved_uid).execute()
    else:
        insert_payload: Dict[str, Any] = {"id": resolved_uid, "user_id": resolved_uid, **updates}
        supabase.table("user_profiles").insert(insert_payload).execute()


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
        existing_customer_id, _ = _get_user_stripe_ids(auth_uid)
        checkout_kwargs: Dict[str, Any] = {
            "mode": "subscription",
            "payment_method_types": ["card"],
            "client_reference_id": auth_uid,
            "line_items": [{"price": price_id, "quantity": 1}],
            "success_url": success_url,
            "cancel_url": cancel_url,
            "metadata": {"user_id": auth_uid, "age_verified_18_plus": "true"},
            "subscription_data": {"metadata": {"user_id": auth_uid, "age_verified_18_plus": "true"}},
        }
        if existing_customer_id:
            checkout_kwargs["customer"] = existing_customer_id
        elif email:
            checkout_kwargs["customer_email"] = email

        session = stripe.checkout.Session.create(**checkout_kwargs)
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
        db_customer_id, _ = _get_user_stripe_ids(auth_uid)
        customer_id = db_customer_id
        if not customer_id and auth_email:
            customers = stripe.Customer.list(email=auth_email, limit=1)
            if customers and customers.data:
                customer_id = customers.data[0].id
        if not customer_id:
            try:
                subs = stripe.Subscription.search(query=f"metadata['user_id']:'{auth_uid}'", limit=1)
                if subs and subs.data:
                    customer_id = _extract_stripe_id(subs.data[0].customer)
            except Exception:
                pass
        if not customer_id:
            return jsonify({"status": "error", "message": "Ingen aktiv Stripe-kund hittades för kontot."}), 404

        if not db_customer_id:
            try:
                _sync_stripe_profile(auth_uid, customer_id, None, None)
            except Exception as sync_err:
                logging.warning(f"Kunde inte cacha stripe_customer_id vid portalöppning: {sync_err}")

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
    except Exception as sig_err:
        logging.error(f"Stripe webhook-signaturfel: {sig_err}")
        return jsonify({"status": "error", "message": str(sig_err)}), 400

    if not event:
        return jsonify({"status": "ignored"}), 200

    try:
        event_type = event.get("type", "")
        obj = event.get("data", {}).get("object", {})

        if event_type == "checkout.session.completed":
            uid = obj.get("client_reference_id") or (obj.get("metadata") or {}).get("user_id")
            cust_id = _extract_stripe_id(obj.get("customer"))
            sub_id = _extract_stripe_id(obj.get("subscription"))
            _sync_stripe_profile(uid, cust_id, sub_id, is_premium=True)

        elif event_type in ("customer.subscription.created", "customer.subscription.updated"):
            uid = (obj.get("metadata") or {}).get("user_id")
            cust_id = _extract_stripe_id(obj.get("customer"))
            sub_id = _extract_stripe_id(obj.get("id"))
            sub_status = str(obj.get("status", "")).lower()
            if sub_status in ("active", "trialing"):
                _sync_stripe_profile(uid, cust_id, sub_id, is_premium=True)
            elif sub_status in ("canceled", "unpaid", "incomplete_expired"):
                _sync_stripe_profile(uid, cust_id, sub_id, is_premium=False, clear_subscription=True)
            else:
                _sync_stripe_profile(uid, cust_id, sub_id, is_premium=None)

        elif event_type == "customer.subscription.deleted":
            uid = (obj.get("metadata") or {}).get("user_id")
            cust_id = _extract_stripe_id(obj.get("customer"))
            sub_id = _extract_stripe_id(obj.get("id"))
            _sync_stripe_profile(uid, cust_id, sub_id, is_premium=False, clear_subscription=True)

        return jsonify({"status": "received"}), 200
    except Exception as e:
        logging.error(f"Stripe webhook-bearbetningsfel: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500



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


# ---------------------------------------------------------------------------
# B2B MULTI-TENANCY (HR / FÖRSÄKRING — STRIKT K-ANONYMITET >= 5)
# ---------------------------------------------------------------------------
_B2B_JOIN_ATTEMPTS: dict[str, list[float]] = {}
_B2B_ADMIN_ROLES = ("hr_admin", "insurer_admin", "org_admin", "admin")
_B2B_VALID_ROLES = ("member", "hr_admin", "insurer_admin", "org_admin", "hr_viewer")


def _get_active_b2b_admin_membership(auth_uid: str, requested_org_id: Optional[str] = None) -> Tuple[Optional[dict], Optional[dict]]:
    if not supabase or not auth_uid:
        return None, None
    try:
        query = (
            supabase.table("organization_members")
            .select("id,org_id,user_id,role,department,status,joined_at")
            .eq("user_id", auth_uid)
            .eq("status", "active")
            .in_("role", list(_B2B_ADMIN_ROLES))
        )
        if requested_org_id:
            query = query.eq("org_id", requested_org_id)
        mem_res = query.limit(10).execute()
        memberships = mem_res.data or []
        for mem in memberships:
            oid = mem.get("org_id")
            if not oid:
                continue
            org_res = (
                supabase.table("organizations")
                .select("id,name,org_type,seat_limit,status,allowed_domains")
                .eq("id", oid)
                .eq("status", "active")
                .limit(1)
                .execute()
            )
            if org_res.data:
                return mem, org_res.data[0]
    except Exception as e:
        logging.warning(f"B2B admin-kontroll misslyckades för {auth_uid}: {e}")
    return None, None


@app.route("/api/b2b/join", methods=["POST", "OPTIONS"])
def b2b_join_organization():
    if request.method == "OPTIONS":
        return "", 200

    auth_uid, auth_email, _ = _resolve_auth_user()
    if not auth_uid:
        return jsonify({
            "status": "error",
            "code": "AUTH_REQUIRED",
            "message": "Du måste vara inloggad för att ansluta till en organisation.",
        }), 401

    if not _verify_adult_and_terms(auth_uid):
        return jsonify({
            "status": "error",
            "code": "AGE_AND_TERMS_REQUIRED",
            "message": "Bekräftelse av 18+ och godkända villkor krävs före aktivering av organisationslicens.",
        }), 403

    if not supabase:
        return jsonify({"status": "error", "message": "Databasanslutning saknas."}), 500

    import time as _time
    from datetime import datetime, timezone

    now_ts = _time.time()
    recent = [ts for ts in _B2B_JOIN_ATTEMPTS.get(auth_uid, []) if now_ts - ts < 600]
    if len(recent) >= 10:
        _B2B_JOIN_ATTEMPTS[auth_uid] = recent
        return jsonify({
            "status": "error",
            "code": "RATE_LIMITED",
            "message": "För många försök. Vänta en stund och försök igen.",
        }), 429
    recent.append(now_ts)
    _B2B_JOIN_ATTEMPTS[auth_uid] = recent

    data = request.get_json(silent=True) or {}
    raw_code = str(data.get("invite_code") or data.get("code") or "").strip()
    requested_org_id = str(data.get("org_id") or "").strip() or None

    now_dt = datetime.now(timezone.utc)
    now_iso = now_dt.isoformat()

    try:
        invite_row = None
        org_row = None
        target_role = "member"
        target_department = None

        if raw_code:
            if len(raw_code) > 64 or "%" in raw_code or "_" in raw_code:
                return jsonify({
                    "status": "error",
                    "code": "INVALID_INVITE_CODE",
                    "message": "Ogiltig inbjudningskod.",
                }), 400

            inv_res = (
                supabase.table("organization_invites")
                .select("id,org_id,invite_code,email,role,department,max_uses,used_count,is_active,expires_at")
                .eq("invite_code", raw_code)
                .limit(1)
                .execute()
            )
            if not inv_res.data and raw_code != raw_code.upper():
                inv_res = (
                    supabase.table("organization_invites")
                    .select("id,org_id,invite_code,email,role,department,max_uses,used_count,is_active,expires_at")
                    .eq("invite_code", raw_code.upper())
                    .limit(1)
                    .execute()
                )
            if not inv_res.data:
                return jsonify({
                    "status": "error",
                    "code": "INVALID_INVITE_CODE",
                    "message": "Inbjudningskoden hittades inte.",
                }), 404

            invite_row = inv_res.data[0]
            if not invite_row.get("is_active"):
                return jsonify({
                    "status": "error",
                    "code": "INVITE_INACTIVE",
                    "message": "Inbjudningskoden är inte längre aktiv.",
                }), 400

            expires_at_raw = invite_row.get("expires_at")
            if expires_at_raw:
                exp_dt = datetime.fromisoformat(str(expires_at_raw).replace("Z", "+00:00"))
                if exp_dt <= now_dt:
                    return jsonify({
                        "status": "error",
                        "code": "INVITE_EXPIRED",
                        "message": "Inbjudningskoden har gått ut.",
                    }), 400

            max_uses = int(invite_row.get("max_uses") or 0)
            used_count = int(invite_row.get("used_count") or 0)
            if max_uses > 0 and used_count >= max_uses:
                return jsonify({
                    "status": "error",
                    "code": "INVITE_EXHAUSTED",
                    "message": "Inbjudningskoden har redan förbrukats.",
                }), 409

            locked_email = (invite_row.get("email") or "").strip().lower()
            if locked_email and (not auth_email or auth_email.strip().lower() != locked_email):
                return jsonify({
                    "status": "error",
                    "code": "INVITE_EMAIL_MISMATCH",
                    "message": "Den här inbjudningskoden är knuten till en annan e-postadress.",
                }), 403

            org_res = (
                supabase.table("organizations")
                .select("id,name,org_type,seat_limit,status,allowed_domains")
                .eq("id", invite_row["org_id"])
                .limit(1)
                .execute()
            )
            if not org_res.data or org_res.data[0].get("status") != "active":
                return jsonify({
                    "status": "error",
                    "code": "ORG_INACTIVE",
                    "message": "Organisationen är inte aktiv.",
                }), 403

            org_row = org_res.data[0]
            candidate_role = str(invite_row.get("role") or "member").strip()
            target_role = candidate_role if candidate_role in _B2B_VALID_ROLES else "member"
            target_department = (invite_row.get("department") or "").strip() or None

        else:
            if not auth_email or "@" not in auth_email:
                return jsonify({
                    "status": "error",
                    "code": "INVITE_CODE_REQUIRED",
                    "message": "Ange en inbjudningskod från din arbetsgivare eller försäkringsgivare.",
                }), 400

            email_domain = auth_email.split("@", 1)[1].strip().lower()
            dom_query = (
                supabase.table("organizations")
                .select("id,name,org_type,seat_limit,status,allowed_domains")
                .eq("status", "active")
                .contains("allowed_domains", [email_domain])
            )
            if requested_org_id:
                dom_query = dom_query.eq("id", requested_org_id)
            dom_res = dom_query.limit(1).execute()
            if not dom_res.data:
                return jsonify({
                    "status": "error",
                    "code": "DOMAIN_NOT_ENROLLED",
                    "message": "Din e-postdomän är inte kopplad till någon aktiv organisation. Ange en giltig inbjudningskod.",
                }), 404

            org_row = dom_res.data[0]
            target_role = "member"
            target_department = str(data.get("department") or "").strip() or None

        org_id = org_row["id"]

        existing_res = (
            supabase.table("organization_members")
            .select("id,role,department,status,joined_at")
            .eq("org_id", org_id)
            .eq("user_id", auth_uid)
            .limit(1)
            .execute()
        )
        existing_member = existing_res.data[0] if existing_res.data else None

        if existing_member and existing_member.get("status") == "active":
            role_rank = {
                "member": 1,
                "hr_viewer": 2,
                "hr_admin": 3,
                "insurer_admin": 3,
                "org_admin": 4,
                "admin": 5,
            }
            current_role = existing_member.get("role") or "member"
            effective_role = current_role
            effective_department = existing_member.get("department")
            role_upgraded = False

            if invite_code and role_rank.get(target_role, 0) > role_rank.get(current_role, 0):
                upd_payload = {"role": target_role}
                if target_department:
                    upd_payload["department"] = target_department
                supabase.table("organization_members").update(upd_payload).eq("id", existing_member["id"]).execute()
                effective_role = target_role
                if target_department:
                    effective_department = target_department
                role_upgraded = True

            return jsonify({
                "status": "success",
                "already_member": not role_upgraded,
                "role_upgraded": role_upgraded,
                "is_premium": True,
                "organization": {
                    "id": org_id,
                    "name": org_row.get("name"),
                    "org_type": org_row.get("org_type"),
                },
                "membership": {
                    "id": existing_member.get("id"),
                    "role": effective_role,
                    "department": effective_department,
                    "status": "active",
                },
            }), 200

        active_seats_res = (
            supabase.table("organization_members")
            .select("id", count="exact")
            .eq("org_id", org_id)
            .eq("status", "active")
            .execute()
        )
        active_seats = active_seats_res.count if active_seats_res.count is not None else len(active_seats_res.data or [])
        seat_limit = int(org_row.get("seat_limit") or 0)
        if seat_limit > 0 and active_seats >= seat_limit:
            return jsonify({
                "status": "error",
                "code": "SEAT_LIMIT_REACHED",
                "message": "Organisationens licenstak är uppnått. Kontakta er administratör.",
            }), 409

        if existing_member:
            upd_res = (
                supabase.table("organization_members")
                .update({
                    "role": target_role,
                    "department": target_department,
                    "status": "active",
                    "joined_at": now_iso,
                    "revoked_at": None,
                })
                .eq("id", existing_member["id"])
                .execute()
            )
            member_row = (upd_res.data or [existing_member])[0]
        else:
            ins_res = (
                supabase.table("organization_members")
                .insert({
                    "org_id": org_id,
                    "user_id": auth_uid,
                    "role": target_role,
                    "department": target_department,
                    "status": "active",
                    "joined_at": now_iso,
                })
                .execute()
            )
            member_row = (ins_res.data or [{}])[0]

        if invite_row:
            new_used = int(invite_row.get("used_count") or 0) + 1
            max_u = int(invite_row.get("max_uses") or 0)
            still_active = False if (max_u > 0 and new_used >= max_u) else True
            supabase.table("organization_invites").update({
                "used_count": new_used,
                "redeemed_by": auth_uid,
                "redeemed_at": now_iso,
                "is_active": still_active,
            }).eq("id", invite_row["id"]).execute()

        return jsonify({
            "status": "success",
            "already_member": False,
            "is_premium": True,
            "message": f"Välkommen! Ditt organisationssäte hos {org_row.get('name')} är nu aktivt.",
            "organization": {
                "id": org_id,
                "name": org_row.get("name"),
                "org_type": org_row.get("org_type"),
            },
            "membership": {
                "id": member_row.get("id"),
                "role": member_row.get("role", target_role),
                "department": member_row.get("department", target_department),
                "status": "active",
            },
        }), 200
    except Exception as e:
        logging.error(f"B2B join-fel för {auth_uid}: {e}")
        return jsonify({"status": "error", "message": "Kunde inte aktivera organisationssätet just nu."}), 500


@app.route("/api/b2b/org/analytics", methods=["GET", "OPTIONS"])
def b2b_org_analytics():
    if request.method == "OPTIONS":
        return "", 200

    auth_uid, _, _ = _resolve_auth_user()
    if not auth_uid:
        return jsonify({"status": "error", "code": "AUTH_REQUIRED", "message": "Inloggning krävs."}), 401

    if not _verify_adult_and_terms(auth_uid):
        return jsonify({
            "status": "error",
            "code": "AGE_AND_TERMS_REQUIRED",
            "message": "Bekräftelse av 18+ och godkända villkor krävs.",
        }), 403

    if not supabase:
        return jsonify({"status": "error", "message": "Databasanslutning saknas."}), 500

    requested_org_id = request.args.get("org_id", "").strip() or None
    department = request.args.get("department", "").strip() or None

    admin_mem, org_row = _get_active_b2b_admin_membership(auth_uid, requested_org_id)
    if not admin_mem or not org_row:
        return jsonify({
            "status": "error",
            "code": "ORG_ADMIN_REQUIRED",
            "message": "Behörighet som HR- eller organisationsadministratör krävs.",
        }), 403

    org_id = org_row["id"]
    try:
        rpc_res = supabase.rpc(
            "get_b2b_org_analytics",
            {"p_org_id": org_id, "p_department": department},
        ).execute()
        payload = rpc_res.data
        if isinstance(payload, list):
            payload = payload[0] if payload else {}
        if not isinstance(payload, dict):
            payload = {}

        return jsonify({
            "status": "success",
            "organization": {
                "id": org_id,
                "name": org_row.get("name"),
                "org_type": org_row.get("org_type"),
                "seat_limit": org_row.get("seat_limit"),
            },
            "department": department,
            "analytics": payload,
        }), 200
    except Exception as e:
        logging.error(f"B2B analytics-fel för org {org_id}: {e}")
        return jsonify({"status": "error", "message": "Kunde inte hämta anonymiserad organisationsanalys."}), 500


@app.route("/api/b2b/org/members", methods=["GET", "POST", "DELETE", "OPTIONS"])
def b2b_org_members():
    if request.method == "OPTIONS":
        return "", 200

    auth_uid, _, _ = _resolve_auth_user()
    if not auth_uid:
        return jsonify({"status": "error", "code": "AUTH_REQUIRED", "message": "Inloggning krävs."}), 401

    if not _verify_adult_and_terms(auth_uid):
        return jsonify({
            "status": "error",
            "code": "AGE_AND_TERMS_REQUIRED",
            "message": "Bekräftelse av 18+ och godkända villkor krävs.",
        }), 403

    if not supabase:
        return jsonify({"status": "error", "message": "Databasanslutning saknas."}), 500

    data = request.get_json(silent=True) or {}
    requested_org_id = (
        request.args.get("org_id", "").strip()
        or str(data.get("org_id") or "").strip()
        or None
    )

    admin_mem, org_row = _get_active_b2b_admin_membership(auth_uid, requested_org_id)
    if not admin_mem or not org_row:
        return jsonify({
            "status": "error",
            "code": "ORG_ADMIN_REQUIRED",
            "message": "Behörighet som HR- eller organisationsadministratör krävs.",
        }), 403

    org_id = org_row["id"]
    seat_limit = int(org_row.get("seat_limit") or 0)

    try:
        if request.method == "GET":
            members_res = (
                supabase.table("organization_members")
                .select("id,user_id,role,department,status,joined_at,revoked_at")
                .eq("org_id", org_id)
                .order("joined_at", desc=True)
                .execute()
            )
            raw_members = members_res.data or []
            active_count = sum(1 for m in raw_members if m.get("status") == "active")

            sanitized_members = []
            for m in raw_members:
                uid_m = m.get("user_id")
                member_email = None
                if SUPABASE_SERVICE_ROLE_KEY and uid_m:
                    try:
                        u_resp = supabase.auth.admin.get_user_by_id(uid_m)
                        u_obj = getattr(u_resp, "user", None)
                        member_email = getattr(u_obj, "email", None)
                    except Exception:
                        member_email = None
                sanitized_members.append({
                    "id": m.get("id"),
                    "user_id": uid_m,
                    "email": member_email,
                    "role": m.get("role"),
                    "department": m.get("department"),
                    "status": m.get("status"),
                    "joined_at": m.get("joined_at"),
                    "revoked_at": m.get("revoked_at"),
                })

            invites_res = (
                supabase.table("organization_invites")
                .select("id,invite_code,email,role,department,max_uses,used_count,is_active,expires_at,created_at")
                .eq("org_id", org_id)
                .order("created_at", desc=True)
                .limit(50)
                .execute()
            )

            return jsonify({
                "status": "success",
                "organization": {
                    "id": org_id,
                    "name": org_row.get("name"),
                    "org_type": org_row.get("org_type"),
                    "seat_limit": seat_limit,
                    "active_seats": active_count,
                    "available_seats": max(0, seat_limit - active_count) if seat_limit > 0 else None,
                },
                "members": sanitized_members,
                "invites": invites_res.data or [],
            }), 200

        if request.method == "POST":
            action = str(data.get("action") or "create_invite").strip().lower()

            if action == "update_member":
                member_id = str(data.get("member_id") or "").strip()
                if not member_id:
                    return jsonify({"status": "error", "message": "member_id krävs."}), 400
                updates = {}
                if "department" in data:
                    updates["department"] = str(data.get("department") or "").strip() or None
                if "role" in data:
                    new_role = str(data.get("role") or "").strip()
                    if new_role not in _B2B_VALID_ROLES:
                        return jsonify({"status": "error", "message": "Ogiltig organisationsroll."}), 400
                    updates["role"] = new_role
                if not updates:
                    return jsonify({"status": "error", "message": "Inga fält att uppdatera."}), 400

                upd_res = (
                    supabase.table("organization_members")
                    .update(updates)
                    .eq("id", member_id)
                    .eq("org_id", org_id)
                    .execute()
                )
                return jsonify({
                    "status": "success",
                    "member": (upd_res.data or [{}])[0],
                }), 200

            import secrets
            from datetime import datetime, timedelta, timezone

            role = str(data.get("role") or "member").strip()
            if role not in _B2B_VALID_ROLES:
                return jsonify({"status": "error", "message": "Ogiltig roll för inbjudan."}), 400

            max_uses = int(data.get("max_uses") or 1)
            if max_uses < 1 or max_uses > 500:
                return jsonify({"status": "error", "message": "max_uses måste vara mellan 1 och 500."}), 400

            department = str(data.get("department") or "").strip() or None
            target_email = str(data.get("email") or "").strip().lower() or None
            expires_days = int(data.get("expires_in_days") or 30)
            expires_at = (datetime.now(timezone.utc) + timedelta(days=max(1, min(365, expires_days)))).isoformat()
            invite_code = f"FALK-{secrets.token_hex(4).upper()}"

            inv_insert = (
                supabase.table("organization_invites")
                .insert({
                    "org_id": org_id,
                    "invite_code": invite_code,
                    "email": target_email,
                    "role": role,
                    "department": department,
                    "max_uses": max_uses,
                    "used_count": 0,
                    "is_active": True,
                    "expires_at": expires_at,
                    "created_by": auth_uid,
                })
                .execute()
            )
            return jsonify({
                "status": "success",
                "invite": (inv_insert.data or [{}])[0],
            }), 201

        # DELETE: Återkalla säte
        from datetime import datetime, timezone

        target_member_id = request.args.get("member_id", "").strip() or str(data.get("member_id") or "").strip()
        target_user_id = request.args.get("user_id", "").strip() or str(data.get("user_id") or "").strip()
        if not target_member_id and not target_user_id:
            return jsonify({"status": "error", "message": "member_id eller user_id krävs för återkallande."}), 400

        if target_user_id == auth_uid or target_member_id == admin_mem.get("id"):
            return jsonify({
                "status": "error",
                "code": "CANNOT_REVOKE_SELF",
                "message": "Du kan inte återkalla din egen administratörsbehörighet.",
            }), 400

        now_iso = datetime.now(timezone.utc).isoformat()
        rev_query = (
            supabase.table("organization_members")
            .update({"status": "revoked", "revoked_at": now_iso})
            .eq("org_id", org_id)
        )
        if target_member_id:
            rev_query = rev_query.eq("id", target_member_id)
        else:
            rev_query = rev_query.eq("user_id", target_user_id)

        rev_res = rev_query.execute()
        if not rev_res.data:
            return jsonify({"status": "error", "message": "Medlemmen hittades inte i organisationen."}), 404

        return jsonify({
            "status": "success",
            "message": "Organisationssätet har återkallats.",
            "member": rev_res.data[0],
        }), 200
    except Exception as e:
        logging.error(f"B2B members-fel för org {org_id}: {e}")
        return jsonify({"status": "error", "message": "Kunde inte hantera organisationsmedlemmar."}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)
