"""
b2b_extensions.py
Isolerat B2B-tilläggslager för FALK (Wayjs Operating System).
Tillhandahåller:
- 4 B2B-kompasser (tilläggslager utöver B2C:s 4 standardkompasser)
- 8 B2B-övningskort för Biblioteket (Ledarskap, Kommunikation, Stresshantering, Effektivisering)
- Aggregering med valfri k-anonymitetsspärr (default k_min=None) och strikt PII-isolering
- Kontextstöd för FALK på individ-, lednings- och företagsnivå
"""

from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# 1. DE 4 B2B-KOMPASSERNA (TILLÄGGSLAGER)
# ---------------------------------------------------------------------------

B2B_COMPASSES: List[Dict[str, Any]] = [
    {
        "id": "b2b_self_leadership",
        "key": "b2b_self_leadership",
        "title": "Självledarskap & Rollklarhet",
        "short_title": "Självledarskap",
        "segment": "b2b",
        "core_question": "Hur tydlig är din riktning, dina prioriteringar och ditt mandat i arbetsvardagen?",
        "description": "Mäter förmågan att leda sig själv, prioritera det viktigaste före det brådskande och navigera sitt mandat med klarhet.",
        "capabilities": ["Prioritering", "Mandat & gränser", "Beslutsförmåga", "Riktning före tempo"],
        "scale_min": 1,
        "scale_max": 10,
    },
    {
        "id": "b2b_team_trust",
        "key": "b2b_team_trust",
        "title": "Samarbete & Psykologisk Trygghet",
        "short_title": "Samarbete & Tillit",
        "segment": "b2b",
        "core_question": "Hur väl fungerar öppen kommunikation, feedback och tillit i teamet?",
        "description": "Mäter upplevelsen av psykologisk trygghet, konstruktiv feedback och förmågan att möta olikheter utan försvar.",
        "capabilities": ["Aktivt lyssnande", "Feedbackkultur", "Konflikthantering", "Psykologisk trygghet"],
        "scale_min": 1,
        "scale_max": 10,
    },
    {
        "id": "b2b_sustainable_energy",
        "key": "b2b_sustainable_energy",
        "title": "Hållbar Energi & Belastningsbalans",
        "short_title": "Hållbar Energi",
        "segment": "b2b",
        "core_question": "Hur hållbart är arbetstempot över tid utan att inre brus och stress tar över?",
        "description": "Mäter balansen mellan krav, återhämtning och fokus – så att prestation sker med lugn snarare än utmattning.",
        "capabilities": ["Stressreglering", "Återhämtning", "Energiflöde", "Kontrollcirkeln"],
        "scale_min": 1,
        "scale_max": 10,
    },
    {
        "id": "b2b_direction_culture",
        "key": "b2b_direction_culture",
        "title": "Strategisk Riktning & Gemensam Kompass",
        "short_title": "Riktning & Kultur",
        "segment": "b2b",
        "core_question": "Hur väl hänger det dagliga arbetet ihop med organisationens syfte, värderingar och mål?",
        "description": "Mäter samstämmighet mellan värderingar, kultur och vardagsbeslut på team- och organisationsnivå.",
        "capabilities": ["Värderingsförankring", "Helhetssyn (Bird's Eye)", "Ansvarstagande", "Långsiktighet"],
        "scale_min": 1,
        "scale_max": 10,
    },
]

# ---------------------------------------------------------------------------
# 2. DE 8 B2B-ÖVNINGSKORTEN FÖR BIBLIOTEKET
# ---------------------------------------------------------------------------

