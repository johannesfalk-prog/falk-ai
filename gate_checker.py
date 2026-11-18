import os
import re
import json
from typing import Dict, Any, List, Optional, Tuple
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_api_key = os.getenv("OPENAI_API_KEY", "").strip()
openai_client = OpenAI(api_key=_api_key or "dummy-key-for-init")

FORBIDDEN_MENTOR_PHRASES = (
    "du borde",
    "du måste",
    "det enda du behöver göra",
    "du är grym",
    "fantastiskt!",
    "wow!",
    "lita på mig",
    "garanterat",
    "hoppas det hjälper",
)

FIVE_GATES_PROMPT = """
Du är Gate Checker-agenten för Falk (WAYJS Wisdom Engine™).
Din uppgift är att utvärdera Falks genererade svar gentemot DE FEM GRINDARNA innan svaret når användaren.

DE FEM GRINDARNA (THE FALK FILTER™):
1. GATE 1 (Truth): Skiljer svaret på fakta och känsla? Bekräftar det upplevelsen utan att godta ogrundade antaganden som sanning?
2. GATE 2 (Helpful & Mänsklig ton): Skapar svaret klarhet med naturligt, mänskligt språk utan robotaktiga mallar?
   - Förbjudet: Mekaniska slentrianöppningar som "Det låter som att..." eller terapeut-spegling när användaren bara småpratar eller är i Medvind (allt flyter).
3. GATE 3 (Timing): Är användaren i rätt fas för detta svar?
   - I faserna TRYGGHET, FÖRSTÅELSE och UTFORSKANDE får ALDRIG direkta råd eller handlingsplaner ges. Vid småprat/Medvind ska svaret vara avslappnat och jämlikt.
4. GATE 4 (Alignment): Är svaret i linje med användarens inre värderingar och riktning?
5. GATE 5 (Independence & En-frågeregeln): Bygger svaret självständighet?
   - Förbjudet: Inställsamt beröm ("Du är grym!", "Fantastiskt!", "Wow!"), pekpinnar ("Du borde...", "Du måste..."), eller att ta över ansvaret för användarens beslut.
   - HÅRD FRÅGEREGEL: Svaret får innehålla MAX ETT (1) frågetecken ('?') totalt (eller noll vid rent småprat). Om proposed_response innehåller fler än ett '?' ska passed sättas till false och svaret skrivas om med högst en fråga.

GÄSTLÄGESKRAV ({guest_mode_label}):
- Om GÄSTLÄGE är aktivt: Säkerställ att svaret är 100 % tryggt för användare under 18 år och aldrig uppmuntrar till oåterkalleliga eller riskfyllda livsbeslut utan samtal med en trygg vuxen/professionell.

AKTUELLT SCENARIO:
- Samtalsfas: [{active_stage}]
- Senaste användarmeddelande: "{user_message}"
- Genererat svar från Falk: "{proposed_response}"

Returnera ENDAST JSON i följande format:
{{
  "passed": true/false,
  "violated_gates": ["GATE 3"],
  "feedback": "Kort motivering",
  "final_response": "Om passed=true: behåll proposed_response exakt. Om passed=false: skriv om svaret så att det följer alla 5 grindar och Falks lugna mentor-ton."
}}
"""


_REPETITIVE_OPENER_RE = re.compile(
    r"^\s*(?:det\s+låter\s+(?:verkligen\s+)?som\s+(?:att|om)\s+|jag\s+hör\s+att\s+)",
    re.IGNORECASE,
)


def _strip_repetitive_opener(text: str) -> Tuple[str, bool]:
    cleaned = (text or "").strip()
    match = _REPETITIVE_OPENER_RE.match(cleaned)
    if not match:
        return cleaned, False
    rest = cleaned[match.end():].lstrip()
    if not rest:
        return cleaned, False
    rest = rest[0].upper() + rest[1:]
    return rest, True


