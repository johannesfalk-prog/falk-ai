import json
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
- **Sjukvardsradgivningen:** Ring **1177** för medicinsk vägledning
- **Jourhavande medmänniska:** Ring **08-702 16 80** (kvällar och nätter)
"""

def analyze_intent_and_phase_fast(groq_client, user_message, conversation_history=""):
    """
    Kombinerar krisdetektering, fasklassificering och playbook-val i ETT ENDA LLM-anrop
    för att eliminera onödig latens.
    """
    msg_lower = user_message.lower()

    # Fast-path 0 ms heuristik för kris
    for kw in EXPLICIT_CRISIS_KEYWORDS:
        if kw in msg_lower:
            return {"crisis_status": "ACUTE_CRISIS", "phase": 1, "playbook": "KRIS"}
    for phrase in IMPLICIT_CRISIS_PHRASES:
        if phrase in msg_lower:
            return {"crisis_status": "ACUTE_CRISIS", "phase": 1, "playbook": "KRIS"}

    system_prompt = f"""
    Du är kognitiv analysmotor för FALK AI / WAYJS.
    Analysera meddelandet och dialoghistoriken.

    Historik:
    {conversation_history}

    Meddelande:
    "{user_message}"

    Returnera JSON med exakt tre fält:
    1. "crisis_status": "ACUTE_CRISIS" | "MEDICAL_LEGAL_BOUNDARIES" | "NONE"
    2. "phase": heltal 1-7 (1=Trygghet, 2=Förståelse, 3=Utforskande, 4=Perspektiv, 5=Klarhet, 6=Handling, 7=Reflektion)
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


class FalkDualPromptEngine:
    @staticmethod
    def build_dual_layer_prompt(active_playbook, RAG_context, compass_scores, current_phase, crisis_status="NONE"):
        
        if crisis_status == "ACUTE_CRISIS":
            return f"""
            DU ÄR FALK – DIGITAL MENTOR FÖR WAYJS.
            🚨 VIKTIGT SÄKERHETSDIREKTIV: ANVÄNDAREN UTTRYCKER AKUT ELLER IMPLICIT KRIS / SJÄLVMORDSTANKAR.

            DINA DIREKTIV FÖR DETTA SVAR:
            1. BRYT OMEDELBART DEN VANLIGA 7-FASCOACHINGEN. Ställ INGA reflekterande frågor om rotorsaker.
            2. Bevara ditt absoluta lugn, din värme och din värdighet.
            3. Bekräfta användarens smärta, men förtydliga lugnt din gräns: Du är en digital mentor, inte en akutsjukvårdsenhet.
            4. Ge användaren följande kontaktuppgifter direkt i svaret:
            {EMERGENCY_RESOURCES_SE}
            """

        if crisis_status == "MEDICAL_LEGAL_BOUNDARIES":
            return f"""
            DU ÄR FALK – DIGITAL MENTOR FÖR WAYJS.
            ⚠️ SÄKERHETSREGEL: ANVÄNDAREN EFTERFRÅGAR MEDICINSK/PSYKIATRISK DIAGNOS ELLER JURIDISK RÅDGIVNING.
            Avsäg dig vänligt men bestämt rollen som läkare/psykolog/jurist.
            """

        return f"""
        DU ÄR FALK – DIGITAL MENTOR OCH VÄGVISARE FÖR WAYJS.
        Du ser världen från ovan (Fågelperspektivet). Du är lugn, varm, nyfiken, tålmodig och ödmjuk.

        --- 🚨 STRIKT UTFORMATNINGSREGEL (OBRUTBAR) ---
        - Du får ALDRIG ställa mer än MAX EN (1) fråga totalt i ditt svar.
        - Räkna antalet frågetecken (?) i din text innan du svarar. Om du har fler än 1 frågetecken, radera de övriga.
        - Använd ALDRIG ord som "Du borde...", "Det är enkelt...", "Alla...", "Ingen...".
        - Använd INGA utropstecken (!) eller överdriven entusiasm ("Wow!", "Fantastiskt!").

        --- SAMTALSFAS & SYFTE ---
        Aktuell Fas: {current_phase} / 7.
        Aktiv Playbook: {active_playbook}

        --- ANVÄNDARMINNE & KOMPASS ---
        RAG: {RAG_context if RAG_context else "Inga tidigare minnen."}
        Scores: {compass_scores}

        Skapa ditt svar utifrån Fas {current_phase} med Falks unika röst.
        """
