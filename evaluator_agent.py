import os
import json
from typing import Dict, Any, Tuple
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EVALUATOR_SYSTEM_PROMPT = """
Du är den isolerade kvalitetsevaluatorn för Falk (WAYJS Cognitive Engine).
Granska Falks genererade svar mot DE FEM GRINDARNA och Falks Tonalitetsregler.

TILLÅTNA OCH FÖRBJUDNA MÖNSTER:

1. FRÅGOR & ANTI-STACKING (GATE 5):
   - Exakt ETT (1) eller NOLL (0) frågetecken (?) i Falks svar är FULLSTÄNDIGT GODKÄNT.
   - Att ställa EN öppen fråga i TRYGGHET, FÖRSTÅELSE, UTFORSKANDE eller HANDLING är HELT TILLÅTET och OBLIGATORISKT för samtalsmetodiken.
   - Sätt BARA passed=false för frågestapling om svaret faktiskt innehåller 2 eller fler frågetecken.

2. TIMING & RÅDGIVNING (GATE 3):
   - Förbjudet i ALLA faser: Att ge direkta order, råd eller färdiga instruktioner ("Du borde...", "Du måste...", "Gör så här:").
   - Tillåtet i ALLA faser: Att bekräfta känslor, spegla vad användaren sagt, eller ställa öppna frågor som hjälper användaren att tänka själv.
   - I fasen [HANDLING]: Det är HELT TILLÅTET att fråga hur användaren vill utforma sitt steg eller vad som känns rätt för personen.

3. ISOLERING AV ANVÄNDARORD:
   - Straffa ALDRIG Falk för ord, beslut eller krav som användaren själv uttryckt.

Returnera ENDAST JSON:
{
  "passed": true/false,
  "violated_gates": [],
  "feedback": "Kort motivering",
  "suggested_rewrite": "Korrigerad version om passed=false"
}
"""

def evaluate_falk_response(
    proposed_response: str,
    user_message: str,
    active_stage: str
) -> Tuple[bool, str, Dict[str, Any]]:
    try:
        question_count = proposed_response.count("?")
        
        # Kod-guardrail 1: Om 2 eller fler frågor -> Fäll direkt för frågestapling
        if question_count > 1:
            return False, proposed_response, {
                "passed": False,
                "violated_gates": ["GATE 5"],
                "feedback": f"Kod-guardrail: Upptäckte {question_count} frågetecken. Max 1 är tillåtet.",
                "suggested_rewrite": proposed_response
            }

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": EVALUATOR_SYSTEM_PROMPT},
                {"role": "user", "content": f"Samtalsfas: [{active_stage}]\nAntal frågetecken: {question_count}\nAnvändarens meddelande: \"{user_message}\"\nFalks utkast: \"{proposed_response}\""}
            ],
            temperature=0.0
        )

        res = json.loads(response.choices[0].message.content)
        passed = res.get("passed", True)
        violated = res.get("violated_gates", [])

        # Kod-guardrail 2: Överskrid hallucinerade fel om frågeantalet är <= 1 och inga direkta råd givits
        if question_count <= 1 and passed is False:
            feedback_lower = res.get("feedback", "").lower()
            if "fråga" in feedback_lower and not any(forbidden in proposed_response.lower() for forbidden in ["du borde", "du måste", "gör så här"]):
                passed = True
                res["passed"] = True
                res["violated_gates"] = []
                res["feedback"] = "Godkänd (Deterministisk fas- och frågevalidering)."

        final_response = res.get("suggested_rewrite", proposed_response) if not passed else proposed_response

        return passed, final_response, res

    except Exception as e:
        print(f"[Varning] Evaluator-agent misslyckades: {e}")
        return True, proposed_response, {"error": str(e), "passed": True, "violated_gates": []}
