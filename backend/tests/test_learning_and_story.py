from engine.adaptive_learning_engine import extract_patterns
from engine.learning_engine import summarize_learning
from engine.life_story_engine import build_life_story
from engine.question_engine import suggest_feedback_questions


def test_summarize_learning_counts_patterns() -> None:
    summary = summarize_learning(
        [
            {
                "transits": [
                    {"planet_a": "jupiter", "aspect": "trine", "planet_b": "venus"},
                    {"planet_a": "saturn", "aspect": "square", "planet_b": "venus"},
                ],
                "rule_hits": [{"code": "marriage_window"}, {"code": "marriage_window"}],
            }
        ]
    )

    assert summary["observed_events"] == 1
    assert summary["pattern_counter"]["jupiter_trine_venus"] == 1
    assert summary["pattern_counter"]["marriage_window"] == 2


def test_build_life_story_returns_chapters() -> None:
    story = build_life_story(
        timeline_periods=[{"headline": "2026-04: relacionamentos ganha forca concreta."}],
        life_events=[
            {
                "label": "Janela forte de uniao ou compromisso serio",
                "window": {"peak": "2026-05-10"},
                "summary": "Entre 2026-05-02 e 2026-05-20, cresce uma janela forte.",
            }
        ],
        turning_points=[
            {
                "date": "2026-05-10",
                "headline": "Relacionamentos ganha pico de movimento",
                "summary": "Janela principal do ciclo.",
            }
        ],
    )

    assert story["chapters"]
    assert "ciclo" in story["overview"].lower()


def test_extract_patterns_accumulates_intensity_from_transits_and_rules() -> None:
    patterns = extract_patterns(
        [
            {
                "real_intensity": 4,
                "transits": [{"planet_a": "saturn", "aspect": "square", "planet_b": "sun"}],
                "rule_hits": [{"code": "career_block"}],
            },
            {
                "real_intensity": 2,
                "transits": [{"planet_a": "saturn", "aspect": "square", "planet_b": "sun"}],
                "rule_hits": [{"code": "career_block"}],
            },
        ]
    )

    assert patterns["saturn_square_sun"]["count"] == 2
    assert patterns["saturn_square_sun"]["total_intensity"] == 6
    assert patterns["career_block"]["count"] == 2


def test_suggest_feedback_questions_uses_life_events_and_turning_points() -> None:
    questions = suggest_feedback_questions(
        life_events=[
            {
                "area_key": "relacionamento",
                "window": {"start": "2026-05-02", "peak": "2026-05-10", "end": "2026-05-20"},
            }
        ],
        turning_points=[
            {"domain": "carreira", "date": "2026-08-14"},
        ],
    )

    assert questions
    assert any(item["source"] == "life_event" for item in questions)
    assert any(item["source"] == "turning_point" for item in questions)
