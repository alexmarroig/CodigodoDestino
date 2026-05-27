"""Tests for essential_dignity.py — Lilly-style natal dignity scoring."""

from __future__ import annotations

from engine.essential_dignity import (
    apply_dignity_to_transit_signal,
    essential_dignity_score,
    enrich_transit_signals_with_dignity,
    is_positive_dignity,
    is_severe_affliction,
    natal_planet_dignity_scores,
)


def test_essential_dignity_domicile_and_fall():
    assert essential_dignity_score("mars", "aries") == 5
    assert essential_dignity_score("mars", "cancer") == -5
    assert is_positive_dignity(5) is True
    assert is_severe_affliction(-5) is True


def test_supportive_transit_to_debilitated_natal_downgrades():
    signal = {
        "technique": "transits",
        "label": "Júpiter em trígono com Vênus",
        "weight": 0.8,
        "polarity": "supportive",
        "evidence": {
            "aspect": "trine",
            "planet_a": "jupiter",
            "planet_b": "venus",
        },
    }
    scores = {"venus": -5}
    updated = apply_dignity_to_transit_signal(signal, scores)
    assert updated.get("dignity_downgrade") == "conforto_ilusorio"
    assert updated["polarity"] == "mixed"
    assert "ilusório" in updated["label"].lower()


def test_positive_dignity_marks_gain_support():
    signal = {
        "technique": "transits",
        "weight": 0.9,
        "polarity": "supportive",
        "evidence": {"aspect": "trine", "planet_a": "jupiter", "planet_b": "venus"},
    }
    updated = apply_dignity_to_transit_signal(signal, {"venus": 5})
    assert (updated.get("evidence") or {}).get("natal_dignity_supports_gain") is True


def test_natal_planet_dignity_scores_from_ephemeris():
    natal = {
        "planets": {
            "mars": {"longitude": 10.0},  # aries
            "venus": {"longitude": 190.0},  # libra — venus detriment in scorpio? 190 = libra actually
        }
    }
    scores = natal_planet_dignity_scores(natal)
    assert "mars" in scores
    assert scores["mars"] == 5


def test_enrich_transit_signals_with_dignity_batch():
    natal = {"planets": {"sun": {"longitude": 0.0}}}
    signals = [
        {
            "technique": "transits",
            "evidence": {"aspect": "sextile", "planet_a": "jupiter", "planet_b": "sun"},
        }
    ]
    out = enrich_transit_signals_with_dignity(signals, natal)
    assert len(out) == 1
    assert "natal_essential_dignity_score" in out[0]["evidence"]
