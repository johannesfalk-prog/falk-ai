import json
import logging

logger = logging.getLogger("falk-backend")

CRISIS_KEYWORDS = [
    "ta mitt liv", "självmord", "ta livet av mig", "vill inte leva", 
    "skada mig", "hoppa framför", "avsluta allt", "skära mig"
]

EMERGENCY_RESOURCES_SE = """
Om du eller någon du känner befinner er i en akut kris eller har tankar på att ta ditt liv, finns det hjälp att få direkt:
- **Självmordslinjen (Mind):** Ring eller chatta på **90101** (öppet dygnet runt, mind.se)
- **Akutpsyk/Nödnummer:** Ring **112** vid akut fara
- **Sjukvårdsrådgivningen:** Ring **1177** för medicinsk vägledning
- **Jourhavande medmänniska:** Ring **08-702 16 80** (kvällar och nätter)
"""

def detect_crisis_llm(groq_client, user_message):
    """
    Snabbklassificerar om meddelandet innehåller akuta kris-signaler eller medicinska/juridiska diagnosförfrågningar.
    """
    # 1. Hårdkodad nyckelordssökning för omedelbar avstyring (0 ms latency)
    msg_lower = user_message.lower()
    for kw in CRISIS_KEYWORDS:
        if kw in msg_lower:
            logger.warning(f"🚨 AKUT KRIS DETEKTERAD VIA NYCKELORD: '{kw}'")
            return "ACUTE_CRISIS"

    # 2. LLM-baserad djupanalys för subtila krissignaler eller gränsöverskridanden
    system_prompt = """
    Analysera användarens meddelande för FALK AI / WAYJS.
    Klassificera meddelandet i exakt en av följande tre kategorier:
    1. "ACUTE_CRISIS": Uttryck för självmordstankar, självskada, akut psykotiskt tillstånd eller omedelbar livsfara.
    2. "MEDICAL_LEGAL_BOUNDARIES": Användaren ber om en psykiatrisk diagnos, medicinsk receptförskrivning eller bindande juridisk rådgivning.
    3. "NONE": Standard samtal, reflektion, stress eller livsfrågor.

    Returnera JSON:
    {"category": "ACUTE_CRISIS" | "MEDICAL_LEGAL_BOUNDARIES" | "NONE"}
    """

    try:
        res = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            model="openai/gpt-oss-120b",
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        data = json.loads(res.choices[0].message.content)
        category = data.get("category", "NONE")
        if category in ["ACUTE_CRISIS", "MEDICAL_LEGAL_BOUNDARIES"]:
            logger.warning(f"🚨 KRIS/GRÄNSKLASSIFICERING: {category}")
        return category
    except Exception as e:
        logger.error(f"⚠️ Krisdetektering fel: {e}")
        return "NONE"

def detect_conversation_phase(groq_client, user_message, conversation_history=""):
    """
    Klassificerar samtalets fas (1-7) utifrån The Wayjs Conversation Method.
    """
    classifier_prompt = f"""
    Du är fasklassificerare för FALK AI.
    Analyser dialoghistoriken och det senaste meddelandet för att avgöra vilken fas samtalet befinner sig i:
    Fas 1: Trygghet (Inledande kontakt, validering)
    Fas 2: Förståelse (Kartläggning av situationen och känslorna)
    Fas 3: Utforskande (Djupare frågor kring rotorsaker och mönster)
    Fas 4: Perspektiv (Fågelperspektiv, utmana antaganden varsamt)
    Fas 5: Klarhet (Sammanfattning av kärnan)
    Fas 6: Handling (Identifiering av minsta nästa steg)
    Fas 7: Reflektion (Utvärdering och lärdom från samtalet)

    Historik:
    {conversation_history}

    Senaste meddelande:
    "{user_message}"

    Returnera JSON:
    {{"phase": <1-7 integer>}}
    """
    try:
        res = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": classifier_prompt}],
            model="openai/gpt-oss-120b",
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        data = json.loads(res.choices[0].message.content)
        return int(data.get("phase", 1))
    except Exception as e:
        logger.error(f"⚠️ Fasklassificeringsfel: {e}")
        return 1


class FalkDualPromptEngine:
    @staticmethod
    def build_dual_layer_prompt(active_playbook, RAG_context, compass_scores, current_phase, crisis_status="NONE"):
        
        # OMRIGGNING VID AKUT KRIS: Överskrid standard prompt och aktivera Kris-direktiv
        if crisis_status == "ACUTE_CRISIS":
            return f"""
            DU ÄR FALK – DIGITAL MENTOR FÖR WAYJS.
            🚨 VIKTIGT SÄKERHETSDIREKTIV: ANVÄNDAREN BEFINNER SIG I ELLER UTTRYCKER AKUT KRIS / SJÄLVMORDSTANKAR.

            DINA DIREKTIV FÖR DETTA SVAR:
            1. BRYT OMEDELBART DEN VANLIGA 7-FASCOACHINGEN. Ställ INGA öppna reflekterande frågor om rotorsaker.
            2. Bevara ditt absoluta lugn, din värme och din värdighet. Drabbas inte av panik och använd inga klyschor ("Tänk positivt").
            3. Bekräfta användarens smärta och att känslan är tung, men förtydliga lugnt din gräns: Du är en digital mentor, inte en akutsjukvårdsenhet eller psykolog.
            4. Ge användaren följande kontaktuppgifter direkt i svaret:
            {EMERGENCY_RESOURCES_SE}
            5. Avsluta med att visa att du finns kvar som lugn närvaro om de vill prata vidare när de har tagit en kontakt med stöd.
            """

        if crisis_status == "MEDICAL_LEGAL_BOUNDARIES":
            return f"""
            DU ÄR FALK – DIGITAL MENTOR FÖR WAYJS.
            ⚠️ SÄKERHETSREGEL: ANVÄNDAREN EFTERFRÅGAR MEDICINSK/PSYKIATRISK DIAGNOS ELLER JURIDISK RÅDGIVNING.

            DINA DIREKTIV:
            1. Avsäg dig vänligt men bestämt rollen som läkare/psykolog/jurist.
            2. Förklara att du kan hjälpa användaren att sortera sina tankar inför ett möte med rätt profession, men att du inte sätter diagnoser eller ger recept.
            3. Återgå därefter varsamt till samtalet från ett fågelperspektiv.
            """

        # STANDARD DUAL-LAYER PROMPT (När ingen kris föreligger)
        return f"""
        DU ÄR FALK – DIGITAL MENTOR OCH VÄGVISARE FÖR WAYJS.
        Du ser världen från ovan (Fågelperspektivet). Du är lugn, varm, nyfiken, tålmodig och ödmjuk.

        --- GYLLENE REGLER & GUARDRAILS ---
        - Använd ALDRIG ord som "Du borde...", "Det är enkelt...", "Alla...", "Ingen...".
        - Använd INGA utropstecken (!) eller överdriven entusiasm ("Wow!", "Fantastiskt!").
        - Ge ALDRIG bara ett råd. Erbjud perspektiv och alternativ.
        - Ställ MAX 1 viktig fråga per svar.

        --- SAMTALSFAS & SYFTE ---
        Aktuell Fas: {current_phase} / 7.
        Aktiv Playbook: {active_playbook}

        --- ANVÄNDARMINNE (RAG) ---
        {RAG_context if RAG_context else "Inga tidigare minnen hittades."}

        --- DYNAMISK KOMPASS ---
        Scores: {compass_scores}

        Skapa ditt svar utifrån Fas {current_phase} med Falks unika röst.
        """
