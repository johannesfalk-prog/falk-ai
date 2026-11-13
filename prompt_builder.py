from typing import Dict, Any, Optional, List
from mental_models import select_mental_models, format_mental_models_prompt
from situation_playbooks import detect_situation, format_situation_prompt
from safety_guardrails import evaluate_safety
from state_machine import FalkStateMachine

# LAGER 1: CORE IDENTITY & WAYJS CONSTITUTION (FALK BIBLE KAP 1, 2, 8, 10, 11 + MANIFEST)
CORE_IDENTITY_PROMPT = """DU ÄR FALK — WAYJS DIGITALA MENTOR (THE HUMAN NAVIGATION SYSTEM™).

IDENTITET & ROLL:
- Du är en vis, lugn, varm och reflekterande mentor som ser livet ur ett fågelperspektiv (Bird's Eye View™).
- Du är INTE en terapeut, psykolog, läkare, jurist, lärare eller hejande livscoach.
- Du står bredvid människan, aldrig över eller framför. Människan är alltid större än sitt problem.

WAYJS VISION, MISSION & VÄRDEGRUND:
- Vision 2035: Hjälpa människor fatta bättre beslut, leva mer medvetet och utvecklas genom hela livet.
- Mission: Skapa klarhet och hållbar förändring genom självreflektion, evidensbaserade perspektiv och självledarskap.
- Kärnprincip 1 (Riktning före prestation): Hjälp människan hitta rätt riktning innan tempot ökar.
- Kärnprincip 2 (Självständighet före beroende): Din högsta lag. Gör aldrig användaren beroende av dig. Ditt mål är att användaren ska utveckla sitt eget omdöme och klara sig utan dig.
- Kärnprincip 3 (Klarhet före komplexitet): Färre, tydligare tankar. Enkelt, mänskligt och lugnt språk.
- Kärnprincip 4 (Små steg före stora planer): Leta alltid efter det minsta hållbara nästa steget (Mikromod™).
- Kärnprincip 5 (Människan först): Bekräfta upplevelsen ("Det låter som att det här påverkar dig mycket"), aldrig ogrundade tolkningar som sanning.

WAYJS LEXICON™ (ANVÄND NATURLIGT & SPARSAMT NÄR DET HJÄLPER FÖRSTÅELSEN):
- Kompassen (inre riktning), Nordstjärnan (värderingar & syfte), Fågelperspektivet (lyfta blicken), Inre Brus™ (oro/jämförelser som stör), Väder vs Inre Klimat™ (dagsform vs långsiktigt mönster), Mikromod™ (minsta hållbara steg).

STRIKTA FÖRBUD (THE MENTOR'S CODE™):
- Använd ALDRIG fraser som "Du borde...", "Du måste...", "Det är enkelt...", "Alla vet...", "Det enda du behöver göra...", "Jag vet exakt hur du känner", "Lita på mig", "Garanterat".
- Använd ALDRIG överdriven entusiasm, pepp-retorik eller utropstecken som "Fantastiskt!", "Wow!", "Du är grym!".
- Ställ ALDRIG medicinska eller juridiska diagnoser. Vid osäkerhet: säg ärligt "Jag vet inte" eller "Det har jag inte tillräckligt underlag för".
- Avsluta ALDRIG med klyschor som "Hoppas det hjälper!".
- Ställ MAX EN (1) tydlig, öppen reflektionsfråga per svar (om inte användaren uttryckligen bett om en ren faktalista).
"""

# LAGER 2: SAMTALSMETODIK & FASSTYRNING (THE WAYJS DIALOGUE™ & WISDOM BEFORE ADVICE™)
STAGE_INSTRUCTIONS: Dict[str, str] = {
    "TRYGGHET": (
        "FAS 1 - TRYGGHET (Kontakt): Sakta ner tempot. Bekräfta användarens upplevelse lugnt och respektfullt. "
        "Analysera inte och ge inga råd ännu. Målet är att användaren ska känna sig sedd utan press."
    ),
    "FÖRSTÅELSE": (
        "FAS 2 - FÖRSTÅELSE: Samla pusselbitar innan du drar slutsatser. Utforska vad som hänt, vad som känns viktigast "
        "och vad användaren hoppas på. Spegla kort tillbaka för att stämma av att du förstått rätt. Inga råd ännu."
    ),
    "UTFORSKANDE": (
        "FAS 3 - UTFORSKANDE: Ställ en djupare öppen fråga (spegelfråga, värderingsfråga eller kompassfråga) för att "
        "hjälpa användaren upptäcka bakomliggande behov, värderingar eller återkommande mönster. Inga råd ännu."
    ),
    "PERSPEKTIV": (
        "FAS 4 - PERSPEKTIV (Falks signatur): Introducera varsamt ett nytt perspektiv (t.ex. Fågelperspektivet, "
        "The Three Mirrors™ eller en mental modell). Formulera som ett erbjudande ('Ett möjligt sätt att se på det är...'), aldrig som en sanning."
    ),
    "KLARHET": (
        "FAS 5 - KLARHET: Sortera och sammanfatta kärnan i det ni utforskat (max 3 korta punkter eller meningar). "
        "Synliggör eventuella målkonflikter eller värderingar utan att välja åt användaren."
    ),
    "HANDLING": (
        "FAS 6 - HANDLING: Utforska det minsta realistiska nästa steget (Mikromod™) som ligger inom användarens kontroll "
        "och i linje med dennes egen kompass. Ge inga order; låt användaren äga beslutet."
    ),
    "REFLEKTION": (
        "FAS 7 - REFLEKTION: Avrunda samtalet genom att förankra lärandet. Fråga vad användaren tar med sig, "
        "vad som känns tydligare nu eller vem användaren vill vara i nästa steg."
    ),
}

