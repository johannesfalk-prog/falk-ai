# safety_guardrails.py - THE WAYJS ETHICAL FRAMEWORK™ (Playbook Kap 11 & FALK_SPEC_2026)

CRISIS_KEYWORDS = [
    "ta mitt liv", "självmord", "suicid", "vill inte leva", "orkar inte leva",
    "avsluta allt", "skada mig själv", "skära mig", "hoppa framför", "överdos",
    "döda mig", "ingen mening att leva", "slåss hemma", "misshandlar mig",
    "utsatt för våld", "övergrepp", "våldtäkt", "akut fara", "vill dö"
]

MEDICAL_LEGAL_KEYWORDS = [
    "diagnos", "har jag adhd", "har jag autism", "är jag bipolär", "depression diagnos",
    "medicin", "dosering", "sluta med antidepressiva", "trappa ner medicin",
    "juridiskt", "stämma", "vårdnadstvist lag", "skattebrott", "investera allt",
    "aktietips", "receptbelagt"
]

CRISIS_RESPONSE_SV = (
    "Tack för att du berättar hur tungt det känns just nu. Din trygghet är det allra viktigaste, "
    "och du ska inte behöva bära det här ensam.\n\n"
    "Eftersom jag är en digital mentor kan jag inte ge akut krisstöd eller ersätta mänsklig vård. "
    "Jag vill varmt be dig att ta kontakt med någon som kan stötta dig direkt:\n\n"
    "- **Vid akut fara:** Ring **112**\n"
    "- **Mind Självmordslinjen (dygnet runt):** Ring **90101** eller chatta på mind.se\n"
    "- **1177 Vårdguiden:** Ring **1177** för sjukvårdsrådgivning och psykiatrisk mottagning\n"
    "- **BRIS (för dig under 18 år):** Ring eller sms:a **116 111**\n"
    "- **Kvinnofridslinjen (vid hot eller våld i nära relation):** Ring **020-50 50 50**\n\n"
    "Finns det en vän, familjemedlem eller vuxen i din närhet som du kan höra av dig till just nu? "
    "Jag finns kvar här i lugn och ro om du vill skriva medan du tar kontakt."
)


def evaluate_safety(user_message: str, is_guest: bool = True) -> dict:
    """
    Utvärderar inkommande meddelande enligt Beslutspyramiden Steg 1 (Säkerhet)
    samt returnerar eventuellt tvingande krissvar och kontextuella säkerhetsinstruktioner.
    """
    msg_lower = (user_message or "").lower().strip()

    if any(kw in msg_lower for kw in CRISIS_KEYWORDS):
        return {
            "is_crisis": True,
            "override_response": CRISIS_RESPONSE_SV,
            "safety_instructions": "",
            "risk_level": "critical",
        }

    instructions = []

    if is_guest:
        instructions.append(
            "SÄKERHETSLÄGE – OINLOGGAD GÄST (POTENTIELLT UNDER 18 ÅR):\n"
            "- Användaren är inte åldersverifierad (kan vara minderårig <18 år). Håll språket helt tryggt, "
            "åldersadekvat och fritt från sexuellt explicit innehåll, droger, självskada eller farliga utmaningar.\n"
            "- Uppmuntra aldrig till stora oåterkalleliga livsbeslut (t.ex. hoppa av skolan, bryta med familj, "
            "ekonomiska risker) utan att varsamt föreslå samtal med en trygg vuxen, kurator eller BRIS (116 111)."
        )

    if any(kw in msg_lower for kw in MEDICAL_LEGAL_KEYWORDS):
        instructions.append(
            "PROFESSIONELL GRÄNSDRAGNING (Playbook Kap 11.8):\n"
            "- Du är varken läkare, psykolog, terapeut, jurist eller finansiell rådgivare.\n"
            "- Ställ aldrig diagnoser och ge aldrig råd om medicinering, nedtrappning, juridik eller investeringar.\n"
            "- Bekräfta upplevelsen med respekt, förklara tydligt och ödmjukt vad som ligger utanför ditt uppdrag, "
            "och erbjud hjälp att formulera frågor som användaren kan ta med till rätt profession (t.ex. 1177/läkare/jurist)."
        )

    return {
        "is_crisis": False,
        "override_response": None,
        "safety_instructions": "\n\n".join(instructions),
        "risk_level": "elevated" if instructions else "normal",
    }


def evaluate_safety_and_crisis(message: str, is_guest: bool = True):
    """
    Bakåtkompatibel wrapper för app.py mot evaluate_safety().
    Returnerar: (is_safe: bool, refusal_text: str, flag_data: dict)
    """
    res = evaluate_safety(user_message=message, is_guest=is_guest)
    if res.get("is_crisis"):
        return False, res.get("override_response", CRISIS_RESPONSE_SV), res
    return True, "", res
