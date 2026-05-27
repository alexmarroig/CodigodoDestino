"""
Essential dignity scoring (Lilly-style) for natal planets receiving transits.

Used to downgrade illusory supportive transits to debilitated natal receivers and
to require positive dignity for strong gain/commitment narratives.
"""

from __future__ import annotations

from typing import Any

from astro.signs import longitude_to_sign

# Sign rulers (domicile)
_SIGN_RULERS: dict[str, str] = {
    "aries": "mars",
    "taurus": "venus",
    "gemini": "mercury",
    "cancer": "moon",
    "leo": "sun",
    "virgo": "mercury",
    "libra": "venus",
    "scorpio": "mars",
    "sagittarius": "jupiter",
    "capricorn": "saturn",
    "aquarius": "saturn",
    "pisces": "jupiter",
}

# Classical exaltation signs
_EXALTATION_SIGN: dict[str, str] = {
    "sun": "aries",
    "moon": "taurus",
    "mercury": "virgo",
    "venus": "pisces",
    "mars": "capricorn",
    "jupiter": "cancer",
    "saturn": "libra",
}

_OPPOSITE_SIGN: dict[str, str] = {
    "aries": "libra",
    "taurus": "scorpio",
    "gemini": "sagittarius",
    "cancer": "capricorn",
    "leo": "aquarius",
    "virgo": "pisces",
    "libra": "aries",
    "scorpio": "taurus",
    "sagittarius": "gemini",
    "capricorn": "cancer",
    "aquarius": "leo",
    "pisces": "virgo",
}

_SUPPORTIVE_ASPECTS: frozenset[str] = frozenset({"trine", "sextile"})
_SEVERE_SCORE_THRESHOLD: int = -4
_POSITIVE_SCORE_THRESHOLD: int = 4


def _norm_planet(name: str) -> str:
    return name.replace("_", " ").strip().lower()


def essential_dignity_score(planet: str, sign_en: str) -> int:
    """
    Return essential dignity score for a planet in a sign.

    +5 domicile, +4 exaltation, -4 detriment, -5 fall, 0 peregrine.
    """
    p = _norm_planet(planet)
    sign = sign_en.strip().lower()
    if not p or not sign:
        return 0

    if _SIGN_RULERS.get(sign) == p:
        return 5
    if _EXALTATION_SIGN.get(p) == sign:
        return 4

    detriment_sign = _OPPOSITE_SIGN.get(
        next((s for s, ruler in _SIGN_RULERS.items() if ruler == p), "")
    )
    if detriment_sign and sign == detriment_sign:
        return -4

    exalt_sign = _EXALTATION_SIGN.get(p)
    if exalt_sign:
        fall_sign = _OPPOSITE_SIGN.get(exalt_sign)
        if fall_sign and sign == fall_sign:
            return -5

    return 0


def dignity_label(score: int) -> str:
    if score >= 5:
        return "domicilio"
    if score >= 4:
        return "exaltacao"
    if score <= -5:
        return "queda"
    if score <= -4:
        return "exilio"
    return "peregrino"


def natal_planet_dignity_scores(natal_ephemeris: dict[str, Any]) -> dict[str, int]:
    """Map natal planet name → essential dignity score from longitude."""
    scores: dict[str, int] = {}
    for planet_name, data in (natal_ephemeris.get("planets") or {}).items():
        longitude = float(data.get("longitude", 0.0))
        sign_en = longitude_to_sign(longitude).sign_en
        scores[_norm_planet(planet_name)] = essential_dignity_score(planet_name, sign_en)
    return scores


def is_positive_dignity(score: int) -> bool:
    return score >= _POSITIVE_SCORE_THRESHOLD


def is_severe_affliction(score: int) -> bool:
    return score <= _SEVERE_SCORE_THRESHOLD


def apply_dignity_to_transit_signal(
    signal: dict[str, Any],
    natal_dignity_scores: dict[str, int],
) -> dict[str, Any]:
    """
    Annotate transit signal evidence with natal receiver dignity; downgrade supportive
    trines/sextiles to severely debilitated natal planets.
    """
    if str(signal.get("technique") or "") != "transits":
        return signal

    evidence = dict(signal.get("evidence") or {})
    aspect = str(evidence.get("aspect") or "")
    natal_planet = _norm_planet(str(evidence.get("planet_b") or ""))
    if not natal_planet or natal_planet in {"asc", "mc", "dsc", "ic", "ascendant", "midheaven"}:
        return signal

    score = natal_dignity_scores.get(natal_planet, 0)
    evidence["natal_essential_dignity_score"] = score
    evidence["natal_essential_dignity"] = dignity_label(score)

    updated = dict(signal)
    updated["evidence"] = evidence

    if aspect in _SUPPORTIVE_ASPECTS and is_severe_affliction(score):
        updated["polarity"] = "mixed"
        updated["dignity_downgrade"] = "conforto_ilusorio"
        updated["label"] = (
            f"{signal.get('label', '')} — conforto ilusório; oportunidade fraca "
            f"(receptor natal em {dignity_label(score)})"
        ).strip(" —")
        updated["weight"] = round(float(signal.get("weight", 1.0)) * 0.55, 3)
    elif aspect in _SUPPORTIVE_ASPECTS and is_positive_dignity(score):
        evidence["natal_dignity_supports_gain"] = True

    return updated


def enrich_transit_signals_with_dignity(
    signals: list[dict[str, Any]],
    natal_ephemeris: dict[str, Any],
) -> list[dict[str, Any]]:
    scores = natal_planet_dignity_scores(natal_ephemeris)
    return [apply_dignity_to_transit_signal(s, scores) for s in signals]
