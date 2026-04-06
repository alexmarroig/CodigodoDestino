from __future__ import annotations

from datetime import date, datetime
from typing import Any

from engine.analysis import DOMAIN_LABELS

CATEGORY_DEFINITIONS = [
    {
        "key": "health",
        "event_type": "Health / illness",
        "domains": {"saude_rotina", "psicologico_espiritual"},
        "allowed_polarities": {"challenging", "mixed"},
        "rule_codes": {
            "accident_risk",
            "emotional_low",
            "psychological_transformation",
        },
        "life_event_types": {"crisis"},
    },
    {
        "key": "career",
        "event_type": "Career changes / job opportunities",
        "domains": {"carreira_status"},
        "allowed_polarities": {"supportive", "challenging", "mixed"},
        "rule_codes": {
            "career_block",
            "career_reset",
            "career_transformation",
            "career_growth",
            "career_change",
            "career_pressure",
            "authority_conflict",
        },
        "life_event_types": {"career_change"},
    },
    {
        "key": "relationships",
        "event_type": "Relationships / emotional events",
        "domains": {"relacionamentos", "criatividade_afetos"},
        "allowed_polarities": {"supportive", "challenging", "mixed"},
        "rule_codes": {
            "relationship_start",
            "love_expansion",
            "relationship_test",
            "relationship_block",
            "intense_relationship",
            "sudden_love",
            "conflict_relationship",
            "emotional_bond",
            "marriage_window",
            "commitment",
        },
        "life_event_types": {"marriage"},
    },
    {
        "key": "rupture",
        "event_type": "Loss / rupture / separation",
        "domains": {"relacionamentos", "familia_lar", "psicologico_espiritual"},
        "allowed_polarities": {"challenging", "mixed"},
        "rule_codes": {
            "breakup",
            "sudden_break",
            "emotional_cut",
            "deep_emotional_break",
            "relationship_block",
            "relationship_test",
        },
        "life_event_types": {"breakup", "crisis"},
    },
    {
        "key": "major_transitions",
        "event_type": "Major life transitions",
        "domains": {
            "identidade",
            "crises_recursos",
            "psicologico_espiritual",
            "expansao_sentido",
            "carreira_status",
        },
        "allowed_polarities": {"supportive", "challenging", "mixed"},
        "rule_codes": {
            "career_change",
            "career_reset",
            "career_transformation",
            "financial_transformation",
            "extreme_conflict",
            "psychological_transformation",
        },
        "life_event_types": {"life_change", "career_change", "crisis"},
    },
]

PROBABILITY_LEVELS = {
    1: "Discard",
    2: "Weak",
    3: "Moderate",
    4: "High",
}


def _parse_iso_date(value: str | None) -> date | None:
    if not value:
        return None
    return datetime.fromisoformat(value).date()


def _merged_window(items: list[dict[str, Any]], reference_date: date) -> dict[str, Any] | None:
    starts = [_parse_iso_date(item.get("time_window", {}).get("start")) for item in items]
    ends = [_parse_iso_date(item.get("time_window", {}).get("end")) for item in items]
    peaks = [_parse_iso_date(item.get("time_window", {}).get("peak")) for item in items]
    starts = [item for item in starts if item is not None]
    ends = [item for item in ends if item is not None]
    peaks = [item for item in peaks if item is not None]

    if not starts or not ends:
        return None

    start = min(starts)
    end = max(ends)
    peak = min(
        peaks or [start],
        key=lambda item: abs((item - reference_date).days),
    )
    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "peak": peak.isoformat(),
        "duration_days": max(1, (end - start).days + 1),
    }


def _relative_timeframe(reference_date: date, window: dict[str, Any] | None) -> str:
    if not window:
        return "timing still forming"

    start = _parse_iso_date(window["start"]) or reference_date
    end = _parse_iso_date(window["end"]) or start
    days_to_start = max(0, (start - reference_date).days)
    duration_days = max(1, (end - start).days + 1)

    if days_to_start <= 7 and duration_days <= 14:
        return "next 1-2 weeks"
    if days_to_start <= 14 and duration_days <= 28:
        return "next 2-4 weeks"
    if days_to_start <= 30 and duration_days <= 60:
        return "within 1-2 months"
    if days_to_start <= 60 and duration_days <= 120:
        return "within 2-4 months"
    if days_to_start <= 120 and duration_days <= 240:
        return "within 6-8 months"
    return "over the next 12-24 months"


