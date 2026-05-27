"""
Thematic hit-cluster convergence (Hand/Brady): count techniques AND distinct astrological targets.
"""

from __future__ import annotations

from typing import Any

from engine.astro_confirmation import filter_self_aspects

# Techniques that alone cannot justify a 3rd "vote" for high certainty
_WEAK_SOLO_TECHNIQUES = frozenset({"numerology"})
_PROFECTION_TECHNIQUE = "annual_profection"


def _norm_planet(name: str) -> str:
    return str(name or "").replace("_", " ").strip().lower()


def _signal_target_key(signal: dict[str, Any]) -> str | None:
    """Distinct theme target: planet pair, house focus, or angle."""
    ev = signal.get("evidence") or {}
    pa = _norm_planet(str(ev.get("planet_a") or ""))
    pb = _norm_planet(str(ev.get("planet_b") or ""))
    if pa and pb and pa != pb:
        pair = tuple(sorted((pa, pb)))
        return f"pair:{pair[0]}|{pair[1]}"
    if pa:
        return f"planet:{pa}"
    th = ev.get("transit_house")
    nh = ev.get("natal_house")
    if isinstance(th, int):
        return f"house_t:{th}"
    if isinstance(nh, int):
        return f"house_n:{nh}"
    domain = str(signal.get("domain") or "")
    if domain:
        return f"domain:{domain}"
    return None


def _rule_target_keys(rule_hits: list[dict[str, Any]]) -> set[str]:
    keys: set[str] = set()
    for hit in rule_hits:
        code = str(hit.get("code") or "")
        if code:
            keys.add(f"rule:{code}")
    return keys


def compute_cluster_metrics(
    signals: list[dict[str, Any]],
    rule_hits: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Returns technique_count, theme_convergence, effective_independent_signals, details.
    """
    clean = filter_self_aspects(list(signals))
    techniques = sorted({str(s.get("technique") or "") for s in clean if s.get("technique")})
    technique_count = len(techniques)

    targets: set[str] = set()
    for signal in clean:
        key = _signal_target_key(signal)
        if key:
            targets.add(key)
    if rule_hits:
        targets |= _rule_target_keys(rule_hits)

    theme_convergence = len(targets)

    # Effective count: need both breadth of techniques and thematic spread
    if technique_count == 0:
        effective = 0
    elif theme_convergence <= 1:
        effective = min(technique_count, 1)
    elif theme_convergence == 2:
        effective = min(technique_count, 2)
    else:
        effective = technique_count

    # Profecção + numerologia alone cannot reach 3
    strong_techniques = [
        t for t in techniques
        if t not in _WEAK_SOLO_TECHNIQUES and t != _PROFECTION_TECHNIQUE
    ]
    has_profection_only_boost = (
        technique_count >= 3
        and len(strong_techniques) < 2
        and _PROFECTION_TECHNIQUE in techniques
    )
    if has_profection_only_boost:
        effective = min(effective, 2)

    if techniques == ["numerology"] or (
        len(techniques) == 1 and techniques[0] in _WEAK_SOLO_TECHNIQUES
    ):
        effective = min(effective, 1)

    return {
        "technique_count": technique_count,
        "theme_convergence": theme_convergence,
        "effective_independent_signals": effective,
        "techniques": techniques,
        "targets": sorted(targets),
    }


def theme_convergence_sufficient(metrics: dict[str, Any], *, minimum: int = 2) -> bool:
    return int(metrics.get("theme_convergence") or 0) >= minimum
