from engine.cluster_convergence import compute_cluster_metrics


def _signal(technique: str, planet_a: str, planet_b: str, house: int | None = None) -> dict:
    ev: dict = {"planet_a": planet_a, "planet_b": planet_b, "aspect": "square"}
    if house is not None:
        ev["natal_house"] = house
    return {"technique": technique, "evidence": ev, "domain": "relacionamentos"}


def test_same_pair_three_techniques_low_effective_convergence() -> None:
    signals = [
        _signal("transits", "saturn", "venus", 7),
        _signal("progressions", "saturn", "venus", 7),
        _signal("solar_arc", "saturn", "venus", 7),
    ]
    metrics = compute_cluster_metrics(signals)
    assert metrics["technique_count"] == 3
    assert metrics["theme_convergence"] == 1
    assert metrics["effective_independent_signals"] <= 2


def test_distinct_targets_higher_convergence() -> None:
    signals = [
        _signal("transits", "uranus", "descendant", 7),
        _signal("solar_return", "saturn", "venus", 7),
        _signal("progressions", "pluto", "moon", 4),
    ]
    metrics = compute_cluster_metrics(signals, [{"code": "breakup"}])
    assert metrics["technique_count"] >= 3
    assert metrics["theme_convergence"] >= 2
    assert metrics["effective_independent_signals"] >= 2
