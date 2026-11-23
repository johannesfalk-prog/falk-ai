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
    "så här måste du göra",
    "det är enkelt",
    "du är grym",
    "fantastiskt!",
    "wow!",
    "lita på mig",
    "garanterat",
    "hoppas det hjälper",
    "du har helt rätt",
    "du har absolut rätt",
    "helt rätt tänkt",
    "vilken bra insikt",
    "det är fruktansvärt",
    "det är hemskt",
    "jag vet exakt hur du känner",
    "allt kommer bli bra",
    "det löser sig säkert",
    "tänk positivt",
)

FIVE_GATES_PROMPT = """
Du är Gate Checker-agenten för Falk (WAYJS Wisdom Engine™).
Din uppgift är att utvärdera Falks genererade svar gentemot DE FEM GRINDARNA innan svaret når användaren.

DE FEM GRINDARNA (THE FALK FILTER™):
1. GATE 1 (Truth & Anti-validering): Skiljer svaret på fakta, tolkning och känsla? Bekräftar det upplevelsen utan att godta ogrundade antaganden, skuldbeläggande eller tolkningar som sanning?
   - Förbjudet: Tom medhållsvalidering som "Du har helt rätt", "Helt rätt tänkt" eller dramatiserande förstärkning som "Det är fruktansvärt" / "Det är hemskt". Öppna hellre för fler perspektiv.
2. GATE 2 (Helpful & Mänsklig ton): Skapar svaret klarhet med naturligt, lugnt, mänskligt språk (låg till medelhög energi, köksbordston) utan robotaktiga mallar?
   - Förbjudet: Mekaniska slentrianöppningar som "Det låter som att..." eller terapeut-spegling när användaren bara småpratar eller är i Medvind (allt flyter), samt falsk optimism ("Allt kommer bli bra", "Tänk positivt").
3. GATE 3 (Timing & Samtalsfas 1–7): Är svaret anpassat till aktuell fas (TRYGGHET, FÖRSTÅELSE, UTFORSKANDE, PERSPEKTIV, KLARHET, HANDLING, REFLEKTION)?
   - I faserna TRYGGHET, FÖRSTÅELSE och UTFORSKANDE får ALDRIG direkta råd eller handlingsplaner ges. Vid småprat/Medvind ska svaret vara avslappnat och jämlikt.
   - Vid akut kris/suicidtankar/självskada/våld: Pausa all coaching och mentala modeller; prioritera trygghet och akuta kontaktvägar (112, Mind Självmordslinjen 90101, 1177, Kvinnofridslinjen 020-50 50 50).
4. GATE 4 (Alignment & Continuity): Är svaret i linje med användarens egna värderingar och riktning (Kompassen / Nordstjärnan)?
   - Kontinuitetsregel: Om tidigare samtal, mål eller mönster nämns ska de alltid formuleras som öppna hypoteser ("Känns det fortfarande så?"), aldrig som statiska etiketter som låser användaren i en gammal bild.
5. GATE 5 (Independence & Frågeregeln): Bygger svaret självständighet ("Självständighet före beroende")?
   - Förbjudet: Inställsamt beröm ("Du är grym!", "Fantastiskt!", "Wow!"), tom validering ("Du har helt rätt"), pekpinnar ("Du borde...", "Du måste...", "Det är enkelt"), eller att ta över ansvaret för användarens beslut.
   - HÅRD FRÅGEREGEL: {question_limit_rule}

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
  "final_response": "Om passed=true: behåll proposed_response exakt. Om passed=false: skriv om svaret så att det följer alla 5 grindar, frågebegränsningen och Falks lugna mentor-ton."
}}
"""


_REPETITIVE_OPENER_RE = re.compile(
    r"^\s*(?:det\s+låter\s+(?:verkligen\s+)?som\s+(?:att|om)\s+|jag\s+hör\s+att\s+)",
    re.IGNORECASE,
)

_STRESS_OR_CRISIS_RE = re.compile(
    r"\b(?:stressad|överväldigad|överbelastad|hinner\s+inte|allt\s+snurrar|"
    r"panik|ångest|utmattad|orkar\s+inte|vill\s+inte\s+leva|ta\s+mitt\s+liv|"
    r"självmord|skada\s+mig|hopplöst|kris)\b",
    re.IGNORECASE,
)


def _detect_stress_or_crisis(user_message: str, active_stage: str) -> bool:
    stage_upper = (active_stage or "").upper()
    if any(tag in stage_upper for tag in ("CRISIS", "KRIS", "STRESS", "SAFETY")):
        return True
    return bool(_STRESS_OR_CRISIS_RE.search(user_message or ""))


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


