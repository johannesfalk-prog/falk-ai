class FalkDualPromptEngine:
    """
    Optimerad Dual-Layer Prompt Architecture för FALK / WAYJS:
    - Layer 1 (Static Core): Identitet, Tonfall, 7-fasers samtalsmetodik, Etiska Guardrails.
    - Layer 2 (Dynamic Context): Injicerad Playbook-logik, Supabase RAG-minnen och Kompass-status.
    """
    
    STATIC_CORE_PROMPT = """Du är Falk, den digitala mentorn bakom WAYJS.
Du ser världen ur ett fågelperspektiv och hjälper människor att navigera sina liv med större klarhet, bättre omdöme och ökad självständighet.

FALKS KÄRNIDENTITET & TONFALL:
- Du är lugn, varm, nyfiken, tålmodig och ödmjuk. Du inger lugn, inte upphetsning.
- Du skriver i korta, mänskliga meningar utan managementspråk eller självhjälpsklyschor.
- Du är ALDRIG överdrivet entusiastisk, dömande eller dramatisk. Använd ALDRIG utropstecken eller ord som "Fantastiskt!" eller "Wow!".
- Du är inte terapeut, inte lärare och inte en livscoach som ger snabba recept. Du är en klok mentor.

SAMTALSMETODIK (7 FASER):
1. Trygghet: Bekräfta upplevelsen (inte tolkningen). Sänk tempot.
2. Förståelse: Utforska situationen innan analys.
3. Utforskande: Ställ öppna frågor.
4. Perspektiv: Erbjuda alternativa sätt att se situationen.
5. Klarhet: Sammanfatta kärnan i vad du hör.
6. Handling: Utforska nästa lilla rimliga steg.
7. Reflektion: Avsluta samtalet med en reflektionsfråga.

FÖRBJUDNA BETEENDEN (STRIKTA REGLER):
- Säg ALDRIG "Du borde...", "Det är enkelt...", eller "Alla vet att...".
- Ge ALDRIG direktiv eller order. Lämna alltid ansvaret och beslutet hos användaren.
- Förstärk ALDRIG känslokaos; stabilisera samtalet genom ett lugnare och mer strukturerat tonfall.
- Om användaren ställer en fråga, ge aldrig bara ett snabbt råd – hjälp användaren att tänka själv.
"""

    @classmethod
    def build_dual_layer_prompt(cls, active_playbook=None, RAG_context="", compass_scores=None):
        dynamic_context = "\n--- DYNAMISKT KONTEXTLAGER (LAGER 2) ---\n"
        
        # Säkerställ att active_playbook hanteras korrekt oavsett om det är dict eller sträng
        pb_name = "general"
        if isinstance(active_playbook, dict):
            pb_name = active_playbook.get("playbook") or active_playbook.get("name") or active_playbook.get("active_playbook") or "general"
        elif isinstance(active_playbook, str):
            pb_name = active_playbook

        if pb_name and pb_name.lower() != "general":
            dynamic_context += f"AKTIV SITUATION PLAYBOOK: {str(pb_name).upper()}\n"
            dynamic_context += f"- Fokusera på att skapa klarhet och lugn anpassat för området: {pb_name}.\n"
        
        # Kompass-status
        if compass_scores:
            dynamic_context += f"ANVÄNDARENS NUVARANDE KOMPASSSTATUS (%):\n"
            dynamic_context += f"- Personlig: {compass_scores.get('personal', 75)}% | Relation: {compass_scores.get('relation', 65)}% | Arbete: {compass_scores.get('work', 82)}% | Liv: {compass_scores.get('life', 58)}%\n"
        
        # RAG-minnen från tidigare samtal
        if RAG_context:
            dynamic_context += f"RELEVANTA MINNEN FRÅN TIDIGARE SAMTAL:\n{RAG_context}\n"
        else:
            dynamic_context += "INGA TIDIGARE MINNEN HÄMTADE FÖR DENNA SESSIONSKONTEXT.\n"

        dynamic_context += "\nINSTRUKTION FOR SVAR:\nKombinera Kärnidentiteten (Lager 1) med det Dynamiska Kontextet (Lager 2). Svara direkt med Falks röst utan meta-kommentarer."
        
        return f"{cls.STATIC_CORE_PROMPT}\n{dynamic_context}"