def _limit_to_single_question(text: str) -> Tuple[str, bool]:
    cleaned = (text or "").strip()
    if cleaned.count("?") <= 1:
        return cleaned, False

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", cleaned) if p.strip()]
    para_sentences: List[List[str]] = []
    all_q_coords: List[Tuple[int, int]] = []

    for p_idx, para in enumerate(paragraphs):
        sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", para) if s.strip()]
        para_sentences.append(sents)
        for s_idx, sent in enumerate(sents):
            if "?" in sent:
                all_q_coords.append((p_idx, s_idx))

    if len(all_q_coords) <= 1:
        # Flera '?' inom samma mening – behåll fram till första '?'
        first_q = cleaned.find("?")
        return cleaned[: first_q + 1].strip(), True

    # Om de två sista frågorna kommer direkt efter varandra (staplade dubbelfrågor),
    # behåll huvudfrågan (den näst sista) och ta bort den påhängda uppföljningsfrågan.
    prev_p, prev_s = all_q_coords[-2]
    last_p, last_s = all_q_coords[-1]
    if prev_p == last_p and last_s == prev_s + 1:
        keep_coord = (prev_p, prev_s)
    else:
        keep_coord = (last_p, last_s)

    rebuilt_paragraphs: List[str] = []
    for p_idx, sents in enumerate(para_sentences):
        kept_sents: List[str] = []
        for s_idx, sent in enumerate(sents):
            if "?" in sent and (p_idx, s_idx) != keep_coord:
                continue
            kept_sents.append(sent)
        if kept_sents:
            rebuilt_paragraphs.append(" ".join(kept_sents))

    result = "\n\n".join(rebuilt_paragraphs).strip()
    if not result:
        kp, ks = keep_coord
        result = para_sentences[kp][ks]

    if result.count("?") > 1:
        first_q = result.find("?")
        result = result[: first_q + 1].strip()

    return result, True


def _enforce_falk_filter(text: str) -> Tuple[str, List[str]]:
    flags: List[str] = []
    current = (text or "").strip()

    current, opener_trimmed = _strip_repetitive_opener(current)
    if opener_trimmed:
        flags.append("GATE 2 (REPETITIVE_OPENER_TRIMMED)")

    current, question_trimmed = _limit_to_single_question(current)
    if question_trimmed:
        flags.append("GATE 5 (DOUBLE_QUESTION_TRIMMED)")

    return current, flags


def validate_response_against_gates(
    proposed_response: str,
    user_message: str,
    active_stage: str,
    is_guest: bool = True,
    previous_assistant_response: Optional[str] = None,
) -> Tuple[bool, str, Dict[str, Any]]:
    lowered = (proposed_response or "").lower()
    hits = [p for p in FORBIDDEN_MENTOR_PHRASES if p in lowered]

    if not _api_key or _api_key == "dummy-key-for-init":
        filtered_response, filter_flags = _enforce_falk_filter(proposed_response)
        violated = (["GATE 5"] if hits else []) + filter_flags
        passed = (len(hits) == 0) and (len(filter_flags) == 0)
        return passed, filtered_response, {
            "skipped": "no_openai_key",
            "violated_gates": violated,
            "forbidden_hits": hits,
        }

    try:
        guest_label = "AKTIVT (måste vara 100% tryggt även för <18 år)" if is_guest else "INLOGGAD ANVÄNDARE"
        formatted_prompt = FIVE_GATES_PROMPT.format(
            guest_mode_label=guest_label,
            active_stage=active_stage,
            user_message=user_message,
            proposed_response=proposed_response,
        )

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": formatted_prompt}],
            temperature=0.0,
        )

        res = json.loads(response.choices[0].message.content)
        raw_final = res.get("final_response") or proposed_response
        final_response, filter_flags = _enforce_falk_filter(raw_final)

        if hits:
            res.setdefault("violated_gates", []).append("GATE 5 (FORBIDDEN_PHRASE)")
        if filter_flags:
            res.setdefault("violated_gates", []).extend(filter_flags)

        passed = bool(res.get("passed", True)) and not hits and not filter_flags
        return passed, final_response, res

    except Exception as e:
        print(f"[Varning] Gate Checker misslyckades: {e}.")
        filtered_response, filter_flags = _enforce_falk_filter(proposed_response)
        violated = (["GATE 5 (FORBIDDEN_PHRASE)"] if hits else []) + filter_flags
        passed = (len(hits) == 0) and (len(filter_flags) == 0)
        return passed, filtered_response, {
            "error": str(e),
            "forbidden_hits": hits,
            "violated_gates": violated,
        }
