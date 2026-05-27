from __future__ import annotations

from typing import Any

CERTAINTY_LEVELS = ("chance", "tendency", "must", "will")

# Categories where impactful events need hard slow transits for high certainty
_IMPACT_CATEGORIES = frozenset({
    "rupture",
    "health",
    "major_transitions",
    "career",
    "finance",
})

CERTAINTY_LABELS = {
    "chance": "Existe chance",
    "tendency": "Forte tendência",
    "must": "Deve acontecer",
    "will": "Alta probabilidade",
}

CERTAINTY_PREFIXES = {
    "chance": "Existe chance de que",
    "tendency": "Há forte tendência de que",
    "must": "Isso deve acontecer:",
    "will": "Isso vai acontecer:",
}


def certainty_from_signal_count(independent_signals: int) -> str:
    if independent_signals >= 4:
        return "will"
    if independent_signals == 3:
        return "must"
    if independent_signals == 2:
        return "tendency"
    return "chance"


def apply_certainty_prefix(text: str, certainty_level: str) -> str:
    body = text.strip()
    if not body:
        return body
    lowered = body[0].lower() + body[1:] if len(body) > 1 else body.lower()
    prefix = CERTAINTY_PREFIXES.get(certainty_level, CERTAINTY_PREFIXES["tendency"])
    if certainty_level in {"must", "will"}:
        return f"{prefix} {lowered}"
    return f"{prefix} {lowered}"


def certainty_with_aspects(independent_signals: int, signals: list[dict]) -> str:
    """
    Determine certainty level considering both signal count and aspect quality.

    'will' requires: >= 4 signals + at least one tense planetary aspect
         and at least one non-numerology signal with that tense aspect.
    'must' requires: >= 3 signals (tense aspect optional).
    Below that: same as certainty_from_signal_count.
    """
    from engine.signal_enrichment import is_tense_aspect

    has_tense = any(
        str(s.get("technique") or "") != "numerology"
        and is_tense_aspect(
            str((s.get("evidence") or {}).get("aspect") or ""),
            str((s.get("evidence") or {}).get("planet_a") or ""),
            str((s.get("evidence") or {}).get("planet_b") or ""),
        )
        for s in signals
    )

    if independent_signals >= 4 and has_tense:
        return "will"
    if independent_signals >= 3:
        return "must"
    if independent_signals == 2:
        return "tendency"
    return "chance"


def _cap_level(level: str, maximum: str) -> str:
    order = list(CERTAINTY_LEVELS)
    if order.index(level) > order.index(maximum):
        return maximum
    return level


def resolve_certainty(
    independent_signals: int,
    signals: list[dict[str, Any]],
    *,
    category_key: str = "",
    theme_convergence: int = 0,
    has_hard_slow: bool | None = None,
) -> str:
    """
    Unified certainty: aspect quality, thematic convergence, hard slow transit for impact categories.
    """
    level = certainty_with_aspects(independent_signals, signals)

    if theme_convergence > 0 and theme_convergence < 2:
        level = _cap_level(level, "tendency")

    if category_key in _IMPACT_CATEGORIES:
        if has_hard_slow is False:
            level = _cap_level(level, "tendency")
        elif has_hard_slow is None:
            try:
                from engine.signal_enrichment import has_hard_slow_transit

                if not has_hard_slow_transit(signals):
                    level = _cap_level(level, "tendency")
            except ImportError:
                pass

    return level
