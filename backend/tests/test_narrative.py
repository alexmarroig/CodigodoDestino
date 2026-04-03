from engine.narrative import build_narrative_prompt


def _analysis_fixture(confidence_level: str = "low") -> dict:
    return {
        "profile_quality": {
            "code": "A",
            "confidence_modifier": 1.0,
        },
        "profections": {
            "activated_house": 10,
            "activated_domain": "carreira_status",
            "lord_of_year": "saturn",
        },
        "solar_return": {
            "available": True,
            "dominant_houses": [{"house": 10, "domain": "carreira_status", "planet_count": 3}],
        },
        "numerology": {
            "life_path_number": 1,
            "personal_year": {"reference_year": 2026, "value": 8, "is_master": False},
        },
        "domain_analysis": {
            "domains": [
                {
                    "domain": "carreira_status",
                    "domain_label": "carreira e status",
                    "probability": 0.82,
                    "tone": "challenging",
                    "converged": True,
                    "independent_techniques": ["profections", "solar_return", "transits"],
                    "signals": [
                        {"label": "Profeccao anual ativa a casa 10"},
                        {"label": "Retorno solar concentra foco na casa 10"},
                        {"label": "Saturn em quadratura com Sun"},
                    ],
                    "time_window": {
                        "start": "2026-04-02",
                        "end": "2026-05-15",
                    },
                }
            ],
            "uncertainties": [],
            "confidence": {
                "level": confidence_level,
                "score": 0.81 if confidence_level == "high" else 0.44,
                "reason": "baseado em convergencia de tecnicas independentes",
                "profile_quality": "A",
            },
        },
        "techniques_used": ["natal", "transits", "profections", "solar_return", "numerology"],
    }


def _events_fixture() -> list[dict]:
    return [
        {
            "id": "career_transition_2026-04-02",
            "title": "Ha pressao real sobre carreira e posicionamento publico.",
            "summary": "Isso costuma se manifestar como cobrancas, necessidade de reposicionamento e decisoes estruturais.",
            "category": "carreira_status",
            "domain": "carreira_status",
            "probability": 0.82,
            "intensity": "high",
            "priority": 82,
            "signals": [
                "Profeccao anual ativa a casa 10",
                "Retorno solar concentra foco na casa 10",
                "Saturn em quadratura com Sun",
            ],
            "time_window": {
                "start": "2026-04-02",
                "end": "2026-05-15",
                "peak": "2026-04-20",
                "duration_days": 44,
                "precision": "mixed",
            },
            "counter_signals": [],
            "recommendations": ["Evite agir por desgaste momentaneo."],
        }
    ]


def test_narrative_prompt_uses_template_strategy_for_low_complexity() -> None:
    prompt = build_narrative_prompt(
        _analysis_fixture(confidence_level="low"),
        _events_fixture(),
        {
            "total": 1,
            "categories": {"carreira_status": 1},
            "average_score": 0.82,
            "highest_priority": 82,
        },
        {"level": "low", "score": 0.44, "reason": "pouca convergencia", "profile_quality": "A"},
        [],
    )

    assert prompt["plan"]["strategy"] == "template"
    assert prompt["plan"]["reason"] == "template-cheaper-and-sufficient"


def test_narrative_prompt_uses_llm_for_high_confidence_convergence() -> None:
    prompt = build_narrative_prompt(
        _analysis_fixture(confidence_level="high"),
        _events_fixture(),
        {
            "total": 1,
            "categories": {"carreira_status": 1},
            "average_score": 0.82,
            "highest_priority": 82,
        },
        {
            "level": "high",
            "score": 0.81,
            "reason": "baseado em convergencia de tecnicas independentes",
            "profile_quality": "A",
        },
        [],
    )

    assert prompt["plan"]["strategy"] == "llm"
    assert prompt["plan"]["reason"] == "high-confidence-convergence"
