from datetime import date

from engine.destiny_narrative import build_destiny_sections


def _fixture_payload() -> dict:
    return {
        "date": "1995-03-10",
        "user_context": {
            "relationship_status": "separated",
            "father_status": "deceased",
            "mother_relationship": "conflict",
            "major_trauma_notes": "Abandono na infancia",
            "marked_separation": True,
        },
    }


def _fixture_analysis() -> dict:
    return {
        "user_context": _fixture_payload()["user_context"],
        "related_people": [],
        "signals": [],
        "rule_hits": [
            {"code": "emotional_low", "label": "Baixa emocional", "domain": "psicologico_espiritual", "weight": 4.0},
            {"code": "breakup", "label": "Ruptura afetiva", "domain": "relacionamentos", "weight": 4.5},
        ],
        "relationship_analysis": {"summary": "Relacao em teste.", "signals": ["Venus pressionada"]},
        "financial_analysis": {"summary": "Dinheiro apertado.", "signals": []},
        "domain_analysis": {
            "domains": [
                {
                    "domain": "psicologico_espiritual",
                    "domain_label": "Psicologico",
                    "tone": "pressao",
                    "converged": True,
                    "summary": "Instabilidade emocional.",
                }
            ]
        },
        "predictive_insights": {
            "detected_events": [
                {
                    "category_key": "rupture",
                    "event_type": "Briga, ruptura ou separacao",
                    "independent_signals": 4,
                    "time_window": {"label": "dentro de 2 a 4 meses", "start": "2026-05-01", "end": "2026-08-01"},
                    "what_is_happening": "Isso vai acontecer: ruptura afetiva.",
                    "what_this_may_look_like_in_real_life": ["Discussao que muda tudo."],
                    "possible_scenarios": ["Separacao."],
                    "signals": ["Marte oposicao"],
                    "rule_hits": ["Ruptura"],
                }
            ],
            "watchlist": [],
            "summary": {},
        },
        "life_story": {"chapters": [{"headline": "Crise aos 28", "age": 28}]},
    }


def test_build_destiny_sections_returns_twelve_sections() -> None:
    sections = build_destiny_sections(
        payload=_fixture_payload(),
        computed={
            "astrology": {
                "signs": {
                    "Sun": {"sign": "Peixes"},
                    "Moon": {"sign": "Escorpiao"},
                    "Asc": {"sign": "Leao"},
                }
            },
            "numerology": {"life_path_number": 1, "personal_year": {"value": 9}},
        },
        analysis=_fixture_analysis(),
        narrative={"text": "Seu destino aponta ruptura e reconstrucao."},
        forecast_360={"areas_da_vida": [], "critical_periods": []},
        timeline={"periods": []},
        life_episodes=[],
        turning_points=[{"date": "2026-06-01", "headline": "Virada afetiva"}],
        reference_date=date(2026, 4, 4),
    )

    assert len(sections) == 12
    assert sections[0]["id"] == "central_reading"
    assert sections[8]["id"] == "life_timeline"
    assert "Abandono" in sections[8]["body"] or "infancia" in sections[8]["body"].lower()
    assert sections[0]["certainty_level"] in {"chance", "tendency", "must", "will"}


# ---------------------------------------------------------------------------
# Task 13: Smoke test for acidente_fisico subtype in destiny pipeline
# ---------------------------------------------------------------------------

def _minimal_analysis_acidente_fisico() -> dict:
    return {
        "user_context": {},
        "related_people": [],
        "signals": [
            {
                "technique": t,
                "domain": "saude_rotina",
                "label": f"Marte pressão saúde {t}",
                "weight": 0.85,
                "polarity": "challenging",
                "time_window": {
                    "start": "2026-05-15",
                    "end": "2026-07-10",
                    "peak": "2026-06-10",
                },
                "evidence": {"aspect": "square", "planet_a": "mars", "planet_b": "saturn"},
            }
            for t in ["transits", "progressions", "solar_return"]
        ],
        "rule_hits": [
            {"code": "accident_risk", "weight": 4.5, "label": "Risco físico elevado",
             "domain": "saude_rotina"}
        ],
        "life_events": [],
        "relationship_analysis": {"summary": "", "signals": []},
        "financial_analysis": {"summary": "", "signals": []},
        "domain_analysis": {"domains": []},
        "life_story": {"chapters": []},
        "predictive_insights": {},
    }


