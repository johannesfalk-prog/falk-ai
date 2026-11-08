import re
from typing import Tuple, Optional, Dict, Any

CRISIS_KEYWORDS = [
    "ta mitt liv", "avsluta mitt liv", "begå självmord", "vill inte leva längre",
    "skada mig själv", "hoppa framför tåget", "skära mig", "inga skäl att leva",
    "döda mig", "avsluta allt"
]

MEDICAL_LEGAL_KEYWORDS = [
    "vilken diagnos har jag", "ge mig ett recept", "är detta cancer",
    "vilken medicin ska jag ta", "stämma min arbetsgivare juridiskt"
]

CRISIS_RESPONSE_TEXT = (
    "Jag hör hur oerhört tungt du har det just nu, och jag vill att du ska veta att du inte behöver bära detta ensam.\n\n"
    "Eftersom jag är en digital mentor och inte en akutsjukvård eller krisenhet, kan jag inte ge dig det stöd du behöver i denna stund. "
    "När livet känns helt obärbart finns det människor som vill och kan hjälpa dig på allvar:\n\n"
    "• Självmordslinjen: Ring eller chatta på 90101 (öppet dygnet runt, suicidezero.se)\n"
    "• SOS Alarm / Akut hjälp: Ring 112\n"
    "• Mind Äldrelinjen / Föräldralinjen: mind.se\n\n"
    "Räck ut en hand till någon av dessa eller en person du litar på i din närhet just nu."
)

def evaluate_safety_and_crisis(user_message: str) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    msg_lower = user_message.lower()

    for kw in CRISIS_KEYWORDS:
        if kw in msg_lower:
            return False, CRISIS_RESPONSE_TEXT, {
                "flagged": True,
                "category": "CRISIS",
                "reason": f"Säkerhetsspärr utlöst: Krisnyckelord '{kw}' identifierat."
            }

    for kw in MEDICAL_LEGAL_KEYWORDS:
        if kw in msg_lower:
            refusal_text = (
                "Det där är en fråga som kräver medicinsk eller juridisk expertis. "
                "Som mentor varken kan eller får jag ge diagnoser eller juridiska råd. "
                "Vilka professionella kontakter skulle du kunna vända dig till för att få ett tryggt svar på detta?"
            )
            return False, refusal_text, {
                "flagged": True,
                "category": "MEDICAL_LEGAL_BOUNDARY",
                "reason": f"Gränsspärr utlöst: '{kw}' kräver licensierad expertis."
            }

    return True, None, {"flagged": False}
