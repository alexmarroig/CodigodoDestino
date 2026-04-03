from datetime import date

from engine.analysis import assess_profile_quality, build_multilayer_analysis, get_house_from_longitude


def test_profile_quality_exact_window_unknown() -> None:
    exact = assess_profile_quality({"time": "14:30:00"})
    window = assess_profile_quality({"time": None, "birth_time_precision": "window", "birth_time_window": "evening"})
    unknown = assess_profile_quality({"time": None, "birth_time_precision": "unknown"})

    assert exact["code"] == "A"
    assert window["code"] == "B"
    assert window["effective_time"] == "21:00:00"
    assert unknown["code"] == "C"
    assert unknown["can_use_houses"] is False


def test_house_mapping_wraps_across_zero_degrees() -> None:
    houses = [350.0, 20.0, 50.0, 80.0, 110.0, 140.0, 170.0, 200.0, 230.0, 260.0, 290.0, 320.0]
    assert get_house_from_longitude(355.0, houses) == 1
    assert get_house_from_longitude(15.0, houses) == 1
    assert get_house_from_longitude(175.0, houses) == 7


def test_build_multilayer_analysis_returns_expected_sections() -> None:
    payload = {
        "date": "1995-03-10",
        "time": "14:30:00",
        "lat": -23.55,
        "lon": -46.63,
        "timezone": "America/Sao_Paulo",
        "house_system": "P",
        "orb_degrees": 6.0,
        "reference_date": "2026-04-02",
    }
    profile_quality = assess_profile_quality(payload)
    natal_ephemeris = {
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
        "houses": {"system": "P", "cusps": [120.0, 150.0, 180.0, 210.0, 240.0, 270.0, 300.0, 330.0, 0.0, 30.0, 60.0, 90.0]},
    }
    numerology = {
        "birth_date": payload["date"],
        "life_path_number": 1,
        "personal_year": {"reference_year": 2026, "value": 8, "is_master": False},
    }

    analysis = build_multilayer_analysis(
        payload=payload,
        utc_metadata={"utc_datetime": natal_ephemeris["utc_datetime"]},
        natal_ephemeris=natal_ephemeris,
        natal_aspects=[],
        numerology=numerology,
        reference_date=date(2026, 4, 2),
        profile_quality=profile_quality,
    )

    assert "transits" in analysis
    assert "profections" in analysis
    assert "solar_return" in analysis
    assert "progressions" in analysis
    assert "solar_arc" in analysis
    assert "signals" in analysis
    assert analysis["profile_quality"]["code"] == "A"