def test_destiny_sections_with_acidente_fisico_subtype():
    sections = build_destiny_sections(
        payload={"date": "1990-03-15", "user_context": {}},
        computed={
            "astrology": {"signs": {"Sun": {"sign": "Peixes"}, "Moon": {"sign": "Touro"}, "Asc": {"sign": "Leão"}}},
            "numerology": {"life_path_number": 3, "personal_year": {"value": 5}},
        },
        analysis=_minimal_analysis_acidente_fisico(),
        narrative={"text": "Período de atenção à saúde."},
        forecast_360={"areas_da_vida": [], "critical_periods": []},
        timeline={"periods": []},
        life_episodes=[],
        turning_points=[],
        reference_date=date(2026, 6, 1),
    )
    assert isinstance(sections, list)
    section_ids = {s["id"] for s in sections}
    assert "future_events" in section_ids or "critical_cycles" in section_ids


# ---------------------------------------------------------------------------
# Readability quality checks
# ---------------------------------------------------------------------------

def _build_sections_with_rupture() -> list[dict]:
    """Build sections with a rupture event for readability checks."""
    analysis = _fixture_analysis()
    # Add enough signals for rupture to be detected
    analysis["signals"] = [
        {
            "technique": t,
            "domain": "relacionamentos",
            "label": f"Ruptura sinal {t}",
            "weight": 0.8,
            "polarity": "challenging",
            "time_window": {"start": "2026-05-01", "end": "2026-08-01", "peak": "2026-06-15"},
            "evidence": {"aspect": "square", "planet_a": "mars", "planet_b": "venus"},
        }
        for t in ["transits", "progressions", "solar_return"]
    ]
    return build_destiny_sections(
        payload=_fixture_payload(),
        computed={
            "astrology": {"signs": {"Sun": {"sign": "Peixes"}, "Moon": {"sign": "Escorpião"}, "Asc": {"sign": "Leão"}}},
            "numerology": {"life_path_number": 1, "personal_year": {"value": 9}},
        },
        analysis=analysis,
        narrative={"text": "Ruptura e reconstrução."},
        forecast_360={"areas_da_vida": [], "critical_periods": []},
        timeline={"periods": []},
        life_episodes=[],
        turning_points=[],
        reference_date=date(2026, 5, 27),
    )


def test_section_body_does_not_contain_leitura_tecnica() -> None:
    """Readability fix: 'Leitura técnica:' must never appear in section body."""
    sections = _build_sections_with_rupture()
    for section in sections:
        body = section.get("body", "")
        assert "Leitura técnica:" not in body, (
            f"Section '{section['id']}' body contains raw technical block.\nBody snippet: {body[:300]}"
        )


def test_section_body_not_same_as_summary() -> None:
    """Readability fix: body must not simply repeat the summary."""
    sections = _build_sections_with_rupture()
    for section in sections:
        summary = section.get("summary", "").strip()
        body = section.get("body", "").strip()
        if summary and body and len(body) > 10:
            assert body != summary, (
                f"Section '{section['id']}' body is identical to summary: {summary[:150]}"
            )
            # Body should not start with the exact same sentence as summary
            summary_first = summary[:60]
            assert not body.startswith(summary_first) or len(body) > len(summary_first) + 50, (
                f"Section '{section['id']}' body starts exactly like summary: {summary_first}"
            )


def test_technical_detail_field_exists() -> None:
    """Each section must have a technical_detail field (may be empty)."""
    sections = _build_sections_with_rupture()
    for section in sections:
        assert "technical_detail" in section, f"Section '{section['id']}' missing technical_detail field"


def test_family_section_does_not_include_romantic_rupture() -> None:
    """Família section must not paste romantic rupture blocks (wrong cross-section reuse)."""
    sections = _build_sections_with_rupture()
    family = next((s for s in sections if s["id"] == "family"), None)
    assert family is not None
    # The family body should not contain the technical rupture block with romance signals
    body = family.get("body", "")
    # Should not contain raw technical content like "Leitura técnica:" in family body
    assert "Leitura técnica:" not in body, f"Family body has technical block: {body[:300]}"


def test_personality_body_does_not_repeat_summary() -> None:
    """Personalidade body must not start with the same sentence as summary."""
    sections = _build_sections_with_rupture()
    personality = next((s for s in sections if s["id"] == "personality"), None)
    assert personality is not None
    summary = personality.get("summary", "").strip()
    body = personality.get("body", "").strip()
    if summary and body and len(body) > 30:
        assert not body.startswith(summary[:50]), (
            f"Personality body starts with summary. Summary: {summary[:100]}, Body: {body[:100]}"
        )
