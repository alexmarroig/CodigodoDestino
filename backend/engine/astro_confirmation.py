"""
Confirmation scoring, signal filtering, and relationship subtype classification
for CodigodoDestino.

Implements the confirmation hierarchy described in the user's rulebook:

1. Signal scoring:
   - Slow planets (Saturn/Uranus/Neptune/Pluto) weigh 2× fast planets
   - Angular houses (1, 4, 7, 10) weigh 1.5×
   - Exact orbs (<1°) weigh 2×, moderate (1-3°) 1.5×
   - Aspects to angles (ASC/MC/DSC/IC) weigh 1.5×
   - Self-aspects (same planet both sides) score 0 and are filtered out

2. Relationship subtype classifier (one primary per event):
   - separacao_termino  — slow planet + Casa 7 + 3+ técnicas + NOT only fast
   - briga_forte        — Marte central + 2+ técnicas
   - ciume_posse        — Plutão-Vênus, Lua-Plutão, Marte-Plutão hard aspects
   - afastamento_emocional — Saturno ativo + NOT Marte dominante
   - conversa_seria     — Mercúrio ativo + sem Marte/Plutão dominante
   - tensao_leve        — único trânsito rápido sem planeta lento
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Planet speed classification
# ---------------------------------------------------------------------------

SLOW_PLANETS: frozenset[str] = frozenset({"saturn", "uranus", "neptune", "pluto"})
FAST_PLANETS: frozenset[str] = frozenset({"sun", "moon", "mercury", "venus", "mars"})

ANGULAR_HOUSES: frozenset[int] = frozenset({1, 4, 7, 10})

# Normalised angle-point names that qualify for the angle aspect bonus
ANGLE_POINTS: frozenset[str] = frozenset({
    "asc", "mc", "dsc", "ic",
    "ascendant", "ascendente",
    "midheaven", "meio-ceu", "meio_ceu",
    "descendant", "descendente",
    "imum_coeli", "ic",
})

TENSE_ASPECTS: frozenset[str] = frozenset({"square", "opposition", "conjunction"})


# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------

def _norm(name: str) -> str:
    return name.replace("_", " ").strip().lower()


# ---------------------------------------------------------------------------
# Scoring helpers (public so they can be tested independently)
# ---------------------------------------------------------------------------

def planet_speed_weight(planet_name: str) -> float:
    """Return 2.0 for slow planets, 1.0 for fast planets."""
    return 2.0 if _norm(planet_name) in SLOW_PLANETS else 1.0


def orb_weight(orb: float | None) -> float:
    """Return higher weight for tighter orbs: <1° → 2.0, 1-3° → 1.5, else 1.0."""
    if orb is None:
        return 1.0
    if orb < 1.0:
        return 2.0
    if orb < 3.0:
        return 1.5
    return 1.0


def house_angular_weight(house: int | None) -> float:
    """Return 1.5 for angular houses (1,4,7,10), else 1.0."""
    return 1.5 if house in ANGULAR_HOUSES else 1.0


def score_signal(signal: dict[str, Any]) -> float:
    """
    Compute the confirmation weight for a single signal.

    Returns 0.0 for self-aspects (same planet on both sides).
    Considers: planet speed, orb exactness, house angularity, angle-point aspects.
    """
    if is_self_aspect(signal):
        return 0.0

    evidence = signal.get("evidence") or {}
    pa = _norm(str(evidence.get("planet_a") or ""))
    pb = _norm(str(evidence.get("planet_b") or ""))
    orb = evidence.get("orb")
    house = evidence.get("transit_house") or evidence.get("natal_house")

    base = float(signal.get("weight", 1.0))
    score = (
        base
        * planet_speed_weight(pa)
        * orb_weight(orb)
        * house_angular_weight(house if isinstance(house, int) else None)
    )

    # Angle-point bonus for ASC/MC/DSC/IC
    if pa in ANGLE_POINTS or pb in ANGLE_POINTS:
        score *= 1.5

    return score


# ---------------------------------------------------------------------------
# Self-aspect detection and filtering
# ---------------------------------------------------------------------------

def is_self_aspect(signal: dict[str, Any]) -> bool:
    """
    Return True when a signal has the same planet on both sides.

    Examples: progressed Pluto conjunct natal Pluto, Sun/Sun progressions.
    These generational positions carry no individual predictive meaning and
    should be filtered from primary explanations and classification.
    """
    ev = signal.get("evidence") or {}
    pa = _norm(str(ev.get("planet_a") or ""))
    pb = _norm(str(ev.get("planet_b") or ""))
    return bool(pa and pb and pa == pb)


def filter_self_aspects(signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return signals with same-body aspects removed."""
    return [s for s in signals if not is_self_aspect(s)]


