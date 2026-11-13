# mental_models.py - THE WAYJS THINKING FRAMEWORK™ (Falk Bible Kap 3-4 & Playbook Kap 8)
from situation_playbooks import SITUATION_PLAYBOOKS

MENTAL_MODELS = {
    "kompassen": {
        "name": "Kompassen (Wayjs Grundmodell)",
        "trigger_keywords": ["riktning", "vilse", "vet inte vad jag vill", "mål", "kurs", "vägval"],
        "questions": [
            "Var står du just nu?",
            "Vart vill du egentligen?",
            "Vad hindrar dig?",
            "Vad blir ditt nästa rimliga steg?"
        ],
        "instruction": "Hjälp användaren orientera sig utifrån inre riktning snarare än yttre prestation eller tempo."
    },
    "fagelperspektivet": {
        "name": "Fågelperspektivet (Bird's Eye View™ - 8 linser)",
        "trigger_keywords": ["fastnat", "överväldigad", "detaljer", "kaos", "helhet", "zooma ut"],
        "questions": [
            "Vad ser du om du höjer dig över situationen och zoomar ut?",
            "Vad blir mindre viktigt på avstånd, och vilket större mönster framträder?"
        ],
        "instruction": "Analysera tyst genom BIRDS EYE™ (Beliefs, Identity, Relationships, Direction, Systems, Emotions, Your Choices, Environment) och hjälp användaren lyfta blicken."
    },
    "nordstjarnan": {
        "name": "Nordstjärnan (The North Star™)",
        "trigger_keywords": ["värderingar", "mening", "syfte", "viktigt på riktigt", "identitet", "kompromissa"],
        "questions": [
            "Stämmer det här beslutet överens med dina djupaste värderingar?",
            "Vilken version av dig själv bygger du genom det här valet?"
        ],
        "instruction": "Jämför situationen mot användarens värderingar, syfte och långsiktiga identitet – aldrig mot omgivningens förväntningar."
    },
    "kontrollcirkeln": {
        "name": "Kontrollcirkeln",
        "trigger_keywords": ["stress", "oro", "kontroll", "andra människor", "chef", "partner", "orättvist", "maktlös"],
        "questions": [
            "Vad i den här situationen ligger faktiskt inom din egen kontroll?",
            "Vad kan du påverka, och vad behöver du acceptera just nu?"
        ],
        "instruction": "Hjälp användaren flytta energi från det okontrollerbara till det som ligger inom egen kontroll."
    },
    "andra_ordningens_tankande": {
        "name": "Andra ordningens tänkande & Tidshorisonten (The Horizon Model™)",
        "trigger_keywords": ["beslut", "välja", "byta jobb", "konsekvenser", "framtid", "ångra", "korsningen"],
        "questions": [
            "Vad händer som första konsekvens – och vad händer efter det?",
            "Hur känns det här beslutet om 3 månader, 1 år och 5 år?"
        ],
        "instruction": "Utforska både omedelbara effekter och långsiktiga ringar över tid (Nu -> 3 mån -> 1 år -> 5 år)."
    },
    "ripple_effect": {
        "name": "Ringar på vattnet (The Ripple Effect™)",
        "trigger_keywords": ["påverkar", "familj", "barn", "ekonomi", "hälsa", "balans", "helheten"],
        "questions": [
            "Vilka ringar på vattnet skapar det här beslutet för dina relationer, din energi, din hälsa och din framtid?"
        ],
        "instruction": "Belys hur ett val inom en kompass (t.ex. Arbete) påverkar övriga kompasser (Personlig, Relation, Liv)."
    },
    "isbergsmodellen": {
        "name": "Isbergsmodellen (The Iceberg Model™)",
        "trigger_keywords": ["varför", "reagerar", "mönster", "alltid", "trigger", "under ytan", "känsla"],
        "questions": [
            "Om det du beskriver är toppen av isberget – vilket behov, vilken rädsla eller vilken värdering ligger under ytan?"
        ],
        "instruction": "Gå varsamt från händelse och symptom till underliggande tankar, känslor, behov och värderingar."
    },
    "identitetsmodellen": {
        "name": "Identitetsmodellen",
        "trigger_keywords": ["vem är jag", "duger inte", "självförtroende", "självkänsla", "osäker", "förebild"],
        "questions": [
            "Vem vill du vara i den här situationen, oavsett hur andra agerar?",
            "Vilken identitet stärker den här handlingen?"
        ],
        "instruction": "Skilj på människan och prestationen/problemet. Förankra förändring i identitet snarare än ren viljestyrka."
    },
    "energiflodesmodellen": {
        "name": "Energiflödesmodellen (Kompassenergi™)",
        "trigger_keywords": ["trött", "energi", "utmattad", "dränerad", "orkar inte", "sömn", "återhämtning"],
        "questions": [
            "Vad i din vardag ger dig kompassenergi just nu, och vad dränerar mest utan att ge något tillbaka?"
        ],
        "instruction": "Fokusera på energi och återhämtning före produktivitet och disciplin."
    },
    "perspektivtriangeln": {
        "name": "Perspektivtriangeln",
        "trigger_keywords": ["konflikt", "bråk", "missförstånd", "relation", "svårt samtal", "arg"],
        "questions": [
            "Hur ser situationen ut från ditt håll, från den andra personens håll, och om en neutral observatör såg er utifrån?"
        ],
        "instruction": "Skapa förståelse utan att ta ställning eller skuldbelägga någon part."
    },
    "smaa_steg": {
        "name": "Tillväxt genom små steg & Mikromod™",
        "trigger_keywords": ["komma igång", "prokrastinerar", "skjuter upp", "vana", "stort", "mod", "vågar inte"],
        "questions": [
            "Vad är den minsta möjliga handlingen (ett mikromod) som känns möjlig även en tung dag?"
        ],
        "instruction": "Bryt ner stora planer till ett enda litet, konkret och hållbart nästa steg."
    },
    "forsta_principer": {
        "name": "Första principer (Fakta vs Antagande)",
        "trigger_keywords": ["alla tycker", "kommer aldrig", "måste", "sant", "antar", "katastrof"],
        "questions": [
            "Vad vet vi faktiskt som ren fakta här, och vad är antaganden eller tolkningar?"
        ],
        "instruction": "Separera fakta från känsla och tolkning i enlighet med Gate 1 (Truth)."
    },
    "invertering": {
        "name": "Invertering",
        "trigger_keywords": ["rädd att misslyckas", "undvika", "saboterar", "fälla"],
        "questions": [
            "Om du skulle garantera att den här situationen blev så dålig som möjligt – vad skulle du göra då, och hur undviker du det?"
        ],
        "instruction": "Använd invertering för att synliggöra dolda risker och självsabotage."
    },
    "80_20_principen": {
        "name": "80/20-principen & Beslutskvadranten",
        "trigger_keywords": ["prioritera", "för mycket att göra", "tidsbrist", "brådskande", "fokus"],
        "questions": [
            "Vilka få saker skapar mest verkligt värde just nu, och vad är bara brådskande brus?"
        ],
        "instruction": "Hjälp användaren skilja på viktigt och brådskande."
    },
    "friktion_och_flode": {
        "name": "Friktion och flöde",
        "trigger_keywords": ["svårt att hålla i", "rutin", "disciplin", "faller tillbaka", "miljö"],
        "questions": [
            "Vad skapar onödig friktion just nu, och hur kan du göra det önskade valet till det enklaste valet?"
        ],
        "instruction": "Designa omgivning och vanor (Växthuset™) istället för att förlita sig på motivation."
    },
    "vader_vs_klimat": {
        "name": "Väder vs Inre Klimat™",
        "trigger_keywords": ["dålig dag", "uppgiven", "hopplöst", "idag", "alltid varit så"],
        "questions": [
            "Är det här ett tillfälligt oväder idag, eller ett långsiktigt mönster i ditt inre klimat?"
        ],
        "instruction": "Avråd från stora livsbeslut baserade på tillfälligt känsloväder."
    },
    "tre_speglar": {
        "name": "The Three Mirrors™ (Nuet, Historien, Framtiden)",
        "trigger_keywords": ["fastnat", "upprepar", "samma sak igen", "tillbaka", "förändring", "ny fas"],
        "questions": [
            "Om vi tittar i tre speglar – vad händer egentligen i nuet, har detta hänt tidigare i din historia, och hur vill du kunna se tillbaka på det här i framtiden?"
        ],
        "instruction": "Använd The Three Mirrors™ (Spegel 1: Nuet, Spegel 2: Historien, Spegel 3: Framtiden) när användaren sitter fast i ett mönster."
    },
    "eagle_circle": {
        "name": "The Eagle Circle™ (Sex höjder)",
        "trigger_keywords": ["stort beslut", "livsval", "skilsmässa", "säga upp mig", "flytta", "avgörande"],
        "questions": [
            "Om vi lyfter blicken genom sex höjder – hur känns det här nu, om en vecka, om ett år, för dina relationer, för din livsvision och när du ser tillbaka om tjugo år?"
        ],
        "instruction": "Använd vid stora, avgörande livsval för maximalt fågelperspektiv."
    },
    "nlp_sex_behov": {
        "name": "De 6 mänskliga drivkrafterna (Hypotesram)",
        "trigger_keywords": ["konflikt i mig", "dras mellan", "trygghet", "frihet", "betydelse", "gemenskap"],
        "questions": [
            "Jag hör två drivkrafter som drar åt olika håll – kanske behovet av trygghet och behovet av förändring. Hur upplever du den spänningen?"
        ],
        "instruction": "Använd de 6 behoven (Trygghet, Variation, Betydelse, Gemenskap, Utveckling, Bidrag) enbart som ödmjuk hypotes, aldrig som diagnos."
    }
}


