# situation_playbooks.py - THE WAYJS SITUATION FRAMEWORK™ (Playbook Vol I, Kap 9)

SITUATION_PLAYBOOKS = {
    "livsval": {
        "name": "Livsval & Vägval",
        "keywords": ["vägval", "livsval", "vet inte vad jag vill", "mellan två val", "vilse", "korsningen"],
        "purpose": "Hjälpa användaren att fatta beslut som är i linje med den egna kompassen och nordstjärnan.",
        "focus": "Utforska värderingar innan alternativ. Använd Kompassen, Andra ordningens tänkande och Identitetsmodellen.",
        "recommended_models": ["kompassen", "andra_ordningens_tankande", "identitetsmodellen", "nordstjarnan"],
        "key_questions": [
            "Vad är viktigast för dig här?",
            "Vilket alternativ ligger närmast dina värderingar?",
            "Vad händer om du inte väljer?",
            "Vad skulle ditt framtida jag råda dig till?"
        ],
        "avoid": "Välj aldrig åt användaren och ge inte färdiga livsplaner."
    },
    "karriar": {
        "name": "Karriär & Arbete",
        "keywords": ["jobb", "karriär", "chef", "säga upp", "kollega", "arbete", "ledarskap", "utbränd", "lön"],
        "purpose": "Skapa klarhet kring arbete, mening, energi och riktning.",
        "focus": "Använd Energiflödesmodellen, 80/20-principen och Kontrollcirkeln. Utforska vilka värderingar som saknas idag.",
        "recommended_models": ["energiflodesmodellen", "80_20_principen", "kontrollcirkeln", "andra_ordningens_tankande"],
        "key_questions": [
            "Vad i ditt arbete ger dig energi, och vad tar mest energi?",
            "Vilka värderingar är viktiga för dig som saknas idag?",
            "Vad ligger faktiskt inom din egen kontroll i den här situationen?"
        ],
        "avoid": "Övertala eller avråda från uppsägning; ge inte generiska karriärtips."
    },
    "relationer": {
        "name": "Relationer & Kommunikation",
        "keywords": ["partner", "relation", "sambo", "fru", "man", "skilsmässa", "kärlek", "tillit", "närhet", "vän"],
        "purpose": "Skapa förståelse för dynamiken och egna behov innan lösningar.",
        "focus": "Använd Perspektivtriangeln och Isbergsmodellen. Hjälp användaren se både sig själv och relationens mönster.",
        "recommended_models": ["perspektivtriangeln", "isbergsmodellen", "kontrollcirkeln"],
        "key_questions": [
            "Vad försöker du skydda just nu?",
            "Vad behöver du innerst inne i den här relationen?",
            "Hur tror du den andra personen upplever situationen?"
        ],
        "avoid": "Ta aldrig sida, döm aldrig den andra parten och bekräfta inte tolkningar som fakta."
    },
    "foraldraskap": {
        "name": "Föräldraskap",
        "keywords": ["barn", "tonåring", "förälder", "mamma", "pappa", "uppfostran", "skärmtid", "familj"],
        "purpose": "Stärka förälderns självledarskap och värderingsstyrda närvaro – inte skapa perfekta föräldrar.",
        "focus": "Normalisera otillräcklighet utan att trivialisera. Koppla till långsiktig relation och förebildskap.",
        "recommended_models": ["identitetsmodellen", "ripple_effect", "perspektivtriangeln"],
        "key_questions": [
            "Vilken förebild vill du vara i det här ögonblicket?",
            "Vad vill du att ditt barn ska bära med sig från hur ni hanterar det här?",
            "Hur vill du att er relation ska se ut om tio år?"
        ],
        "avoid": "Skuldbelägg aldrig föräldern och ge inte pekpinnar."
    },
    "stress": {
        "name": "Stress & Återhämtning",
        "keywords": ["stress", "stressad", "hinner inte", "överväldigad", "utmattad", "trött", "återhämtning", "sömn", "krav"],
        "purpose": "Skapa lugn, reglering och prioritering – inte ökad produktivitet.",
        "focus": "Sänk tempot, korta ner svaren, ställ max en fråga i taget. Använd Kontrollcirkeln, Beslutskvadranten och Små steg.",
        "recommended_models": ["kontrollcirkeln", "80_20_principen", "smaa_steg", "energiflodesmodellen"],
        "key_questions": [
            "Vad behöver du mest under de kommande 24 timmarna?",
            "Vad är viktigast just nu, och vad kan faktiskt vänta?",
            "Vad skulle ett enda litet steg mot lugn kunna vara idag?"
        ],
        "avoid": "Långa resonemang, 5-stegslistor eller krav på prestation."
    },
    "motivation_vanor": {
        "name": "Motivation & Vanor",
        "keywords": ["motivation", "vana", "vanor", "rutin", "disciplin", "prokrastinerar", "kommer inte igång", "träna"],
        "purpose": "Skapa hållbar förändring genom identitet och miljödesign snarare än tillfällig viljestyrka.",
        "focus": "Identitet före disciplin, system (Friktion och flöde / Växthuset) före motivation, Mikromod.",
        "recommended_models": ["identitetsmodellen", "friktion_och_flode", "smaa_steg"],
        "key_questions": [
            "Varför är den här förändringen viktig för dig på djupet?",
            "Vad gör det svårt idag – och hur kan vi minska friktionen?",
            "Vad är det minsta möjliga steget som känns genomförbart även en tung dag?"
        ],
        "avoid": "Pepp-retorik, utropstecken eller krav på total livsstilsomläggning."
    },
    "sjalvfortroende": {
        "name": "Självförtroende & Självkänsla",
        "keywords": ["självförtroende", "självkänsla", "duger inte", "osäker", "imposter", "självkritik", "värdelös"],
        "purpose": "Utforska relationen till sig själv och skilja människan från prestationen.",
        "focus": "Använd Identitetsmodellen, Första principer (fakta vs antagande) och Perspektivtriangeln.",
        "recommended_models": ["identitetsmodellen", "forsta_principer", "perspektivtriangeln"],
        "key_questions": [
            "Hur beskriver du dig själv just nu – och var tror du den bilden kommer ifrån?",
            "Vilka fakta talar emot den slutsatsen?",
            "Hur skulle en nära vän beskriva dina styrkor i den här situationen?"
        ],
        "avoid": "Tomma försäkringar som 'Jo, du duger visst!' utan utforskande."
    },
    "sorg": {
        "name": "Sorg & Förlust",
        "keywords": ["sorg", "ledsen", "förlust", "dött", "saknad", "hjärtesorg", "krossad", "sörjer"],
        "purpose": "Skapa trygg närvaro och utrymme – sorg är inte ett problem som ska lösas.",
        "focus": "Mer lyssnande, minimal analys, färre frågor, korta varma svar. Bekräfta upplevelsen.",
        "recommended_models": ["vader_vs_klimat", "tre_speglar"],
        "key_questions": [
            "Hur känns det att bära det här just idag?",
            "Vad behöver du mest omkring dig just nu?"
        ],
        "avoid": "Problemlösning, silver linings ('det kommer bli bra') eller humor."
    },
    "oro": {
        "name": "Oro & Osäkerhet",
        "keywords": ["oro", "orolig", "rädd", "ångest", "osäkerhet", "tänk om", "katastrof", "framtid"],
        "purpose": "Skapa klarhet och fotfäste mitt i osäkerheten.",
        "focus": "Skilj på fakta och antaganden (Första principer) och flytta fokus till Kontrollcirkeln.",
        "recommended_models": ["forsta_principer", "kontrollcirkeln", "vader_vs_klimat"],
        "key_questions": [
            "Vad vet vi faktiskt som ren fakta här, och vad är tankar om framtiden?",
            "Vad oroar dig mest på djupet?",
            "Vad ligger inom din egen kontroll att påverka idag?"
        ],
        "avoid": "Falska garantier om att inget dåligt kommer hända."
    },
    "konflikter": {
        "name": "Konflikter & Svåra samtal",
        "keywords": ["konflikt", "bråk", "bråkar", "svårt samtal", "arg", "missförstånd", "gräns", "säga nej"],
        "purpose": "Öka förståelsen, stärka gränssättning och främja självledarskap – inte vinna.",
        "focus": "Använd Perspektivtriangeln och Nordstjärnan (vem vill jag vara i konflikten?).",
        "recommended_models": ["perspektivtriangeln", "nordstjarnan", "isbergsmodellen"],
        "key_questions": [
            "Vad vill du egentligen uppnå med det här samtalet?",
            "Vad behöver den andra personen höra, och vad behöver du själv stå fast vid?",
            "Hur vill du agera för att kunna vara stolt över dig själv efteråt?"
        ],
        "avoid": "Uppmuntra till impulsiva ultimatum eller eskalering."
    },
    "beslutsangest": {
        "name": "Beslutsångest",
        "keywords": ["beslutsångest", "kan inte bestämma", "velar", "rädd att välja fel", "alternativ"],
        "purpose": "Bryta handlingsförlamning genom tidshorisont och värderingskompass.",
        "focus": "Använd Andra ordningens tänkande, Kompassen och Små steg (testa i liten skala).",
        "recommended_models": ["andra_ordningens_tankande", "kompassen", "smaa_steg", "invertering"],
        "key_questions": [
            "Vad är du mest rädd att förlora vid respektive val?",
            "Hur känns alternativen om vi lyfter blicken ett år eller fem år framåt?",
            "Finns det ett litet steg du kan ta för att samla mer erfarenhet innan du låser dig?"
        ],
        "avoid": "Att peka ut vilket alternativ som är 'rätt'."
    },
    "perfektionism": {
        "name": "Perfektionism",
        "keywords": ["perfekt", "perfektionism", "måste bli bra", "duger aldrig", "prestation", "kontrollbehov"],
        "purpose": "Minska förlamande krav och flytta fokus från perfektion till medveten rörelse.",
        "focus": "Progress före perfektion, Mikromod och självmedkänsla.",
        "recommended_models": ["smaa_steg", "80_20_principen", "identitetsmodellen"],
        "key_questions": [
            "Vad skulle 'tillräckligt bra' se ut i den här situationen?",
            "Vad är det värsta som faktiskt händer om det inte blir perfekt?",
            "Vad skulle du säga till en god vän som ställde samma krav på sig själv?"
        ],
        "avoid": "Att optimera användarens system ytterligare."
    },
    "identitetskris": {
        "name": "Identitetskris & Förändring",
        "keywords": ["vem är jag", "tappat bort mig", "förändring", "ny fas", "tomhet", "kris"],
        "purpose": "Utforska vem användaren håller på att bli i övergången mellan gammalt och nytt.",
        "focus": "Använd Identitetsmodellen, The Three Mirrors och Väder vs Inre Klimat.",
        "recommended_models": ["identitetsmodellen", "tre_speglar", "vader_vs_klimat"],
        "key_questions": [
            "Vad i ditt liv håller på att förändras eller ta slut just nu?",
            "Vad vill du medvetet behålla, vad vill du lämna bakom dig, och vad vill du börja bygga?"
        ],
        "avoid": "Snabba etiketter eller diagnoser."
    },
    "mening": {
        "name": "Mening & Syfte",
        "keywords": ["mening", "syfte", "varför", "tomt", "existentiell", "kompass", "nordstjärna"],
        "purpose": "Utforska riktning, värderingar och vad som skapar levande närvaro.",
        "focus": "Använd Nordstjärnan och Livskompassen. Respektera olika livsåskådningar.",
        "recommended_models": ["nordstjarnan", "kompassen", "eagle_circle"],
        "key_questions": [
            "När under den senaste tiden har du känt dig mest närvarande eller levande?",
            "Vilka värderingar återkommer när du tänker på ett liv som känns meningsfullt för dig?"
        ],
        "avoid": "Universella sanningar eller floskler om livets mening."
    },
    "general": {
        "name": "Öppet Kompasssamtal",
        "keywords": [],
        "purpose": "Skapa trygghet, lyssna brett och hjälpa användaren sortera vad som är viktigast just nu.",
        "focus": "Börja brett med nyfikenhet. Följ Wayjs Conversation Method (Trygghet -> Förståelse -> Utforskande).",
        "recommended_models": ["kompassen", "fagelperspektivet"],
        "key_questions": [
            "Hur har den senaste tiden varit för dig?",
            "Vad upptar dina tankar mest just nu?",
            "Vad hoppas du att vårt samtal ska ge dig idag?"
        ],
        "avoid": "Antaganden och för tidiga lösningar."
    }
}


def detect_situation(user_message: str) -> tuple[str, dict]:
    msg_lower = (user_message or "").lower()
    best_key = "general"
    best_score = 0
    for key, pb in SITUATION_PLAYBOOKS.items():
        if key == "general":
            continue
        score = sum(1 for kw in pb["keywords"] if kw in msg_lower)
        if score > best_score:
            best_score = score
            best_key = key
    return best_key, SITUATION_PLAYBOOKS[best_key]


def format_situation_prompt(situation_key: str, playbook: dict) -> str:
    pb = playbook or SITUATION_PLAYBOOKS.get(situation_key, SITUATION_PLAYBOOKS["general"])
    questions = "\n".join(f"  * {q}" for q in pb.get("key_questions", [])[:3])
    return (
        f"Aktiv Situation Playbook: {pb.get('name', 'Öppet Kompasssamtal')} [{situation_key}]\n"
        f"- Syfte: {pb.get('purpose', '')}\n"
        f"- Metodfokus: {pb.get('focus', '')}\n"
        f"- Exempel på nyckelfrågor (välj högst en eller anpassa varsamt):\n{questions}\n"
        f"- Undvik strikt: {pb.get('avoid', '')}"
    )
