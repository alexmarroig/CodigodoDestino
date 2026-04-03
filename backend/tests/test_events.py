from engine.events import build_domain_analysis, generate_events, summarize_events


def _analysis_fixture() -> dict:
    return {
        "profile_quality": {
            "code": "A",
            "confidence_modifier": 1.0,
        },
        "signals": [
            {
                "technique": "profections",
                "domain": "carreira_status",
                "label": "Profeccao anual ativa a casa 10",
                "weight": 1.0,
                "polarity": "mixed",
                "kind": "annual_theme",
                "time_window": {
                    "start": "2026-01-01",
                    "end": "2026-12-31",
                },
                "evidence": {"activated_house": 10},
            },
            {
                "technique": "solar_return",
                "domain": "carreira_status",
                "label": "Retorno solar concentra foco na casa 10",
                "weight": 0.9,
                "polarity": "mixed",
                "kind": "annual_theme",
                "time_window": {
                    "start": "2026-01-01",
                    "end": "2026-12-31",
                },
                "evidence": {"house": 10},
            },
            {
                "technique": "transits",
                "domain": "carreira_status",
                "label": "Saturn em quadratura com Sun",
                "weight": 0.82,
                "polarity": "challenging",
                "kind": "aspect",
                "time_window": {
                    "start": "2026-04-02",
                    "end": "2026-05-15",
                },
                "evidence": {"aspect": "square", "planet_a": "saturn"},
            },
            {
                "technique": "numerology",
                "domain": "carreira_status",
                "label": "Ano pessoal 8 reforca carreira",
                "weight": 0.35,
                "polarity": "mixed",
                "kind": "numerology",
                "time_window": {
                    "start": "2026-01-01",
                    "end": "2026-12-31",
                },
                "evidence": {"personal_year": 8},
            },
            {
                "technique": "transits",
                "domain": "relacionamentos",
                "label": "Venus em oposicao com Saturn",
                "weight": 0.73,
                "polarity": "challenging",
                "kind": "aspect",
                "time_window": {
                    "start": "2026-04-02",
                    "end": "2026-04-20",
                },
                "evidence": {"aspect": "opposition", "planet_a": "venus"},
            },
            {
                "technique": "profections",
                "domain": "relacionamentos",
                "label": "Profeccao mensal toca a casa 7",
                "weight": 0.66,
                "polarity": "mixed",
                "kind": "annual_theme",
                "time_window": {
                    "start": "2026-04-01",
                    "end": "2026-04-30",
                },
                "evidence": {"activated_house": 7},
            },
        ],
    }


def test_events_require_real_convergence() -> None:
    analysis = _analysis_fixture()
    events = generate_events(analysis, reference_date=__import__("datetime").date(2026, 4, 2))

    assert len(events) == 1
    first_event = events[0]
    assert first_event["type"] == "career_transition"
    assert first_event["domains"] == ["carreira_status"]
    assert len(first_event["signals"]) >= 3
    assert first_event["probability"] >= 0.7
    assert "counter_signals" in first_event


def test_domain_analysis_tracks_uncertainty_when_not_enough_convergence() -> None:
    analysis = _analysis_fixture()
    domain_bundle = build_domain_analysis(analysis)

    relationship_domain = next(
        item for item in domain_bundle["domains"] if item["domain"] == "relacionamentos"
    )
    assert relationship_domain["converged"] is False
    assert any(
        item["domain"] == "relacionamentos"
        for item in domain_bundle["uncertainties"]
    )


def test_event_summary_counts_categories() -> None:
    analysis = _analysis_fixture()
    events = generate_events(analysis, reference_date=__import__("datetime").date(2026, 4, 2))
    summary = summarize_events(events)

    assert summary["total"] == len(events)
    assert summary["highest_priority"] >= max(event["priority"] for event in events)
    assert isinstance(summary["categories"], dict)