# ---------------------------------------------------------------------------
# Planet / house presence helpers (used by classifier)
# ---------------------------------------------------------------------------

def has_slow_planet(signals: list[dict[str, Any]]) -> bool:
    """True if any meaningful signal (non-self-aspect) involves a slow planet."""
    for s in filter_self_aspects(signals):
        ev = s.get("evidence") or {}
        pa = _norm(str(ev.get("planet_a") or ""))
        pb = _norm(str(ev.get("planet_b") or ""))
        if pa in SLOW_PLANETS or pb in SLOW_PLANETS:
            return True
    return False


def is_fast_only_transit(signals: list[dict[str, Any]]) -> bool:
    """
    True if ALL non-self-aspect signals involve only fast planets.

    A fast-only transit alone → maximum tension category is "tensao_leve".
    """
    clean = filter_self_aspects(signals)
    if not clean:
        return False
    return not has_slow_planet(clean)


def _has_planet(signals: list[dict[str, Any]], planet: str) -> bool:
    p = _norm(planet)
    for s in signals:
        ev = s.get("evidence") or {}
        if _norm(str(ev.get("planet_a") or "")) == p:
            return True
        if _norm(str(ev.get("planet_b") or "")) == p:
            return True
    return False


def _has_hard_aspect_pair(
    signals: list[dict[str, Any]],
    p1: str,
    p2: str,
) -> bool:
    """True if there is a tense aspect (conjunction/square/opposition) between p1 and p2."""
    n1, n2 = _norm(p1), _norm(p2)
    for s in signals:
        ev = s.get("evidence") or {}
        if _norm(str(ev.get("aspect") or "")) not in TENSE_ASPECTS:
            continue
        pa = _norm(str(ev.get("planet_a") or ""))
        pb = _norm(str(ev.get("planet_b") or ""))
        if (pa == n1 and pb == n2) or (pa == n2 and pb == n1):
            return True
    return False


def _has_planet_in_house(
    signals: list[dict[str, Any]],
    planet: str,
    house: int,
) -> bool:
    p = _norm(planet)
    for s in signals:
        ev = s.get("evidence") or {}
        if _norm(str(ev.get("planet_a") or "")) == p:
            h = ev.get("transit_house") or ev.get("natal_house")
            if h == house:
                return True
    return False


def _house_7_activated(signals: list[dict[str, Any]]) -> bool:
    for s in signals:
        ev = s.get("evidence") or {}
        if ev.get("transit_house") == 7 or ev.get("natal_house") == 7:
            return True
    return False


def _has_afflicted_venus(signals: list[dict[str, Any]]) -> bool:
    """True if Venus appears in any tense aspect."""
    for s in signals:
        ev = s.get("evidence") or {}
        if _norm(str(ev.get("aspect") or "")) not in TENSE_ASPECTS:
            continue
        pa = _norm(str(ev.get("planet_a") or ""))
        pb = _norm(str(ev.get("planet_b") or ""))
        if pa == "venus" or pb == "venus":
            return True
    return False


def _is_mars_dominant(
    signals: list[dict[str, Any]],
    rule_codes: set[str],
) -> bool:
    """
    True if Mars is the primary active planet:
    - Appears in a tense aspect, OR
    - Is placed in an angular house, OR
    - A conflict rule code is present alongside Mars.
    """
    mars_signals = [
        s for s in signals
        if (
            _norm(str((s.get("evidence") or {}).get("planet_a") or "")) == "mars"
            or _norm(str((s.get("evidence") or {}).get("planet_b") or "")) == "mars"
        )
    ]
    if not mars_signals:
        return False
    for s in mars_signals:
        ev = s.get("evidence") or {}
        if _norm(str(ev.get("aspect") or "")) in TENSE_ASPECTS:
            return True
        h = ev.get("transit_house") or ev.get("natal_house")
        if isinstance(h, int) and h in ANGULAR_HOUSES:
            return True
    conflict_codes: frozenset[str] = frozenset(
        {"conflict_relationship", "extreme_conflict", "breakup", "sudden_break"}
    )
    if rule_codes & conflict_codes:
        return True
    return False


def _only_mercury_mars_fast(signals: list[dict[str, Any]]) -> bool:
    """
    True if signals contain ONLY fast planets (Mercury/Mars/Sun/Moon/Venus)
    with no slow planet whatsoever.
    """
    return not has_slow_planet(signals)


# ---------------------------------------------------------------------------
# Primary classifier
# ---------------------------------------------------------------------------

