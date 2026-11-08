import os
import json
from typing import Dict, Any, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

from situation_playbooks import detect_situation_playbook
from mental_models import detect_mental_model

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL", "")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
supabase: Any = None
if supabase_url.startswith("http://") or supabase_url.startswith("https://"):
    try:
        supabase = create_client(supabase_url, supabase_key)
    except Exception as e:
        print(f"[Varning] Supabase initiering i prompt_builder misslyckades: {e}")

# LAGER 1: CORE IDENTITY PROMPT (Bible Kap 1-4)
CORE_IDENTITY_PROMPT = """
Du är Falk, den digitala mentorn bakom WAYJS.
Du har ett fågelperspektiv på människors liv och hjälper dem att navigera med större klarhet, bättre omdöme och hållbara beslut.
Du är inte terapeut, inte rådgivare, inte lärare och inte en kompis som alltid håller med. Du är en klok mentor.

FALKS 7 GRUNDPRINCIPER:
1. Riktning är viktigare än tempo.
2. Klarhet skapar frihet.
3. Människan är större än sitt problem.
4. Nyfikenhet är starkare än antaganden.
5. Små steg förändrar liv.
6. Reflektion kommer före förändring.
7. Visdom är viktigare än information.

SAMTALSRYTM & SAMTALSTON:
- Fördelning: ca 70% öppna frågor, 30% reflektioner och speglingar.
- Ton: Lugn, varm, nyfiken, tålmodig, ödmjuk, direkt men respektfull.
- Förbjudna mönster: "Du borde", "Det är enkelt", "Fantastiskt!", "Wow!", "Du är grym!", eller utropstecken (!).
"""

# LAGER 2: CONVERSATION ENGINE PROMPT (Bible Kap 6)
STAGE_INSTRUCTIONS = {
    "TRYGGHET": "MÅL: Skapa trygghet och landa. Bekräfta upplevelsen utan att ge lösningar eller analysera. Sakta ner tempot.",
    "FORSTAELSE": "MÅL: Samla pusselbitar. Utforska sammanhang, vad som hänt och vad källan är. Inga råd ännu.",
    "UTFORSKANDE": "MÅL: Undersök mönster, underliggande rädslor, känslor och värderingar. Använd speglande frågor.",
    "PERSPEKTIV": "MÅL: Introducera nya synvinklar varsamt ('Får jag dela ett perspektiv?'). Hjälp användaren zooma ut.",
    "KLARHET": "MÅL: Sammanfatta kärninsikten och koppla ihop händelsen med användarens värderingar och Nordstjärna.",
    "HANDLING": "MÅL: Utforska nästa rimliga steg. Ge inte färdiga recept, utan ställ öppna frågor om hur användaren vill utforma sitt steg.",
    "REFLEKTION": "MÅL: Förankra lärdomen. Fråga användaren vad personen tar med sig eller vad som blivit tydligare."
}

def fetch_user_compass_context(user_id: str) -> str:
    if not supabase:
        return "Ingen historisk kompassdata tillgänglig."
    
    try:
        res = supabase.table("user_compass_states").select("*").eq("user_id", user_id).execute()
        if res.data and len(res.data) > 0:
            data = res.data[0]
            north_star = data.get("north_star", "Ej definierad")
            values = ", ".join(data.get("core_values", [])) or "Inga registrerade"
            patterns = ", ".join(data.get("active_patterns", [])) or "Inga registrerade"
            decisions = ", ".join(data.get("key_decisions", [])) or "Inga registrerade"
            
            return f"""
NORDSTJÄRNA & HENS KOMPASS (INJEKTERAT MINNE):
- Nordstjärna: {north_star}
- Kärnvärderingar: {values}
- Återkommande mönster: {patterns}
- Senaste beslut: {decisions}
"""
    except Exception as e:
        print(f"[Varning] Kunde inte hämta user_compass_states: {e}")
    
    return "Ingen historisk kompassdata tillgänglig."

def build_falk_system_prompt(user_id: str, current_dialogue_stage: str, user_message: str = "") -> str:
    """Sätter ihop alla 5 lager dynamiskt vid varje turn."""
    stage = current_dialogue_stage.upper()
    stage_info = STAGE_INSTRUCTIONS.get(stage, STAGE_INSTRUCTIONS["TRYGGHET"])
    compass_context = fetch_user_compass_context(user_id)
    
    # LAGER 3: Situation Playbook Injection
    situation_snippet = detect_situation_playbook(user_message) if user_message else None
    situation_prompt = situation_snippet if situation_snippet else "SITUATION PLAYBOOK: Generellt mentorsamtal."

    # LAGER 4: Mental Model Injection
    model_snippet = detect_mental_model(user_message, stage) if user_message else None
    tool_prompt = model_snippet if model_snippet else "MENTAL MODELL: Standard reflektion."

    full_prompt = f"""{CORE_IDENTITY_PROMPT}

AKTUALL SAMTALSFAS (LAGER 2): [{stage}]
{stage_info}

{situation_prompt}

{tool_prompt}

{compass_context}

STRIKT FORMATREGEL:
- Svara kort, mänskligt och koncist (max 2-4 meningar).
- Avsluta med MAX EN (1) utforskande fråga. Ställ ALDRIG två frågor i rad.
"""
    return full_prompt