B2B_EXERCISE_CARDS: List[Dict[str, Any]] = [
    # --- LEDARSKAP (2 kort) ---
    {
        "id": "b2b-lead-01",
        "title": "Ledarens Nordstjärna – Riktning före tempo",
        "category": "Ledarskap",
        "segment": "b2b",
        "levels": ["individ", "ledning"],
        "duration": "15 min",
        "compass_key": "b2b_direction_culture",
        "mental_models": ["Nordstjärnan", "Fågelperspektivet", "Kompassen"],
        "summary": "Lyft blicken från akuta operativa krav och kalibrera vilken riktning och kultur ditt ledarskap faktiskt bygger.",
        "description": "Ett reflekterande samtal för chefer och ledare som vill stanna upp, sortera bruset och tydliggöra vad som skapar långsiktig riktning i teamet.",
        "starter_prompt": (
            "Jag vill göra B2B-övningen 'Ledarens Nordstjärna – Riktning före tempo'. "
            "Hjälp mig att zooma ut från vardagens akuta uppgifter och utforska vilken riktning jag vill leda mot."
        ),
    },
    {
        "id": "b2b-lead-02",
        "title": "Delegering med tillit – Mandat utan detaljstyrning",
        "category": "Ledarskap",
        "segment": "b2b",
        "levels": ["individ", "ledning"],
        "duration": "15 min",
        "compass_key": "b2b_self_leadership",
        "mental_models": ["Kontrollcirkeln", "Andra ordningens tänkande", "Små steg"],
        "summary": "Utforska var du håller kvar kontroll av vana och identifiera ett konkret ansvar som kan lämnas över med tydligt mandat.",
        "description": "Hjälper ledare och nyckelpersoner att frigöra tid och bygga självledarskap hos medarbetare utan att tappa trygghet.",
        "starter_prompt": (
            "Jag vill göra B2B-övningen 'Delegering med tillit – Mandat utan detaljstyrning'. "
            "Hjälp mig utforska vad jag håller fast vid i onödan och hur jag kan ge tydligare mandat."
        ),
    },
    # --- KOMMUNIKATION (2 kort) ---
    {
        "id": "b2b-comm-01",
        "title": "Det svåra samtalet – Klarhet utan försvar",
        "category": "Kommunikation",
        "segment": "b2b",
        "levels": ["individ", "ledning"],
        "duration": "15 min",
        "compass_key": "b2b_team_trust",
        "mental_models": ["Perspektivtriangeln", "Isbergsmodellen", "Reflektion före reaktion"],
        "summary": "Förbered ett viktigt samtal med kollega, chef eller team genom att skilja på observation, tolkning och behov.",
        "description": "Strukturerar ett laddat eller uppskjutet samtal så att du möter den andra personen med lugn, respekt och tydlighet.",
        "starter_prompt": (
            "Jag vill göra B2B-övningen 'Det svåra samtalet – Klarhet utan försvar'. "
            "Hjälp mig sortera vad som faktiskt har hänt, vad jag tolkar och vad jag vill uppnå i samtalet."
        ),
    },
    {
        "id": "b2b-comm-02",
        "title": "Psykologisk trygghet i mötesrummet",
        "category": "Kommunikation",
        "segment": "b2b",
        "levels": ["ledning", "foretag"],
        "duration": "10 min",
        "compass_key": "b2b_team_trust",
        "mental_models": ["Fågelperspektivet", "Mönster före undantag", "Kompasskalibrering"],
        "summary": "Granska hur samtalen förs i ert team eller er organisation: vad vågar man säga högt, och vad stannar i korridoren?",
        "description": "En dialogövning för team och ledningsgrupper som vill stärka tillit, nyfikenhet och tidig problemlösning.",
        "starter_prompt": (
            "Jag vill göra B2B-övningen 'Psykologisk trygghet i mötesrummet'. "
            "Hjälp oss utforska hur öppet klimatet är i våra möten och vilket litet steg som kan öka tryggheten."
        ),
    },
    # --- STRESSHANTERING (2 kort) ---
    {
        "id": "b2b-stress-01",
        "title": "Kontrollcirkeln under hög arbetsbelastning",
        "category": "Stresshantering",
        "segment": "b2b",
        "levels": ["individ", "ledning"],
        "duration": "10 min",
        "compass_key": "b2b_sustainable_energy",
        "mental_models": ["Kontrollcirkeln", "Små steg", "Inre Brus"],
        "summary": "Sakta ner tempot och sortera det du kan kontrollera, det du kan påverka och det du behöver släppa taget om idag.",
        "description": "Skapar omedelbar mental avlastning vid hög arbetsbelastning genom lugn sortering och ett enda realistiskt nästa steg.",
        "starter_prompt": (
            "Jag vill göra B2B-övningen 'Kontrollcirkeln under hög arbetsbelastning'. "
            "Hjälp mig sortera allt som snurrar just nu så att jag ser vad som faktiskt ligger inom min kontroll."
        ),
    },
    {
        "id": "b2b-stress-02",
        "title": "Väder eller klimat – Kalibrera arbetsenergin",
        "category": "Stresshantering",
        "segment": "b2b",
        "levels": ["individ", "ledning", "foretag"],
        "duration": "15 min",
        "compass_key": "b2b_sustainable_energy",
        "mental_models": ["Energiflödesmodellen", "Väder vs Klimat", "Livshjulet"],
        "summary": "Skilj på en tillfällig intensiv vecka och ett långsiktigt mönster av energiläckage i arbetet.",
        "description": "Kartlägger vad som ger och tar energi i arbetsvardagen och identifierar den minsta hållbara justeringen för återhämtning.",
        "starter_prompt": (
            "Jag vill göra B2B-övningen 'Väder eller klimat – Kalibrera arbetsenergin'. "
            "Hjälp mig undersöka hur min energi utvecklats över tid och vad som tar mest kraft."
        ),
    },
    # --- EFFEKTIVISERING (2 kort) ---
    {
        "id": "b2b-eff-01",
        "title": "80/20-kompassen – Rätt saker före fler saker",
        "category": "Effektivisering",
        "segment": "b2b",
        "levels": ["individ", "ledning", "foretag"],
        "duration": "15 min",
        "compass_key": "b2b_self_leadership",
        "mental_models": ["80/20-principen", "Beslutskvadranten", "Kompassen"],
        "summary": "Identifiera de få insatser som skapar störst verkligt värde – och vad ni medvetet bör sluta lägga tid på.",
        "description": "Bryter aktivitetsfällan genom att skilja på hög sysselsättning och verklig effekt i linje med målen.",
        "starter_prompt": (
            "Jag vill göra B2B-övningen '80/20-kompassen – Rätt saker före fler saker'. "
            "Hjälp mig se vilka 20 procent av mitt arbete som skapar störst värde och vad som kan väljas bort."
        ),
    },
    {
        "id": "b2b-eff-02",
        "title": "Friktion och flöde i arbetsvardagen",
        "category": "Effektivisering",
        "segment": "b2b",
        "levels": ["individ", "ledning", "foretag"],
        "duration": "10 min",
        "compass_key": "b2b_direction_culture",
        "mental_models": ["Friktion och flöde", "Systemtänkande", "Små steg"],
        "summary": "Hitta återkommande flaskhalsar, avbrott och otydliga överlämningar – och designa ett enklare arbetssätt.",
        "description": "Fokuserar på system och vanor snarare än viljestyrka för att skapa lugnare och mer fokuserat arbete i teamet.",
        "starter_prompt": (
            "Jag vill göra B2B-övningen 'Friktion och flöde i arbetsvardagen'. "
            "Hjälp mig identifiera var det uppstår mest onödig friktion i vårt arbetssätt och hur vi kan förenkla."
        ),
    },
]

