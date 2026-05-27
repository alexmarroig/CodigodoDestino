"""Tests for signal_enrichment.py — Brady fields and hard-aspect gates."""

from __future__ import annotations

from engine.signal_enrichment import (
    enrich_brady_evidence,
    format_brady_por_que_line,
    has_hard_slow_transit,
    only_soft_slow_transits,
    soft_aspect_opportunity_note,
    subtype_requires_hard_aspect,
)


def test_enrich_brady_evidence_adds_cause_action_effect():
    ev = enrich_brady_evidence(
        {"aspect": "square", "transit_house": 10, "natal_house": 2}
    )
    assert ev["aspect_nature"] == "choque e tensão"
    assert ev["cause_house_theme"] == "carreira e status"
    assert ev["effect_house_theme"] == "dinheiro e recursos"


def test_format_brady_por_que_line_pt():
    line = format_brady_por_que_line(
        {
            "aspect": "opposition",
            "transit_house": 7,
            "natal_house": 1,
            "aspect_nature": "conflito ou polarização (muitas vezes com terceiros)",
            "cause_house_theme": "parcerias e contratos",
            "effect_house_theme": "identidade e corpo",
        }
    )
    assert line is not None
    assert "Causa:" in line
    assert "Ação:" in line
    assert "Efeito:" in line


def test_has_hard_slow_transit():
    signals = [
        {
            "technique": "transits",
            "evidence": {"aspect": "trine", "planet_a": "saturn", "planet_b": "moon"},
        }
    ]
    assert has_hard_slow_transit(signals) is False
    signals[0]["evidence"]["aspect"] = "square"
    assert has_hard_slow_transit(signals) is True


def test_only_soft_slow_transits_note():
    signals = [
        {
            "technique": "transits",
            "evidence": {"aspect": "trine", "planet_a": "pluto", "planet_b": "venus"},
        }
    ]
    assert only_soft_slow_transits(signals) is True
    note = soft_aspect_opportunity_note(signals)
    assert note is not None
    assert "oportunidade" in note.lower()


def test_subtype_requires_hard_aspect_for_crises():
    assert subtype_requires_hard_aspect("crise_saude") is True
    assert subtype_requires_hard_aspect("doenca_leve") is False
