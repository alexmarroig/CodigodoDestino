from __future__ import annotations

CERTAINTY_LEVELS = ("chance", "tendency", "must", "will")

CERTAINTY_LABELS = {
    "chance": "Existe chance",
    "tendency": "Forte tendência",
    "must": "Deve acontecer",
    "will": "Vai acontecer",
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
    _tense = frozenset({"square", "opposition", "conjunction"})

    has_tense = any(
        str((s.get("evidence") or {}).get("aspect") or "") in _tense
        and str(s.get("technique") or "") != "numerology"
        for s in signals
    )

    if independent_signals >= 4 and has_tense:
        return "will"
    if independent_signals >= 3:
        return "must"
    if independent_signals == 2:
        return "tendency"
    return "chance"
