from datetime import date

from engine.exact_timing_engine import (
    cluster_events_by_date,
    detect_critical_periods,
    find_exact_hit,
    is_applying,
)


def test_is_applying_detects_approach() -> None:
    assert is_applying(95, 92, 90) is True
    assert is_applying(89, 92, 90) is False


def test_find_exact_hit_returns_start_peak_end_from_snapshots() -> None:
    natal = {
        "planets": {"venus": {"longitude": 90.0}},
        "angles": {},
    }
    snapshots = [
        {"date": date(2026, 4, 5), "planets": {"uranus": {"longitude": 177.8}}, "angles": {}},
        {"date": date(2026, 4, 6), "planets": {"uranus": {"longitude": 178.9}}, "angles": {}},
        {"date": date(2026, 4, 7), "planets": {"uranus": {"longitude": 180.1}}, "angles": {}},
        {"date": date(2026, 4, 8), "planets": {"uranus": {"longitude": 181.3}}, "angles": {}},
        {"date": date(2026, 4, 9), "planets": {"uranus": {"longitude": 182.8}}, "angles": {}},
    ]

    hit = find_exact_hit(
        natal_ephemeris=natal,
        snapshots=snapshots,
        planet_a="uranus",
        planet_b="venus",
        aspect_degree=90,
    )

    assert hit is not None
    assert hit["start"] == "2026-04-05"
    assert hit["peak"] == "2026-04-07"
    assert hit["end"] == "2026-04-08"
    assert hit["orb"] <= 0.2


def test_cluster_events_and_critical_periods_group_heavy_months() -> None:
    events = [
        {"date": "2026-04-07", "weight": 5.0, "type": "breakup"},
        {"date": "2026-04-12", "weight": 5.0, "type": "career_reset"},
        {"date": "2026-04-20", "weight": 4.2, "type": "financial_restriction"},
        {"date": "2026-05-10", "weight": 3.0, "type": "commitment"},
    ]

    clusters = cluster_events_by_date(events)
    critical = detect_critical_periods(clusters)

    assert any(item["month"] == "2026-04" for item in clusters)
    assert critical[0]["month"] == "2026-04"
    assert critical[0]["intensity"] in {"high", "medium"}
