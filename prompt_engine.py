import json
import re
import logging

logger = logging.getLogger("falk-backend")

EXPLICIT_CRISIS_KEYWORDS = [
    "ta mitt liv", "självmord", "ta livet av mig", "vill inte leva", 
    "skada mig", "hoppa framför", "avsluta allt", "skära mig"
]

IMPLICIT_CRISIS_PHRASES = [
    "bättre utan mig", "inte vakna", "ingen idé att fortsätta", 
    "orka inte vakna", "försvinna från allt", "ingen anledning att leva",
    "skulle alla få det bättre om jag", "inte finnas mer"
]

EMERGENCY_RESOURCES_SE = """
Om du eller någon du känner befinner er i en akut kris eller har tankar på att ta ditt liv, finns det hjälp att få direkt:
- **Självmordslinjen (Mind):** Ring eller chatta på **90101** (öppet dygnet runt, mind.se)
- **Akutpsyk/Nödnummer:** Ring **112** vid akut fara
- **Sjukvårdsrådgivningen:** Ring **1177** för medicinsk vägledning
"""

def analyze_intent_and_phase_fast(groq_client, user_message, conversation_history=""):
    msg_lower = user_message.lower()

    for kw in EXPLICIT_CRISIS_KEYWORDS:
        if kw in msg_lower:
            return {"crisis_status": "ACUTE_CRISIS", "phase": 1, "playbook": "KRIS"}
    for phrase in IMPLICIT_CRISIS_PHRASES:
        if phrase in msg_lower:
            return {"crisis_status": "ACUTE_CRISIS", "phase": 1, "playbook": "KRIS"}

    system_prompt = f"""
    Analysera meddelandet för FALK AI / WAYJS.
    Historik: {conversation_history}
    Meddelande: "{user_message}"

    Returnera JSON med exakt tre fält:
    1. "crisis_status": "ACUTE_CRISIS" | "MEDICAL_LEGAL_BOUNDARIES" | "NONE"
    2. "phase": heltal 1-7
    3. "playbook": "STRESS" | "KARRIÄR" | "RELATIONER" | "GENERELL"

    JSON Format:
    {{"crisis_status": "NONE", "phase": 1, "playbook": "GENERELL"}}
    """
    try:
        res = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": system_prompt}],
            model="openai/gpt-oss-120b",
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        data = json.loads(res.choices[0].message.content)
        return {
            "crisis_status": data.get("crisis_status", "NONE"),
            "phase": int(data.get("phase", 1)),
            "playbook": data.get("playbook", "GENERELL")
        }
    except Exception as e:
        logger.error(f"⚠️ Fail-safe aktiverad i fast classifier: {e}")
        return {"crisis_status": "FAIL_SAFE_CAUTION", "phase": 1, "playbook": "GENERELL"}

class ModularPromptEngine:
    @staticmethod
    def compile_5_layer_prompt(phase=1, playbook="GENERELL", RAG_context="", crisis_status="NONE"):
        if crisis_status == "ACUTE_CRISIS":
            return f"DU ÄR FALK (WAYJS). ANVÄNDAREN BEFINNER SIG I AKUT KRIS. BRYT COACHING. GE KRISHJÄLP DIRECT:\n{EMERGENCY_RESOURCES_SE}"

        if crisis_status == "MEDICAL_LEGAL_BOUNDARIES":
            return "DU ÄR FALK (WAYJS). ANVÄNDAREN BER OM DIAGNOS/MEDICIN. Du MÅSTE avsäga dig rollen som läkare och psykolog. Förklara att du inte ställer diagnoser eller förskriver medicin, men kan hjälpa dem sortera tankar inför möte med legitimerad läkare eller psykolog."

        return f"""
        DU ÄR FALK – DIGITAL MENTOR FÖR WAYJS.
        Du ser världen från fågelperspektivet. Lugn, varm, ödmjuk.

        --- STRIKT FORMERING ---
        - DU FÅR ALDRIG STÄLLA MER ÄN MAX EN (1) FRÅGA TOTALT.
        - Använd ALDRIG ord som "Du borde...", "Det är enkelt...", "Wow!", "Fantastiskt!".

        Aktuell Fas: {phase} / 7.
        Aktiv Playbook: {playbook}
        Kontext: {RAG_context}
        """

    @staticmethod
    def deterministic_post_processing(response_text):
        clean_text = response_text

        # 1. Tvätta förbjudna fraser
        clean_text = re.sub(r"\bdu borde\b", "du skulle kunna utforska att", clean_text, flags=re.IGNORECASE)
        clean_text = re.sub(r"\bdet är enkelt\b", "det kan kännas utmanande", clean_text, flags=re.IGNORECASE)

        # 2. Hård fråge-begränsning: Behåll endast SISTA frågetecknet
        q_indices = [m.start() for m in re.finditer(r"\?", clean_text)]
        if len(q_indices) > 1:
            chars = list(clean_text)
            for idx in q_indices[:-1]:
                chars[idx] = "."
            clean_text = "".join(chars)

        return clean_text.strip()
