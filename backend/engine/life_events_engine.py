from __future__ import annotations

from datetime import date, timedelta
from typing import Any


LIFE_EVENT_RULES = {
    "marriage": [
        ("jupiter", "conjunction", "venus"),
        ("jupiter", "trine", "venus"),
        ("saturn", "trine", "venus"),
        ("saturn", "conjunction", "venus"),
    ],
    "breakup": [
        ("uranus", "square", "venus"),
        ("uranus", "opposition", "venus"),
        ("pluto", "square", "venus"),
        ("saturn", "opposition", "venus"),
    ],
    "career_change": [
        ("saturn", "conjunction", "MC"),
        ("pluto", "conjunction", "MC"),
        ("uranus", "conjunction", "MC"),
    ],
    "life_change": [
        ("uranus", "conjunction", "sun"),
        ("pluto", "conjunction", "sun"),
        ("saturn", "square", "sun"),
    ],
    "financial_peak": [
        ("jupiter", "conjunction", "venus"),
        ("jupiter", "trine", "venus"),
    ],
    "crisis": [
        ("mars", "square", "saturn"),
        ("mars", "opposition", "pluto"),
        ("saturn", "square", "moon"),
    ],
}

LIFE_EVENT_LABELS = {
    "marriage": "Janela forte de uniao ou compromisso serio",
    "breakup": "Janela forte de ruptura ou separacao",
    "career_change": "Mudanca concreta de carreira ou reposicionamento",
    "life_change": "Virada maior de vida, cidade ou identidade",
    "financial_peak": "Virada financeira ou oportunidade material",
    "crisis": "Periodo de crise, ruptura emocional ou tensao extrema",
}

LIFE_EVENT_AREA_MAP = {
    "marriage": "relacionamento",
    "breakup": "relacionamento",
    "career_change": "carreira",
    "life_change": "transicoes",
    "financial_peak": "financas",
    "crisis": "transicoes",
}


def match_event(transit: dict[str, Any], rule: tuple[str, str, str]) -> bool:
    return (
        str(transit.get("planet_a")) == rule[0]
        and str(transit.get("aspect")) == rule[1]
        and str(transit.get("planet_b")) == rule[2]
    )


def _parse_date(value: str) -> date:
    return date.fromisoformat(str(value))


def _build_event_window(event: dict[str, Any]) -> dict[str, Any]:
    transits = list(event["transits"])
    exact_dates = [_parse_date(item["date"]) for item in transits]
    peak_date = _parse_date(event["date"])

    first_exact = min(exact_dates, default=peak_date)
    last_exact = max(exact_dates, default=peak_date)
    padded_start = first_exact - timedelta(days=7)
    padded_end = last_exact + timedelta(days=10)

    return {
        "start": padded_start.isoformat(),
        "peak": peak_date.isoformat(),
        "end": padded_end.isoformat(),
        "duration_days": max(1, (padded_end - padded_start).days + 1),
        "precision": "day",
    }


def classify_intensity(event: dict[str, Any]) -> str:
    strength = int(event["strength"])
    if strength >= 4:
        return "high"
    if strength >= 2:
        return "medium"
    return "low"


def detect_life_events(timed_transits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []

    for event_type, rules in LIFE_EVENT_RULES.items():
        matches: list[dict[str, Any]] = []
        for transit in timed_transits:
            for rule in rules:
                if match_event(transit, rule):
                    matches.append(transit)

        if len(matches) < 2:
            continue

        sorted_matches = sorted(matches, key=lambda item: item["date"])
        clusters: list[list[dict[str, Any]]] = []
        current_cluster: list[dict[str, Any]] = []
        last_date: date | None = None

        for match in sorted_matches:
            match_date = _parse_date(match["date"])
            if last_date is None or (match_date - last_date).days <= 45:
                current_cluster.append(match)
            else:
                clusters.append(current_cluster)
                current_cluster = [match]
            last_date = match_date

        if current_cluster:
            clusters.append(current_cluster)

        for cluster in clusters:
            if len(cluster) < 2:
                continue
            peak = min(cluster, key=lambda item: (float(item["orb"]), item["date"]))
            events.append(
                {
                    "type": event_type,
                    "label": LIFE_EVENT_LABELS[event_type],
                    "area_key": LIFE_EVENT_AREA_MAP[event_type],
                    "date": peak["date"],
                    "strength": len(cluster),
                    "transits": sorted(cluster, key=lambda item: (float(item["orb"]), item["date"])),
                }
            )

    return sorted(events, key=lambda item: (item["date"], -int(item["strength"]), item["type"]))


def full_life_event_analysis(timed_transits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    raw_events = detect_life_events(timed_transits)
    final: list[dict[str, Any]] = []

    for event in raw_events:
        window = _build_event_window(event)
        intensity = classify_intensity(event)
        peak = event["transits"][0]
        final.append(
            {
                "type": event["type"],
                "label": event["label"],
                "area_key": event["area_key"],
                "window": window,
                "date": window["peak"],
                "intensity": intensity,
                "strength": event["strength"],
                "cause": f"{peak['planet_a']} {peak['aspect']} {peak['planet_b']}",
                "summary": (
                    f"Entre {window['start']} e {window['end']}, cresce uma janela forte para {event['label'].lower()} "
                    f"com pico em {window['peak']}."
                ),
                "transits": event["transits"],
            }
        )

    return final
