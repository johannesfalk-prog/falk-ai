import os
import re
import time
import logging
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Tuple, List

import requests
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from supabase import create_client, Client

from safety_guardrails import evaluate_safety_and_crisis
from state_machine import FalkStateMachine
from prompt_builder import build_falk_system_prompt, COMPASS_SESSIONS
from gate_checker import validate_response_against_gates
from exercise_library import FALK_15_EXERCISE_CARDS, get_library_cards
from b2b_extensions import (
    B2B_COMPASSES,
    get_b2b_compasses,
    aggregate_b2b_compass_data,
    recommend_b2b_exercises,
)
from dotenv import load_dotenv
from pdf_exporter import generate_session_pdf_html
from vector_memory import retrieve_rag_memories, store_memory_vector

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
FALK_PRIMARY_MODEL = os.getenv("FALK_PRIMARY_MODEL", "gpt-4.1").strip() or "gpt-4.1"
FALK_GROQ_MODEL = os.getenv("FALK_GROQ_MODEL", "llama-3.3-70b-versatile").strip() or "llama-3.3-70b-versatile"

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
    import time
    full_messages = [{"role": "system", "content": system_prompt}] + messages_payload
    deadline = time.monotonic() + 24.0

    if OPENAI_API_KEY:
        try:
            import openai
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            openai_models = list(dict.fromkeys([FALK_PRIMARY_MODEL, "gpt-4o", "gpt-4o-mini"]))
            for model_name in openai_models:
                remaining = deadline - time.monotonic()
                if remaining < 4.0:
                    break
                try:
                    res = client.chat.completions.create(
                        model=model_name,
                        messages=full_messages,
                        temperature=0.65,
                        max_tokens=max_tokens,
                        timeout=min(15.0, remaining),
                    )
                    content = (res.choices[0].message.content or "").strip()
                    if content:
                        return content
                except Exception as model_err:
                    logging.warning(f"OpenAI ({model_name}) misslyckades: {model_err}")
        except Exception as e:
            logging.error(f"OpenAI-klientfel: {e}")

    if GROQ_API_KEY:
        remaining = deadline - time.monotonic()
        if remaining >= 3.0:
            try:
                res = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {GROQ_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": FALK_GROQ_MODEL,
                        "messages": full_messages,
                        "temperature": 0.65,
                        "max_tokens": max_tokens,
                    },
                    timeout=min(12.0, remaining),
                )
                if res.status_code == 200:
                    content = res.json()["choices"][0]["message"]["content"].strip()
                    if content:
                        return content
                logging.warning(f"Groq API status {res.status_code}: {res.text[:200]}")
            except Exception as e:
                logging.error(f"Groq-anrop misslyckades: {e}")

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
    "du har helt rätt",
    "du har absolut rätt",
    "helt rätt tänkt",
    "vilken bra insikt",
    "det är fruktansvärt",
    "det är hemskt",
)


def _apply_gate_filter(
    reply: str,
    user_message: str,
    stage: str,
    system_prompt: str,
    is_guest: bool = True,
    previous_assistant_response: Optional[str] = None,
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
        previous_assistant_response=previous_assistant_response,
    )
    if not passed:
        logging.info(f"Five Gates justerade svar: {meta.get('violated_gates')} - {meta.get('feedback')}")
    return final_response or reply


def _maybe_store_continuity_vector(uid: str, session_id: Optional[str], user_message: str) -> None:
    """
    Sparar selektivt långsiktiga utvecklingsmarkörer (värderingar, riktning, mål,
    mönster, lärdomar) i vektorlagret i bakgrunden för inloggade användare.
    """
    if not uid or not user_message or len(user_message.strip()) < 35:
        return
    markers = (
        "värdering", "viktigt för mig", "riktning", "nordstjärna", "mål",
        "mönster", "lärdom", "insikt", "beslut", "rädd för", "längtar efter",
        "vill förändra", "gräns", "balans", "syfte", "mening",
    )
    lowered = user_message.lower()
    if not any(m in lowered for m in markers):
        return

    def _worker():
        try:
            store_memory_vector(
                user_id=uid,
                session_id=session_id or "general",
                content=user_message.strip()[:800],
                memory_layer="LONG_TERM",
            )
        except Exception as e:
            logging.warning(f"Bakgrundslagring i vector_memory misslyckades: {e}")

    threading.Thread(target=_worker, daemon=True).start()