def select_mental_models(user_message: str, situation_key: str = "general", max_models: int = 2) -> list:
    msg_lower = (user_message or "").lower()
    pb = SITUATION_PLAYBOOKS.get(situation_key, SITUATION_PLAYBOOKS["general"])
    recommended = set(pb.get("recommended_models", []))

    scored = []
    for key, model in MENTAL_MODELS.items():
        kw_score = sum(1 for kw in model["trigger_keywords"] if kw in msg_lower)
        sit_bonus = 1 if key in recommended else 0
        total = kw_score * 2 + sit_bonus
        if total > 0:
            scored.append((total, kw_score, key, model))

    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    selected = [item[3] for item in scored[:max_models]]
    if not selected:
        selected = [MENTAL_MODELS["kompassen"], MENTAL_MODELS["fagelperspektivet"]]
    return selected


def format_mental_models_prompt(models: list) -> str:
    if not models:
        models = [MENTAL_MODELS["kompassen"], MENTAL_MODELS["fagelperspektivet"]]
    blocks = []
    for m in models:
        q_example = m.get("questions", [""])[0]
        blocks.append(
            f"- {m.get('name', '')}: {m.get('instruction', '')} "
            f"(Exempelfråga: \"{q_example}\")"
        )
    return (
        "Använd följande mentala modeller som tyst analysram eller varsamt erbjudet perspektiv "
        "(människan går alltid före modellen):\n" + "\n".join(blocks)
    )
