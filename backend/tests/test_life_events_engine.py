from engine.life_events_engine import detect_life_events, full_life_event_analysis


def _timed_transits_fixture() -> list[dict]:
    return [
        {
            "planet_a": "jupiter",
            "planet_b": "venus",
            "aspect": "trine",
            "type": "marriage_window",
            "domain": "relacionamentos",
            "label": "Janela de compromisso ou casamento",
            "date": "2026-05-10",
            "orb": 0.2,
            "weight": 5.0,
            "time_window": {"start": "2026-05-02", "peak": "2026-05-10", "end": "2026-05-20"},
        },
        {
            "planet_a": "saturn",
            "planet_b": "venus",
            "aspect": "trine",
            "type": "commitment",
            "domain": "relacionamentos",
            "label": "Compromisso e estabilizacao",
            "date": "2026-05-12",
            "orb": 0.6,
            "weight": 5.0,
            "time_window": {"start": "2026-05-03", "peak": "2026-05-12", "end": "2026-05-24"},
        },
        {
            "planet_a": "saturn",
            "planet_b": "MC",
            "aspect": "conjunction",
            "type": "career_reset",
            "domain": "carreira_status",
            "label": "Reinicio estrutural da carreira",
            "date": "2026-08-18",
            "orb": 0.3,
            "weight": 5.0,
            "time_window": {"start": "2026-08-11", "peak": "2026-08-18", "end": "2026-08-28"},
        },
        {
            "planet_a": "uranus",
            "planet_b": "MC",
            "aspect": "conjunction",
            "type": "career_change",
            "domain": "carreira_status",
            "label": "Mudanca brusca de rumo profissional",
            "date": "2026-08-20",
            "orb": 0.5,
            "weight": 5.0,
            "time_window": {"start": "2026-08-14", "peak": "2026-08-20", "end": "2026-08-31"},
        },
    ]


def test_detect_life_events_clusters_real_windows() -> None:
    events = detect_life_events(_timed_transits_fixture())
    event_types = {event["type"] for event in events}

    assert "marriage" in event_types
    assert "career_change" in event_types


def test_full_life_event_analysis_builds_window_and_intensity() -> None:
    events = full_life_event_analysis(_timed_transits_fixture())
    marriage = next(event for event in events if event["type"] == "marriage")

    assert marriage["window"]["peak"] == "2026-05-10"
    assert marriage["intensity"] in {"medium", "high"}
    assert "compromisso" in marriage["label"].lower() or "uniao" in marriage["label"].lower()