def _explanation(
    *,
    event_type: str,
    signals: list[dict[str, Any]],
    rule_hits: list[dict[str, Any]],
    life_events: list[dict[str, Any]],
) -> str:
    lead_labels = [item["label"] for item in sorted(signals, key=lambda item: -float(item["weight"]))[:3]]
    rule_labels = [item["label"] for item in sorted(rule_hits, key=lambda item: -float(item["weight"]))[:2]]
    life_labels = [item["type"] for item in life_events[:1]]
    evidence = lead_labels + rule_labels + life_labels
    evidence = evidence[:4]

    if not evidence:
        return f"{event_type} has some activation, but the pattern is still forming."

    return (
        "There is a convergence of signals around this theme. "
        f"Main drivers: {', '.join(evidence)}."
    )


def _sort_signals(signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        signals,
        key=lambda item: (
            -float(item.get("weight", 0.0)),
            item.get("technique", ""),
            item.get("label", ""),
        ),
    )


def build_predictive_insights(
    analysis: dict[str, Any],
    *,
    reference_date: date,
) -> dict[str, Any]:
    signals = list(analysis.get("signals", []))
    rule_hits = list(analysis.get("rule_hits", []))
    life_events = list(analysis.get("life_events", []))
    exact_timed_events = list(analysis.get("exact_timing", {}).get("timed_events", []))

    detected_events: list[dict[str, Any]] = []
    watchlist: list[dict[str, Any]] = []

    for definition in CATEGORY_DEFINITIONS:
        category_signals = [
            signal
            for signal in signals
            if signal.get("domain") in definition["domains"]
            and signal.get("polarity") in definition["allowed_polarities"]
        ]
        category_rule_hits = [
            hit
            for hit in rule_hits
            if hit.get("code") in definition["rule_codes"]
            or hit.get("domain") in definition["domains"]
        ]
        category_life_events = [
            event
            for event in life_events
            if event.get("type") in definition["life_event_types"]
        ]
        category_timed_events = [
            event
            for event in exact_timed_events
            if event.get("code") in definition["rule_codes"]
            or event.get("domain") in definition["domains"]
        ]

        techniques = sorted({str(signal["technique"]) for signal in category_signals})
        independent_signals = len(techniques)
        probability_level = PROBABILITY_LEVELS.get(min(independent_signals, 4), "High")

        if independent_signals <= 1:
            continue

        merged_items = [
            *category_signals,
            *[
                {"time_window": event.get("window") or event.get("time_window", {})}
                for event in category_life_events
            ],
            *[
                {"time_window": event.get("time_window", {})}
                for event in category_timed_events
            ],
        ]
        time_window = _merged_window(merged_items, reference_date)
        probability_score = round(
            min(
                0.95,
                (
                    (independent_signals * 0.19)
                    + (sum(float(signal["weight"]) for signal in category_signals[:4]) * 0.08)
                ),
            ),
            2,
        )
        entry = {
            "category_key": definition["key"],
            "event_type": definition["event_type"],
            "probability_level": probability_level,
            "independent_signals": independent_signals,
            "probability_score": probability_score,
            "time_window": {
                **(time_window or {}),
                "label": _relative_timeframe(reference_date, time_window),
            },
            "techniques": techniques,
            "signals": [signal["label"] for signal in _sort_signals(category_signals)[:4]],
            "rule_hits": [hit["label"] for hit in category_rule_hits[:3]],
            "exact_dates": [
                event.get("date")
                or event.get("window", {}).get("peak")
                for event in [*category_timed_events[:2], *category_life_events[:2]]
                if event.get("date") or event.get("window", {}).get("peak")
            ],
            "explanation": _explanation(
                event_type=definition["event_type"],
                signals=category_signals,
                rule_hits=category_rule_hits,
                life_events=category_life_events,
            ),
            "domains": sorted(
                {
                    DOMAIN_LABELS.get(str(signal["domain"]), str(signal["domain"]).replace("_", " "))
                    for signal in category_signals
                }
            ),
        }

        if independent_signals >= 3:
            detected_events.append(entry)
        else:
            watchlist.append(entry)

    detected_events.sort(
        key=lambda item: (
            item["probability_level"] != "High",
            -float(item["probability_score"]),
            item["event_type"],
        )
    )
    watchlist.sort(key=lambda item: (-float(item["probability_score"]), item["event_type"]))

    return {
        "detected_events": detected_events,
        "watchlist": watchlist,
        "summary": {
            "detected_count": len(detected_events),
            "watchlist_count": len(watchlist),
            "strongest_category": detected_events[0]["event_type"] if detected_events else None,
        },
    }
