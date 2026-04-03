from datetime import date

from astro.aspects import calculate_aspects
from engine.analysis import assess_profile_quality
from engine.timeline import build_forecast_360, generate_timeline


def _natal_ephemeris_fixture() -> dict:
    return {
        "utc_datetime": "1995-03-10T17:30:00Z",
        "julian_day": 2449787.229167,
        "planets": {
            "sun": {"longitude": 349.0},
            "moon": {"longitude": 100.0},
            "mercury": {"longitude": 330.0},
            "venus": {"longitude": 10.0},
            "mars": {"longitude": 140.0},
            "jupiter": {"longitude": 250.0},
            "saturn": {"longitude": 340.0},
            "uranus": {"longitude": 300.0},
            "neptune": {"longitude": 295.0},
            "pluto": {"longitude": 240.0},
        },
        "angles": {
            "ascendant": 120.0,
            "descendant": 300.0,
            "midheaven": 10.0,
            "imum_coeli": 190.0,
            "vertex": 200.0,
        },
        "houses": {
            "system": "P",
            "cusps": [120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0, 0.0, 30.0, 60.0, 90.0],
        },
    }


def test_generate_timeline_builds_months_and_quarters() -> None:
    periods = generate_timeline(date(2026, 4, 3))

    assert len(periods) == 16
    assert periods[0]["granularity"] == "month"
    assert periods[11]["granularity"] == "month"
    assert periods[12]["granularity"] == "quarter"
    assert periods[-1]["horizon"] == "long"


def test_build_forecast_360_returns_fixed_shapes() -> None:
    payload = {
        "date": "1995-03-10",
        "time": "14:30:00",
        "lat": -23.55,
        "lon": -46.63,
        "timezone": "America/Sao_Paulo",
        "house_system": "P",
        "orb_degrees": 6.0,
        "reference_date": "2026-04-03",
    }
    natal_ephemeris = _natal_ephemeris_fixture()
    positions = {planet_name: float(data["longitude"]) for planet_name, data in natal_ephemeris["planets"].items()}
    natal_aspects = calculate_aspects(positions, 6.0)
    profile_quality = assess_profile_quality(payload)

    forecast = build_forecast_360(
        payload=payload,
        natal_ephemeris=natal_ephemeris,
        natal_aspects=natal_aspects,
        profile_quality=profile_quality,
        reference_date=date(2026, 4, 3),
    )

    assert len(forecast["areas_da_vida"]) == 8
    assert len(forecast["casas"]) == 12
    assert len(forecast["timeline"]["periods"]) == 16
    assert "summary" in forecast
    assert "life_episodes" in forecast
    assert "turning_points" in forecast
    assert "proposito" in forecast
