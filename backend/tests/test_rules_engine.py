from engine.rules_engine import build_rule_hits, build_specialized_insights


def _analysis_fixture() -> dict:
    return {
        "utc_reference": {
            "input_local": {
                "date": "2026-04-03",
                "time": "14:30:00",
                "timezone": "America/Sao_Paulo",
            }
        },
        "transits": {
            "aspects": [
                {
                    "planet_a": "jupiter",
                    "planet_b": "venus",
                    "aspect": "trine",
                    "orb": 0.4,
                    "phase": "applying",
                    "time_window": {"start": "2026-04-03", "end": "2026-05-04", "peak": "2026-04-16"},
                },
                {
                    "planet_a": "saturn",
                    "planet_b": "venus",
                    "aspect": "square",
                    "orb": 1.0,
                    "phase": "applying",
                    "time_window": {"start": "2026-04-03", "end": "2026-05-10", "peak": "2026-04-22"},
                },
                {
                    "planet_a": "saturn",
                    "planet_b": "MC",
                    "aspect": "conjunction",
                    "orb": 0.2,
                    "phase": "applying",
                    "time_window": {"start": "2026-04-03", "end": "2026-05-12", "peak": "2026-04-18"},
                },
            ]
        },
        "progressions": {"aspects": []},
        "solar_arc": {"aspects": []},
        "natal": {
            "planet_houses": {
                "sun": 10,
                "moon": 4,
                "jupiter": 9,
                "saturn": 10,
                "venus": 7,
            }
        },
        "profections": {"activated_domain": "carreira_status"},
        "solar_return": {
            "dominant_houses": [
                {"house": 10, "domain": "carreira_status", "planet_count": 3},
                {"house": 9, "domain": "expansao_sentido", "planet_count": 2},
            ]
        },
        "numerology": {"life_path_number": 8},
    }


def test_rule_bank_matches_key_aspects() -> None:
    hits = build_rule_hits(_analysis_fixture())
    codes = {hit["code"] for hit in hits}

    assert "marriage_window" in codes
    assert "relationship_block" in codes
    assert "career_reset" in codes


def test_specialized_insights_return_relationship_financial_and_purpose() -> None:
    insights = build_specialized_insights(_analysis_fixture())

    assert insights["relationship"]["marriage_probability"] > 0.3
    assert insights["relationship"]["tension_probability"] > 0.3
    assert insights["relationship"]["summary"]
    assert "summary" in insights["financial"]
    assert insights["purpose"]["focus_domains"]


def test_rule_hits_apply_user_specific_weight_overrides() -> None:
    analysis = _analysis_fixture()
    analysis["user_rule_overrides"] = {"career_reset": 9.1}

    hits = build_rule_hits(analysis)
    career_reset = next(hit for hit in hits if hit["code"] == "career_reset")

    assert career_reset["weight"] > 8.0