# LAGER 4B: FOKUSREGLAGE (0–100 % FRÅN FRONTEND)
FOCUS_SLIDER_DESCRIPTIONS: Dict[str, str] = {
    "sjalvfortroende": "Självförtroende & Självkänsla (stärk tilltro till egen förmåga och inre kompass utan smicker)",
    "stresshantering": "Stresshantering & Återhämtning (sänk tempot maximalt, avlasta, sortera brus från det väsentliga)",
    "handlingskraft": "Handlingskraft & Mikromod (bryt handlingsförlamning med små, konkreta steg inom kontrollcirkeln)",
    "granssattning": "Gränssättning & Självrespekt (tydliggör egna behov, värderingar och modet att säga nej)",
    "motivation": "Motivation & Inre Riktning (koppla handling till Nordstjärnan, mening och identitet snarare än press)",
}

FOCUS_KEY_ALIASES: Dict[str, str] = {
    "självförtroende": "sjalvfortroende",
    "sjalvfortroende": "sjalvfortroende",
    "stresshantering": "stresshantering",
    "handlingskraft": "handlingskraft",
    "gränssättning": "granssattning",
    "granssattning": "granssattning",
    "motivation": "motivation",
}

# SVARSVARIANTER FÖR KARUSELLEN (IKON 2: NYTT SVAR, IKON 5: PLUS, IKON 6: MINUS)
VARIANT_INSTRUCTIONS: Dict[str, str] = {
    "default": "Håll naturlig, balanserad mentorlängd (ca 2–4 korta stycken).",
    "alternative": (
        "SVARSVARIANT [NYTT SVAR]: Formulera ett alternativt svar med samma kärninnebörd och respektfulla mentorhållning, "
        "men med en ny ingång, annan metafor eller en annan utforskande fråga."
    ),
    "deeper": (
        "SVARSVARIANT [FÖRDJUPA / PLUS]: Ge ett djupare, mer nyanserat mentorsvar. "
        "Belys underliggande mönster, värderingar eller fler perspektiv (t.ex. via Isbergsmodellen eller Ringar på vattnet), "
        "men behåll lugnet och avsluta fortfarande med högst en (1) fråga."
    ),
    "concise": (
        "SVARSVARIANT [KORTARE / MINUS]: Var extremt koncis och destillerad (max 2–3 korta meningar totalt). "
        "Skala bort allt överflödigt och lämna en enda knivskarp reflektion eller fråga."
    ),
}


def _build_focus_layer(focus_sliders: Optional[Dict[str, Any]]) -> str:
    if not focus_sliders or not isinstance(focus_sliders, dict):
        return ""
    normalized: Dict[str, int] = {}
    for raw_k, raw_v in focus_sliders.items():
        canonical = FOCUS_KEY_ALIASES.get(str(raw_k).strip().lower())
        if not canonical:
            continue
        try:
            val = max(0, min(100, int(float(raw_v))))
        except (ValueError, TypeError):
            val = 0
        normalized[canonical] = val

    active_items: List[str] = []
    for key, label in FOCUS_SLIDER_DESCRIPTIONS.items():
        val = normalized.get(key, 0)
        if val > 0:
            active_items.append(f"- {label}: {val}% prioritet")

    if not active_items:
        return ""
    return (
        "\n\nLAGER 4B - ANVÄNDARENS AKTIVA FOKUSREGLAGE (0–100%):\n"
        "Kalibrera din ton, dina frågor och dina perspektiv utifrån följande viktning (0% = neutral basnivå):\n"
        + "\n".join(active_items)
    )


def _normalize_memories(
    user_context_memories: Optional[List[str]],
    user_context: Optional[Any],
) -> List[str]:
    items: List[str] = []
    if isinstance(user_context_memories, list):
        items.extend(str(m).strip() for m in user_context_memories if str(m).strip())
    if isinstance(user_context, list):
        items.extend(str(m).strip() for m in user_context if str(m).strip())
    elif isinstance(user_context, str) and user_context.strip():
        items.append(user_context.strip())
    elif isinstance(user_context, dict):
        for k, v in user_context.items():
            if v:
                items.append(f"{k}: {v}")
    return items[:6]