# ---------------------------------------------------------------------------
# 3. HJÄLPFUNKTIONER FÖR KOMPASSER, BIBLIOTEK & AGGREGERING
# ---------------------------------------------------------------------------

VALID_B2B_LEVELS = {"individ", "ledning", "foretag"}


def get_b2b_compasses() -> List[Dict[str, Any]]:
    """Returnerar de 4 B2B-kompasserna."""
    return [dict(c) for c in B2B_COMPASSES]


def get_b2b_exercise_cards(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Returnerar B2B-övningskorten, valfritt filtrerade på kategori."""
    if not category:
        _b2b_cards = [dict(_c) for _c in ([dict(card) for card in B2B_EXERCISE_CARDS])]
        for _c in _b2b_cards:
            _c.setdefault("prompt_trigger", _c.get("starter_prompt", ""))
            _c.setdefault("tag", _c.get("duration", ""))
        return _b2b_cards
    norm = category.strip().lower()
    _b2b_cards = [dict(_c) for _c in ([
        dict(card)
        for card in B2B_EXERCISE_CARDS
        if card.get("category", "").strip().lower() == norm
    ])]
    for _c in _b2b_cards:
        _c.setdefault("prompt_trigger", _c.get("starter_prompt", ""))
        _c.setdefault("tag", _c.get("duration", ""))
    return _b2b_cards


def aggregate_b2b_compass_data(
    records: List[Dict[str, Any]],
    k_min: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Aggregerar B2B-kompassvärden på grupp-/lednings-/företagsnivå.
    Strippar ALL individidentifierande data (user_id, email, name, råtext) ovillkorligen.
    Om k_min anges (t.ex. 5) och antal respondenter < k_min döljs numeriska snitt.
    """
    respondent_count = len(records)
    if k_min is not None and respondent_count < k_min:
        return {
            "respondent_count": respondent_count,
            "k_min": k_min,
            "k_suppressed": True,
            "compass_averages": {},
            "lowest_compass": None,
        }

    sums: Dict[str, float] = {}
    counts: Dict[str, int] = {}
    valid_keys = {c["key"] for c in B2B_COMPASSES}

    for rec in records:
        scores = rec.get("scores") if isinstance(rec.get("scores"), dict) else rec
        if not isinstance(scores, dict):
            continue
        for key in valid_keys:
            val = scores.get(key)
            if isinstance(val, (int, float)):
                sums[key] = sums.get(key, 0.0) + float(val)
                counts[key] = counts.get(key, 0) + 1

    averages: Dict[str, float] = {
        key: round(sums[key] / counts[key], 2)
        for key in sums
        if counts.get(key, 0) > 0
    }

    lowest_compass = min(averages, key=averages.get) if averages else None

    return {
        "respondent_count": respondent_count,
        "k_min": k_min,
        "k_suppressed": False,
        "compass_averages": averages,
        "lowest_compass": lowest_compass,
    }


def recommend_b2b_exercises(
    level: str = "individ",
    compass_scores: Optional[Dict[str, float]] = None,
    topic_hint: Optional[str] = None,
    limit: int = 2,
) -> List[Dict[str, Any]]:
    """
    Väljer ut mest relevanta B2B-övningar utifrån nivå (individ/ledning/foretag),
    lägsta kompassvärde och valfritt ämnesord.
    """
    norm_level = level.strip().lower() if level else "individ"
    if norm_level not in VALID_B2B_LEVELS:
        norm_level = "individ"

    candidates = [
        card for card in B2B_EXERCISE_CARDS
        if norm_level in card.get("levels", [])
    ]
    if not candidates:
        candidates = list(B2B_EXERCISE_CARDS)

    target_compass: Optional[str] = None
    if compass_scores:
        valid_scores = {
            k: v for k, v in compass_scores.items()
            if isinstance(v, (int, float))
        }
        if valid_scores:
            target_compass = min(valid_scores, key=valid_scores.get)

    hint_norm = topic_hint.strip().lower() if topic_hint else ""

    def _score_card(card: Dict[str, Any]) -> int:
        score = 0
        if target_compass and card.get("compass_key") == target_compass:
            score += 3
        if hint_norm:
            haystack = " ".join([
                card.get("title", ""),
                card.get("category", ""),
                card.get("summary", ""),
            ]).lower()
            if hint_norm in haystack:
                score += 4
        return score

    ranked = sorted(candidates, key=_score_card, reverse=True)
    return [dict(c) for c in ranked[:max(1, limit)]]


# ---------------------------------------------------------------------------
# 4. PROMPTLAGER FÖR FALK (INDIVID-, LEDNINGS- & FÖRETAGSNIVÅ)
# ---------------------------------------------------------------------------

def build_b2b_prompt_layer(
    b2b_context: Optional[Dict[str, Any]] = None,
    k_min: Optional[int] = None,
) -> str:
    """
    Bygger ett modulärt B2B-kontextlager för FALK enligt Wayjs filosofi:
    - Människan före prestationen, riktning före tempo, självständighet före beroende.
    - Aldrig managementspråk eller floskler; lugn, nyfiken mentor med fågelperspektiv.
    - Anpassar roll och inbjudan till nivå: individ, ledning eller foretag.
    """
    if not b2b_context:
        return ""

    raw_level = str(b2b_context.get("level") or "individ").strip().lower()
    level = raw_level if raw_level in VALID_B2B_LEVELS else "individ"

    org_name = str(b2b_context.get("org_name") or "").strip()
    role_title = str(b2b_context.get("role") or "").strip()
    topic_hint = str(b2b_context.get("topic_hint") or "").strip()

    # Hantera kompassdata säkert beroende på nivå
    compass_scores: Dict[str, float] = {}
    aggregation_note = ""

    if level == "individ":
        raw_scores = b2b_context.get("compass_scores") or {}
        if isinstance(raw_scores, dict):
            compass_scores = {
                k: float(v)
                for k, v in raw_scores.items()
                if isinstance(v, (int, float))
            }
    else:
        # På lednings- och företagsnivå används ENDAST aggregerad, anonymiserad data
        if isinstance(b2b_context.get("records"), list):
            agg = aggregate_b2b_compass_data(b2b_context["records"], k_min=k_min)
        else:
            agg = aggregate_b2b_compass_data([], k_min=k_min)
            if isinstance(b2b_context.get("compass_averages"), dict):
                count = int(b2b_context.get("respondent_count") or 0)
                if k_min is not None and count < k_min:
                    agg["k_suppressed"] = True
                else:
                    agg["k_suppressed"] = False
                    agg["compass_averages"] = {
                        k: float(v)
                        for k, v in b2b_context["compass_averages"].items()
                        if isinstance(v, (int, float))
                    }

        if agg.get("k_suppressed"):
            aggregation_note = (
                "Underlaget understiger konfigurerad anonymitetsgräns. "
                "Nämn inga exakta snittsiffror och spekulera aldrig kring enskilda individer."
            )
        else:
            compass_scores = agg.get("compass_averages", {})
            if compass_scores:
                aggregation_note = (
                    "Aggregerade B2B-kompassvärden (anonymiserat gruppunderlag, skala 1-10): "
                    + ", ".join(f"{k}={v}" for k, v in compass_scores.items())
                )

    recommended = recommend_b2b_exercises(
        level=level,
        compass_scores=compass_scores,
        topic_hint=topic_hint or None,
        limit=2,
    )

    compass_by_key = {c["key"]: c["title"] for c in B2B_COMPASSES}
    score_lines = [
        f"- {compass_by_key.get(k, k)}: {v}/10"
        for k, v in compass_scores.items()
    ]

    rec_lines = [
        f"- '{r['title']}' (Kategori: {r['category']}, {r['duration']}): {r['summary']}"
        for r in recommended
    ]

    if level == "individ":
        level_instructions = (
            "NIVÅ: INDIVID (Medarbetare / Ledare i organisation)\n"
            "- Möter individen i arbetsvardagen utan att tappa helheten (sambandet mellan arbete, energi, relationer och livsriktning).\n"
            "- Utforska först upplevelsen med öppna frågor innan du föreslår en övning.\n"
            "- När det passar naturligt i samtalet, bjud in till ett fördjupande reflektionssamtal eller föreslå 1 relevant övning ur Biblioteket."
        )
    elif level == "ledning":
        level_instructions = (
            "NIVÅ: LEDNING (Chef / Ledningsgrupp)\n"
            "- Anta fågelperspektivet över teamdynamik, mandat, psykologisk trygghet och hållbart ledarskap.\n"
            "- Skydda individsekretessen totalt: prata om mönster, struktur och kultur – aldrig om enskilda medarbetare som problem.\n"
            "- Bjud in till strukturerade ledningssamtal och föreslå konkreta B2B-övningar som ledningsgruppen eller chefen kan arbeta med."
        )
    else:
        level_instructions = (
            "NIVÅ: FÖRETAG (Organisation / HR / Kultur & Strategi)\n"
            "- Anta system- och fågelperspektivet över organisationens gemensamma kompass, värderingsförankring och hållbara prestation.\n"
            "- Skydda individsekretessen totalt: resonera på kultur-, struktur- och systemnivå.\n"
            "- Bjud in till strategisk dialog kring organisationsutveckling och föreslå lämpliga B2B-övningar för bred utrullning eller workshops."
        )

    parts = [
        "=== B2B KONTEXTLAGER (WAYJS WORKPLACE NAVIGATION) ===",
        "Grundhållning: Människan före prestationen. Riktning före tempo. Inget managementspråk eller floskler. Stärk självledarskap och eget omdöme.",
        level_instructions,
    ]

    if org_name:
        parts.append(f"Organisation: {org_name}")
    if role_title and level == "individ":
        parts.append(f"Användarens roll: {role_title}")
    if aggregation_note:
        parts.append(aggregation_note)
    if score_lines and level == "individ":
        parts.append("Aktuella B2B-kompassvärden (1-10):\n" + "\n".join(score_lines))
    if rec_lines:
        parts.append(
            "Relevanta B2B-övningar i Biblioteket att varsamt föreslå när användaren är mottaglig (max 1 åt gången, aldrig påtvingat):\n"
            + "\n".join(rec_lines)
        )

    return "\n\n".join(parts)