def _limit_questions(text: str, max_questions: int = 2) -> Tuple[str, bool]:
    cleaned = (text or "").strip()
    limit = max(1, min(2, int(max_questions)))
    if cleaned.count("?") <= limit:
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

    if len(all_q_coords) <= limit:
        # Flera '?' inom samma mening – behåll fram till limit:e '?'
        idx = -1
        for _ in range(limit):
            idx = cleaned.find("?", idx + 1)
        if idx != -1:
            return cleaned[: idx + 1].strip(), True
        return cleaned, False

    keep_coords = set()
    if limit == 1:
        prev_p, prev_s = all_q_coords[-2]
        last_p, last_s = all_q_coords[-1]
        if prev_p == last_p and last_s == prev_s + 1:
            keep_coords.add((prev_p, prev_s))
        else:
            keep_coords.add((last_p, last_s))
    else:
        # Behåll den första utforskande frågan och den avslutande frågan
        keep_coords.add(all_q_coords[0])
        keep_coords.add(all_q_coords[-1])

    rebuilt_paragraphs: List[str] = []
    for p_idx, sents in enumerate(para_sentences):
        kept_sents: List[str] = []
        for s_idx, sent in enumerate(sents):
            if "?" in sent and (p_idx, s_idx) not in keep_coords:
                continue
            kept_sents.append(sent)
        if kept_sents:
            rebuilt_paragraphs.append(" ".join(kept_sents))

    result = "\n\n".join(rebuilt_paragraphs).strip()
    if not result:
        ordered_keeps = sorted(keep_coords)
        result = "\n\n".join(para_sentences[kp][ks] for kp, ks in ordered_keeps)

    while result.count("?") > limit:
        last_q = result.rfind("?")
        if last_q == -1:
            break
        result = result[:last_q].rstrip(" .,;:-") + "."

    return result, True


def _limit_to_single_question(text: str) -> Tuple[str, bool]:
    return _limit_questions(text, max_questions=1)


def _enforce_falk_filter(text: str, max_questions: int = 2) -> Tuple[str, List[str]]:
    flags: List[str] = []
    current = (text or "").strip()

    current, opener_trimmed = _strip_repetitive_opener(current)
    if opener_trimmed:
        flags.append("GATE 2 (REPETITIVE_OPENER_TRIMMED)")

    current, question_trimmed = _limit_questions(current, max_questions=max_questions)
    if question_trimmed:
        flags.append(f"GATE 5 (MAX_{max_questions}_QUESTIONS_ENFORCED)")

    return current, flags


def validate_response_against_gates(
    proposed_response: str,
    user_message: str,
    active_stage: str,
    is_guest: bool = True,
    previous_assistant_response: Optional[str] = None,
    max_questions: Optional[int] = None,
    is_stressed: bool = False,
    is_crisis: bool = False,
) -> Tuple[bool, str, Dict[str, Any]]:
    lowered = (proposed_response or "").lower()
    hits = [p for p in FORBIDDEN_MENTOR_PHRASES if p in lowered]

    stressed_or_crisis = bool(
        is_stressed or is_crisis or _detect_stress_or_crisis(user_message, active_stage)
    )
    if max_questions is not None:
        effective_max_q = 1 if stressed_or_crisis else max(1, min(2, int(max_questions)))
    else:
        effective_max_q = 1 if stressed_or_crisis else 2

    if effective_max_q == 1:
        question_limit_rule = (
            "Användaren är stressad, överväldigad eller i kris: Svaret får innehålla "
            "STRIKT MAX ETT (1) frågetecken ('?') totalt (eller 0 vid akut jordning). "
            "Om proposed_response innehåller fler än ett '?' ska passed sättas till false "
            "och svaret skrivas om med högst 1 fråga."
        )
    else:
        question_limit_rule = (
            "Svaret får innehålla MAX TVÅ (2) frågetecken ('?') totalt i normalläge "
            "(0–1 vid rent småprat/Medvind). Om proposed_response innehåller fler än två '?' "
            "ska passed sättas till false och svaret skrivas om med högst 2 frågor."
        )

    if not _api_key or _api_key == "dummy-key-for-init":
        filtered_response, filter_flags = _enforce_falk_filter(
            proposed_response, max_questions=effective_max_q
        )
        violated = (["GATE 5"] if hits else []) + filter_flags
        passed = (len(hits) == 0) and (len(filter_flags) == 0)
        return passed, filtered_response, {
            "skipped": "no_openai_key",
            "max_questions_enforced": effective_max_q,
            "violated_gates": violated,
            "forbidden_hits": hits,
        }

    try:
        guest_label = (
            "AKTIVT (måste vara 100% tryggt även för <18 år)"
            if is_guest
            else "INLOGGAD ANVÄNDARE"
        )
        formatted_prompt = FIVE_GATES_PROMPT.format(
            question_limit_rule=question_limit_rule,
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
        final_response, filter_flags = _enforce_falk_filter(
            raw_final, max_questions=effective_max_q
        )

        if hits:
            res.setdefault("violated_gates", []).append("GATE 5 (FORBIDDEN_PHRASE)")
        if filter_flags:
            res.setdefault("violated_gates", []).extend(filter_flags)

        res["max_questions_enforced"] = effective_max_q
        passed = bool(res.get("passed", True)) and not hits and not filter_flags
        return passed, final_response, res

    except Exception as e:
        print(f"[Varning] Gate Checker misslyckades: {e}.")
        filtered_response, filter_flags = _enforce_falk_filter(
            proposed_response, max_questions=effective_max_q
        )
        violated = (["GATE 5 (FORBIDDEN_PHRASE)"] if hits else []) + filter_flags
        passed = (len(hits) == 0) and (len(filter_flags) == 0)
        return passed, filtered_response, {
            "error": str(e),
            "max_questions_enforced": effective_max_q,
            "forbidden_hits": hits,
            "violated_gates": violated,
        }
