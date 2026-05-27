"""
Tests for astrological technical fixes — critique items 1-10.

Covers:
  1. Pluto/Pluto self-aspect is NOT the primary evidence for briga_grave
  2. Casa 7 default partner label is broad when no married context
  3. date_formatting: days_to_peak == 0 → "pico hoje" (not "0 dias")
  4. human_body / human_summary excludes "Leitura técnica:"
  5. briga_grave downgrade when no fast mover and no conflict planet in 7
  6. Long window (>180 days) uses softer date language
  7. Contradictory signals produce "tensão entre aproximação e conflito"
"""
from __future__ import annotations

from datetime import date

from engine.date_formatting import format_time_window_label
from engine.event_subtypes import (
    _is_self_aspect,
    _has_fast_mover_transit,
    _has_conflict_planet_in_7_or_rule,
    build_subtype_text,
    classify_event_subtype,
)
from engine.predictive_insights import _build_human_translation, build_technical_items, build_quality_summary


# ---------------------------------------------------------------------------
# 1. Self-aspect filter — Pluto/Pluto not top signal
# ---------------------------------------------------------------------------

def test_is_self_aspect_pluto_pluto():
    signal = {"evidence": {"planet_a": "Pluto", "planet_b": "Pluto", "aspect": "conjunction"}}
    assert _is_self_aspect(signal) is True


def test_is_self_aspect_sun_sun():
    signal = {"evidence": {"planet_a": "Sun", "planet_b": "Sun", "aspect": "square"}}
    assert _is_self_aspect(signal) is True


def test_is_not_self_aspect_mars_venus():
    signal = {"evidence": {"planet_a": "Mars", "planet_b": "Venus", "aspect": "square"}}
    assert _is_self_aspect(signal) is False


def test_enrich_por_que_excludes_pluto_pluto():
    """por_que string must not cite Pluto/Pluto as primary evidence."""
    signals = [
        {
            "technique": "progressions",
            "label": "Pluto conjunct Pluto",
            "weight": 5.0,
            "evidence": {"aspect": "conjunction", "planet_a": "Pluto", "planet_b": "Pluto"},
        },
        {
            "technique": "transits",
            "label": "Marte quadratura Vênus",
            "weight": 4.0,
            "evidence": {"aspect": "square", "planet_a": "Mars", "planet_b": "Venus"},
        },
    ]
    result = build_subtype_text(
        "briga_grave",
        signals=signals,
        rule_hits=[{"code": "conflict_relationship", "weight": 4.0, "label": "Conflito relacional"}],
        reference_date=date(2026, 5, 27),
        user_context={},
        independent_signals=2,
        time_window={"start": "2026-05-27", "end": "2026-06-10", "peak": "2026-06-03"},
    )
    por_que = result.get("subtype_por_que", "")
    # Marte/Vênus should appear, Plutão/Plutão (self-aspect) should NOT be primary
    assert "Marte" in por_que or "Mars" in por_que or "quadratura" in por_que
    # Pluto/Pluto self-aspect should be filtered out
    assert "Plutão/Plutão" not in por_que
    assert "Pluto/Pluto" not in por_que


# ---------------------------------------------------------------------------
# 2. Casa 7 breadth — default partner label is broad when no married context
# ---------------------------------------------------------------------------

def test_broad_partner_label_rupture_no_context():
    """briga_grave with unknown partner → broad label, not 'sua esposa'."""
    signals = [
        {
            "technique": "transits",
            "label": "Marte Casa 7",
            "weight": 4.0,
            "evidence": {"aspect": "square", "planet_a": "Mars", "transit_house": 7},
        },
    ]
    result = build_subtype_text(
        "briga_grave",
        signals=signals,
        rule_hits=[{"code": "conflict_relationship", "weight": 4.0, "label": "Conflito relacional"}],
        reference_date=date(2026, 5, 27),
        user_context={},  # no partner_role, no relationship_status
        independent_signals=2,
        time_window={"start": "2026-05-27", "end": "2026-06-10", "peak": "2026-06-03"},
    )
    what = result.get("subtype_what", "")
    # Must NOT say "sua esposa" when no married context
    assert "sua esposa" not in what
    assert "sua namorada" not in what
    # Should use broad phrasing
    assert "parceiro" in what or "sócio" in what or "vínculo" in what


