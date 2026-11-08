from typing import Optional, Dict, Any

SITUATION_PLAYBOOKS: Dict[str, Dict[str, Any]] = {
    "STRESS": {
        "name": "Stress & Återhämtning",
        "keywords": ["stress", "hinner inte", "överbelastad", "utbränd", "kalender", "orkar inte", "utmattad"],
        "prompt_snippet": """
SITUATION PLAYBOOK [STRESS & ÅTERHÄMTNING]:
- Prioritera lugn och sänk tempot direkt. Ge inga stora förändringsplaner.
- Hjälp användaren sortera vad som är akuta krav kontra vad som kan vänta.
- Använd Kontrollcirkeln (fokusera enbart på det användaren kan påverka idag).
"""
    },
    "CAREER": {
        "name": "Karriär & Vägval",
        "keywords": ["jobb", "karriär", "chef", "säga upp", "byta jobb", "erbjudande", "kollega", "lön"],
        "prompt_snippet": """
SITUATION PLAYBOOK [KARRIÄR & VÄGVAL]:
- Utforska värderingar och energiflöde innan du diskuterar konkreta alternativ.
- Fråga vad som ger kontra tar energi på nuvarande plats.
- Använd Andra ordningens tänkande (hur ser detta beslut ut om 1 år och 5 år?).
"""
    },
    "RELATIONSHIPS": {
        "name": "Relationer & Konflikter",
        "keywords": ["partner", "skilsmässa", "bråk", "relation", "familj", "vän", "konflikt", "breeka"],
        "prompt_snippet": """
SITUATION PLAYBOOK [RELATIONER & KONFLIKTER]:
- Ta aldrig sida i en konflikt. Fokusera på användarens eget självledarskap.
- Utforska vad användaren försöker skydda eller vad för Behov som inte blir mött.
- Använd Perspektivtriangeln (mitt perspektiv, andras perspektiv, det neutrala perspektivet).
"""
    },
    "SELF_CRITICISM": {
        "name": "Självkritik & Skuld",
        "keywords": ["värdelös", "misslyckats", "duger inte", "mitt fel", "skam", "dålig förälder", "skuld"],
        "prompt_snippet": """
SITUATION PLAYBOOK [SJÄLVKRITIK & SKULD]:
- Bekräfta upplevelsen med djup medkänsla utan att godta den självkritiska domen som fakta.
- Skilj strikt på vem personen ÄR och vad personen har GJORT.
- Hjälp användaren att se situationen med samma värme som mot en nära vän.
"""
    }
}

def detect_situation_playbook(user_message: str) -> Optional[str]:
    """Analyserar användarmeddelandet och returnerar lämpligt situations-snippet."""
    msg_lower = user_message.lower()
    for key, playbook in SITUATION_PLAYBOOKS.items():
        if any(word in msg_lower for word in playbook["keywords"]):
            return playbook["prompt_snippet"]
    return None
