from __future__ import annotations

import json
from pathlib import Path

KNOWLEDGE_BASE_PATH = Path(__file__).with_name("knowledge_base.json")


def load_knowledge_base() -> dict[str, dict]:
    return json.loads(KNOWLEDGE_BASE_PATH.read_text(encoding="utf-8"))


def _find_aspect(aspects: list[dict], a: str, b: str, aspect: str) -> bool:
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


def generate_events(
    aspects: list[dict],
    houses: list[float],
    numerology: dict,
    reference_date: str,
) -> list[dict]:
    kb = load_knowledge_base()
    events: list[dict] = []

    if _find_aspect(aspects, "venus", "mars", "square"):
        key = "venus_square_mars"
        score = min(1.0, kb[key]["weight"] + (0.1 if len(houses) == 12 else 0.0))
        events.append(
            {
                "event": "Fase de tensão e ajustes em vínculos afetivos",
                "category": kb[key]["category"],
                "intensity": _intensity(score),
                "score": round(score, 2),
                "drivers": [key],
                "time_window": {"start": reference_date, "end": reference_date},
            }
        )

    if _find_aspect(aspects, "sun", "saturn", "opposition"):
        key = "sun_opposition_saturn"
        score = kb[key]["weight"]
        events.append(
            {
                "event": "Pressão por resultados e amadurecimento de metas",
                "category": kb[key]["category"],
                "intensity": _intensity(score),
                "score": round(score, 2),
                "drivers": [key],
                "time_window": {"start": reference_date, "end": reference_date},
            }
        )

    if numerology.get("life_path_number") == 1:
        key = "life_path_1"
        score = kb[key]["weight"]
        events.append(
            {
                "event": "Momento favorável para autonomia e liderança",
                "category": kb[key]["category"],
                "intensity": _intensity(score),
                "score": round(score, 2),
                "drivers": [key],
                "time_window": {"start": reference_date, "end": reference_date},
            }
        )

    if not events:
        events.append(
            {
                "event": "Ciclo estável com avanços graduais",
                "category": "geral",
                "intensity": "low",
                "score": 0.3,
                "drivers": ["baseline"],
                "time_window": {"start": reference_date, "end": reference_date},
            }
        )

    return events
