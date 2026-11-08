from typing import Optional, Dict, Any

MENTAL_MODELS: Dict[str, Dict[str, Any]] = {
    "BIRDS_EYE": {
        "name": "Fågelperspektivet",
        "trigger_stages": ["UTFORSKANDE", "PERSPEKTIV", "KLARHET"],
        "keywords": ["perspektiv", "zooma ut", "helhet", "mönster", "överblick"],
        "prompt_snippet": """
MENTAL MODELL [FÅGELPERSPEKTIVET]:
- Hjälp användaren att zooma ut från det akuta problemet och se hela sitt livslandskap.
- Fråga: 'Om du ser på detta från ovan, vad blir då egentligen viktigast?'
"""
    },
    "ICEBERG": {
        "name": "Isbergsmodellen",
        "trigger_stages": ["FORSTAELSE", "UTFORSKANDE"],
        "keywords": ["varför", "orsak", "under ytan", "känsla", "egentligen"],
        "prompt_snippet": """
MENTAL MODELL [ISBERGSMODELLEN]:
- Påminn om att händelsen bara är toppen av isberget.
- Utforska vad som finns under ytan (känslor, rädslor, drivkrafter och inre värderingar).
"""
    },
    "CONTROL_CIRCLE": {
        "name": "Kontrollcirkeln",
        "trigger_stages": ["TRYGGHET", "FORSTAELSE", "HANDLING"],
        "keywords": ["kontroll", "påverka", "oroar", "maktlös", "måste"],
        "prompt_snippet": """
MENTAL MODELL [KONTROLLCIRKELN]:
- Sortera strikt mellan vad användaren kan KONTROLLERA, PÅVERKA eller helt behöver ACCEPTERA.
- Hjälp användaren att flytta all sin energi till det som ligger inom den egna kontrollen.
"""
    }
}

def detect_mental_model(user_message: str, active_stage: str) -> Optional[str]:
    """Väljer och aktiverar en mental modell baserat på fas och nyckelord."""
    msg_lower = user_message.lower()
    for key, model in MENTAL_MODELS.items():
        if active_stage in model["trigger_stages"]:
            if any(word in msg_lower for word in model["keywords"]):
                return model["prompt_snippet"]
    
    # Standardmodell för PERSPEKTIV och KLARHET
    if active_stage in ["PERSPEKTIV", "KLARHET"]:
        return MENTAL_MODELS["BIRDS_EYE"]["prompt_snippet"]
        
    return None
