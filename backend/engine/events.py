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
# LOAD KNOWLEDGE BASE
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
# CORE
# -----------------------------------

def generate_events(
    aspects: List[Dict],
    houses: List[float],
    numerology: Dict,
    reference_date: date,
) -> List[Dict]:

    kb = load_knowledge_base()
    events: List[Dict] = []

    ref_date_str = reference_date.isoformat()

    # -------------------------
    # VENUS SQUARE MARS
    # -------------------------

    if _has_aspect(aspects, "venus", "mars", "square"):
        key = "venus_square_mars"
        weight = kb.get(key, {}).get("weight", 0.7)

        score = min(1.0, weight + 0.1)

        events.append(
            {
                "id": _event_id(key, reference_date),
                "event": "Fase de tensão e ajustes em vínculos afetivos",
                "category": kb.get(key, {}).get("category", "relacionamento"),
                "intensity": _intensity(score),
                "score": round(score, 2),
                "drivers": [key],
                "time_window": {
                    "start": ref_date_str,
                    "end": ref_date_str,
                },
            }
        )

    # -------------------------
    # SUN OPP SATURN
    # -------------------------

    if _has_aspect(aspects, "sun", "saturn", "opposition"):
        key = "sun_opposition_saturn"
        weight = kb.get(key, {}).get("weight", 0.6)

        score = weight

        events.append(
            {
                "id": _event_id(key, reference_date),
                "event": "Pressão por resultados e amadurecimento de metas",
                "category": kb.get(key, {}).get("category", "carreira"),
                "intensity": _intensity(score),
                "score": round(score, 2),
                "drivers": [key],
                "time_window": {
                    "start": ref_date_str,
                    "end": ref_date_str,
                },
            }
        )

    # -------------------------
    # NUMEROLOGIA
    # -------------------------

    if numerology.get("life_path_number") == 1:
        key = "life_path_1"
        weight = kb.get(key, {}).get("weight", 0.6)

        score = weight

        events.append(
            {
                "id": _event_id(key, reference_date),
                "event": "Momento favorável para autonomia e liderança",
                "category": kb.get(key, {}).get("category", "desenvolvimento_pessoal"),
                "intensity": _intensity(score),
                "score": round(score, 2),
                "drivers": [key],
                "time_window": {
                    "start": ref_date_str,
                    "end": ref_date_str,
                },
            }
        )

    # -------------------------
    # FALLBACK
    # -------------------------

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
                    "start": ref_date_str,
                    "end": ref_date_str,
                },
            }
        )

    return events