"""
Acceptance-style checks for married user, reference 2026-05-27 (UI regressions).
"""

from datetime import date

from engine.cluster_convergence import compute_cluster_metrics
from engine.certainty import resolve_certainty
from engine.event_subtypes import classify_event_subtype
from engine.predictive_insights import _pick_primary_scenario
from engine.signal_enrichment import is_tense_aspect, only_soft_slow_transits


def test_sol_jupiter_not_tense_for_certainty() -> None:
    assert not is_tense_aspect("square", "sun", "jupiter")


def test_soft_saturn_mc_scenario_is_opportunity_not_pressure() -> None:
    signals = [
        {
            "technique": "transits",
            "evidence": {"aspect": "trine", "planet_a": "saturn", "planet_b": "midheaven"},
        },
        {
            "technique": "transits",
            "evidence": {"aspect": "trine", "planet_a": "sun", "planet_b": "midheaven"},
        },
    ]
    scenarios = [
        "Chefe pressiona",
        "Surge proposta ou promoção",
        "Corte ou saída forçada",
    ]
    assert only_soft_slow_transits(signals) or not any(
        s["evidence"]["aspect"] in {"square", "opposition"} for s in signals
    )
    picked = _pick_primary_scenario("career", scenarios, signals)
    assert "proposta" in picked.lower() or "promoção" in picked.lower()


def test_rupture_sol_jupiter_classifies_light_not_termino() -> None:
    signals = [
        {
            "technique": "transits",
            "label": "Sol quadratura Júpiter",
            "domain": "relacionamentos",
            "evidence": {
                "aspect": "square",
                "planet_a": "sun",
                "planet_b": "jupiter",
                "natal_house": 7,
            },
        },
    ]
    subtype = classify_event_subtype(
        category_key="rupture",
        category_signals=signals,
        rule_hits=[],
        life_events=[],
        user_context={"relationship_status": "married", "current_partner_role": "wife"},
    )
    assert subtype in {"tensao_leve", "conversa_seria", None, "afastamento_emocional"}
    assert subtype != "separacao_termino"


def test_married_rupture_certainty_capped_with_single_technique_theme() -> None:
    signals = [
        {
            "technique": "transits",
            "evidence": {"aspect": "square", "planet_a": "sun", "planet_b": "jupiter", "natal_house": 7},
        },
    ]
    metrics = compute_cluster_metrics(signals)
    level = resolve_certainty(
        metrics["effective_independent_signals"],
        signals,
        category_key="rupture",
        theme_convergence=metrics["theme_convergence"],
        has_hard_slow=False,
    )
    assert level in {"chance", "tendency"}


def test_reference_date_placeholder() -> None:
    assert date(2026, 5, 27).isoformat() == "2026-05-27"
