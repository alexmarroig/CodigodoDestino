from __future__ import annotations

from typing import Any


QUESTION_MAP = {
    "relacionamento": "Algo importante aconteceu na sua vida amorosa nesse periodo?",
    "carreira": "Houve mudanca de emprego, cargo ou direcao profissional nesse periodo?",
    "financas": "Voce percebeu ganho, perda ou ajuste forte de dinheiro nesse periodo?",
    "saude": "Seu corpo, rotina ou energia passaram por pressao relevante nesse periodo?",
    "transicoes": "Voce sentiu uma virada forte de vida, identidade ou rumo nesse periodo?",
}


def suggest_feedback_questions(
    *,
    life_events: list[dict[str, Any]],
    turning_points: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    questions: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for event in life_events[:4]:
        area_key = str(event.get("area_key"))
        prompt = QUESTION_MAP.get(area_key)
        if not prompt:
            continue
        marker = (area_key, str(event["window"]["peak"]))
        if marker in seen:
            continue
        seen.add(marker)
        questions.append(
            {
                "area_key": area_key,
                "question": prompt,
                "window_start": event["window"]["start"],
                "window_peak": event["window"]["peak"],
                "window_end": event["window"]["end"],
                "source": "life_event",
            }
        )

    for point in turning_points[:4]:
        area_key = str(point.get("domain"))
        prompt = QUESTION_MAP.get(area_key)
        if not prompt:
            continue
        marker = (area_key, str(point["date"]))
        if marker in seen:
            continue
        seen.add(marker)
        questions.append(
            {
                "area_key": area_key,
                "question": prompt,
                "window_start": point["date"],
                "window_peak": point["date"],
                "window_end": point["date"],
                "source": "turning_point",
            }
        )

    return questions[:6]