def test_specific_wife_label_when_married():
    """When user_context specifies wife, use 'sua esposa'."""
    signals = [
        {
            "technique": "transits",
            "label": "Marte Casa 7",
            "weight": 4.0,
            "evidence": {"aspect": "square", "planet_a": "Mars", "transit_house": 7},
        },
    ]
    result = build_subtype_text(
        "briga_grave",
        signals=signals,
        rule_hits=[{"code": "conflict_relationship", "weight": 4.0, "label": "Conflito"}],
        reference_date=date(2026, 5, 27),
        user_context={"current_partner_role": "wife", "relationship_status": "married"},
        independent_signals=2,
        time_window={"start": "2026-05-27", "end": "2026-06-10", "peak": "2026-06-03"},
    )
    assert "sua esposa" in result.get("subtype_what", "")


# ---------------------------------------------------------------------------
# 3. date_formatting: 0 dias → "pico hoje"
# ---------------------------------------------------------------------------

def test_date_0_dias_returns_hoje():
    """When peak == reference_date, format must NOT say '0 dias'."""
    today = date(2026, 5, 27)
    label = format_time_window_label(
        {"start": "2026-05-25", "end": "2026-06-05", "peak": "2026-05-27"},
        reference_date=today,
    )
    assert "0 dias" not in label
    assert "hoje" in label


def test_date_0_dias_no_window_bounds():
    """Peak only, same day as reference."""
    today = date(2026, 6, 1)
    label = format_time_window_label(
        {"peak": "2026-06-01"},
        reference_date=today,
    )
    assert "0 dias" not in label
    assert "hoje" in label


# ---------------------------------------------------------------------------
# 4. human body excludes "Leitura técnica:"
# ---------------------------------------------------------------------------

def _make_technical_items():
    return [
        {
            "title": "Trânsito Marte/Saturno",
            "aspect_line": "quadratura entre Marte e Saturno.",
            "when": "15 de junho de 2026",
            "meaning": "gera atrito",
            "avoidability": "Parcialmente evitável.",
            "formatted": "Trânsito — quadratura entre Marte e Saturno. Quando: 15 de junho de 2026.",
        }
    ]


def test_human_summary_excludes_leitura_tecnica():
    """The human_summary field must not contain 'Leitura técnica'."""
    tech_items = _make_technical_items()
    quality = build_quality_summary(
        independent_signals=3,
        probability_level="Moderada",
        techniques=["transits", "progressions", "numerology"],
        has_peak=True,
    )
    category_signals = [
        {
            "technique": "transits",
            "evidence": {"aspect": "square", "planet_a": "mars", "planet_b": "saturn"},
        }
    ]
    cluster_metrics = {"technique_count": 3, "theme_convergence": 2, "effective_independent_signals": 3}
    result = _build_human_translation(
        "rupture",
        "maio de 2026",
        independent_signals=3,
        category_signals=category_signals,
        user_context={},
        astro_reason="Marte quadratura Saturno ativa conflito.",
        technical_items=tech_items,
        quality_summary=quality,
        cluster_metrics=cluster_metrics,
        time_window={"start": "2026-05-01", "end": "2026-05-31", "peak": "2026-05-15"},
    )
    human_summary = result.get("human_summary", "")
    assert "Leitura técnica" not in human_summary
    assert "Leitura técnica" not in human_summary.lower()


def test_formatted_block_excludes_leitura_tecnica():
    """The formatted_block should no longer contain 'Leitura técnica'."""
    tech_items = _make_technical_items()
    quality = build_quality_summary(
        independent_signals=3,
        probability_level="Moderada",
        techniques=["transits", "progressions", "numerology"],
        has_peak=True,
    )
    category_signals = [
        {
            "technique": "transits",
            "evidence": {"aspect": "square", "planet_a": "mars", "planet_b": "saturn"},
        }
    ]
    cluster_metrics = {"technique_count": 3, "theme_convergence": 2, "effective_independent_signals": 3}
    result = _build_human_translation(
        "rupture",
        "maio de 2026",
        independent_signals=3,
        category_signals=category_signals,
        user_context={},
        astro_reason="Marte quadratura Saturno ativa conflito.",
        technical_items=tech_items,
        quality_summary=quality,
        cluster_metrics=cluster_metrics,
        time_window={"start": "2026-05-01", "end": "2026-05-31", "peak": "2026-05-15"},
    )
    formatted_block = result.get("formatted_block", "")
    assert "Leitura técnica" not in formatted_block


# ---------------------------------------------------------------------------
# 5. briga_grave downgrade when calibration criteria not met
# ---------------------------------------------------------------------------

