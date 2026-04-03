from __future__ import annotations

from collections import Counter
from typing import Any


def learn_from_events(events: list[dict[str, Any]]) -> dict[str, int]:
    pattern_counter: Counter[str] = Counter()

    for event in events:
        for transit in list(event.get("transits", []) or []):
            key = f"{transit.get('planet_a')}_{transit.get('aspect')}_{transit.get('planet_b')}"
            pattern_counter[key] += 1

        for hit in list(event.get("rule_hits", []) or []):
            key = str(hit.get("code") or "")
            if key:
                pattern_counter[key] += 1

    return dict(pattern_counter)


def build_weight_adjustments(patterns: dict[str, int]) -> list[dict[str, Any]]:
    adjustments: list[dict[str, Any]] = []
    for key, count in sorted(patterns.items(), key=lambda item: (-item[1], item[0])):
        adjustments.append(
            {
                "pattern": key,
                "observed_count": count,
                "suggested_delta": round(count * 0.2, 2),
            }
        )
    return adjustments[:10]


def summarize_learning(events: list[dict[str, Any]]) -> dict[str, Any]:
    patterns = learn_from_events(events)
    return {
        "observed_events": len(events),
        "pattern_counter": patterns,
        "weight_hints": build_weight_adjustments(patterns),
    }
