from __future__ import annotations
from typing import Any, Dict, List
from datetime import date
import math

PLANET_WEIGHTS = {
    "pluto": 2.0,
    "uranus": 1.8,
    "saturn": 1.7,
    "jupiter": 1.4,
    "mars": 1.3,
    "sun": 1.1,
    "moon": 1.1,
    "venus": 1.1,
    "mercury": 1.0,
    "neptune": 1.5,
}

ASPECT_TYPE_WEIGHTS = {
    "conjunction": 1.2,
    "opposition": 1.3,
    "square": 1.4,
    "trine": 1.0,
    "sextile": 0.9,
}

HOUSE_PERSON_MAP = {
    3: ("Alguém do cotidiano", "Troca e comunicação"),
    4: ("Familiar ou pessoa da base", "Segurança emocional"),
    5: ("Interesse romântico ou criativo", "Prazer e expressão"),
    6: ("Colega ou pessoa da rotina", "Trabalho diário"),
    7: ("Parceiro(a) ou relação direta", "Vínculo importante"),
    10: ("Chefe ou figura de autoridade", "Carreira e status"),
}

PLANET_DYNAMIC_MAP = {
    "mars": ("Testa", "Conflito e tensão"),
    "venus": ("Aproxima", "Vínculo e atração"),
    "saturno": ("Define", "Cobrança e distância"),
    "uranus": ("Redefine", "Ruptura e surpresa"),
    "pluto": ("Redefine", "Intensidade e transformação"),
}

def rank_events(events: List[Dict[str, Any]], reference_date: date) -> Dict[str, Any]:
    if not events:
        return {"dominant": None, "secondary": None, "all_ranked": []}

    ranked_events = []
    for event in events:
        base_score = float(event.get("probability", 0.5)) * 10.0

        max_planet_weight = 1.0
        max_aspect_weight = 1.0
        for driver in event.get("drivers", []):
            evidence = driver.get("evidence", {})
            p_a = str(evidence.get("planet_a", "")).lower()
            p_b = str(evidence.get("planet_b", "")).lower()
            max_planet_weight = max(max_planet_weight, PLANET_WEIGHTS.get(p_a, 1.0), PLANET_WEIGHTS.get(p_b, 1.0))

            aspect = str(evidence.get("aspect", "")).lower()
            max_aspect_weight = max(max_aspect_weight, ASPECT_TYPE_WEIGHTS.get(aspect, 1.0))

        time_window = event.get("time_window", {})
        proximity_factor = 1.0
        peak_str = time_window.get("peak")
        if peak_str:
            try:
                peak_date = date.fromisoformat(peak_str)
                days_to_peak = abs((peak_date - reference_date).days)
                proximity_factor = 1.5 * math.exp(-days_to_peak / 60.0)
            except (ValueError, TypeError):
                pass

        activation_count = len(event.get("signals", []))
        activation_factor = 1.0 + (activation_count * 0.1)

        final_score = (base_score * max_planet_weight * max_aspect_weight * proximity_factor * activation_factor)
        event["decision_score"] = round(final_score, 2)
        ranked_events.append(event)

    ranked_events.sort(key=lambda x: x["decision_score"], reverse=True)
    dominant = ranked_events[0]
    secondary = ranked_events[1] if len(ranked_events) > 1 else None

    return {
        "dominant": dominant,
        "secondary": secondary,
        "all_ranked": ranked_events
    }

def identify_involved_person(event: Dict[str, Any]) -> Dict[str, Any]:
    person_type = "Pessoa do círculo próximo"
    role = "Influência no momento"
    dynamic = "Define o tom"
    impact = "Moderado"

    drivers = sorted(event.get("drivers", []), key=lambda x: float(x.get("weight", 0)), reverse=True)
    if not drivers:
        return {"type": person_type, "role": role, "dynamic": dynamic, "impact": impact}

    best_driver = drivers[0]
    evidence = best_driver.get("evidence", {})

    # Try to find house
    house = evidence.get("house")
    if house is None:
        # Fallback to domain mapping if house not directly in evidence
        domain_to_house = {
            "relacionamentos": 7,
            "carreira_status": 10,
            "familia_lar": 4,
            "amigos_rede": 11,
            "saude_rotina": 6,
            "comunicacao": 3,
            "criatividade_afetos": 5,
        }
        house = domain_to_house.get(event.get("category", ""))

    if house in HOUSE_PERSON_MAP:
        person_type, role = HOUSE_PERSON_MAP[house]
    elif house == 11:
        person_type, role = "Amigo ou grupo social", "Troca e ideais"

    # Refine dynamic based on planet_a (the triggering planet)
    p_a = str(evidence.get("planet_a", "")).lower()
    if p_a in PLANET_DYNAMIC_MAP:
        dyn_label, dyn_desc = PLANET_DYNAMIC_MAP[p_a]
        dynamic = f"{dyn_label} ({dyn_desc.split(' ')[0].lower()})"

    # Impact Level
    intensity = event.get("intensity", "low")
    impact_map = {
        "low": "Leve",
        "medium": "Moderado",
        "high": "Alto",
        "extreme": "Decisivo",
    }
    impact = impact_map.get(intensity, "Moderado")

    return {
        "type": person_type,
        "role": role,
        "dynamic": dynamic,
        "impact": impact
    }

def calculate_scores(all_ranked_events: List[Dict[str, Any]], reference_date: date) -> Dict[str, float]:
    """
    Calculates 0-10 scores for Amor, Carreira, Dinheiro, e Saúde.
    Score = Base(5) + (Pico Ponderado).
    """
    categories = {
        "amor": ["relacionamentos", "criatividade_afetos"],
        "carreira": ["carreira_status"],
        "dinheiro": ["financeiro", "crises_recursos"],
        "saude": ["saude_rotina"]
    }

    final_scores = {}

    for label, domains in categories.items():
        # Filter events for these domains
        relevant_events = [e for e in all_ranked_events if e.get("category") in domains]

        if not relevant_events:
            final_scores[label] = 5.0 # Neutral
            continue

        # Find the most intense event (highest decision_score)
        # This aligns with the "Pico Ponderado" rule
        top_event = max(relevant_events, key=lambda x: x["decision_score"])

        # Calculate score based on tone and intensity
        # probability is 0-1
        prob = float(top_event.get("probability", 0.5))
        tone = str(top_event.get("tone", "mixed"))

        # Base score 5.0
        # Supportive moves it towards 10, Challenging towards 0
        if tone == "supportive":
            score = 5.0 + (prob * 5.0)
        elif tone == "challenging":
            score = 5.0 - (prob * 5.0)
        else:
            # Mixed/Neutral
            # If intensity is high but mixed, we stay closer to 5 or move slightly based on weights
            supp_w = float(top_event.get("context", {}).get("supportive_weight", 0))
            chal_w = float(top_event.get("context", {}).get("challenging_weight", 0))
            diff = (supp_w - chal_w) / max(1, supp_w + chal_w)
            score = 5.0 + (diff * 2.5)

        final_scores[label] = round(max(0, min(10, score)), 1)

    return final_scores

def determine_trends(current_scores: Dict[str, float], past_scores: Dict[str, float] | None = None) -> Dict[str, str]:
    """
    Determines if scores are increasing, decreasing, or stable.
    For now, since we don't have historical data easily, we can infer from the 'phase' of the top event.
    """
    trends = {}
    for label in current_scores:
        trends[label] = "stable" # Default
    return trends
