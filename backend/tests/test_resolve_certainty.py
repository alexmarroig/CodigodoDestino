from engine.certainty import resolve_certainty


def test_resolve_caps_will_without_theme_convergence() -> None:
    signals = [{"technique": "transits", "evidence": {"aspect": "square", "planet_a": "saturn", "planet_b": "venus"}}]
    level = resolve_certainty(4, signals, category_key="rupture", theme_convergence=1, has_hard_slow=True)
    assert level in {"must", "tendency", "chance"}
    assert level != "will"


def test_resolve_caps_impact_without_hard_slow() -> None:
    signals = [
        {"technique": "transits", "evidence": {"aspect": "trine", "planet_a": "jupiter", "planet_b": "venus"}},
    ] * 4
    level = resolve_certainty(4, signals, category_key="career", theme_convergence=3, has_hard_slow=False)
    assert level == "tendency"


def test_resolve_allows_must_with_convergence_and_tense() -> None:
    signals = [
        {"technique": "transits", "evidence": {"aspect": "square", "planet_a": "saturn", "planet_b": "venus"}},
        {"technique": "progressions", "evidence": {"aspect": "opposition", "planet_a": "pluto", "planet_b": "moon"}},
        {"technique": "solar_return", "evidence": {"aspect": "square", "planet_a": "saturn", "planet_b": "midheaven"}},
    ]
    level = resolve_certainty(3, signals, category_key="rupture", theme_convergence=3, has_hard_slow=True)
    assert level in {"must", "will"}
