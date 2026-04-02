from astro.aspects import calculate_aspects


def test_square_detected() -> None:
    aspects = calculate_aspects({"venus": 10.0, "mars": 100.0}, orb_degrees=2)
    assert any(a["aspect"] == "square" for a in aspects)
