from typing import List, Dict, Any, Optional

FALK_15_EXERCISE_CARDS: List[Dict[str, Any]] = [
    {
        "id": "card_01",
        "title": "Kontrollcirkeln",
        "category": "Personlig",
        "tag": "Självledarskap",
        "description": "Identifiera vad du kan kontrollera, vad du kan påverka och vad du måste acceptera.",
        "prompt_trigger": "Jag vill använda Kontrollcirkeln för att sortera vad som ligger inom min kontroll i min nuvarande situation."
    },
    {
        "id": "card_02",
        "title": "Isberget",
        "category": "Personlig",
        "tag": "Självinsikt",
        "description": "Utforska tankar, känslor och behov som ligger under ytan av ditt symptom.",
        "prompt_trigger": "Hjälp mig använda Isbergsmodellen för att förstå vad som ligger under ytan på det jag känner."
    },
    {
        "id": "card_03",
        "title": "Fågelperspektivet",
        "category": "Liv",
        "tag": "Reflektion",
        "description": "Höj dig över bruset och betrakta ditt liv ur ett helhetsperspektiv.",
        "prompt_trigger": "Jag behöver ett Fågelperspektiv. Hjälp mig att zooma ut från min nuvarande situation."
    },
    {
        "id": "card_04",
        "title": "Hitta din Nordstjärna",
        "category": "Personlig",
        "tag": "Värderingar",
        "description": "Klargör dina tre mest grundläggande värderingar inför ett svårt beslut.",
        "prompt_trigger": "Jag vill förstå min Nordstjärna och vilka värderingar som ska vägleda mitt nästa beslut."
    },
    {
        "id": "card_05",
        "title": "Ringar på Vattnet",
        "category": "Relation",
        "tag": "Konsekvenser",
        "description": "Analysera hur dina beslut påverkar partner, familj och omgivning.",
        "prompt_trigger": "Hjälp mig analysera vilka ringar på vattnet mitt beslut skapar för mina nära relationer."
    },
    {
        "id": "card_06",
        "title": "Horisontmodellen",
        "category": "Arbete",
        "tag": "Framtid",
        "description": "Utvärdera ditt val ur ett 3-månaders, 1-års och 5-årsperspektiv.",
        "prompt_trigger": "Jag vill utvärdera mitt vägval genom Horisontmodellen: 3 månader, 1 år och 5 år framåt."
    },
    {
        "id": "card_07",
        "title": "80/20-Principen för Energi",
        "category": "Arbete",
        "tag": "Prioritering",
        "description": "Identifiera de 20% av dina aktiviteter som ger 80% av din återhämtning.",
        "prompt_trigger": "Hjälp mig hitta de 20% av mina vanor som ger 80% av min kompassenergi."
    },
    {
        "id": "card_08",
        "title": "Energiflödeskartan",
        "category": "Liv",
        "tag": "Balans",
        "description": "Kartlägg vad som dränerar din energi respektive vad som fyller på den.",
        "prompt_trigger": "Jag vill göra en Energiflödeskarta för att sortera vad som dränerar vs ger mig kraft."
    },
    {
        "id": "card_09",
        "title": "Identitetsmodellen",
        "category": "Personlig",
        "tag": "Utveckling",
        "description": "Skifta fokus från vad du vill uppnå till vem du vill bli.",
        "prompt_trigger": "Hjälp mig utforska vilken identitet och person mina nuvarande handlingar bygger."
    },
    {
        "id": "card_10",
        "title": "Perspektivtriangeln",
        "category": "Relation",
        "tag": "Kommunikation",
        "description": "Se en pågående konflikt från ditt, motpartens och en neutral betraktares perspektiv.",
        "prompt_trigger": "Jag har en konflikt och vill analysera den via Perspektivtriangeln."
    },
    {
        "id": "card_11",
        "title": "Inre Klimat vs Väder",
        "category": "Personlig",
        "tag": "Resiliens",
        "description": "Skilj på tillfälliga emotionella stormar (väder) och din långsiktiga riktning (klimat).",
        "prompt_trigger": "Hjälp mig förstå om det jag upplever nu är tillfälligt väder eller mitt långsiktiga inre klimat."
    },
    {
        "id": "card_12",
        "title": "Mikromod",
        "category": "Liv",
        "tag": "Handling",
        "description": "Identifiera den minsta obekväma handlingen som tar dig ett steg framåt idag.",
        "prompt_trigger": "Jag vill identifiera en konkret Mikromod som jag kan genomföra inom 24 timmar."
    },
    {
        "id": "card_13",
        "title": "Kompasskalibrering",
        "category": "Arbete",
        "tag": "Mål",
        "description": "Stanna upp och justera din livskurs utifrån ditt nuvarande stämningsläge.",
        "prompt_trigger": "Jag behöver göra en Kompasskalibrering för att se om min nuvarande kurs fortfarande stämmer."
    },
    {
        "id": "card_14",
        "title": "Friktion & Flöde",
        "category": "Arbete",
        "tag": "Vanor",
        "description": "Ta bort hinder för bra vanor och lägg till friktion för godtyckliga snedsteg.",
        "prompt_trigger": "Hjälp mig designa min miljö så att mina goda vanor får lägre friktion."
    },
    {
        "id": "card_15",
        "title": "De Tre Speglarna",
        "category": "Liv",
        "tag": "Reflektion",
        "description": "Granska ditt dilemma genom Nuet, Historien och Framtiden.",
        "prompt_trigger": "Jag vill spegla min nuvarande utmaning genom De Tre Speglarna: Nuet, Historien och Framtiden."
    }
]

def get_library_cards(category: Optional[str] = None) -> List[Dict[str, Any]]:
    if not category or category.lower() == "alla":
        return FALK_15_EXERCISE_CARDS
    return [c for c in FALK_15_EXERCISE_CARDS if c["category"].lower() == category.lower()]