def _fetch_user_continuity(uid: str) -> Tuple[List[str], Optional[str]]:
    """
    Hämtar och prioriterar användarens kontinuitet enligt Falk Bible Kap 7
    och Falk Playbook Kap 10 (The Wayjs Continuity System):
    påminnelser, aktiva mål, mönster/värderingar/framsteg med tidsstämplar,
    senaste kapitel ur Livsboken, insikter samt kompassrörelse över tid.
    """
    if not supabase or not uid:
        return [], None

    def _fmt_date(raw_ts: Any) -> str:
        if not raw_ts:
            return ""
        s = str(raw_ts).strip()
        return s[:10] if len(s) >= 10 else s

    reminders_ctx: List[str] = []
    goals_ctx: List[str] = []
    memories_ctx: List[str] = []
    journal_ctx: List[str] = []
    insights_ctx: List[str] = []
    compass_summary: Optional[str] = None

    # 1. Kommande/aktiva påminnelser (Playbook 15.15)
    try:
        rem_res = (
            supabase.table("falk_reminders")
            .select("title, description, frequency, next_trigger_at")
            .eq("user_id", uid)
            .order("next_trigger_at", desc=False)
            .limit(3)
            .execute()
        )
        for r in (rem_res.data or [])[:2]:
            title = (r.get("title") or "").strip()
            desc = (r.get("description") or "").strip()
            when = _fmt_date(r.get("next_trigger_at"))
            freq = (r.get("frequency") or "").strip()
            if title:
                meta = ", ".join(p for p in [when, freq] if p)
                prefix = f"[Påminnelse · {meta}]" if meta else "[Påminnelse]"
                detail = f" – {desc}" if desc else ""
                reminders_ctx.append(f"{prefix} {title}{detail}")
    except Exception as e:
        logging.warning(f"Kunde inte hämta falk_reminders: {e}")

    # 2. Aktiva mål (Playbook 10.13 Målbibliotek)
    try:
        goal_res = (
            supabase.table("falk_goals")
            .select("title, description, area, progress, target_date")
            .eq("user_id", uid)
            .limit(5)
            .execute()
        )
        active_goals = [
            g for g in (goal_res.data or [])
            if (g.get("progress") is None or int(g.get("progress") or 0) < 100)
        ]
        for g in active_goals[:2]:
            title = (g.get("title") or "").strip()
            area = (g.get("area") or "").strip()
            prog = g.get("progress")
            target = _fmt_date(g.get("target_date"))
            if title:
                meta_parts = [p for p in [area, f"{prog}%" if prog is not None else "", f"mål {target}" if target else ""] if p]
                meta = f" ({', '.join(meta_parts)})" if meta_parts else ""
                goals_ctx.append(f"[Aktivt mål] {title}{meta}")
    except Exception as e:
        logging.warning(f"Kunde inte hämta falk_goals: {e}")

    # 3. Långtidsminnen, återkommande mönster & framsteg (Falk Bible 7.3, 7.6 & Playbook 10.5, 10.11)
    try:
        mem_res = (
            supabase.table("falk_memory")
            .select("memory_type, content, importance, created_at")
            .eq("user_id", uid)
            .order("importance", desc=True)
            .order("created_at", desc=True)
            .limit(8)
            .execute()
        )
        type_meta = {
            "pattern": ("Återkommande mönster", 0),
            "north_star": ("Nordstjärna/Riktning", 1),
            "direction": ("Riktning", 1),
            "value": ("Värdering", 1),
            "progress": ("Framsteg/Mod", 2),
            "milestone": ("Milstolpe", 2),
            "decision": ("Beslut", 3),
            "lesson": ("Lärdom", 4),
            "habit": ("Vana", 4),
            "preference": ("Preferens", 5),
        }
        raw_mems = [m for m in (mem_res.data or []) if (m.get("content") or "").strip()]
        raw_mems.sort(
            key=lambda m: (
                type_meta.get(str(m.get("memory_type") or "").lower(), ("Minne", 6))[1],
                -(int(m.get("importance") or 0)),
            )
        )
        for m in raw_mems[:4]:
            mtype = str(m.get("memory_type") or "").lower()
            label, _ = type_meta.get(mtype, ("Minne", 6))
            dt = _fmt_date(m.get("created_at"))
            header = f"[{label} · {dt}]" if dt else f"[{label}]"
            memories_ctx.append(f"{header} {m['content'].strip()}")
    except Exception as e:
        logging.warning(f"Kunde inte hämta falk_memory: {e}")

    # 4. Senaste kapitel i Livsboken / The Compass Journal (Falk Bible 7.1, 7.14)
    try:
        j_res = (
            supabase.table("falk_compass_journal")
            .select("chapter_number, chapter_title, summary, key_themes, created_at")
            .eq("user_id", uid)
            .order("chapter_number", desc=True)
            .limit(2)
            .execute()
        )
        for ch in (j_res.data or []):
            num = ch.get("chapter_number")
            title = (ch.get("chapter_title") or "").strip()
            summary = (ch.get("summary") or "").strip()
            dt = _fmt_date(ch.get("created_at"))
            themes = ch.get("key_themes") or []
            theme_str = f" (Teman: {', '.join(str(t) for t in themes[:4])})" if themes else ""
            if summary or title:
                dt_part = f" · {dt}" if dt else ""
                journal_ctx.append(f"[Livsboken Kap {num}{dt_part}: {title}] {summary}{theme_str}")
    except Exception as e:
        logging.warning(f"Kunde inte hämta falk_compass_journal: {e}")

    # 5. Senaste insikter (Playbook 10.12 Insiktsbibliotek)
    try:
        ins_res = (
            supabase.table("falk_insights")
            .select("title, content, category, created_at")
            .eq("user_id", uid)
            .order("created_at", desc=True)
            .limit(2)
            .execute()
        )
        for ins in (ins_res.data or []):
            title = (ins.get("title") or "").strip()
            content = (ins.get("content") or "").strip()
            cat = (ins.get("category") or "").strip()
            dt = _fmt_date(ins.get("created_at"))
            meta = " · ".join(p for p in [dt, cat] if p)
            prefix = f"[Insikt · {meta}]" if meta else "[Insikt]"
            body = f"{title}: {content}" if (title and content and title != content) else (title or content)
            if body:
                insights_ctx.append(f"{prefix} {body}")
    except Exception as e:
        logging.warning(f"Kunde inte hämta falk_insights: {e}")

    # 6. Kompassen över tid – senaste mätning + progression mot föregående (Falk Bible 7.5 & Playbook 10.10)
    try:
        sc_res = (
            supabase.table("compass_scores")
            .select("riktning, balans, handling, reflektion, overall_index, created_at")
            .eq("user_id", uid)
            .order("created_at", desc=True)
            .limit(2)
            .execute()
        )
        rows = sc_res.data or []
        if rows:
            curr = rows[0]
            curr_dt = _fmt_date(curr.get("created_at"))
            base_line = (
                f"Senaste kompasskalibrering ({curr_dt or 'aktuell'}): "
                f"Helhetsindex {curr.get('overall_index')}/100 "
                f"(Riktning: {curr.get('riktning')}, Balans: {curr.get('balans')}, "
                f"Handling: {curr.get('handling')}, Reflektion: {curr.get('reflektion')})."
            )
            if len(rows) >= 2:
                prev = rows[1]
                prev_dt = _fmt_date(prev.get("created_at"))
                def _d(k: str) -> str:
                    try:
                        diff = int(round(float(curr.get(k) or 0) - float(prev.get(k) or 0)))
                        return f"{diff:+d}"
                    except Exception:
                        return "0"
                delta_line = (
                    f" Utveckling sedan {prev_dt or 'föregående mätning'}: "
                    f"Helhet {_d('overall_index')}, Riktning {_d('riktning')}, "
                    f"Balans {_d('balans')}, Handling {_d('handling')}, Reflektion {_d('reflektion')}."
                )
                compass_summary = base_line + delta_line
            else:
                compass_summary = base_line
    except Exception as e:
        logging.warning(f"Kunde inte hämta compass_scores: {e}")

    ordered_memories = reminders_ctx + goals_ctx + memories_ctx + journal_ctx + insights_ctx
    return ordered_memories, compass_summary



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
        try:
            rag_block = retrieve_rag_memories(auth_uid, message, limit=3)
            if rag_block:
                memories.append(rag_block.strip())
        except Exception as e:
            logging.warning(f"Hybrid RAG-hämtning hoppades över: {e}")

    sanitized_b2b_context = None
    raw_b2b = data.get("b2b_context")
    if not is_guest and auth_uid and isinstance(raw_b2b, dict):
        b2b_level = str(raw_b2b.get("level") or "individ").strip().lower()
        if b2b_level not in ("individ", "ledning", "foretag"):
            b2b_level = "individ"
        sanitized_b2b_context = {
            "level": b2b_level,
            "org_name": str(raw_b2b.get("org_name") or "").strip()[:120],
            "topic_hint": str(raw_b2b.get("topic_hint") or "").strip()[:120],
        }
        if b2b_level == "individ":
            sanitized_b2b_context["role"] = str(raw_b2b.get("role") or "").strip()[:80]
            if isinstance(raw_b2b.get("compass_scores"), dict):
                sanitized_b2b_context["compass_scores"] = {
                    str(k): float(v)
                    for k, v in raw_b2b["compass_scores"].items()
                    if isinstance(v, (int, float))
                }
        else:
            if isinstance(raw_b2b.get("records"), list):
                agg = aggregate_b2b_compass_data(raw_b2b["records"], k_min=None)
                sanitized_b2b_context["compass_averages"] = agg.get("compass_averages", {})
                sanitized_b2b_context["respondent_count"] = agg.get("respondent_count", 0)
            elif isinstance(raw_b2b.get("compass_averages"), dict):
                sanitized_b2b_context["compass_averages"] = {
                    str(k): float(v)
                    for k, v in raw_b2b["compass_averages"].items()
                    if isinstance(v, (int, float))
                }
                sanitized_b2b_context["respondent_count"] = int(raw_b2b.get("respondent_count") or 0)

    sanitized_session_mode = None
    final_compass_flag = False
    is_moderator_session = False
    raw_session = data.get("session_mode")
    requested_moderator = (
        (isinstance(raw_session, str) and raw_session.strip().lower() == "moderator")
        or (isinstance(raw_session, dict) and str(raw_session.get("track") or "").strip().lower() == "moderator")
    )
    if requested_moderator:
        if is_guest or not is_premium:
            return jsonify({
                "status": "error",
                "code": "PREMIUM_REQUIRED",
                "message": "Moderatorläget för par- och gruppsamtal kräver FALK Premium.",
            }), 403
        mod_context = "private"
        is_checkin_synth = False
        mod_participants = []
        mod_current_speaker = ""
        mod_next_speaker = ""
        mod_overlap_event = None
        if isinstance(raw_session, dict):
            if str(raw_session.get("context") or "").strip().lower() == "b2b":
                mod_context = "b2b"
            is_checkin_synth = bool(raw_session.get("check_in_synthesis"))
            raw_parts = raw_session.get("participants")
            if isinstance(raw_parts, list):
                for item in raw_parts[:8]:
                    cp = " ".join(str(item or "").split()).strip()[:60]
                    if cp and cp not in mod_participants:
                        mod_participants.append(cp)
            mod_current_speaker = " ".join(str(raw_session.get("current_speaker") or "").split()).strip()[:60]
            mod_next_speaker = " ".join(str(raw_session.get("next_speaker") or "").split()).strip()[:60]
            raw_ov = raw_session.get("overlap_event")
            if isinstance(raw_ov, dict):
                sel_sp = " ".join(str(raw_ov.get("selected_speaker") or "").split()).strip()[:60]
                def_sp = " ".join(str(raw_ov.get("deferred_speaker") or "").split()).strip()[:60]
                raw_cands = raw_ov.get("candidates")
                if not sel_sp and isinstance(raw_cands, list):
                    clean_cands = []
                    for c in raw_cands[:8]:
                        cc = " ".join(str(c or "").split()).strip()[:60]
                        if cc and cc not in clean_cands:
                            clean_cands.append(cc)
                    if len(clean_cands) >= 2:
                        picked = _mod_secrets.SystemRandom().sample(clean_cands, 2)
                        sel_sp, def_sp = picked[0], picked[1]
                if sel_sp:
                    mod_overlap_event = {
                        "selected_speaker": sel_sp,
                        "deferred_speaker": def_sp,
                    }
                    mod_next_speaker = sel_sp
        sanitized_session_mode = {
            "track": "moderator",
            "context": mod_context,
            "check_in_synthesis": is_checkin_synth,
            "participants": mod_participants,
            "current_speaker": mod_current_speaker,
            "next_speaker": mod_next_speaker,
            "overlap_event": mod_overlap_event,
        }
        is_moderator_session = True
    elif not is_guest and is_premium:
        if isinstance(raw_session, dict):
            track = str(raw_session.get("track") or "").strip().lower()
            if track in COMPASS_SESSIONS:
                try:
                    dur = int(raw_session.get("duration_minutes") or 15)
                except (ValueError, TypeError):
                    dur = 15
                if dur not in (15, 30, 60):
                    dur = 15
                sanitized_session_mode = {"track": track, "duration_minutes": dur}
        final_compass_flag = bool(data.get("final_compass"))

    if is_moderator_session:
        memories = []
        compass_summary = None

    # Prioritera semantiska RAG-träffar före bakgrundskontinuitet så de inte trunkeras av [:10]-taket
    if memories:
        _structured_prefixes = (
            "[Påminnelse", "[Aktivt mål", "[Återkommande mönster", "[Nordstjärna",
            "[Riktning", "[Värdering", "[Framsteg", "[Milstolpe", "[Beslut",
            "[Lärdom", "[Vana", "[Preferens", "[Minne", "[Livsboken", "[Insikt",
        )
        _rag_hits = [
            f"[Relevant tidigare samtal] {m}" if not m.startswith("[") else m
            for m in memories
            if not m.startswith(_structured_prefixes)
        ][:3]
        _cont_hits = [m for m in memories if m.startswith(_structured_prefixes)]
        memories = _rag_hits + _cont_hits

    _active_uid = auth_uid if 'auth_uid' in locals() else None
    _resolved_user_name = _resolve_user_display_name(
        _active_uid,
        is_guest if 'is_guest' in locals() else True,
        fallback_name=data.get("display_name"),
    )
    _created_reminder = None if is_moderator_session else _maybe_create_chat_reminder(message, _active_uid, is_guest if 'is_guest' in locals() else True)
    system_prompt = build_falk_system_prompt(
        user_message=message,
        current_stage=next_stage,
        is_guest=is_guest,
        focus_sliders=focus_sliders,
        user_context_memories=memories,
        compass_summary=compass_summary,
        response_variant=response_variant,
        b2b_context=sanitized_b2b_context,
        session_mode=sanitized_session_mode,
        final_compass=final_compass_flag,
        is_new_session=(len(clean_history) == 0),
        user_name=_resolved_user_name,
    )
    if _created_reminder:
        system_prompt += (
            "\n\n[SYSTEMBEKRÄFTELSE – PÅMINNELSE SKAPAD]\n"
            f"En påminnelse har nu sparats i användarens konto och schemalagts för push-notis:\n"
            f"- Innehåll: \"{_created_reminder.get('content', '')}\"\n"
            f"- Tidpunkt (svensk tid): {_created_reminder.get('local_time_label', '')}\n"
            "Bekräfta detta naturligt, lugnt och varmt i ditt svar som FALK. "
            "Säg INTE att du saknar förmåga att skapa påminnelser."
        )

    convo_messages = clean_history + [{"role": "user", "content": message}]
    raw_reply = _call_llm(system_prompt, convo_messages)
    prev_assistant = next(
        (m.get("content") for m in reversed(clean_history) if m.get("role") == "assistant" and m.get("content")),
        None,
    )
    final_reply = _apply_gate_filter(
        raw_reply,
        message,
        next_stage,
        system_prompt,
        is_guest=is_guest,
        previous_assistant_response=prev_assistant,
    )

    conversation_id = data.get("conversation_id")
    if supabase and not is_guest and auth_uid and not is_moderator_session:
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
        _maybe_store_continuity_vector(auth_uid, conversation_id, message)
        _sync_journal_and_memory(auth_uid, conversation_id, message, final_reply, next_stage)

    moderator_meta = None
    if is_moderator_session:
        final_reply, moderator_meta = _parse_moderator_reply_meta(final_reply)
        if isinstance(moderator_meta, dict):
            if mod_overlap_event:
                moderator_meta["overlap_event"] = mod_overlap_event
                moderator_meta["next_speaker"] = mod_overlap_event["selected_speaker"]
            elif not moderator_meta.get("next_speaker") and mod_next_speaker:
                moderator_meta["next_speaker"] = mod_next_speaker

    return jsonify({
        "status": "success",
        "reply": final_reply,
        "stage": next_stage,
        "variant": response_variant,
        "user_tier": user_tier,
        "conversation_id": conversation_id,
        "guest_remaining": guest_remaining,
        "suggested_goal": None if is_moderator_session else _extract_goal_suggestion(message if "message" in locals() else "", is_guest if "is_guest" in locals() else True),
        "reminder": _created_reminder,
        "moderator_meta": moderator_meta,
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

    _resolved_user_name = _resolve_user_display_name(
        auth_uid,
        is_guest,
        fallback_name=data.get("display_name"),
    )
    system_prompt = build_falk_system_prompt(
        user_message=check_target,
        current_stage=active_stage,
        is_guest=is_guest,
        focus_sliders=focus_sliders,
        user_context_memories=memories,
        compass_summary=compass_summary,
        response_variant=response_variant,
        user_name=_resolved_user_name,
    )

    context_input = (
        f"Användarens ursprungliga fråga: {user_prompt}\n"
        f"Tidigare FALK-svar att omformulera/justera: {original_reply}"
        if user_prompt
        else original_reply
    )
    variant_max_tokens = {"deeper": 1100, "concise": 320}.get(response_variant, 650)
    raw_reply = _call_llm(
        system_prompt,
        [{"role": "user", "content": context_input}],
        max_tokens=variant_max_tokens,
    )
    final_reply = _apply_gate_filter(
        raw_reply,
        check_target,
        active_stage,
        system_prompt,
        is_guest=is_guest,
        previous_assistant_response=original_reply,
    )

    return jsonify({
        "status": "success",
        "action": action,
        "variant": response_variant,
        "reply": final_reply,
    }), 200


def _sync_journal_and_memory(
    uid: str,
    conversation_id: Optional[str],
    user_message: str,
    assistant_reply: str,
    stage: str,
) -> None:
    """
    Uppdaterar användarens sessionskopplade kapitel i falk_compass_journal (ackumulerande syntes)
    och destillerar selektiva utvecklingsminnen i falk_memory (endast inloggade, ej småprat).
    """
    if not supabase or not uid:
        return

    from datetime import datetime as _dt, timezone as _tz
    import json as _json
    import re as _re

    clean_msg = (user_message or "").strip()
    clean_reply = (assistant_reply or "").strip()
    if not clean_msg:
        return

    # Ignorera rent småprat / korta hälsningar (Playbook Kap 10.4)
    trivial_phrases = {
        "hej", "hejsan", "hallå", "tja", "god morgon", "god kväll",
        "tack", "tack så mycket", "ok", "okej", "ja", "nej", "mm", "bra", "toppen",
    }
    norm_check = _re.sub(r"[.!?,\s]+$", "", clean_msg.lower())
    is_trivial = len(clean_msg) < 18 or norm_check in trivial_phrases

    existing_row = None
    prev_summary = ""
    prev_title = ""
    if conversation_id:
        try:
            existing = (
                supabase.table("falk_compass_journal")
                .select("id, chapter_number, chapter_title, summary")
                .eq("user_id", uid)
                .eq("conversation_id", conversation_id)
                .limit(1)
                .execute()
            )
            if existing.data:
                existing_row = existing.data[0]
                prev_summary = (existing_row.get("summary") or "").strip()
                prev_title = (existing_row.get("chapter_title") or "").strip()
        except Exception as e:
            logging.warning(f"Kunde inte läsa befintligt kapitel i falk_compass_journal: {e}")

    recent_memories: List[str] = []
    try:
        rmem = (
            supabase.table("falk_memory")
            .select("content")
            .eq("user_id", uid)
            .order("created_at", desc=True)
            .limit(6)
            .execute()
        )
        if rmem.data:
            recent_memories = [(r.get("content") or "").strip() for r in rmem.data if r.get("content")]
    except Exception as e:
        logging.warning(f"Kunde inte hämta befintliga minnen för dedup: {e}")

    distilled = None
    if not is_trivial:
        distill_system = (
            "Du är Wayjs Continuity Engine för FALK (en lugn, vis mentor). "
            "Destillera samtalsutbytet till strukturerad JSON på svenska enligt Falk Bible Kap 7 & Playbook Kap 10. "
            "REGLER: "
            "1. Spara ALDRIG småprat, tillfälliga känslor utan riktning eller råa citat. "
            "2. 'chapter_title': En varm, konkret kapiteltitel på svenska (3–7 ord, inga citattecken). "
            "3. 'chapter_summary': Syntetisera den röda tråden i samtalet (2–3 lugna meningar, max 420 tecken). "
            "Om ett tidigare kapitelutkast finns, väv samman den nya fördjupningen med det befintliga utan att tappa kärnan. "
            "4. 'save_memory': true ENDAST om användaren uttryckt en tydlig värdering, livsriktning, återkommande mönster, "
            "viktigt beslut, lärdom eller milstolpe som är värdefull om 6 månader (och inte redan täcks av befintliga minnen). Annars false. "
            "5. 'memory_category': En av 'riktning', 'varderingar', 'monster', 'beslut', 'insikt', 'framsteg', 'utveckling'. "
            "6. 'memory_content': En koncis, icke-dömande mening på svenska (max 220 tecken) som beskriver användarens riktning eller insikt. "
            "Svara Uteslutande med giltig JSON med nycklarna: chapter_title, chapter_summary, save_memory, memory_category, memory_content."
        )
        distill_user = (
            f"Samtalsfas: {stage}\n"
            f"Befintlig kapiteltitel: {prev_title or '(nytt kapitel)'}\n"
            f"Befintligt kapitelutkast: {prev_summary or '(inget ännu)'}\n"
            f"Redan sparade minnen: {recent_memories[:4]}\n"
            f"Användarens meddelande: {clean_msg[:900]}\n"
            f"FALKs svar: {clean_reply[:900]}"
        )
        try:
            raw_json = _call_llm(
                distill_system,
                [{"role": "user", "content": distill_user}],
                max_tokens=700,
            )
            match = _re.search(r"\{.*\}", raw_json or "", _re.DOTALL)
            if match:
                parsed = _json.loads(match.group(0))
                if isinstance(parsed, dict):
                    distilled = parsed
        except Exception as e:
            logging.warning(f"AI-destillering av minne/journal föll tillbaka till säker standard: {e}")

    # 1. Compass Journal (1 ackumulerande kapitel per conversation_id -> ON DELETE CASCADE)
    if conversation_id:
        try:
            now_iso = _dt.now(_tz.utc).isoformat()
            if distilled and (distilled.get("chapter_summary") or "").strip():
                summary_text = str(distilled["chapter_summary"]).strip()[:480]
                ai_title = str(distilled.get("chapter_title") or "").strip().strip('"')[:80]
            else:
                fallback_core = clean_msg[:220]
                if prev_summary:
                    summary_text = f"{prev_summary[:240]} Vidare reflektion: {fallback_core}"[:480]
                else:
                    summary_text = f"Reflektion kring: {fallback_core}"[:480]
                ai_title = ""

            if existing_row:
                row_id = existing_row["id"]
                update_payload = {
                    "summary": summary_text,
                    "updated_at": now_iso,
                }
                if ai_title and (not prev_title or prev_title.startswith("Kapitel ") or len(prev_title) < 6):
                    update_payload["chapter_title"] = ai_title
                supabase.table("falk_compass_journal").update(update_payload).eq("id", row_id).eq("user_id", uid).execute()
            else:
                all_ch = (
                    supabase.table("falk_compass_journal")
                    .select("chapter_number")
                    .eq("user_id", uid)
                    .order("chapter_number", desc=True)
                    .limit(1)
                    .execute()
                )
                next_ch = (all_ch.data[0]["chapter_number"] + 1) if all_ch.data else 1
                title_text = ai_title or (clean_msg[:60] if len(clean_msg) >= 4 else f"Kapitel {next_ch}")
                supabase.table("falk_compass_journal").insert({
                    "user_id": uid,
                    "conversation_id": conversation_id,
                    "chapter_number": next_ch,
                    "chapter_title": title_text,
                    "summary": summary_text,
                    "updated_at": now_iso,
                }).execute()
        except Exception as e:
            logging.warning(f"Kunde inte synka falk_compass_journal: {e}")

    # 2. Selektivt långtidsminne (spara endast destillerad utveckling, aldrig småprat)
    if distilled and distilled.get("save_memory") is True:
        try:
            allowed_cats = {
                "riktning", "varderingar", "monster", "beslut", "insikt", "framsteg", "utveckling"
            }
            raw_cat = str(distilled.get("memory_category") or "utveckling").strip().lower()
            category = raw_cat if raw_cat in allowed_cats else "utveckling"
            mem_content = str(distilled.get("memory_content") or "").strip()[:300]

            if len(mem_content) >= 12:
                norm_new = mem_content.lower()
                is_dup = any(
                    norm_new == m.lower() or norm_new in m.lower() or m.lower() in norm_new
                    for m in recent_memories
                )
                if not is_dup:
                    supabase.table("falk_memory").insert({
                        "user_id": uid,
                        "category": category,
                        "content": mem_content,
                    }).execute()
        except Exception as e:
            logging.warning(f"Kunde inte synka falk_memory: {e}")


@app.route("/api/journal", methods=["GET", "OPTIONS"])
def get_compass_journal():
    if request.method == "OPTIONS":
        return "", 200
    auth_uid, _, _ = _resolve_auth_user()
    if not auth_uid:
        return jsonify({"status": "error", "message": "Autentisering krävs."}), 401
    if not supabase:
        return jsonify({"status": "error", "message": "Databas ej tillgänglig."}), 503
    try:
        res = (
            supabase.table("falk_compass_journal")
            .select("id, conversation_id, chapter_number, chapter_title, summary, created_at, updated_at")
            .eq("user_id", auth_uid)
            .order("chapter_number", desc=False)
            .execute()
        )
        return jsonify({"status": "success", "chapters": res.data or []}), 200
    except Exception as e:
        logging.error(f"Fel vid hämtning av falk_compass_journal: {e}")
        return jsonify({"status": "error", "message": "Kunde inte hämta journalen."}), 500


@app.route("/api/memories", methods=["GET", "OPTIONS"])
def get_user_memories():
    if request.method == "OPTIONS":
        return "", 200
    auth_uid, _, _ = _resolve_auth_user()
    if not auth_uid:
        return jsonify({"status": "error", "message": "Autentisering krävs."}), 401
    if not supabase:
        return jsonify({"status": "error", "message": "Databas ej tillgänglig."}), 503
    try:
        res = (
            supabase.table("falk_memory")
            .select("id, category, content, created_at")
            .eq("user_id", auth_uid)
            .order("created_at", desc=True)
            .limit(50)
            .execute()
        )
        return jsonify({"status": "success", "memories": res.data or []}), 200
    except Exception as e:
        logging.error(f"Fel vid hämtning av falk_memory: {e}")
        return jsonify({"status": "error", "message": "Kunde inte hämta minnen."}), 500


@app.route("/api/memories/<memory_id>", methods=["DELETE", "OPTIONS"])
def delete_user_memory(memory_id):
    if request.method == "OPTIONS":
        return "", 200
    auth_uid, _, _ = _resolve_auth_user()
    if not auth_uid:
        return jsonify({"status": "error", "message": "Autentisering krävs."}), 401
    if not supabase:
        return jsonify({"status": "error", "message": "Databas ej tillgänglig."}), 503
    if not memory_id or len(memory_id) > 64:
        return jsonify({"status": "error", "message": "Ogiltigt minnes-ID."}), 400
    try:
        (
            supabase.table("falk_memory")
            .delete()
            .eq("id", memory_id)
            .eq("user_id", auth_uid)
            .execute()
        )
        return jsonify({"status": "success", "deleted_id": memory_id}), 200
    except Exception as e:
        logging.error(f"Fel vid radering av falk_memory {memory_id}: {e}")
        return jsonify({"status": "error", "message": "Kunde inte ta bort minnet."}), 500


# ---------------------------------------------------------------------------
# BIBLIOTEK (15 ÖVNINGSKORT) & PDF-EXPORT
# ---------------------------------------------------------------------------
@app.route("/api/sessions/templates", methods=["GET", "OPTIONS"])
def get_compass_session_templates():
    if request.method == "OPTIONS":
        return "", 200
    items = [
        {"key": k, "title": v["title"], "goal": v["goal"], "durations": [15, 30, 60]}
        for k, v in COMPASS_SESSIONS.items()
    ]
    return jsonify({"status": "success", "sessions": items}), 200


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
    segment = (request.args.get("segment") or "b2c").strip().lower()
    if segment in ("b2b", "all"):
        cards = get_library_cards(category=category, segment=segment)
    else:
        segment = "b2c"
        cards = get_library_cards(category) if category else FALK_15_EXERCISE_CARDS
    return jsonify({"status": "success", "segment": segment, "count": len(cards), "cards": cards}), 200


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

    req_data = request.get_json(silent=True) or {}
    segment = (request.args.get("segment") or req_data.get("segment") or "b2c").strip().lower()

    if segment == "b2b":
        valid_b2b_keys = {c["key"] for c in B2B_COMPASSES}

        def _sanitize_b2b_scores(raw_scores):
            if not isinstance(raw_scores, dict):
                return {}
            cleaned = {}
            for k, v in raw_scores.items():
                key = str(k).strip()
                if key not in valid_b2b_keys:
                    continue
                try:
                    num = float(v)
                    if num == num:
                        cleaned[key] = round(max(1.0, min(10.0, num)), 2)
                except (ValueError, TypeError):
                    continue
            return cleaned

        if request.method == "GET":
            b2b_compasses = get_b2b_compasses()
            if not auth_uid or not supabase:
                return jsonify({
                    "status": "success",
                    "segment": "b2b",
                    "b2b_compasses": b2b_compasses,
                    "calibrations": [],
                }), 200
            b2b_rows = []
            try:
                r = (
                    supabase.table("compass_scores")
                    .select("*")
                    .eq("user_id", auth_uid)
                    .order("created_at", desc=True)
                    .limit(30)
                    .execute()
                )
                for item in (r.data or []):
                    clean_b2b = _sanitize_b2b_scores(item.get("scores"))
                    if clean_b2b:
                        b2b_rows.append({**item, "scores": clean_b2b})
            except Exception as e:
                logging.warning(f"Kunde inte läsa B2B-kompasser för {auth_uid}: {e}")
            return jsonify({
                "status": "success",
                "segment": "b2b",
                "b2b_compasses": b2b_compasses,
                "calibrations": b2b_rows[:30],
            }), 200

        b2b_scores = _sanitize_b2b_scores(req_data.get("scores", {}))
        if not b2b_scores:
            return jsonify({"status": "error", "message": "Inga giltiga B2B-kompassvärden angavs."}), 400
        if auth_uid and supabase:
            try:
                res = supabase.table("compass_scores").insert({
                    "user_id": auth_uid,
                    "scores": b2b_scores,
                }).execute()
                return jsonify({"status": "success", "segment": "b2b", "data": res.data}), 200
            except Exception as e:
                logging.error(f"Kunde inte spara B2B-kompasskalibrering: {e}")
                return jsonify({"status": "error", "message": str(e)}), 500
        return jsonify({
            "status": "success",
            "segment": "b2b",
            "message": "B2B-kalibrering mottagen lokalt.",
            "data": b2b_scores,
        }), 200

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

    data = req_data
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
        "compass_journal": [],
        "falk_memory": [],
        "memory_vectors": [],
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
        jrn = supabase.table("falk_compass_journal").select("*").eq("user_id", auth_uid).execute()
        fmem = supabase.table("falk_memory").select("*").eq("user_id", auth_uid).execute()

        export_payload["promo_redemptions"] = promos.data or []
        export_payload["organization_members"] = org_members.data or []
        export_payload["compass_journal"] = jrn.data or []
        export_payload["falk_memory"] = fmem.data or []
        try:
            mvecs = supabase.table("user_memory_vectors").select("id, session_id, memory_layer, content, metadata, created_at").eq("user_id", auth_uid).execute()
            export_payload["memory_vectors"] = mvecs.data or []
        except Exception:
            export_payload["memory_vectors"] = []
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
            "falk_compass_journal",
            "falk_memory",
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

        try:
            supabase.table("user_memory_vectors").delete().eq("user_id", auth_uid).execute()
        except Exception as vec_del_err:
            logging.warning(f"user_memory_vectors radering hoppades över: {vec_del_err}")

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

        caller_role = str(admin_mem.get("role") or "").strip()
        is_caller_org_admin = caller_role in ("org_admin", "admin")

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

                target_res = (
                    supabase.table("organization_members")
                    .select("id,user_id,role,department,status")
                    .eq("id", member_id)
                    .eq("org_id", org_id)
                    .limit(1)
                    .execute()
                )
                target_mem = (target_res.data or [None])[0]
                if not target_mem:
                    return jsonify({"status": "error", "message": "Medlemmen hittades inte i organisationen."}), 404

                target_role = str(target_mem.get("role") or "").strip()
                if "role" in updates and (
                    target_mem.get("id") == admin_mem.get("id")
                    or target_mem.get("user_id") == auth_uid
                ):
                    return jsonify({
                        "status": "error",
                        "code": "CANNOT_CHANGE_OWN_ROLE",
                        "message": "Du kan inte ändra din egen organisationsroll.",
                    }), 403

                if target_role in ("org_admin", "admin") and not is_caller_org_admin:
                    return jsonify({
                        "status": "error",
                        "code": "HIERARCHY_VIOLATION",
                        "message": "Endast org_admin kan ändra en organisationsadministratör.",
                    }), 403

                if updates.get("role") in ("org_admin", "admin") and not is_caller_org_admin:
                    return jsonify({
                        "status": "error",
                        "code": "HIERARCHY_VIOLATION",
                        "message": "Endast org_admin kan tilldela rollen org_admin.",
                    }), 403

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
            if role in ("org_admin", "admin") and not is_caller_org_admin:
                return jsonify({
                    "status": "error",
                    "code": "HIERARCHY_VIOLATION",
                    "message": "Endast org_admin kan skapa inbjudan med rollen org_admin.",
                }), 403

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

        lookup_query = (
            supabase.table("organization_members")
            .select("id,user_id,role,status")
            .eq("org_id", org_id)
        )
        if target_member_id:
            lookup_query = lookup_query.eq("id", target_member_id)
        else:
            lookup_query = lookup_query.eq("user_id", target_user_id)

        lookup_res = lookup_query.limit(1).execute()
        target_mem = (lookup_res.data or [None])[0]
        if not target_mem:
            return jsonify({"status": "error", "message": "Medlemmen hittades inte i organisationen."}), 404

        if target_mem.get("user_id") == auth_uid or target_mem.get("id") == admin_mem.get("id"):
            return jsonify({
                "status": "error",
                "code": "CANNOT_REVOKE_SELF",
                "message": "Du kan inte återkalla din egen administratörsbehörighet.",
            }), 400

        if str(target_mem.get("role") or "").strip() in ("org_admin", "admin") and not is_caller_org_admin:
            return jsonify({
                "status": "error",
                "code": "HIERARCHY_VIOLATION",
                "message": "Endast org_admin kan återkalla en organisationsadministratör.",
            }), 403

        now_iso = datetime.now(timezone.utc).isoformat()
        rev_res = (
            supabase.table("organization_members")
            .update({"status": "revoked", "revoked_at": now_iso})
            .eq("org_id", org_id)
            .eq("id", target_mem["id"])
            .execute()
        )
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



# === FALK_STEP4_PUSH_AND_PROFILE_PATCH ===
try:
    import fcntl as _falk_fcntl
except Exception:
    _falk_fcntl = None

try:
    from pywebpush import webpush as _pywebpush_send, WebPushException as _WebPushException
except Exception:
    _pywebpush_send = None
    _WebPushException = Exception


def _resolve_user_display_name(
    uid: Optional[str],
    is_guest: bool = True,
    fallback_name: Optional[str] = None,
) -> Optional[str]:
    if is_guest:
        return None

    clean_fallback = None
    if isinstance(fallback_name, str):
        stripped = " ".join(fallback_name.strip().split())
        if stripped:
            clean_fallback = stripped[:80]

    if not uid or not supabase:
        return clean_fallback

    try:
        res = (
            supabase.table("user_profiles")
            .select("display_name")
            .eq("user_id", uid)
            .limit(1)
            .execute()
        )
        rows = res.data or []
        if not rows:
            res = (
                supabase.table("user_profiles")
                .select("display_name")
                .eq("id", uid)
                .limit(1)
                .execute()
            )
            rows = res.data or []
        if rows:
            name = (rows[0].get("display_name") or "").strip()
            if name:
                return name[:80]
    except Exception as e:
        logging.warning(f"Kunde inte hämta display_name från user_profiles: {e}")

    try:
        auth_res = supabase.auth.admin.get_user_by_id(uid)
        u_obj = getattr(auth_res, "user", None)
        meta = getattr(u_obj, "user_metadata", None) or {}
        if isinstance(meta, dict):
            for k in ("display_name", "full_name", "name", "first_name"):
                val = str(meta.get(k) or "").strip()
                if val:
                    return val[:80]
    except Exception as e:
        logging.warning(f"Kunde inte hämta display_name från auth metadata: {e}")
    return clean_fallback


def _maybe_create_chat_reminder(user_message: str, auth_uid: Optional[str], is_guest: bool = True) -> Optional[Dict[str, Any]]:
    """
    Detekterar när en inloggad Premium-användare ber FALK sätta en påminnelse i chatten,
    beräknar svensk tid (Europe/Stockholm -> UTC) och sparar i user_reminders.
    Triggas aldrig för gäster.
    """
    if is_guest or not auth_uid or not supabase or not user_message:
        return None

    text = user_message.strip()
    if len(text) < 8 or len(text) > 320:
        return None

    lowered = text.lower()
    if any(skip in lowered for skip in ("vad vi pratade om", "vad jag sa", "påminner det här om")):
        return None

    has_trigger = bool(re.search(
        r"\b(påminn\s+mig|sätt\s+(?:en\s+)?påminnelse|skapa\s+(?:en\s+)?påminnelse|lägg\s+in\s+(?:en\s+)?påminnelse)\b",
        lowered,
    ))
    if not has_trigger:
        return None
    if text.endswith("?") and not re.search(r"^(kan|skulle|vill)\s+du\s+påminna\s+mig", lowered):
        return None

    try:
        from zoneinfo import ZoneInfo
        stockholm_tz = ZoneInfo("Europe/Stockholm")
    except Exception:
        stockholm_tz = timezone(timedelta(hours=1))

    now_local = datetime.now(stockholm_tz)
    due_local: Optional[datetime] = None

    rel_match = re.search(
        r"\bom\s+(\d{1,3})\s*(sekunder|sekund|sek|minuter|minut|min|timmar|timme|tim|h)\b",
        lowered,
    )
    clock_match = re.search(
        r"\b(?:kl\.?|klockan)\s*(\d{1,2})(?:[:.](\d{2}))?\b",
        lowered,
    )
    is_tomorrow = bool(re.search(r"\b(imorgon|i\s+morgon)\b", lowered))

    if rel_match:
        amount = max(1, int(rel_match.group(1)))
        unit = rel_match.group(2)
        if unit.startswith("sek"):
            due_local = now_local + timedelta(seconds=amount)
        elif unit.startswith("min"):
            due_local = now_local + timedelta(minutes=amount)
        else:
            due_local = now_local + timedelta(hours=amount)
    elif clock_match:
        hour = int(clock_match.group(1))
        minute = int(clock_match.group(2) or 0)
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            candidate = now_local.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if is_tomorrow:
                candidate = candidate + timedelta(days=1)
            elif candidate <= now_local - timedelta(seconds=30):
                candidate = candidate + timedelta(days=1)
            due_local = candidate

    if due_local is None:
        due_local = (now_local + timedelta(hours=1)).replace(second=0, microsecond=0)

    cleaned = re.sub(
        r"^(?:hej\s+falk[,!.\s]*|falk[,!.\s]*)?(?:kan\s+du\s+|skulle\s+du\s+kunna\s+|vill\s+du\s+)?(?:påminna|påminn)\s+mig\s*",
        "",
        text,
        flags=re.IGNORECASE,
    ).strip()
    cleaned = re.sub(
        r"^(?:sätt|skapa|lägg\s+in)\s+(?:en\s+)?påminnelse\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    ).strip()
    cleaned = re.sub(
        r"\b(?:imorgon|i\s+morgon|idag|i\s+dag)\b",
        "",
        cleaned,
        flags=re.IGNORECASE,
    ).strip()
    cleaned = re.sub(
        r"\bom\s+\d{1,3}\s*(?:sekunder|sekund|sek|minuter|minut|min|timmar|timme|tim|h)\b",
        "",
        cleaned,
        flags=re.IGNORECASE,
    ).strip()
    cleaned = re.sub(
        r"\b(?:kl\.?|klockan)\s*\d{1,2}(?:[:.]\d{2})?\b",
        "",
        cleaned,
        flags=re.IGNORECASE,
    ).strip()
    cleaned = re.sub(r"^(?:att|om|för\s+att)\s+", "", cleaned, flags=re.IGNORECASE).strip(" .!?,-")
    if not cleaned:
        cleaned = "Påminnelse från samtal med FALK"
    else:
        cleaned = cleaned[0].upper() + cleaned[1:]
    if len(cleaned) > 160:
        cleaned = cleaned[:157].rstrip() + "..."

    due_utc_iso = due_local.astimezone(timezone.utc).isoformat()
    local_label = due_local.strftime("%Y-%m-%d %H:%M")

    base_payload: Dict[str, Any] = {
        "user_id": auth_uid,
        "content": cleaned,
        "frequency": "once",
        "reminder_at": due_utc_iso,
        "remind_at": due_utc_iso,
    }
    saved_row: Dict[str, Any] = dict(base_payload)
    try:
        res = supabase.table("user_reminders").insert(base_payload).execute()
        if res.data:
            saved_row = dict(res.data[0])
    except Exception:
        try:
            alt_payload = {
                "user_id": auth_uid,
                "content": cleaned,
                "frequency": "once",
                "reminder_at": due_utc_iso,
            }
            res = supabase.table("user_reminders").insert(alt_payload).execute()
            if res.data:
                saved_row = dict(res.data[0])
        except Exception as e:
            logging.warning(f"Kunde inte spara chatt-påminnelse i user_reminders: {e}")
            return None

    saved_row.setdefault("content", cleaned)
    saved_row.setdefault("reminder_at", due_utc_iso)
    saved_row["local_time_label"] = local_label
    return saved_row


def _extract_goal_suggestion(user_message: str, is_guest: bool = True) -> Optional[Dict[str, str]]:
    """
    Identifierar om en inloggad användare i samtalet formulerar ett konkret mål
    eller åtagande så att gränssnittet kan erbjuda att spara det i Kompassen.
    Triggas aldrig för gäster.
    """
    if is_guest or not user_message:
        return None
    text = user_message.strip()
    if len(text) < 12 or len(text) > 260 or text.endswith("?"):
        return None

    lowered = text.lower()
    triggers = (
        "mitt mål är",
        "jag vill sätta som mål",
        "sätt ett mål",
        "spara som mål",
        "mitt nästa steg är att",
        "jag har bestämt mig för att",
        "jag ska börja",
        "jag vill börja",
        "jag vill uppnå",
    )
    if not any(t in lowered for t in triggers):
        return None

    area = "Personlig utveckling"
    area_keywords = (
        ("Hälsa och träning", ("träna", "sömn", "sova", "hälsa", "promenad", "springa", "vila", "återhämtning", "energi")),
        ("Jobb och karriär", ("jobb", "karriär", "chef", "arbete", "projekt", "företag", "studier")),
        ("Familj", ("familj", "barn", "förälder", "mamma", "pappa", "syskon")),
        ("Intim relation", ("partner", "relation", "kärlek", "sambo", "fru", "man", "dejta")),
        ("Finans", ("ekonomi", "spara", "pengar", "budget", "lön", "investera")),
        ("Spiritualitet", ("meditation", "mening", "syfte", "inre ro", "närvaro", "tacksamhet")),
    )
    for candidate_area, kws in area_keywords:
        if any(k in lowered for k in kws):
            area = candidate_area
            break

    cleaned_title = text.rstrip(".!").strip()
    if len(cleaned_title) > 110:
        cleaned_title = cleaned_title[:107].rstrip() + "..."
    return {"title": cleaned_title, "area": area}


def _get_push_auth_uid() -> Optional[str]:
    if not supabase:
        return None
    auth_header = (request.headers.get("Authorization") or "").strip()
    if not auth_header.lower().startswith("bearer "):
        return None
    token = auth_header.split(" ", 1)[1].strip()
    if not token:
        return None
    try:
        user_resp = supabase.auth.get_user(token)
        user_obj = getattr(user_resp, "user", None)
        if user_obj and getattr(user_obj, "id", None):
            return str(user_obj.id)
    except Exception as e:
        logging.warning(f"Push auth-verifiering misslyckades: {e}")
    return None


def _send_web_push_to_user(user_id: str, title: str, body: str, url: str = "/", tag: str = "falk-reminder") -> int:
    if not _pywebpush_send or not supabase or not user_id:
        return 0
    vapid_private = (os.environ.get("VAPID_PRIVATE_KEY") or "").strip()
    vapid_subject = (os.environ.get("VAPID_SUBJECT") or "mailto:hej@wayjs.se").strip()
    if not vapid_private:
        return 0

    try:
        subs_res = (
            supabase.table("push_subscriptions")
            .select("id, endpoint, p256dh, auth")
            .eq("user_id", user_id)
            .execute()
        )
        subs = subs_res.data or []
    except Exception as e:
        logging.warning(f"Kunde inte hämta push_subscriptions för {user_id}: {e}")
        return 0

    sent_count = 0
    payload = json.dumps({
        "title": title,
        "body": body,
        "url": url,
        "tag": tag,
    }, ensure_ascii=False)

    for sub in subs:
        endpoint = sub.get("endpoint")
        p256dh = sub.get("p256dh")
        auth_key = sub.get("auth")
        if not endpoint or not p256dh or not auth_key:
            continue
        try:
            _pywebpush_send(
                subscription_info={
                    "endpoint": endpoint,
                    "keys": {"p256dh": p256dh, "auth": auth_key},
                },
                data=payload,
                vapid_private_key=vapid_private,
                vapid_claims={"sub": vapid_subject},
                ttl=3600,
            )
            sent_count += 1
        except _WebPushException as ex:
            status_code = getattr(getattr(ex, "response", None), "status_code", None)
            if status_code in (404, 410) and sub.get("id"):
                try:
                    supabase.table("push_subscriptions").delete().eq("id", sub["id"]).execute()
                except Exception:
                    pass
            else:
                logging.warning(f"WebPushException för {user_id}: {ex}")
        except Exception as e:
            logging.warning(f"Oväntat fel vid Web Push till {user_id}: {e}")
    return sent_count


@app.route("/api/push/vapid-public-key", methods=["GET"])
def get_vapid_public_key():
    pub = (os.environ.get("VAPID_PUBLIC_KEY") or "").strip()
    return jsonify({"status": "success", "publicKey": pub}), 200


@app.route("/api/push/subscribe", methods=["POST"])
def subscribe_web_push():
    uid = _get_push_auth_uid()
    if not uid:
        return jsonify({"status": "error", "message": "Inloggning krävs för push-notiser."}), 401

    data = request.get_json(silent=True) or {}
    sub = data.get("subscription") or data
    endpoint = (sub.get("endpoint") or "").strip()
    keys = sub.get("keys") or {}
    p256dh = (keys.get("p256dh") or "").strip()
    auth_key = (keys.get("auth") or "").strip()
    user_agent = (request.headers.get("User-Agent") or "")[:250]

    if not endpoint or not p256dh or not auth_key:
        return jsonify({"status": "error", "message": "Ogiltig push-prenumeration."}), 400

    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        existing = (
            supabase.table("push_subscriptions")
            .select("id")
            .eq("user_id", uid)
            .eq("endpoint", endpoint)
            .limit(1)
            .execute()
        )
        if existing.data:
            supabase.table("push_subscriptions").update({
                "p256dh": p256dh,
                "auth": auth_key,
                "user_agent": user_agent,
                "updated_at": now_iso,
            }).eq("id", existing.data[0]["id"]).execute()
        else:
            supabase.table("push_subscriptions").insert({
                "user_id": uid,
                "endpoint": endpoint,
                "p256dh": p256dh,
                "auth": auth_key,
                "user_agent": user_agent,
                "updated_at": now_iso,
            }).execute()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logging.error(f"Fel vid sparande av push-prenumeration: {e}")
        return jsonify({"status": "error", "message": "Kunde inte aktivera push-notiser."}), 500


@app.route("/api/push/unsubscribe", methods=["POST"])
def unsubscribe_web_push():
    uid = _get_push_auth_uid()
    if not uid:
        return jsonify({"status": "error", "message": "Inloggning krävs."}), 401

    data = request.get_json(silent=True) or {}
    endpoint = (data.get("endpoint") or "").strip()
    try:
        query = supabase.table("push_subscriptions").delete().eq("user_id", uid)
        if endpoint:
            query = query.eq("endpoint", endpoint)
        query.execute()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logging.error(f"Fel vid avregistrering av push-prenumeration: {e}")
        return jsonify({"status": "error", "message": "Kunde inte stänga av push-notiser."}), 500


_sent_push_reminder_keys = set()


def _parse_utc_timestamp(raw_val: Any) -> Optional[datetime]:
    if not raw_val:
        return None
    s = str(raw_val).strip()
    if not s:
        return None
    try:
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def _reminder_push_worker_loop() -> None:
    lock_fd = None
    if _falk_fcntl is not None:
        try:
            lock_fd = open("/tmp/falk_push_worker.lock", "w")
            _falk_fcntl.flock(lock_fd.fileno(), _falk_fcntl.LOCK_EX | _falk_fcntl.LOCK_NB)
        except Exception:
            # En annan Gunicorn-worker håller redan låset
            return

    while True:
        try:
            if supabase and _pywebpush_send and (os.environ.get("VAPID_PRIVATE_KEY") or "").strip():
                now_utc = datetime.now(timezone.utc)
                res = supabase.table("user_reminders").select("*").limit(200).execute()
                for row in (res.data or []):
                    if row.get("is_completed") is True:
                        continue
                    status_val = str(row.get("status") or "active").lower()
                    if status_val in ("completed", "done", "dismissed", "cancelled"):
                        continue

                    raw_due = (
                        row.get("reminder_at")
                        or row.get("remind_at")
                        or row.get("due_at")
                        or row.get("next_trigger_at")
                        or row.get("scheduled_at")
                    )
                    due_dt = _parse_utc_timestamp(raw_due)
                    if not due_dt:
                        continue

                    # Skicka endast för påminnelser som förfallit inom senaste 15 min (undviker historik-spam)
                    delta_sec = (now_utc - due_dt).total_seconds()
                    if delta_sec < 0 or delta_sec > 900:
                        continue

                    rem_id = str(row.get("id") or "")
                    uid = str(row.get("user_id") or "")
                    dedup_key = f"{rem_id}:{due_dt.isoformat()}"
                    if not rem_id or not uid or dedup_key in _sent_push_reminder_keys:
                        continue

                    content_txt = (row.get("content") or "").strip()
                    title_txt = (row.get("title") or row.get("text") or content_txt or "Påminnelse från FALK").strip()
                    body_txt = (row.get("context") or row.get("description") or content_txt or "Dags att stanna upp och reflektera.").strip()
                    _sent_push_reminder_keys.add(dedup_key)
                    if len(_sent_push_reminder_keys) > 2000:
                        _sent_push_reminder_keys.clear()

                    _send_web_push_to_user(
                        user_id=uid,
                        title=f"FALK · {title_txt[:60]}",
                        body=body_txt[:160],
                        url="/",
                        tag=f"falk-rem-{rem_id}",
                    )
        except Exception as e:
            logging.warning(f"Reminder push worker-varv felade: {e}")
        time.sleep(45)


def _start_reminder_push_worker() -> None:
    if os.environ.get("FALK_DISABLE_PUSH_WORKER") == "1":
        return
    t = threading.Thread(target=_reminder_push_worker_loop, daemon=True, name="falk-push-worker")
    t.start()


_start_reminder_push_worker()
# === END FALK_STEP4_PUSH_AND_PROFILE_PATCH ===

# === START FALK_MODERATOR_ROOMS_AND_META ===
import fcntl
import json as _mod_json
import re as _mod_re
import secrets as _mod_secrets
from pathlib import Path as _ModPath

_MOD_ROOM_DIR = _ModPath("/tmp/falk_mod_rooms")
_MOD_ROOM_TTL_SEC = 4 * 3600  # 4 timmar max livslängd i flyktigt minne/tmp
_MOD_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def _default_moderator_meta() -> dict:
    return {
        "phase": "TRYGGHET",
        "next_speaker": "",
        "overlap_event": None,
        "perspective_triangle": {
            "part_1_need": "",
            "part_2_need": "",
            "shared_ground": "",
            "core_question": "",
        },
        "compass_summary": None,
    }


def _parse_moderator_reply_meta(reply_text: str):
    text = str(reply_text or "")
    meta = _default_moderator_meta()
    pattern = _mod_re.compile(r"<<<MODERATOR_META>>>\s*(\{.*?\})\s*<<<END_MODERATOR_META>>>", _mod_re.DOTALL)
    match = pattern.search(text)
    if match:
        raw_json = match.group(1).strip()
        clean_text = (text[:match.start()] + text[match.end():]).strip()
        try:
            parsed = _mod_json.loads(raw_json)
            if isinstance(parsed, dict):
                phase = str(parsed.get("phase") or "TRYGGHET").strip().upper()
                if phase in {"TRYGGHET", "FÖRSTÅELSE", "PERSPEKTIV", "KLARHET", "NÄSTA_STEG"}:
                    meta["phase"] = phase
                next_sp = " ".join(str(parsed.get("next_speaker") or "").split()).strip()[:60]
                if next_sp:
                    meta["next_speaker"] = next_sp
                tri = parsed.get("perspective_triangle")
                if isinstance(tri, dict):
                    meta["perspective_triangle"] = {
                        "part_1_need": str(tri.get("part_1_need") or "").strip()[:140],
                        "part_2_need": str(tri.get("part_2_need") or "").strip()[:140],
                        "shared_ground": str(tri.get("shared_ground") or "").strip()[:160],
                        "core_question": str(tri.get("core_question") or "").strip()[:160],
                    }
                cs = parsed.get("compass_summary")
                if isinstance(cs, dict):
                    steps = cs.get("next_steps")
                    meta["compass_summary"] = {
                        "understood": str(cs.get("understood") or "").strip()[:400],
                        "most_important": str(cs.get("most_important") or "").strip()[:400],
                        "missing_perspective": str(cs.get("missing_perspective") or "").strip()[:400],
                        "most_true_now": str(cs.get("most_true_now") or "").strip()[:400],
                        "next_steps": [str(s).strip()[:200] for s in steps[:4]] if isinstance(steps, list) else [],
                    }
        except Exception as parse_err:
            logging.warning(f"Kunde inte parsa MODERATOR_META JSON: {parse_err}")
        return clean_text, meta
    # Fallback om markörer delvis läckt
    clean_text = _mod_re.sub(r"<<<(?:END_)?MODERATOR_META>>>.*", "", text, flags=_mod_re.DOTALL).strip()
    return clean_text, meta


def _sanitize_room_code(code: str) -> str:
    cleaned = "".join(ch for ch in str(code or "").upper().strip() if ch in _MOD_CODE_ALPHABET)
    return cleaned[:8]


def _ensure_mod_room_dir() -> None:
    _MOD_ROOM_DIR.mkdir(parents=True, exist_ok=True)
    now = time.time()
    try:
        for p in _MOD_ROOM_DIR.glob("*.json"):
            try:
                if now - p.stat().st_mtime > _MOD_ROOM_TTL_SEC:
                    p.unlink(missing_ok=True)
            except Exception:
                pass
    except Exception:
        pass


def _mod_room_file(code: str) -> _ModPath:
    return _MOD_ROOM_DIR / f"{code}.json"


def _read_mod_room(code: str):
    _ensure_mod_room_dir()
    fp = _mod_room_file(code)
    if not fp.exists():
        return None
    try:
        with fp.open("r", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            data = _mod_json.load(f)
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        if time.time() - float(data.get("created_at") or 0) > _MOD_ROOM_TTL_SEC:
            fp.unlink(missing_ok=True)
            return None
        return data
    except Exception:
        return None


def _write_mod_room(code: str, room_data: dict) -> None:
    _ensure_mod_room_dir()
    fp = _mod_room_file(code)
    with fp.open("w", encoding="utf-8") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        _mod_json.dump(room_data, f, ensure_ascii=False)
        f.flush()
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def _delete_mod_room(code: str) -> None:
    try:
        _mod_room_file(code).unlink(missing_ok=True)
    except Exception:
        pass


def _verify_premium_host_from_request():
    auth_header = request.headers.get("Authorization") or ""
    if not auth_header.startswith("Bearer ") or not supabase:
        return None
    token = auth_header.split(" ", 1)[1].strip()
    if not token:
        return None
    try:
        user_resp = supabase.auth.get_user(token)
        user_obj = getattr(user_resp, "user", None)
        uid = getattr(user_obj, "id", None) if user_obj else None
        if not uid:
            return None
        prof = (
            supabase.table("user_profiles")
            .select("is_premium")
            .eq("user_id", uid)
            .limit(1)
            .execute()
        )
        rows = prof.data or []
        if rows and bool(rows[0].get("is_premium")):
            return str(uid)
    except Exception as e:
        logging.warning(f"Moderator host auth check misslyckades: {e}")
    return None


def _resolve_room_next_role(room: dict, current_role: str = "") -> str:
    if current_role == "part_1":
        return "part_2"
    if current_role == "part_2":
        return "part_1"
    counts = room.get("speaker_counts") or {"part_1": 0, "part_2": 0}
    c1 = int(counts.get("part_1") or 0)
    c2 = int(counts.get("part_2") or 0)
    return "part_2" if c2 < c1 else "part_1"


def _draw_room_overlap_winner(room: dict) -> dict:
    p1_name = room.get("part_1_name", "Part 1")
    p2_name = room.get("part_2_name", "Part 2")
    pair = [("part_1", p1_name), ("part_2", p2_name)]
    winner, deferred = _mod_secrets.SystemRandom().sample(pair, 2)
    return {
        "id": _mod_secrets.token_hex(4),
        "selected_role": winner[0],
        "selected_speaker": winner[1],
        "deferred_role": deferred[0],
        "deferred_speaker": deferred[1],
        "ts": int(time.time() * 1000),
    }


def _serialize_mod_room_public(room: dict, viewer_role: str = "") -> dict:
    # Exponerar ALDRIG råa enskilda incheckningstexter för motparten
    checkins = room.get("private_checkins") or {}
    p1_name = room.get("part_1_name", "Part 1")
    p2_name = room.get("part_2_name", "Part 2")
    active_role = room.get("active_turn_role") or "part_1"
    if active_role not in {"part_1", "part_2"}:
        active_role = "part_1"
    active_speaker = p2_name if active_role == "part_2" else p1_name
    return {
        "room_code": room.get("room_code"),
        "context": room.get("context", "private"),
        "part_1_name": p1_name,
        "part_2_name": p2_name,
        "guest_joined": bool(room.get("guest_joined")),
        "active_turn_role": active_role,
        "active_turn_speaker": active_speaker,
        "last_speaker_role": room.get("last_speaker_role") or "",
        "overlap_event": room.get("overlap_event"),
        "checkin_status": {
            "part_1_submitted": bool(checkins.get("part_1_done")),
            "part_2_submitted": bool(checkins.get("part_2_done")),
            "synthesized": bool(checkins.get("synthesized")),
        },
        "messages": room.get("messages") or [],
        "moderator_meta": room.get("moderator_meta") or _default_moderator_meta(),
        "speaker_counts": room.get("speaker_counts") or {"part_1": 0, "part_2": 0},
        "expires_at": int((room.get("created_at") or time.time()) + _MOD_ROOM_TTL_SEC),
        "viewer_role": viewer_role,
    }


def _run_moderator_room_falk_turn(
    room: dict,
    is_checkin_synthesis: bool = False,
    final_compass: bool = False,
    current_role: str = "",
    overlap_event: dict = None,
):
    convo = []
    for m in (room.get("messages") or [])[-24:]:
        role = m.get("role")
        content = str(m.get("content") or "").strip()
        if not content:
            continue
        if role == "falk":
            convo.append({"role": "assistant", "content": content})
        else:
            speaker = str(m.get("speaker_name") or ("Part 1" if role == "part_1" else "Part 2")).strip()
            convo.append({"role": "user", "content": f"[{speaker}]: {content}"})

    p1_name = room.get("part_1_name", "Part 1")
    p2_name = room.get("part_2_name", "Part 2")
    current_speaker_name = (
        (p1_name if current_role == "part_1" else p2_name)
        if current_role in {"part_1", "part_2"}
        else ""
    )

    if isinstance(overlap_event, dict) and overlap_event.get("selected_speaker"):
        next_role = overlap_event.get("selected_role") or _resolve_room_next_role(room, current_role)
        next_speaker_name = overlap_event["selected_speaker"]
    else:
        next_role = _resolve_room_next_role(room, current_role)
        next_speaker_name = p2_name if next_role == "part_2" else p1_name

    default_prompt_msg = (
        f"Röstavbrott upptäckt mellan {p1_name} och {p2_name}. Lottat ord: {next_speaker_name}."
        if overlap_event
        else "Syntetisera parternas enskilda incheckning."
    )
    latest_user_msg = convo[-1]["content"] if convo and convo[-1]["role"] == "user" else default_prompt_msg
    sys_prompt = build_falk_system_prompt(
        user_message=latest_user_msg,
        current_stage="EXPLORATION",
        is_guest=False,
        focus_sliders={},
        user_context_memories=[],
        compass_summary=None,
        response_variant="default",
        b2b_context=None,
        session_mode={
            "track": "moderator",
            "context": room.get("context", "private"),
            "check_in_synthesis": is_checkin_synthesis,
            "participants": [p1_name, p2_name],
            "current_speaker": current_speaker_name,
            "next_speaker": next_speaker_name,
            "overlap_event": overlap_event,
        },
        final_compass=final_compass,
        is_new_session=(len(convo) <= 1),
        user_name=f"{p1_name} & {p2_name}",
    )
    raw = _call_llm(sys_prompt, convo or [{"role": "user", "content": latest_user_msg}])
    prev_falk = next((m["content"] for m in reversed(convo) if m["role"] == "assistant"), None)
    filtered = _apply_gate_filter(
        raw,
        latest_user_msg,
        "EXPLORATION",
        sys_prompt,
        is_guest=False,
        previous_assistant_response=prev_falk,
    )
    clean_reply, meta = _parse_moderator_reply_meta(filtered)

    if isinstance(overlap_event, dict) and overlap_event.get("selected_speaker"):
        resolved_role = overlap_event.get("selected_role") or next_role
        meta["next_speaker"] = overlap_event["selected_speaker"]
        meta["overlap_event"] = overlap_event
    else:
        parsed_next = str(meta.get("next_speaker") or "").strip().lower()
        if parsed_next == p2_name.strip().lower():
            resolved_role = "part_2"
            meta["next_speaker"] = p2_name
        elif parsed_next == p1_name.strip().lower():
            resolved_role = "part_1"
            meta["next_speaker"] = p1_name
        else:
            resolved_role = next_role
            meta["next_speaker"] = next_speaker_name

    room["active_turn_role"] = resolved_role
    room["messages"].append({
        "id": _mod_secrets.token_hex(6),
        "role": "falk",
        "speaker_name": "FALK",
        "content": clean_reply,
        "ts": int(time.time() * 1000),
    })
    room["moderator_meta"] = meta


@app.route("/api/moderator/room", methods=["POST"])
def create_moderator_room():
    host_uid = _verify_premium_host_from_request()
    if not host_uid:
        return jsonify({
            "status": "error",
            "code": "PREMIUM_REQUIRED",
            "message": "Endast inloggade FALK Premium-användare kan skapa delade moderatorrum.",
        }), 403

    payload = request.get_json(silent=True) or {}
    context = "b2b" if str(payload.get("context") or "").strip().lower() == "b2b" else "private"
    part_1_name = str(payload.get("part_1_name") or "Part 1").strip()[:40] or "Part 1"
    part_2_name = str(payload.get("part_2_name") or "Part 2").strip()[:40] or "Part 2"

    _ensure_mod_room_dir()
    room_code = ""
    for _ in range(12):
        candidate = "".join(_mod_secrets.choice(_MOD_CODE_ALPHABET) for _ in range(6))
        if not _mod_room_file(candidate).exists():
            room_code = candidate
            break
    if not room_code:
        return jsonify({"status": "error", "message": "Kunde inte generera rumskod."}), 500

    host_token = _mod_secrets.token_urlsafe(24)
    room_data = {
        "room_code": room_code,
        "created_at": time.time(),
        "context": context,
        "part_1_name": part_1_name,
        "part_2_name": part_2_name,
        "host_token": host_token,
        "guest_token": "",
        "guest_joined": False,
        "private_checkins": {
            "part_1_text": "",
            "part_2_text": "",
            "part_1_done": False,
            "part_2_done": False,
            "synthesized": False,
        },
        "active_turn_role": "part_1",
        "last_speaker_role": "",
        "overlap_event": None,
        "messages": [],
        "moderator_meta": _default_moderator_meta(),
        "speaker_counts": {"part_1": 0, "part_2": 0},
    }
    _write_mod_room(room_code, room_data)
    return jsonify({
        "status": "success",
        "participant_token": host_token,
        "role": "part_1",
        "room": _serialize_mod_room_public(room_data, viewer_role="part_1"),
    }), 201


@app.route("/api/moderator/room/<room_code>", methods=["GET"])
def get_moderator_room(room_code):
    code = _sanitize_room_code(room_code)
    room = _read_mod_room(code)
    if not room:
        return jsonify({"status": "error", "code": "ROOM_NOT_FOUND", "message": "Rummet hittades inte eller har löpt ut."}), 404

    token = str(request.headers.get("X-Moderator-Token") or request.args.get("token") or "").strip()
    viewer_role = ""
    if token and token == room.get("host_token"):
        viewer_role = "part_1"
    elif token and token == room.get("guest_token"):
        viewer_role = "part_2"

    return jsonify({
        "status": "success",
        "room": _serialize_mod_room_public(room, viewer_role=viewer_role),
    }), 200


@app.route("/api/moderator/room/<room_code>/join", methods=["POST"])
def join_moderator_room(room_code):
    code = _sanitize_room_code(room_code)
    room = _read_mod_room(code)
    if not room:
        return jsonify({"status": "error", "code": "ROOM_NOT_FOUND", "message": "Rummet hittades inte eller har löpt ut."}), 404

    payload = request.get_json(silent=True) or {}
    guest_name = str(payload.get("guest_name") or room.get("part_2_name") or "Part 2").strip()[:40] or "Part 2"
    existing_token = str(payload.get("participant_token") or "").strip()

    if existing_token and existing_token == room.get("guest_token"):
        room["part_2_name"] = guest_name
        _write_mod_room(code, room)
        return jsonify({
            "status": "success",
            "participant_token": existing_token,
            "role": "part_2",
            "room": _serialize_mod_room_public(room, viewer_role="part_2"),
        }), 200

    guest_token = _mod_secrets.token_urlsafe(24)
    room["guest_token"] = guest_token
    room["guest_joined"] = True
    room["part_2_name"] = guest_name
    _write_mod_room(code, room)

    return jsonify({
        "status": "success",
        "participant_token": guest_token,
        "role": "part_2",
        "room": _serialize_mod_room_public(room, viewer_role="part_2"),
    }), 200


@app.route("/api/moderator/room/<room_code>/checkin", methods=["POST"])
def submit_moderator_room_checkin(room_code):
    code = _sanitize_room_code(room_code)
    room = _read_mod_room(code)
    if not room:
        return jsonify({"status": "error", "code": "ROOM_NOT_FOUND", "message": "Rummet hittades inte eller har löpt ut."}), 404

    payload = request.get_json(silent=True) or {}
    token = str(payload.get("participant_token") or request.headers.get("X-Moderator-Token") or "").strip()
    private_text = str(payload.get("private_text") or "").strip()[:2000]
    force_synthesize = bool(payload.get("force_synthesize"))

    role = ""
    if token and token == room.get("host_token"):
        role = "part_1"
    elif token and token == room.get("guest_token"):
        role = "part_2"
    else:
        return jsonify({"status": "error", "code": "UNAUTHORIZED_PARTICIPANT", "message": "Ogiltig deltagarnyckel."}), 403

    checkins = room.setdefault("private_checkins", {})
    if private_text:
        checkins[f"{role}_text"] = private_text
        checkins[f"{role}_done"] = True

    both_ready = bool(checkins.get("part_1_done")) and bool(checkins.get("part_2_done"))
    if (both_ready or (force_synthesize and role == "part_1")) and not checkins.get("synthesized"):
        p1_raw = str(checkins.get("part_1_text") or "(Ej inskickad)").strip()
        p2_raw = str(checkins.get("part_2_text") or "(Ej inskickad)").strip()
        synth_instruction = (
            f"ENSKILD FÖRBEREDELSE (KONFIDENTIELLT UNDERLAG – ÅTERGE EJ ORDAGRANT):\n"
            f"- {room.get('part_1_name', 'Part 1')} delade enskilt: {p1_raw}\n"
            f"- {room.get('part_2_name', 'Part 2')} delade enskilt: {p2_raw}\n\n"
            "Översätt nu bådas utsagor till underliggande mänskliga behov och gemensam riktning utan att citera eller avslöja anklagelser, och öppna det gemensamma samtalet."
        )
        # Rådata raderas omedelbart efter syntes
        checkins["part_1_text"] = ""
        checkins["part_2_text"] = ""
        checkins["synthesized"] = True

        # Temporär syntes-prompt som inte sparas som synligt råmeddelande
        temp_room = dict(room)
        temp_room["messages"] = list(room.get("messages") or []) + [{
            "role": "part_1",
            "speaker_name": "System (Enskild incheckning)",
            "content": synth_instruction,
        }]
        _run_moderator_room_falk_turn(temp_room, is_checkin_synthesis=True, final_compass=False)
        room["messages"] = [m for m in temp_room["messages"] if m.get("speaker_name") != "System (Enskild incheckning)"]
        room["moderator_meta"] = temp_room.get("moderator_meta") or room["moderator_meta"]

    _write_mod_room(code, room)
    return jsonify({
        "status": "success",
        "room": _serialize_mod_room_public(room, viewer_role=role),
    }), 200


@app.route("/api/moderator/room/<room_code>/overlap", methods=["POST"])
def resolve_moderator_room_overlap(room_code):
    code = _sanitize_room_code(room_code)
    room = _read_mod_room(code)
    if not room:
        return jsonify({"status": "error", "code": "ROOM_NOT_FOUND", "message": "Rummet hittades inte eller har löpt ut."}), 404

    payload = request.get_json(silent=True) or {}
    token = str(payload.get("participant_token") or request.headers.get("X-Moderator-Token") or "").strip()
    announce_falk = payload.get("announce_falk", True)

    role = ""
    if token and token == room.get("host_token"):
        role = "part_1"
    elif token and token == room.get("guest_token"):
        role = "part_2"
    else:
        return jsonify({"status": "error", "code": "UNAUTHORIZED_PARTICIPANT", "message": "Ogiltig deltagarnyckel."}), 403

    now_ms = int(time.time() * 1000)
    existing_ov = room.get("overlap_event")
    if isinstance(existing_ov, dict) and (now_ms - int(existing_ov.get("ts") or 0)) < 3500:
        return jsonify({
            "status": "success",
            "overlap_event": existing_ov,
            "room": _serialize_mod_room_public(room, viewer_role=role),
        }), 200

    overlap_event = _draw_room_overlap_winner(room)
    room["overlap_event"] = overlap_event
    room["active_turn_role"] = overlap_event["selected_role"]

    if announce_falk:
        _run_moderator_room_falk_turn(
            room,
            is_checkin_synthesis=False,
            final_compass=False,
            current_role="",
            overlap_event=overlap_event,
        )
    else:
        meta = room.get("moderator_meta") or _default_moderator_meta()
        meta["next_speaker"] = overlap_event["selected_speaker"]
        meta["overlap_event"] = overlap_event
        room["moderator_meta"] = meta

    _write_mod_room(code, room)
    return jsonify({
        "status": "success",
        "overlap_event": overlap_event,
        "room": _serialize_mod_room_public(room, viewer_role=role),
    }), 200


@app.route("/api/moderator/room/<room_code>/message", methods=["POST"])
def post_moderator_room_message(room_code):
    code = _sanitize_room_code(room_code)
    room = _read_mod_room(code)
    if not room:
        return jsonify({"status": "error", "code": "ROOM_NOT_FOUND", "message": "Rummet hittades inte eller har löpt ut."}), 404

    payload = request.get_json(silent=True) or {}
    token = str(payload.get("participant_token") or request.headers.get("X-Moderator-Token") or "").strip()
    content = str(payload.get("content") or "").strip()[:3000]
    request_falk = payload.get("request_falk", True)
    final_compass = bool(payload.get("final_compass"))
    overlap_detected = bool(payload.get("overlap_detected"))

    role = ""
    if token and token == room.get("host_token"):
        role = "part_1"
    elif token and token == room.get("guest_token"):
        role = "part_2"
    else:
        return jsonify({"status": "error", "code": "UNAUTHORIZED_PARTICIPANT", "message": "Ogiltig deltagarnyckel."}), 403

    now_ms = int(time.time() * 1000)
    msgs = room.get("messages") or []
    prev_msg = msgs[-1] if msgs else None
    rapid_collision = (
        isinstance(prev_msg, dict)
        and prev_msg.get("role") in {"part_1", "part_2"}
        and prev_msg.get("role") != role
        and (now_ms - int(prev_msg.get("ts") or 0)) <= 4500
    )

    if content:
        speaker_name = room.get("part_1_name", "Part 1") if role == "part_1" else room.get("part_2_name", "Part 2")
        room["messages"].append({
            "id": _mod_secrets.token_hex(6),
            "role": role,
            "speaker_name": speaker_name,
            "content": content,
            "ts": now_ms,
        })
        counts = room.setdefault("speaker_counts", {"part_1": 0, "part_2": 0})
        counts[role] = int(counts.get(role) or 0) + 1
        room["last_speaker_role"] = role

    active_overlap = None
    if overlap_detected or rapid_collision:
        existing_ov = room.get("overlap_event")
        if isinstance(existing_ov, dict) and (now_ms - int(existing_ov.get("ts") or 0)) < 3500:
            active_overlap = existing_ov
        else:
            active_overlap = _draw_room_overlap_winner(room)
        room["overlap_event"] = active_overlap
        room["active_turn_role"] = active_overlap["selected_role"]
    elif role in {"part_1", "part_2"}:
        room["overlap_event"] = None
        room["active_turn_role"] = _resolve_room_next_role(room, role)

    if request_falk or final_compass or active_overlap is not None:
        _run_moderator_room_falk_turn(
            room,
            is_checkin_synthesis=False,
            final_compass=final_compass,
            current_role=role,
            overlap_event=active_overlap,
        )

    _write_mod_room(code, room)
    return jsonify({
        "status": "success",
        "room": _serialize_mod_room_public(room, viewer_role=role),
    }), 200


@app.route("/api/moderator/room/<room_code>", methods=["DELETE"])
def delete_moderator_room(room_code):
    code = _sanitize_room_code(room_code)
    room = _read_mod_room(code)
    if not room:
        return jsonify({"status": "success", "deleted": True}), 200

    token = str(request.headers.get("X-Moderator-Token") or request.args.get("token") or "").strip()
    if token not in {room.get("host_token"), room.get("guest_token")}:
        return jsonify({"status": "error", "message": "Behörighet saknas."}), 403

    _delete_mod_room(code)
    return jsonify({"status": "success", "deleted": True}), 200
# === END FALK_MODERATOR_ROOMS_AND_META ===


# === FALK PREMIUM TTS (OPENAI AUDIO SPEECH) ===
ALLOWED_TTS_VOICES = {
    "onyx",
    "sage",
    "ash",
    "nova",
    "echo",
    "shimmer",
    "fable",
    "alloy",
    "coral",
}


@app.route("/api/tts", methods=["POST"])
def generate_tts_audio():
    """
    Genererar röstljud (MP3) via OpenAI TTS för autentiserade Premium- och B2B-användare.
    Ingen ljuddata eller text lagras i databas (GDPR-kompatibel direktström).
    """
    uid, _email, is_premium = _resolve_auth_user()
    if not uid:
        return jsonify({"error": "Inloggning krävs för AI-röst."}), 401
    if not is_premium:
        return jsonify({"error": "AI-röst och röstval kräver Premium eller aktiv B2B-licens."}), 403

    if not OPENAI_API_KEY:
        return jsonify({"error": "Röstsyntes är inte konfigurerad på servern."}), 503

    data = request.get_json(silent=True) or {}
    raw_text = str(data.get("text") or "").strip()
    clean_text = re.sub(r"[#*`_~>]+", "", raw_text)
    clean_text = " ".join(clean_text.split())

    if not clean_text:
        return jsonify({"error": "Ingen text att läsa upp."}), 400

    # Hårt teckentak per anrop för kostnads- och latensskydd
    clean_text = clean_text[:1500]

    voice = str(data.get("voice") or "onyx").strip().lower()
    if voice not in ALLOWED_TTS_VOICES:
        voice = "onyx"

    try:
        speed = float(data.get("speed", 0.98))
    except (TypeError, ValueError):
        speed = 0.98
    speed = max(0.85, min(1.15, speed))

    try:
        import openai
        tts_client = openai.OpenAI(api_key=OPENAI_API_KEY, timeout=25.0)
        speech_resp = tts_client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=clean_text,
            speed=speed,
            response_format="mp3",
        )
        audio_bytes = getattr(speech_resp, "content", None)
        if audio_bytes is None:
            audio_bytes = speech_resp.read()

        return Response(
            audio_bytes,
            status=200,
            mimetype="audio/mpeg",
            headers={"Cache-Control": "no-store"},
        )
    except Exception as e:
        logging.error(f"TTS-generering misslyckades för uid={uid}: {type(e).__name__}")
        return jsonify({"error": "Kunde inte generera röstljud just nu."}), 502
# === END FALK PREMIUM TTS ===


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)
