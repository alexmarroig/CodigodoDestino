from engine.astro_provenance import build_astro_provenance, build_human_por_que_from_provenance


def test_provenance_lists_drivers_and_excludes_generational() -> None:
    signals = [
        {
            "technique": "transits",
            "label": "Saturno quadratura Vênus",
            "domain": "relacionamentos",
            "evidence": {
                "aspect": "square",
                "planet_a": "saturn",
                "planet_b": "venus",
                "orb_degrees": 0.5,
                "transit_house": 7,
                "natal_house": 7,
            },
        },
        {
            "technique": "solar_arc",
            "label": "Arco solar Netuno toca Plutão",
            "domain": "major_transitions",
            "evidence": {
                "aspect": "square",
                "planet_a": "neptune",
                "planet_b": "pluto",
                "orb_degrees": 0.7,
            },
        },
    ]
    prov = build_astro_provenance(
        signals=signals,
        category_key="rupture",
        certainty_level="tendency",
    )
    assert len(prov["primary_drivers"]) >= 1
    assert prov["primary_drivers"][0]["planet_a"] == "saturn"
    labels = " ".join(d.get("label", "") for d in prov["primary_drivers"]).lower()
    assert "saturn" in labels
    assert not any("plut" in d.get("planet_b", "").lower() and "neptune" in d.get("planet_a", "").lower() for d in prov["primary_drivers"])
    human = build_human_por_que_from_provenance(prov)
    assert "Causa:" in human or "Saturno" in human