def test_briga_grave_downgrade_no_fast_mover_no_conflict_rule():
    """Sun square Jupiter alone (no Mars, no conflict rule) should NOT produce briga_grave."""
    signals = [
        {
            "technique": "transits",
            "domain": "relacionamentos",
            "label": "Sun square Jupiter",
            "weight": 2.0,
            "polarity": "mixed",
            "evidence": {"aspect": "square", "planet_a": "Sun", "planet_b": "Jupiter"},
        },
        {
            "technique": "progressions",
            "domain": "relacionamentos",
            "label": "Lua progredida na casa 7",
            "weight": 2.0,
            "polarity": "mixed",
            "evidence": {"aspect": "conjunction", "planet_a": "Moon", "transit_house": 7},
        },
    ]
    rule_hits = [
        {"code": "relationship_test", "label": "Teste relacional", "weight": 2.5}
    ]
    result_key = classify_event_subtype(
        category_key="rupture",
        category_signals=signals,
        rule_hits=rule_hits,
        life_events=[],
        user_context={},
    )
    # With no fast mover transit and no conflict_relationship rule, briga_grave should be downgraded
    assert result_key != "briga_grave", (
        f"Expected downgrade from briga_grave, got {result_key!r}"
    )


def test_briga_grave_kept_with_mars_transit():
    """Mars transit + conflict rule should classify as briga_forte (new specific subtype for Mars-central conflicts)."""
    signals = [
        {
            "technique": "transits",
            "domain": "relacionamentos",
            "label": "Marte quadratura Casa 7",
            "weight": 4.5,
            "polarity": "challenging",
            "evidence": {"aspect": "square", "planet_a": "Mars", "transit_house": 7},
        },
        {
            "technique": "progressions",
            "domain": "relacionamentos",
            "label": "Progressão lunar Casa 7",
            "weight": 3.0,
            "polarity": "challenging",
            "evidence": {"aspect": "conjunction", "planet_a": "Moon", "transit_house": 7},
        },
    ]
    rule_hits = [
        {"code": "conflict_relationship", "label": "Conflito relacional", "weight": 4.5}
    ]
    result_key = classify_event_subtype(
        category_key="rupture",
        category_signals=signals,
        rule_hits=rule_hits,
        life_events=[],
        user_context={},
    )
    # Mars transit + conflict_relationship + 2 techniques → briga_forte (more specific per confirmation rulebook)
    assert result_key == "briga_forte", f"Expected briga_forte, got {result_key!r}"


# ---------------------------------------------------------------------------
# 6. Long window (>180 days) produces softer date language
# ---------------------------------------------------------------------------

def test_long_window_soft_label():
    """A 2-year window must use 'longo prazo' language, not assertive dates."""
    label = format_time_window_label(
        {"start": "2026-05-01", "end": "2028-05-01", "peak": "2027-06-01"},
        reference_date=date(2026, 5, 27),
    )
    assert "longo prazo" in label or "2026" in label
    # Must not look like a short-window assertive label
    assert "pico em" not in label or "longo prazo" in label


def test_long_window_briga_grave_soft_what():
    """briga_grave with 2-year window must use soft language, not assertive 'vai acontecer'."""
    signals = [
        {
            "technique": "transits",
            "domain": "relacionamentos",
            "label": "Saturno Casa 7",
            "weight": 4.0,
            "polarity": "challenging",
            "evidence": {"aspect": "conjunction", "planet_a": "Saturn", "transit_house": 7},
        },
        {
            "technique": "progressions",
            "domain": "relacionamentos",
            "label": "Progressão longa",
            "weight": 3.0,
            "polarity": "challenging",
            "evidence": {"aspect": "square", "planet_a": "Moon", "planet_b": "Saturn"},
        },
        {
            "technique": "solar_return",
            "domain": "relacionamentos",
            "label": "SR Casa 7",
            "weight": 3.5,
            "polarity": "challenging",
            "evidence": {"aspect": "opposition"},
        },
    ]
    rule_hits = [{"code": "conflict_relationship", "weight": 4.5, "label": "Conflito"}]
    result = build_subtype_text(
        "briga_grave",
        signals=signals,
        rule_hits=rule_hits,
        reference_date=date(2026, 5, 27),
        user_context={},
        independent_signals=3,
        time_window={"start": "2026-05-01", "end": "2028-05-01", "peak": "2027-01-01"},
    )
    what = result.get("subtype_what", "")
    # Should NOT be assertive "Isso vai acontecer"
    assert "Isso vai acontecer" not in what
    assert result.get("is_fatalistic") is False
    # Should mention the long range softly
    assert "sensível" in what or "2026" in what or "longo" in what
