from __future__ import annotations

from typing import Any


def build_life_story(
    *,
    timeline_periods: list[dict[str, Any]],
    life_events: list[dict[str, Any]],
    turning_points: list[dict[str, Any]],
) -> dict[str, Any]:
    chapters: list[dict[str, Any]] = []

    for event in life_events:
        chapters.append(
            {
                "date": event["window"]["peak"],
                "title": event["label"],
                "phase": "build-up -> peak -> resolution",
                "summary": event["summary"],
                "kind": "life_event",
            }
        )

    for point in turning_points[:6]:
        chapters.append(
            {
                "date": point["date"],
                "title": point["headline"],
                "phase": "virada",
                "summary": point["summary"],
                "kind": "turning_point",
            }
        )

    chapters.sort(key=lambda item: item["date"])
    lead_periods = [period["headline"] for period in timeline_periods[:4] if period.get("headline")]

    if chapters:
        overview = (
            f"O ciclo abre com {lead_periods[0].lower() if lead_periods else 'movimentos graduais'}, "
            f"ganha pico em {chapters[0]['date']} e depois redistribui as consequencias nos capitulos seguintes."
        )
    else:
        overview = (
            "O ciclo avanca mais por acumulacao de fases do que por um unico grande evento, "
            "pedindo leitura continua das proximas etapas."
        )

    return {
        "overview": overview,
        "chapters": chapters[:12],
    }
