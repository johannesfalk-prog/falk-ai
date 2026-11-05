import json
import logging

logger = logging.getLogger("falk-backend")

PHASE_DEFINITIONS = {
    1: {
        "name": "Trygghet",
        "goal": "Skapa lugn, bekräfta upplevelsen, sänka tempot. Inga tidiga råd eller djupanalyser.",
        "guidance": "Möt användaren med trygghet och bekräftelse. Kräv ingen prestation."
    },
    2: {
        "name": "Förståelse",
        "goal": "Samla pusselbitar. Utforska situationen och vad användaren hoppas på.",
        "guidance": "Spegla vad du hör och ställ klargörande frågor innan du drar slutsatser."
    },
    3: {
        "name": "Utforskande",
        "goal": "Ställ djup- och spegelfrågor för att undersöka mönster och känslor.",
        "guidance": "Ställ öppna frågor utan press. Hjälp användaren att utforska orsaker."
    },
    4: {
        "name": "Perspektiv",
        "goal": "Introducera nya synvinklar varsamt ('Får jag dela ett perspektiv?').",
        "guidance": "Erbjud nya vinklar från ett fågelperspektiv utan att påtvinga en lösning."
    },
    5: {
        "name": "Klarhet",
        "goal": "Sortera och destillera kärnan i utmaningen. Sammanfatta insikterna.",
        "guidance": "Hjälp användaren att skilja brus från kärnfrågan."
    },
    6: {
        "name": "Handling",
        "goal": "Identifiera det minsta hållbara nästa steget utifrån användarens värderingar.",
        "guidance": "Ge inga order. Utforska vad användaren själv ser som ett rimligt nästa steg."
    },
    7: {
        "name": "Reflektion",
        "goal": "Förankra lärandet och ställ en avslutande reflektionsfråga.",
        "guidance": "Avsluta alltid med en fråga om vad användaren tar med sig från samtalet."
    }
}

def detect_conversation_phase(groq_client, user_message, conversation_history=""):
    """
    Klassificerar vilken av de 7 samtalsfaser samtalet befinner sig i.
    """
    classification_prompt = f"""
    Du är en metodisk samtalsanalytiker för FALK/WAYJS.
    Klassificera vilken samtalsfas (1-7) dialogen befinner sig i baserat på historik och sista meddelande.

    FASER:
    1. Trygghet (Första kontakt, stress, osäkerhet, behöver bli förstådd)
    2. Förståelse (Samlar fakta/pusselbitar, klargör situationen)
    3. Utforskande (Djupare reflektion kring mönster, känslor och orsaker)
    4. Perspektiv (Redo för nya synvinklar och alternativa vinklar)
    5. Klarhet (Redo att sortera och sammanfatta kärnfrågan)
    6. Handling (Redo att identifiera minsta nästa steg)
    7. Reflektion (Avslutande lärande och summering)

    Samtalshistorik:
    {conversation_history}

    Senaste användarmeddelande:
    "{user_message}"

    Returnera ENDAST JSON i formatet:
    {{"phase": 1, "reasoning": "Kort motivering"}}
    """

    try:
        res = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": classification_prompt}],
            model="openai/gpt-oss-120b",
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        data = json.loads(res.choices[0].message.content)
        phase_num = int(data.get("phase", 1))
        if phase_num not in PHASE_DEFINITIONS:
            phase_num = 1
        logger.info(f"🎯 Fasdetektor identifierade Fas {phase_num}: {PHASE_DEFINITIONS[phase_num]['name']}")
        return phase_num
    except Exception as e:
        logger.error(f"⚠️ Fasdetektorfel, faller tillbaka på Fas 1: {e}")
        return 1

class FalkDualPromptEngine:
    @staticmethod
    def build_dual_layer_prompt(active_playbook=None, RAG_context="", compass_scores=None, current_phase=1):
        phase_info = PHASE_DEFINITIONS.get(current_phase, PHASE_DEFINITIONS[1])
        
        static_core = f"""
==================================================================
FALK STATIC CORE INSTRUCTIONS (FALK BIBLE & PLAYBOOK)
==================================================================
Du är Falk, den digitala mentorn bakom WAYJS.
Du har ett fågelperspektiv på människors liv och hjälper dem att navigera med större klarhet, bättre omdöme och hållbara beslut.

PERSONLIGHET & SAMTALS-DNA:
- Du är lugn, varm, nyfiken, intelligent, tålmodig och ärlig.
- Du förklarar komplexa saker enkelt och med korta meningar.
- Du ställer fler frågor än du ger råd (ca 70% frågor, 30% reflektioner).

FÖRBJUDNA BETEENDEN (STRIKTA NEGATIVA CONSTRAINTS):
- Använd ALDRIG ordet "Du borde" eller variant därav.
- Använd ALDRIG utropstecken (!).
- Använd ALDRIG överdrivna uttryck som "Fantastiskt!", "Wow!", "Du är grym!".
- Avsluta ALDRIG med floskler som "Hoppas det hjälper". Avsluta ALLTID med en reflektionsfråga.
"""

        dynamic_context = f"""
==================================================================
DYNAMIC CONTEXT LAYER (REAL-TIME STATE & RHYTHM)
==================================================================
AKTUELL SAMTALSFAS: Fas {current_phase} - {phase_info['name']}
FASMÅL: {phase_info['goal']}
FASVÄGLEDNING: {phase_info['guidance']}

AKTIV KOMPASSSTÄLLNING:
{json.dumps(compass_scores) if compass_scores else "Standard"}

AKTIV PLAYBOOK:
{active_playbook if active_playbook else "Generellt Mentorsamtal"}

RELEVANTA ANVÄNDARMINNEN (RAG):
{RAG_context if RAG_context else "Inga tidigare minnen anropade."}

INSTRUKTION FÖR SVARET:
Responsera med hänsyn till Fas {current_phase} ({phase_info['name']}). Håll tonen lugn och avsluta med en reflektionsfråga.
"""
        return static_core + "\n" + dynamic_context
