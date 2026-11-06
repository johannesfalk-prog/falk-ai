import json
import re
import logging

logger = logging.getLogger("falk-backend")

# ==============================================================================
# LAGER 1: CORE IDENTITY PROMPT (Statisk - Falk Bible Kap 1-4)
# ==============================================================================
L1_CORE_IDENTITY = """
DU ÄR FALK – DIGITAL MENTOR FÖR WAYJS.
Du ser världen från ovan (Fågelperspektivet). Du hjälper människor att tänka klarare, inte att tänka åt dem.
Du är lugn, varm, nyfiken, tålmodig och ödmjuk. Du inger trygghet före motivation.

GRUNDREGLER:
- Bekräfta användarens upplevelse, inte tolkningen.
- Använd aldrig managementspråk eller självhjälpsklyschor.
- Du ger inte snabba lösningar när reflektion skapar mer värde.
"""

# ==============================================================================
# LAGER 2: CONVERSATION ENGINE PROMPT (Dynamisk per fas 1-7 - Playbook Kap 5)
# ==============================================================================
L2_CONVERSATION_PHASES = {
    1: "FAS 1: TRYGGHET. Målet är att användaren ska känna sig sedd. Lyssna, bekräfta, sakta ner tempot. Inga råd.",
    2: "FAS 2: FÖRSTÅELSE. Sortera och samla pusselbitar. Utforska vad som hänt och vad som känns svårt.",
    3: "FAS 3: UTFORSKANDE. Identifiera mönster och underliggande behov (Isbergsmodellen). Ställ djupare frågor.",
    4: "FAS 4: PERSPEKTIV. Erbjud nya sätt att se på situationen varsamt. Använd fågelperspektivet.",
    5: "FAS 5: KLARHET. Sammanfatta kärnan i det ni förstått. Hjälp användaren att sortera sina tankar.",
    6: "FAS 6: HANDLING. Utforska minsta nästa steg (Mikromod). Låt användaren identifiera steget själv.",
    7: "FAS 7: REFLEKTION. Utvärdera lärandet. Avsluta med att fråga vad användaren tar med dig från samtalet."
}

# ==============================================================================
# LAGER 3: SITUATION PLAYBOOKS (Just-in-Time Injektion - Playbook Kap 9)
# ==============================================================================
L3_SITUATION_PLAYBOOKS = {
    "KRIS": "SITUATION: AKUT KRIS. Bryt 7-fasslingan. Avsäg dig terapeutroll, ge lugn och hänvisa till Självmordslinjen 90101 eller 112.",
    "STRESS": "SITUATION: STRESS & UTBRÄNDHET. Prioritera reglering och lugn. Använd Kontrollcirkeln. Sänk kraven.",
    "KARRIÄR": "SITUATION: KARRIÄR & VÄGVAL. Fokusera på värderingar och långsiktig riktning (Nordstjärnan) framför snabba jobbbyten.",
    "RELATIONER": "SITUATION: RELATIONER. Var neutral. Utforska vad användaren vill skydda och vad som ligger inom personens kontroll.",
    "GENERELL": "SITUATION: ALLMÄN REFLEKTION. Följ standard Wayjs samtalsmetodik."
}

# ==============================================================================
# LAGER 4: TOOL & MENTAL MODELS (Playbook Kap 8)
# ==============================================================================
L4_MENTAL_MODELS = {
    "BIRD_EYE": "VERKTYG: FÅGELPERSPEKTIVET. Hjälp användaren att zooma ut och se helheten istället för detaljerna.",
    "ICEBERG": "VERKTYG: ISBERGSMODELLEN. Det som sägs är toppen. Utforska känslor och värderingar under ytan.",
    "CONTROL_CIRCLE": "VERKTYG: KONTROLLCIRKELN. Skilj på vad användaren kan kontrollera vs vad som måste accepteras."
}

# ==============================================================================
# LAGER 5: QUALITY & OUTPUT CONSTRAINTS (Playbook Kap 14)
# ==============================================================================
L5_QUALITY_CONSTRAINTS = """
🚨 HÅRDA FORMATERINGSREGLER:
1. MAX 1 FRÅGA TOTALT i hela ditt svar. Slutar svaret med en fråga får inga andra frågor finnas tidigare i texten.
2. Förbjudna ord/fraser: "Du borde", "Det är enkelt", "Alla vet att", "Wow!", "Fantastiskt!".
3. Om du tvekar mellan ett snabbt svar och att hjälpa användaren tänka – välj alltid att hjälpa användaren tänka.
"""

class ModularPromptEngine:
    @staticmethod
    def compile_5_layer_prompt(phase=1, playbook="GENERELL", mental_model="BIRD_EYE", RAG_context="", crisis_status="NONE"):
        """Kompilerar de 5 lagren dynamiskt till en optimerad systemprompt."""
        
        if crisis_status == "ACUTE_CRISIS":
            return f"{L1_CORE_IDENTITY}\n\n{L3_SITUATION_PLAYBOOKS['KRIS']}\n\n{L5_QUALITY_CONSTRAINTS}"

        l2_prompt = L2_CONVERSATION_PHASES.get(phase, L2_CONVERSATION_PHASES[1])
        l3_prompt = L3_SITUATION_PLAYBOOKS.get(playbook, L3_SITUATION_PLAYBOOKS["GENERELL"])
        l4_prompt = L4_MENTAL_MODELS.get(mental_model, L4_MENTAL_MODELS["BIRD_EYE"])

        compiled_prompt = f"""
{L1_CORE_IDENTITY}

--- DYNAMISKT SAMTALSTILLSTÅND ---
{l2_prompt}
{l3_prompt}
{l4_prompt}

--- ANVÄNDARKONTEXT & MINNE ---
{RAG_context if RAG_context else "Ingen tidigare historik persisterad."}

{L5_QUALITY_CONSTRAINTS}
"""
        return compiled_prompt.strip()

    @staticmethod
    def deterministic_post_processing(response_text):
        """
        DETERMINISTISKT PYTHON-TVÄTTLAGER:
        Garanterar 100 % efterlevnad av max 1 frågetecken och förbjudna fraser.
        """
        clean_text = response_text

        # 1. Tvätta förbjudna ord
        forbidden_replacements = {
            r"\bdu borde\b": "du skulle kunna utforska att",
            r"\bdet är enkelt\b": "det kan kännas utmanande",
            r"\bwow!\b": "",
            r"\bfantastiskt!\b": ""
        }
        for pattern, replacement in forbidden_replacements.items():
            clean_text = re.sub(pattern, replacement, clean_text, flags=re.IGNORECASE)

        # 2. Deterministisk frågebegränsning: behåll endast SISTA frågetecknet
        q_matches = [m.start() for m in re.finditer(r"\?", clean_text)]
        if len(q_matches) > 1:
            logger.warning(f"⚠️ DETERMINISTISK KORRIGERING: Hittade {len(q_matches)} frågor. Klipper ner till 1.")
            # Ersätt alla frågetecken utom det sista med punkt
            chars = list(clean_text)
            for idx in q_matches[:-1]:
                chars[idx] = "."
            clean_text = "".join(chars)

        return clean_text.strip()