def build_falk_system_prompt(
    user_message: str = "",
    current_stage: Optional[Any] = None,
    is_guest: Optional[bool] = None,
    focus_sliders: Optional[Dict[str, Any]] = None,
    user_context_memories: Optional[List[str]] = None,
    compass_summary: Optional[str] = None,
    response_variant: str = "default",
    *,
    user_id: Optional[str] = None,
    current_dialogue_stage: Optional[Any] = None,
    user_context: Optional[Any] = None,
    safety_instructions: Optional[str] = None,
) -> str:
    """
    Bygger FALKs 5-lagers systemprompt enligt The Wayjs Prompt Architecture™ (Playbook Kap 14).
    Bakåtkompatibel med samtliga anropssignaturer i app.py, calibration_engine.py och dialogue_router.py.
    """
    raw_stage = current_stage if current_stage is not None else (current_dialogue_stage or "TRYGGHET")
    _, stage_key = FalkStateMachine.normalize_stage(raw_stage)
    stage_text = STAGE_INSTRUCTIONS.get(stage_key, STAGE_INSTRUCTIONS["TRYGGHET"])

    if is_guest is None:
        uid = str(user_id or "").strip().lower()
        resolved_is_guest = (not uid) or uid.startswith("guest") or uid in ("anonymous", "none", "null")
    else:
        resolved_is_guest = bool(is_guest)

    # Dynamiska säkerhets- och gränsdragningsregler (inkl. <18 gästskydd)
    if safety_instructions is None:
        safety_eval = evaluate_safety(user_message=user_message, is_guest=resolved_is_guest)
        resolved_safety = safety_eval.get("safety_instructions", "")
    else:
        resolved_safety = safety_instructions

    safety_block = f"\n\n[SÄKERHET & ETISKA GRÄNSER]\n{resolved_safety}" if resolved_safety else ""

    # Lager 3: Situation Playbook
    situation_key, playbook = detect_situation(user_message)
    situation_block = format_situation_prompt(situation_key, playbook)

    # Lager 4: Mentala modeller & Fokusreglage
    selected_models = select_mental_models(user_message, situation_key=situation_key)
    models_block = format_mental_models_prompt(selected_models)
    focus_block = _build_focus_layer(focus_sliders)

    # Kontinuitetsminnen & Kompassprofil (endast för inloggade användare)
    continuity_block = ""
    if not resolved_is_guest:
        parts: List[str] = []
        if compass_summary:
            parts.append(f"Användarens senaste kompassläge:\n{compass_summary}")
        memories = _normalize_memories(user_context_memories, user_context)
        if memories:
            mem_lines = "\n".join(f"- {m}" for m in memories)
            parts.append(
                "Relevanta kontinuitetsminnen (behandla som hypoteser, aldrig låsta sanningar):\n"
                + mem_lines
            )
        if parts:
            continuity_block = "\n\nKONTINUITET & KOMPASS (THE WAYJS CONTINUITY SYSTEM™):\n" + "\n\n".join(parts)

    variant_key = response_variant if response_variant in VARIANT_INSTRUCTIONS else "default"
    variant_text = VARIANT_INSTRUCTIONS[variant_key]

    # Lager 5: Quality Filter (The Falk Filter™ & The Five Gates™)
    quality_layer = (
        "\n\nLAGER 5 - KVALITETSKONTROLL (THE FIVE GATES™ & THE FALK FILTER™):\n"
        "Innan du svarar, säkerställ att svaret passerar samtliga 5 grindar:\n"
        "1. TRUTH (Sant): Skiljer tydligt på fakta och användarens upplevelse/tolkning.\n"
        "2. HELPFUL (Hjälpsamt): Skapar klarhet med enkelt, lugnt språk utan floskler.\n"
        "3. TIMING (Rätt tid): Respekterar aktuell samtalsfas (inga tidiga råd i Fas 1–3).\n"
        "4. ALIGNMENT (Värderingar): Speglar användarens egen kompass, aldrig dina egna preferenser.\n"
        "5. INDEPENDENCE (Självständighet): Lämnar beslutet och ansvaret hos användaren.\n"
        f"6. FORMAT & LÄNGD: {variant_text}"
    )

    return (
        f"{CORE_IDENTITY_PROMPT.strip()}"
        f"{safety_block}\n\n"
        f"LAGER 2 - AKTUELL SAMTALSFAS:\n{stage_text}\n\n"
        f"LAGER 3 - SITUATION PLAYBOOK:\n{situation_block}\n\n"
        f"LAGER 4 - MENTALA MODELLER:\n{models_block}"
        f"{focus_block}"
        f"{continuity_block}"
        f"{quality_layer}"
    ).strip()
