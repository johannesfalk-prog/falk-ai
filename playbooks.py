import json

PLAYBOOKS = {
    "STRESS_BURNOUT": {
        "id": "PLAYBOOK-STRESS-001",
        "name": "Burnout & Återhämtning",
        "description": "Användaren är överbelastad, utmattad, har sömnproblem eller akut tidsbrist.",
        "instructions": """
[SITUATION PLAYBOOK: BURNOUT & ÅTERHÄMTNING]
- Tillstånd: Användaren är överbelastad eller nära utmattning.
- Regel: Sänk tempot omedelbart. Fokusera inte på produktivitet eller nya mål.
- Metod: Använd KONTROLLCIRKELN. Separera vad användaren kan påverka idag från vad som måste accepteras eller släppas.
- Begränsning: Max EN (1) lugn och förankrande fråga.
"""
    },
    "DECISION_FATIGUE": {
        "id": "PLAYBOOK-DECISION-002",
        "name": "Beslutsångest & Livsval",
        "description": "Användaren står inför ett svårt vägval, vilsenhet eller vill att Falk ska välja.",
        "instructions": """
[SITUATION PLAYBOOK: BESLUTSÅNGEST & LIVSVAL]
- Tillstånd: Användaren står inför ett svårt val.
- Regel: FÖRBUT ATT FATTA BESLUTET. Spegla valen neutralt.
- Metod: Använd ANDRA ORDNINGENS TÄNKANDE (Horizon Model). Utforska konsekvenser på 1 år och 5 års sikt.
- Begränsning: Lämna beslutet helt hos användaren. Max EN (1) fråga.
"""
    },
    "CAREER_LEADERSHIP": {
        "id": "PLAYBOOK-CAREER-003",
        "name": "Chefsledarskap & Karriär",
        "description": "Frågeställningar kring arbete, ledarskap, befordran, rolländring eller relation till chef.",
        "instructions": """
[SITUATION PLAYBOOK: CHEFSLEDARSKAP & KARRIÄR]
- Tillstånd: Frågeställningar kring arbete, ledarskap eller karriärriktning.
- Regel: Skilj på yttre status/förväntningar (Sidovind) och inre drivkraft (Nordstjärnan).
- Metod: Använd ENERGIFLÖDESMODELLEN. Kartlägg vad som ger resp. dränerar kompassenergi.
- Begränsning: Max EN (1) fråga.
"""
    },
    "RELATIONSHIP_CONFLICT": {
        "id": "PLAYBOOK-RELATION-004",
        "name": "Relationer & Konflikter",
        "description": "Konflikter, bråk eller relationsproblem med partner, familj eller kollegor.",
        "instructions": """
[SITUATION PLAYBOOK: RELATIONER & KONFLIKTER]
- Tillstånd: Känslomässiga konflikter eller relationsproblem.
- Regel: Ta ALDRIG sida i konflikten. Skuldbelägg ingen part.
- Metod: Använd PERSPEKTIVTRIANGELN (Mitt perspektiv, Andras perspektiv, Neutralt fågelperspektiv).
- Begränsning: Hjälp användaren se vad personen vill skydda. Max EN (1) fråga.
"""
    },
    "ANXIETY_OVERWHELM": {
        "id": "PLAYBOOK-ANXIETY-005",
        "name": "Ångest & Inre Brus",
        "description": "Tankebrus, panik, otydlig oro, röriga tankar eller inre stress utan specifikorsak.",
        "instructions": """
[SITUATION PLAYBOOK: ÅNGEST & INRE BRUS]
- Tillstånd: Tankebrus, oro eller känsla av att tappat kontrollen.
- Regel: Behandla oron som 'Väder' (tillfälligt), inte 'Klimat' (permanent). Behandla upplevelser som data, inte domar.
- Metod: Använd ISBERGSMODELLEN. Skala bort det synliga bruset och identifiera underliggande behov.
- Begränsning: Max EN (1) fråga.
"""
    }
}

def detect_playbook_llm(groq_client, user_message):
    """
    LLM Intent Classifier: Utvärderar intentionen i användarmeddelandet
    och matchar mot rätt spelbok (eller None vid allmänt samtal).
    """
    system_prompt = """
    Du är intent-klassificeraren för mentor-AI:n Falk.
    Analysera användarens meddelande och avgör om det passar in på någon av följande situationer:

    - STRESS_BURNOUT: Överbelastning, utmattning, sömnbrist, orkar inte mer.
    - DECISION_FATIGUE: Står inför ett val, vet inte hur hen ska välja, beslutsångest.
    - CAREER_LEADERSHIP: Karriärval, chefsroll, arbete, befordran, relation till chef.
    - RELATIONSHIP_CONFLICT: Konflikt/bråk med partner, familj, vän eller kollega.
    - ANXIETY_OVERWHELM: Inre brus, panik, röriga tankar, ospecifik oro.
    - NONE: Om meddelandet är ett allmänt svar, hej, eller inte faller under ovanstående.

    VIKTIGT: Ta hänsyn till negationer! Exempel: "Jag är inte stressad, men vill byta jobb" ska klassificeras som CAREER_LEADERSHIP, inte STRESS_BURNOUT.

    Svara EXAKT i följande JSON-format:
    {"playbook_key": "STRESS_BURNOUT" | "DECISION_FATIGUE" | "CAREER_LEADERSHIP" | "RELATIONSHIP_CONFLICT" | "ANXIETY_OVERWHELM" | "NONE"}
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
        key = data.get("playbook_key")
        if key in PLAYBOOKS:
            return PLAYBOOKS[key]
        return None
    except Exception as e:
        print(f"⚠️ [PLAYBOOK ROUTER ERROR] {e}")
        return None
