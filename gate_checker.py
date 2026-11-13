import os
import json
from typing import Dict, Any, Tuple
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

DE FEM GRINDARNA:
1. GATE 1 (Truth): Skiljer svaret på fakta och känsla? Bekräftar det upplevelsen utan att godta ogrundade antaganden som sanning?
2. GATE 2 (Helpful): Skapar svaret klarhet med lugnt, mänskligt språk utan att vara pratigt eller överflödigt?
3. GATE 3 (Timing): Är användaren i rätt fas för detta svar?
   - I faserna TRYGGHET, FÖRSTÅELSE och UTFORSKANDE får ALDRIG direkta råd eller handlingsplaner ges.
4. GATE 4 (Alignment): Är svaret i linje med användarens inre värderingar och riktning?
5. GATE 5 (Independence): Bygger svaret självständighet?
   - Förbjudet: Inställsamt beröm ("Du är grym!", "Fantastiskt!", "Wow!"), pekpinnar ("Du borde...", "Du måste..."), eller att ta över ansvaret för användarens beslut.
   - TILLÅTET OCH ÖNSKVÄRT: Att ställa högst EN (1) öppen reflektionsfråga och uppmuntra användaren att utforska vidare.

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


def validate_response_against_gates(
    proposed_response: str,
    user_message: str,
    active_stage: str,
    is_guest: bool = True,
) -> Tuple[bool, str, Dict[str, Any]]:
    lowered = (proposed_response or "").lower()
    hits = [p for p in FORBIDDEN_MENTOR_PHRASES if p in lowered]

    if not _api_key or _api_key == "dummy-key-for-init":
        if hits:
            return False, proposed_response, {"violated_gates": ["GATE 5"], "forbidden_hits": hits}
        return True, proposed_response, {"skipped": "no_openai_key"}

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
        passed = bool(res.get("passed", True)) and not hits
        if hits:
            res.setdefault("violated_gates", []).append("GATE 5 (FORBIDDEN_PHRASE)")
        final_response = res.get("final_response") or proposed_response
        return passed, final_response, res

    except Exception as e:
        print(f"[Varning] Gate Checker misslyckades: {e}.")
        return (len(hits) == 0), proposed_response, {"error": str(e), "forbidden_hits": hits}
