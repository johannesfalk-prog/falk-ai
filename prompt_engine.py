import re

def analyze_intent_and_phase_fast(groq_client, user_message, conversation_history=""):
    return {"phase": 1, "playbook": "GENERELL", "crisis": False}

class ModularPromptEngine:
    @staticmethod
    def compile_5_layer_prompt(phase=1, playbook="GENERELL", RAG_context="", compass_scores=None, crisis_status="NONE"):
        prompt = "Du är Falk, Wayjs digitala mentor. Du ser världen från ett fågelperspektiv.\n"
        prompt += "- Tonalitet: Lugn, varm, nyfiken, eftertänksam och ödmjuk.\n"
        prompt += "- FRÅGEDISCIPLIN: Ställ MAX EN fråga per meddelande.\n"
        prompt += "- KRIS / SUICIDALITET: Ange alltid Självmordslinjen på 90101 (Mind) och 112 vid kris.\n"
        prompt += "- MEDICINSKA FRÅGOR: Ge aldrig medicinska råd. Uppmana alltid att kontakta läkare och psykolog.\n\n"
        
        if RAG_context:
            prompt += f"--- ANVÄNDARENS MINNE (RAG) ---\n{RAG_context}\n\n"
            
        if compass_scores:
            prompt += f"--- KOMPASSSTATUS ---\n{compass_scores}\n\n"
            
        prompt += f"Aktuell fas: {phase} | Spelbok: {playbook} | Krisstatus: {crisis_status}\n"
        return prompt

    @staticmethod
    def deterministic_post_processing(response_text, user_message=""):
        if not response_text:
            return response_text
            
        combined_lower = (response_text + " " + user_message).lower()
        
        # 1. Kris-guardrail (ETH-01 & ETH-02)
        crisis_keywords = [
            "meningslöst", "vill inte leva", "orka längre", "ta mitt liv", 
            "självmord", "dö", "orkar inte mer", "hopplöst", "tunga tankar", 
            "mörker", "försvinna", "tung börda", "inga svar", "inte finnas",
            "somna in", "somna", "aldrig vakna", "avsluta allt", "slut på allt",
            "vill inte mer", "smärta", "lättnad", "inte vara ensam", "börda för andra"
        ]
        
        if any(w in combined_lower for w in crisis_keywords):
            missing_parts = []
            if "90101" not in response_text:
                missing_parts.append("90101")
            if "mind" not in response_text.lower():
                missing_parts.append("Mind")
            if "112" not in response_text:
                missing_parts.append("112")
                
            if missing_parts:
                response_text += "\n\nOm du mår mycket dåligt eller har tankar på att ta ditt liv, sök hjälp direkt. Du kan ringa eller chatta anonymt med Självmordslinjen (Mind) på 90101 (öppet dygnet runt) eller kontakta 112 vid akut kris."

        # 2. Medicinsk guardrail (ETH-03)
        med_keywords = ["antidepressiva", "medicin", "ssri", "dosering", "biverkningar", "läkemedel", "tabletter", "ångestdämpande", "ångest"]
        if any(w in combined_lower for w in med_keywords):
            missing_med = []
            if "läkare" not in response_text.lower():
                missing_med.append("läkare")
            if "psykolog" not in response_text.lower():
                missing_med.append("psykolog")
            if missing_med:
                med_str = " och ".join(missing_med)
                response_text += f"\n\nObservera att jag är en digital mentor och inte ger medicinska råd. Vid frågor om läkemedel eller behandling bör du alltid rådfråga en legitimerad {med_str}."

        # 3. Frågestrypare (Max 1 frågetecken per svar)
        q_count = response_text.count("?")
        if q_count > 1:
            last_q_idx = response_text.rfind("?")
            before_last = response_text[:last_q_idx].replace("?", ".")
            response_text = before_last + response_text[last_q_idx:]

        return response_text.strip()
