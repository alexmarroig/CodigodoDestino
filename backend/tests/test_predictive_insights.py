from datetime import date

from engine.predictive_insights import build_predictive_insights


def _analysis_fixture() -> dict:
    return {
        "signals": [
            {
                "technique": "transits",
                "domain": "carreira_status",
                "label": "Saturno pressiona o MC",
                "weight": 0.86,
                "polarity": "challenging",
                "time_window": {
                    "start": "2026-04-10",
                    "end": "2026-05-02",
                    "peak": "2026-04-18",
                },
            },
            {
                "technique": "progressions",
                "domain": "carreira_status",
                "label": "Lua progredida muda o foco profissional",
                "weight": 0.74,
                "polarity": "mixed",
                "time_window": {
                    "start": "2026-04-01",
                    "end": "2026-07-30",
                    "peak": "2026-05-20",
                },
            },
            {
                "technique": "solar_return",
                "domain": "carreira_status",
                "label": "Retorno solar reforca a casa 10",
                "weight": 0.91,
                "polarity": "mixed",
                "time_window": {
                    "start": "2026-01-01",
                    "end": "2026-12-31",
                    "peak": "2026-06-01",
                },
            },
            {
                "technique": "numerology",
                "domain": "carreira_status",
                "label": "Ano pessoal 8 amplia ambicao e metas",
                "weight": 0.32,
                "polarity": "mixed",
                "time_window": {
                    "start": "2026-01-01",
                    "end": "2026-12-31",
                    "peak": "2026-06-01",
                },
            },
            {
                "technique": "transits",
                "domain": "saude_rotina",
                "label": "Marte pressiona rotina e desgaste",
                "weight": 0.7,
                "polarity": "challenging",
                "time_window": {
                    "start": "2026-04-05",
                    "end": "2026-04-19",
                    "peak": "2026-04-11",
                },
            },
            {
                "technique": "numerology",
                "domain": "saude_rotina",
                "label": "Mes pessoal pede recolhimento",
                "weight": 0.28,
                "polarity": "mixed",
                "time_window": {
                    "start": "2026-04-01",
                    "end": "2026-04-30",
                    "peak": "2026-04-15",
                },
            },
        ],
        "rule_hits": [
            {
                "code": "career_reset",
                "label": "Reinicio estrutural da carreira",
                "domain": "carreira_status",
                "weight": 4.9,
            },
            {
                "code": "accident_risk",
                "label": "Sobrecarga, atrito ou risco fisico",
                "domain": "saude_rotina",
                "weight": 4.2,
            },
        ],
        "life_events": [
            {
                "type": "career_change",
                "window": {
                    "start": "2026-04-12",
                    "peak": "2026-04-18",
                    "end": "2026-04-28",
                },
            }
        ],
        "exact_timing": {
            "timed_events": [
                {
                    "code": "career_reset",
                    "domain": "carreira_status",
                    "date": "2026-04-18",
                    "time_window": {
                        "start": "2026-04-12",
                        "peak": "2026-04-18",
                        "end": "2026-04-28",
                    },
                }
            ]
        },
    }


def test_predictive_insights_require_three_independent_signals() -> None:
    result = build_predictive_insights(_analysis_fixture(), reference_date=date(2026, 4, 4))

    detected = {item["category_key"]: item for item in result["detected_events"]}
    watchlist = {item["category_key"]: item for item in result["watchlist"]}

    assert detected["career"]["probability_level"] == "High"
    assert detected["career"]["independent_signals"] == 4
    assert detected["career"]["time_window"]["label"]
    assert "convergence" in detected["career"]["explanation"].lower()
    assert watchlist["health"]["probability_level"] == "Weak"
    assert watchlist["health"]["independent_signals"] == 2
