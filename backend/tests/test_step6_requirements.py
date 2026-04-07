import pytest
from engine.events import generate_events, get_probability_label
from engine.narrative import build_narrative_prompt

def test_probability_labels():
    assert "Confirmado" in get_probability_label(0.95)
    assert "Muito Provável" in get_probability_label(0.85)
    assert "Provável" in get_probability_label(0.75)
    assert "Possível" in get_probability_label(0.65)
    assert "Tendência" in get_probability_label(0.55)
    assert "95%" in get_probability_label(0.95)

def test_generate_events_includes_probability_label():
    analysis = {
        "profile_quality": {"confidence_modifier": 1.0, "code": "A"},
        "signals": [
            {"domain": "financeiro", "technique": "T1", "weight": 0.9, "polarity": "supportive", "label": "S1", "kind": "K1", "evidence": "E1", "time_window": {"start": "2026-01-01", "end": "2026-02-01"}},
            {"domain": "financeiro", "technique": "T2", "weight": 0.9, "polarity": "supportive", "label": "S2", "kind": "K2", "evidence": "E2", "time_window": {"start": "2026-01-01", "end": "2026-02-01"}},
            {"domain": "financeiro", "technique": "T3", "weight": 0.9, "polarity": "supportive", "label": "S3", "kind": "K3", "evidence": "E3", "time_window": {"start": "2026-01-01", "end": "2026-02-01"}},
        ]
    }
    from datetime import date
    events = generate_events(analysis, date(2026, 1, 1))
    assert len(events) > 0
    assert "probability_label" in events[0]
    assert "Confirmado" in events[0]["probability_label"]

def test_narrative_prompt_instructions_include_step6():
    analysis = {
        "profile_quality": {"code": "A"},
        "domain_analysis": {"domains": [], "coverage": []},
    }
    events = []
    event_summary = {"total": 0}
    confidence = {"level": "low"}
    uncertainties = []
    forecast_360 = {}
    timeline = {"periods": []}
    life_episodes = []
    turning_points = []

    prompt_data = build_narrative_prompt(
        analysis, events, event_summary, confidence, uncertainties,
        forecast_360, timeline, life_episodes, turning_points
    )

    prompt_text = prompt_data["prompt"]
    assert "TRADUÇÃO PARA REALIDADE HUMANA" in prompt_text
    assert "NÃO use termos abstratos como energia, vibração, fluxo ou alinhamento." in prompt_text
    assert "Risco:" in prompt_text
    assert "Impacto:" in prompt_text
