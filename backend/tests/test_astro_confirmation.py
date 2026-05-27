"""
Tests for astro_confirmation.py — confirmation hierarchy, signal scoring,
self-aspect filtering, and relationship subtype classifier.

Key cases from the user's critique:
  - Pluto/Pluto self-aspect → should NOT classify briga_grave or any serious subtype
  - Sun/Jupiter alone (fast-only, no slow planet) → tensao_leve or conversa_seria, NOT briga_forte
  - Mars central + 2 techniques → briga_forte
  - Saturn on Venus + Casa 7 → afastamento_emocional
  - Slow planet + Casa 7 + 3 techniques → separacao_termino
  - Mercury without Mars/Pluto → conversa_seria
  - Pluto-Venus hard → ciume_posse
"""

from __future__ import annotations

import pytest

from engine.astro_confirmation import (
    SLOW_PLANETS,
    FAST_PLANETS,
    classify_relationship_conflict_subtype,
    filter_self_aspects,
    has_slow_planet,
    is_fast_only_transit,
    is_self_aspect,
    orb_weight,
    planet_speed_weight,
    house_angular_weight,
    score_signal,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _signal(planet_a: str, planet_b: str = "", aspect: str = "square",
            technique: str = "transits", house: int | None = None,
            orb: float | None = None, weight: float = 1.0) -> dict:
    evidence: dict = {"planet_a": planet_a, "aspect": aspect}
    if planet_b:
        evidence["planet_b"] = planet_b
    if house is not None:
        evidence["transit_house"] = house
    if orb is not None:
        evidence["orb"] = orb
    return {"technique": technique, "weight": weight, "evidence": evidence}


def _rule(code: str, weight: float = 3.0) -> dict:
    return {"code": code, "weight": weight, "label": code}


# ---------------------------------------------------------------------------
# planet_speed_weight
# ---------------------------------------------------------------------------

def test_slow_planets_weight_2():
    for p in ["saturn", "uranus", "neptune", "pluto"]:
        assert planet_speed_weight(p) == 2.0


def test_fast_planets_weight_1():
    for p in ["sun", "moon", "mercury", "venus", "mars"]:
        assert planet_speed_weight(p) == 1.0


def test_unknown_planet_weight_1():
    assert planet_speed_weight("chiron") == 1.0


# ---------------------------------------------------------------------------
# orb_weight
# ---------------------------------------------------------------------------

def test_exact_orb_weight():
    assert orb_weight(0.5) == 2.0


def test_moderate_orb_weight():
    assert orb_weight(2.0) == 1.5


def test_wide_orb_weight():
    assert orb_weight(5.0) == 1.0


def test_none_orb_weight():
    assert orb_weight(None) == 1.0


# ---------------------------------------------------------------------------
# house_angular_weight
# ---------------------------------------------------------------------------

def test_angular_houses_weight():
    for h in [1, 4, 7, 10]:
        assert house_angular_weight(h) == 1.5


def test_non_angular_house_weight():
    for h in [2, 3, 5, 6, 8, 9, 11, 12]:
        assert house_angular_weight(h) == 1.0


def test_none_house_weight():
    assert house_angular_weight(None) == 1.0


# ---------------------------------------------------------------------------
# is_self_aspect / filter_self_aspects
# ---------------------------------------------------------------------------

def test_pluto_pluto_is_self_aspect():
    s = _signal("pluto", "pluto", "conjunction")
    assert is_self_aspect(s) is True


def test_sun_sun_is_self_aspect():
    s = _signal("sun", "sun", "conjunction")
    assert is_self_aspect(s) is True


def test_different_planets_not_self_aspect():
    s = _signal("mars", "saturn", "square")
    assert is_self_aspect(s) is False


def test_single_planet_not_self_aspect():
    s = _signal("pluto", "", "conjunction")
    assert is_self_aspect(s) is False


def test_filter_self_aspects_removes_same_body():
    signals = [
        _signal("pluto", "pluto", "conjunction"),
        _signal("mars", "saturn", "square"),
        _signal("sun", "sun", "conjunction"),
    ]
    filtered = filter_self_aspects(signals)
    assert len(filtered) == 1
    assert filtered[0]["evidence"]["planet_a"] == "mars"


def test_filter_self_aspects_empty():
    assert filter_self_aspects([]) == []


# ---------------------------------------------------------------------------
# score_signal
# ---------------------------------------------------------------------------

def test_self_aspect_scores_zero():
    s = _signal("pluto", "pluto", "conjunction")
    assert score_signal(s) == 0.0


def test_slow_planet_scores_higher():
    slow = _signal("saturn", "venus", "square", weight=1.0)
    fast = _signal("mars", "venus", "square", weight=1.0)
    assert score_signal(slow) > score_signal(fast)


def test_angular_house_scores_higher():
    angular = _signal("mars", "venus", "square", house=7, weight=1.0)
    cadent = _signal("mars", "venus", "square", house=3, weight=1.0)
    assert score_signal(angular) > score_signal(cadent)


def test_exact_orb_scores_higher():
    exact = _signal("saturn", "venus", "square", orb=0.5, weight=1.0)
    wide = _signal("saturn", "venus", "square", orb=6.0, weight=1.0)
    assert score_signal(exact) > score_signal(wide)


# ---------------------------------------------------------------------------
# has_slow_planet / is_fast_only_transit
# ---------------------------------------------------------------------------

def test_has_slow_planet_true():
    signals = [_signal("saturn", "moon", "square")]
    assert has_slow_planet(signals) is True


def test_has_slow_planet_false():
    signals = [_signal("mars", "venus", "square"), _signal("sun", "moon", "opposition")]
    assert has_slow_planet(signals) is False


def test_self_aspect_not_counted_as_slow():
    # Pluto/Pluto self-aspect should be filtered and not count as slow planet
    signals = [_signal("pluto", "pluto", "conjunction")]
    assert has_slow_planet(signals) is False


def test_fast_only_transit_true():
    signals = [_signal("sun", "jupiter", "square"), _signal("mars", "venus", "opposition")]
    assert is_fast_only_transit(signals) is True


def test_fast_only_transit_false_with_slow():
    signals = [_signal("sun", "jupiter", "square"), _signal("saturn", "venus", "square")]
    assert is_fast_only_transit(signals) is False


# ---------------------------------------------------------------------------
# classify_relationship_conflict_subtype — core cases
# ---------------------------------------------------------------------------

class TestSeparacaoTermino:
    def test_sun_jupiter_h7_with_slow_elsewhere_not_separacao(self):
        """Sun/Jupiter in H7 alone must not qualify as separacao even with 3 techniques."""
        signals = [
            _signal("sun", "jupiter", "square", technique="transits", house=7),
            _signal("mercury", "saturn", "square", technique="progressions"),
            _signal("moon", "uranus", "trine", technique="solar_return"),
        ]
        result = classify_relationship_conflict_subtype(signals, [], num_techniques=3)
        assert result != "separacao_termino"

    def test_neptune_pluto_solar_arc_not_separacao(self):
        signals = [
            _signal("neptune", "pluto", "conjunction", technique="solar_arc"),
            _signal("sun", "jupiter", "square", technique="transits", house=7),
            _signal("saturn", "venus", "square", technique="transits", house=7),
        ]
        result = classify_relationship_conflict_subtype(signals, [], num_techniques=3)
        assert result == "separacao_termino"

    def test_slow_planet_h7_3_techniques(self):
        signals = [
            _signal("saturn", "venus", "square", technique="transits", house=7),
            _signal("pluto", "venus", "opposition", technique="progressions"),
            _signal("uranus", "sun", "square", technique="solar_return"),
        ]
        result = classify_relationship_conflict_subtype(signals, [], num_techniques=3)
        assert result == "separacao_termino"

    def test_requires_3_techniques_minimum(self):
        signals = [
            _signal("saturn", "venus", "square", technique="transits", house=7),
            _signal("pluto", "venus", "opposition", technique="progressions"),
        ]
        result = classify_relationship_conflict_subtype(signals, [], num_techniques=2)
        assert result != "separacao_termino"


class TestBrigaForte:
    def test_mars_central_2_techniques(self):
        signals = [
            _signal("mars", "moon", "square", technique="transits", house=7),
            _signal("mars", "saturn", "opposition", technique="progressions"),
        ]
        rule_hits = [_rule("conflict_relationship")]
        result = classify_relationship_conflict_subtype(signals, rule_hits, num_techniques=2)
        assert result == "briga_forte"

    def test_mars_without_dominance_not_briga_forte(self):
        # Mars present but with trine only (not dominant)
        signals = [
            _signal("mars", "venus", "trine", technique="transits"),
        ]
        result = classify_relationship_conflict_subtype(signals, [], num_techniques=1)
        # Should NOT be briga_forte since Mars is not dominant
        assert result != "briga_forte"


class TestCiumePosse:
    def test_pluto_venus_hard(self):
        signals = [_signal("pluto", "venus", "square", technique="transits")]
        result = classify_relationship_conflict_subtype(signals, [], num_techniques=1)
        assert result == "ciume_posse"

    def test_moon_pluto_hard(self):
        signals = [_signal("moon", "pluto", "opposition", technique="transits")]
        result = classify_relationship_conflict_subtype(signals, [], num_techniques=1)
        assert result == "ciume_posse"

    def test_mars_pluto_hard(self):
        signals = [_signal("mars", "pluto", "square", technique="transits")]
        result = classify_relationship_conflict_subtype(signals, [], num_techniques=1)
        assert result == "ciume_posse"


class TestAfastamentoEmocional:
    def test_saturn_venus_no_mars(self):
        signals = [_signal("saturn", "venus", "square", technique="transits")]
        result = classify_relationship_conflict_subtype(signals, [], num_techniques=1)
        assert result == "afastamento_emocional"

    def test_saturn_moon_no_mars(self):
        signals = [_signal("saturn", "moon", "square", technique="transits")]
        result = classify_relationship_conflict_subtype(signals, [], num_techniques=1)
        assert result == "afastamento_emocional"

    def test_saturn_h7_no_mars(self):
        signals = [_signal("saturn", "", "conjunction", house=7, technique="transits")]
        result = classify_relationship_conflict_subtype(signals, [], num_techniques=1)
        assert result == "afastamento_emocional"

    def test_saturn_with_mars_dominant_not_afastamento(self):
        signals = [
            _signal("saturn", "moon", "square", technique="transits"),
            _signal("mars", "venus", "square", technique="transits", house=7),
        ]
        rule_hits = [_rule("conflict_relationship")]
        result = classify_relationship_conflict_subtype(signals, rule_hits, num_techniques=2)
        # Mars dominant → should NOT be afastamento_emocional
        assert result != "afastamento_emocional"


class TestConversa:
    def test_mercury_no_mars(self):
        signals = [_signal("mercury", "saturn", "square", technique="transits")]
        result = classify_relationship_conflict_subtype(signals, [], num_techniques=1)
        assert result == "conversa_seria"

    def test_mercury_with_mars_not_conversa(self):
        signals = [
            _signal("mercury", "saturn", "square", technique="transits"),
            _signal("mars", "moon", "square", technique="transits", house=7),
        ]
        rule_hits = [_rule("conflict_relationship")]
        result = classify_relationship_conflict_subtype(signals, rule_hits, num_techniques=2)
        assert result != "conversa_seria"

    def test_mercury_neptune_no_mars(self):
        signals = [_signal("mercury", "neptune", "opposition", technique="transits")]
        result = classify_relationship_conflict_subtype(signals, [], num_techniques=1)
        assert result == "conversa_seria"


class TestTensaoLeve:
    def test_fast_only_single_technique(self):
        signals = [_signal("sun", "jupiter", "square", technique="transits")]
        result = classify_relationship_conflict_subtype(signals, [], num_techniques=1)
        assert result == "tensao_leve"

    def test_pluto_pluto_self_aspect_fast_only(self):
        # Pluto/Pluto self-aspect filtered out → effectively empty/fast-only
        signals = [
            _signal("pluto", "pluto", "conjunction", technique="progressions"),
            _signal("sun", "jupiter", "square", technique="transits"),
        ]
        result = classify_relationship_conflict_subtype(signals, [], num_techniques=1)
        # After self-aspect filter, only Sun/Jupiter remains → tensao_leve
        assert result == "tensao_leve"

    def test_sun_jupiter_not_briga_grave(self):
        """Original bug: Sun/Jupiter alone should NOT classify as briga_forte or separacao_termino."""
        signals = [_signal("sun", "jupiter", "square", technique="transits")]
        result = classify_relationship_conflict_subtype(signals, [], num_techniques=1)
        assert result not in {"briga_forte", "separacao_termino", "ciume_posse"}

    def test_pluto_pluto_not_serious_conflict(self):
        """Pluto/Pluto self-aspect should NOT trigger serious conflict classification."""
        signals = [_signal("pluto", "pluto", "conjunction", technique="progressions")]
        result = classify_relationship_conflict_subtype(signals, [], num_techniques=1)
        # No meaningful signals after filter → tensao_leve
        assert result == "tensao_leve"


# ---------------------------------------------------------------------------
# Integration: subtype definitions include new types
# ---------------------------------------------------------------------------

def test_new_subtypes_in_definitions():
    from engine.event_subtypes import SUBTYPE_DEFINITIONS
    for key in ["separacao_termino", "briga_forte", "ciume_posse",
                "afastamento_emocional", "conversa_seria", "tensao_leve"]:
        assert key in SUBTYPE_DEFINITIONS, f"Missing subtype: {key}"


def test_new_subtypes_in_rupture_category():
    from engine.event_subtypes import CATEGORY_SUBTYPES
    rupture_keys = CATEGORY_SUBTYPES.get("rupture", [])
    for key in ["separacao_termino", "briga_forte", "ciume_posse",
                "afastamento_emocional", "conversa_seria", "tensao_leve"]:
        assert key in rupture_keys, f"'{key}' missing from rupture category"


def test_classify_event_subtype_rupture_uses_new_classifier():
    """classify_event_subtype for rupture category should return new subtype keys."""
    from engine.event_subtypes import classify_event_subtype
    signals = [
        {"technique": "transits", "domain": "relacionamentos", "polarity": "challenging",
         "weight": 2.0, "evidence": {"planet_a": "saturn", "planet_b": "venus", "aspect": "square"}},
    ]
    rule_hits = [{"code": "relationship_block", "weight": 3.5, "label": "Bloqueio relacional"}]
    result = classify_event_subtype("rupture", signals, rule_hits, [], {})
    assert result == "afastamento_emocional"


def test_classify_event_subtype_pluto_pluto_not_briga_grave():
    """Pluto/Pluto self-aspect in rupture category should NOT classify as briga_forte."""
    from engine.event_subtypes import classify_event_subtype
    signals = [
        {"technique": "progressions", "domain": "relacionamentos", "polarity": "challenging",
         "weight": 3.0, "evidence": {"planet_a": "pluto", "planet_b": "pluto", "aspect": "conjunction"}},
    ]
    rule_hits = [{"code": "relationship_test", "weight": 2.0, "label": "Teste relacional"}]
    result = classify_event_subtype("rupture", signals, rule_hits, [], {})
    # After self-aspect filtering, no meaningful signals → tensao_leve
    assert result not in {"briga_forte", "separacao_termino", "ciume_posse"}


def test_build_subtype_text_for_briga_forte():
    from datetime import date
    from engine.event_subtypes import build_subtype_text
    signals = [
        {"technique": "transits", "label": "Marte sq Lua", "weight": 3.0,
         "evidence": {"aspect": "square", "planet_a": "mars", "planet_b": "moon", "transit_house": 7}},
    ]
    rule_hits = [{"code": "conflict_relationship", "weight": 3.5, "label": "Conflito relacional"}]
    result = build_subtype_text(
        "briga_forte",
        signals=signals,
        rule_hits=rule_hits,
        reference_date=date(2026, 6, 1),
        user_context={},
        independent_signals=2,
        time_window={"start": "2026-06-01", "end": "2026-07-01", "peak": "2026-06-15"},
    )
    assert result["subtype_key"] == "briga_forte"
    assert "marte" in result["subtype_what"].lower() or "confronto" in result["subtype_what"].lower()


def test_build_subtype_text_for_separacao_termino():
    from datetime import date
    from engine.event_subtypes import build_subtype_text
    signals = [
        {"technique": "transits", "label": "Saturno sq Vênus", "weight": 4.0,
         "evidence": {"aspect": "square", "planet_a": "saturn", "planet_b": "venus", "transit_house": 7}},
    ]
    rule_hits = [{"code": "breakup", "weight": 4.0, "label": "Ruptura detectada"}]
    result = build_subtype_text(
        "separacao_termino",
        signals=signals,
        rule_hits=rule_hits,
        reference_date=date(2026, 6, 1),
        user_context={},
        independent_signals=3,
        time_window={"start": "2026-06-01", "end": "2026-07-31", "peak": "2026-06-20"},
    )
    assert result["subtype_key"] == "separacao_termino"
    assert "encerramento" in result["subtype_what"].lower() or "término" in result["subtype_what"].lower()
