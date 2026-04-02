from __future__ import annotations

import json
from pathlib import Path
from datetime import date
from typing import List, Dict

# -----------------------------------
# CONFIG
# -----------------------------------

KNOWLEDGE_BASE_PATH = Path(__file__).with_name("knowledge_base.json")


# -----------------------------------
# LOAD
# -----------------------------------

def load_knowledge_base() -> Dict[str, Dict]:
    return json.loads(KNOWLEDGE_BASE_PATH.read_text(encoding="utf-8"))


# -----------------------------------
# UTILS
# -----------------------------------

def _has_aspect(aspects: List[Dict], a: str, b: str, aspect: str) -> bool:
    for item in aspects:
        if {item["planet_a"], item["planet_b"]} == {a, b} and item["aspect"] == aspect:
            return True
    return False


def _intensity(score: float) -> str:
    if score >= 0.75:
        return "high"
    if score >= 0.45:
        return "medium"
    return "low"


def _event_id(key: str, reference_date: date) -> str:
    return f"{key}_{reference_date.isoformat()}"


# -----------------------------------
# 🔥 CORE ENGINE
# -----------------------------------

def generate_events(
    aspects: List[Dict],
    houses: List[float],
    numerology: Dict,
    reference_date: date,
) -> List[Dict]:

    kb = load_knowledge_base()
    events: List[Dict] = []

    ref_date = reference_date.isoformat()

    # =================================
    # REGRAS ASTROLÓGICAS
    # =================================

    rules_triggered = []

    if _has_aspect(aspects, "venus", "mars", "square"):
        rules_triggered.append("venus_square_mars")

    if _has_aspect(aspects, "sun", "saturn", "opposition"):
        rules_triggered.append("sun_opposition_saturn")

    # =================================
    # REGRAS NUMEROLÓGICAS
    # =================================

    if numerology.get("life_path_number") == 1:
        rules_triggered.append("life_path_1")

    # =================================
    # 🔥 COMPOSIÇÃO DE EVENTOS
    # =================================

    for key in rules_triggered:
        rule = kb.get(key, {})

        base_weight = rule.get("weight", 0.5)

        # 🔥 AUMENTO DE INTENSIDADE POR COMBINAÇÃO
        combo_bonus = 0.1 * (len(rules_triggered) - 1)

        score = min(1.0, base_weight + combo_bonus)

        events.append(
            {
                "id": _event_id(key, reference_date),
                "event": rule.get("event", key),
                "category": rule.get("category", "geral"),
                "intensity": _intensity(score),
                "score": round(score, 2),
                "drivers": [key],
                "time_window": {
                    "start": ref_date,
                    "end": ref_date,
                },
                # 🔥 NOVO (IMPORTANTE PRA IA)
                "context": {
                    "total_active_rules": len(rules_triggered),
                },
            }
        )

    # =================================
    # FALLBACK
    # =================================

    if not events:
        key = "baseline"

        events.append(
            {
                "id": _event_id(key, reference_date),
                "event": "Ciclo estável com avanços graduais",
                "category": "geral",
                "intensity": "low",
                "score": 0.3,
                "drivers": [key],
                "time_window": {
                    "start": ref_date,
                    "end": ref_date,
                },
                "context": {
                    "total_active_rules": 0,
                },
            }
        )

    return events