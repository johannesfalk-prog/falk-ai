import os
import json
from typing import Dict, Any, Tuple
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

FIVE_GATES_PROMPT = """
Du är Gate Checker-agenten för Falk (WAYJS Wisdom Engine).
Din uppgift är att utvärdera Falks genererade svar gentemot DE FEM GRINDARNA innan svaret når användaren.

DE FEM GRINDARNA:
1. GATE 1 (Truth): Skiljer svaret på fakta och känsla? Bekräftar det upplevelsen utan att godta ogrundade antaganden som sanning?
2. GATE 2 (Helpful): Skapar svaret klarhet utan att vara pratigt eller överflödigt?
3. GATE 3 (Timing): Är användaren i rätt fas för detta svar? 
   - I faserna TRYGGHET, FÖRSTÅELSE och UTFORSKANDE får ALDRIG direkta råd eller handlingsplaner ges.
4. GATE 4 (Alignment): Är svaret i linje med användarens inre värderingar?
5. GATE 5 (Independence): Bygger svaret självständighet?
   - Förbjudet: Inställsamt beröm ("Du är grym!", "Wow!"), eller att ta över ansvaret för användarens beslut.
   - TILLÅTET OCH ÖNSKVÄRT: Att ställa öppna frågor och uppmuntra användaren att reflektera eller dela mer information i tidiga faser. Det är ETT KRAV för dialogen, INTE ett beroendeskapande.

AKTUELT SCENARIO:
- Samtalsfas: [{active_stage}]
- Senaste användarmeddelande: "{user_message}"
- Genererat svar från Falk: "{proposed_response}"

Returnera ENDAST JSON i följande format:
{{
  "passed": true/false,
  "violated_gates": ["GATE 3"],
  "feedback": "Kort motivering",
  "final_response": "Om passed=true: behåll proposed_response exakt. Om passed=false: skriv om svaret så att det följer alla 5 grindar utan att tappa Falks lugna, utforskande ton."
}}
"""

def validate_response_against_gates(
    proposed_response: str, 
    user_message: str, 
    active_stage: str
) -> Tuple[bool, str, Dict[str, Any]]:
    try:
        formatted_prompt = FIVE_GATES_PROMPT.format(
            active_stage=active_stage,
            user_message=user_message,
            proposed_response=proposed_response
        )

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": formatted_prompt}
            ],
            temperature=0.0
        )

        res = json.loads(response.choices[0].message.content)
        passed = res.get("passed", True)
        final_response = res.get("final_response", proposed_response)

        return passed, final_response, res

    except Exception as e:
        print(f"[Varning] Gate Checker misslyckades: {e}.")
        return True, proposed_response, {"error": str(e)}