def classify_relationship_conflict_subtype(
    signals: list[dict[str, Any]],
    rule_hits: list[dict[str, Any]],
    num_techniques: int,
    time_window: dict[str, Any] | None = None,
) -> str:
    """
    Classify the most specific relationship conflict subtype from signals.

    Classification priority (highest to lowest):
      1. separacao_termino   — slow planet + Casa 7 + 3+ técnicas + não só rápidos
      2. briga_forte         — Marte central + 2+ técnicas
      3. ciume_posse         — Plutão-Vênus / Lua-Plutão / Marte-Plutão tense
      4. afastamento_emocional — Saturno + não Marte dominante
      5. conversa_seria      — Mercúrio ativo + sem Marte / Plutão dominante
      6. tensao_leve         — fallback (único trânsito rápido)

    Parameters
    ----------
    signals       : Raw signal list (self-aspects are filtered internally)
    rule_hits     : Rule hit list with 'code' keys
    num_techniques: Count of independent astrological techniques active
    time_window   : Optional timing dict (used for future long-window downgrade)

    Returns
    -------
    str: one of 'separacao_termino' | 'briga_forte' | 'ciume_posse' |
         'afastamento_emocional' | 'conversa_seria' | 'tensao_leve'
    """
    clean = filter_self_aspects(signals)
    rule_codes: set[str] = {str(h.get("code") or "") for h in rule_hits}

    # Fast-only with single technique → cap at tensao_leve
    if is_fast_only_transit(clean) and num_techniques <= 1:
        return "tensao_leve"

    has_saturn = _has_planet(clean, "saturn")
    has_uranus = _has_planet(clean, "uranus")
    has_pluto = _has_planet(clean, "pluto")
    has_neptune = _has_planet(clean, "neptune")
    has_mercury = _has_planet(clean, "mercury")
    has_venus = _has_planet(clean, "venus")
    has_mars = _has_planet(clean, "mars")
    has_moon = _has_planet(clean, "moon")

    h7 = _house_7_activated(clean)

    # ── 1. separacao_termino ───────────────────────────────────────────────
    # Requires slow planet + Casa 7 under pressure + 3+ independent techniques
    # + not only Mercury/Mars fast signals
    if (
        (has_saturn or has_uranus or has_pluto)
        and h7
        and num_techniques >= 3
        and not _only_mercury_mars_fast(clean)
    ):
        return "separacao_termino"

    # ── 2. briga_forte ────────────────────────────────────────────────────
    # Mars must be the dominant actor + 2+ techniques
    if has_mars and num_techniques >= 2 and _is_mars_dominant(clean, rule_codes):
        return "briga_forte"

    # ── 3. ciume_posse ────────────────────────────────────────────────────
    # Pluto-Venus, Moon-Pluto, or Mars-Pluto tense; Neptune afflicting Venus
    ciume = (
        _has_hard_aspect_pair(clean, "pluto", "venus")
        or _has_hard_aspect_pair(clean, "moon", "pluto")
        or _has_hard_aspect_pair(clean, "mars", "pluto")
        or (has_neptune and _has_afflicted_venus(clean))
    )
    if ciume:
        return "ciume_posse"

    # ── 4. afastamento_emocional ──────────────────────────────────────────
    # Saturn active but Mars NOT dominant; Venus, Moon, or Casa 7 targeted
    if has_saturn and not _is_mars_dominant(clean, rule_codes):
        saturn_venus = _has_hard_aspect_pair(clean, "saturn", "venus")
        saturn_h7 = _has_planet_in_house(clean, "saturn", 7)
        saturn_moon = _has_hard_aspect_pair(clean, "saturn", "moon")
        if saturn_venus or saturn_h7 or saturn_moon or h7:
            return "afastamento_emocional"

    # ── 5. conversa_seria ─────────────────────────────────────────────────
    # Mercury activated; no Mars dominance; no heavy Pluto-Venus tension
    heavy_pluto = has_pluto and _has_afflicted_venus(clean)
    if has_mercury and not has_mars and not heavy_pluto:
        mercury_active = (
            _has_hard_aspect_pair(clean, "mercury", "mercury")
            or _has_hard_aspect_pair(clean, "mercury", "saturn")
            or _has_hard_aspect_pair(clean, "mercury", "neptune")
            or _has_hard_aspect_pair(clean, "mercury", "pluto")
            or _has_planet(clean, "mercury")  # any Mercury involvement
        )
        if mercury_active:
            return "conversa_seria"

    # ── 6. tensao_leve (fallback) ─────────────────────────────────────────
    return "tensao_leve"
