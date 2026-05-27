from __future__ import annotations

from datetime import date

from engine.event_subtypes import (
    SUBTYPE_DEFINITIONS,
    _has_tense_aspect,
    _primary_source_label,
    build_subtype_text,
    classify_event_subtype,
)


# ---------------------------------------------------------------------------
# Task 1: _has_tense_aspect
# ---------------------------------------------------------------------------

def test_has_tense_aspect_square():
    signals = [{"evidence": {"aspect": "square"}}]
    assert _has_tense_aspect(signals) is True


def test_has_tense_aspect_trine_only():
    signals = [{"evidence": {"aspect": "trine"}}, {"evidence": {"aspect": "sextile"}}]
    assert _has_tense_aspect(signals) is False


def test_has_tense_aspect_empty():
    assert _has_tense_aspect([]) is False


def test_has_tense_aspect_conjunction():
    signals = [{"evidence": {"aspect": "conjunction"}}]
    assert _has_tense_aspect(signals) is True


def test_has_tense_aspect_opposition():
    signals = [{"evidence": {"aspect": "opposition"}}, {"technique": "numerology"}]
    assert _has_tense_aspect(signals) is True


# ---------------------------------------------------------------------------
# Task 2: is_fatalistic requires tense aspect
# ---------------------------------------------------------------------------

def _make_signals(aspect: str, technique: str = "transits", count: int = 3) -> list[dict]:
    return [
        {
            "technique": technique,
            "label": f"Sinal {i}",
            "weight": 4.0,
            "evidence": {"aspect": aspect},
        }
        for i in range(count)
    ]


def test_fatalistic_requires_tense_aspect():
    signals = _make_signals("trine", count=3)
    rule_hits = [{"code": "breakup", "weight": 4.0, "label": "Ruptura detectada"}]
    result = build_subtype_text(
        "separacao_abrupta",
        signals=signals,
        rule_hits=rule_hits,
        reference_date=date(2026, 6, 1),
        user_context={},
        independent_signals=3,
        time_window={"start": "2026-06-01", "end": "2026-07-01", "peak": "2026-06-15"},
    )
    assert result["is_fatalistic"] is False
    assert not result["subtype_what"].startswith("Isso vai acontecer")


def test_fatalistic_with_tense_aspect_and_threshold():
    signals = _make_signals("square", count=3)
    rule_hits = [{"code": "breakup", "weight": 4.0, "label": "Ruptura detectada"}]
    result = build_subtype_text(
        "separacao_abrupta",
        signals=signals,
        rule_hits=rule_hits,
        reference_date=date(2026, 6, 1),
        user_context={},
        independent_signals=3,
        time_window={"start": "2026-06-01", "end": "2026-07-01", "peak": "2026-06-15"},
    )
    assert result["is_fatalistic"] is True
    assert result["subtype_what"].startswith("Isso vai acontecer")


# ---------------------------------------------------------------------------
# Task 5: _primary_source_label and source_technique field
# ---------------------------------------------------------------------------

def test_source_label_astrology():
    signals = [
        {"technique": "transits", "label": "Marte sq Saturno", "evidence": {"aspect": "square"}},
        {"technique": "numerology", "label": "Ano pessoal 5"},
    ]
    assert _primary_source_label(signals) == "astrologia"


def test_source_label_numerology_only():
    signals = [
        {"technique": "numerology", "label": "Ano pessoal 8"},
        {"technique": "numerology", "label": "Ciclo do dia"},
    ]
    assert _primary_source_label(signals) == "numerologia"


def test_source_label_empty():
    assert _primary_source_label([]) == "astrologia"


def test_build_subtype_text_includes_source_technique():
    signals = [
        {"technique": "transits", "label": "Saturno pressiona MC", "weight": 3.0,
         "evidence": {"aspect": "square"}},
    ]
    rule_hits = [{"code": "career_reset", "weight": 4.0, "label": "Reset de carreira"}]
    result = build_subtype_text(
        "perda_emprego",
        signals=signals,
        rule_hits=rule_hits,
        reference_date=date(2026, 6, 1),
        user_context={},
        independent_signals=2,
    )
    assert "source_technique" in result
    assert result["source_technique"] in ("astrologia", "numerologia")


def test_build_subtype_numerology_source_in_what():
    signals = [{"technique": "numerology", "label": "Ano pessoal 9", "weight": 2.0, "evidence": {}}]
    rule_hits = [{"code": "career_reset", "weight": 4.0, "label": "Reset numerológico"}]
    result = build_subtype_text(
        "perda_emprego",
        signals=signals,
        rule_hits=rule_hits,
        reference_date=date(2026, 6, 1),
        user_context={},
        independent_signals=1,
    )
    assert result["source_technique"] == "numerologia"


# ---------------------------------------------------------------------------
# Task 6: por_que enriquecido com técnica/aspecto/casa
# ---------------------------------------------------------------------------

def test_por_que_includes_technique_and_aspect():
    signals = [
        {
            "technique": "transits",
            "label": "Saturno quadratura Sol",
            "weight": 4.0,
            "evidence": {
                "aspect": "square",
                "planet_a": "saturn",
                "planet_b": "sun",
                "transit_house": 10,
            },
        },
        {
            "technique": "progressions",
            "label": "Lua progredida muda setor",
            "weight": 3.0,
            "evidence": {"aspect": "conjunction", "planet_a": "moon", "transit_house": 6},
        },
    ]
    rule_hits = [{"code": "career_block", "weight": 4.0, "label": "Bloqueio de carreira"}]
    result = build_subtype_text(
        "perda_emprego",
        signals=signals,
        rule_hits=rule_hits,
        reference_date=date(2026, 6, 1),
        user_context={},
        independent_signals=2,
    )
    por_que = result["subtype_por_que"]
    assert "Trânsito" in por_que or "Progressão" in por_que
    assert "Casa 10" in por_que or "Casa 6" in por_que


# ---------------------------------------------------------------------------
# Task 7: acidente_fisico and acidente_emocional subtypes
# ---------------------------------------------------------------------------

def test_acidente_fisico_classification():
    rule_hits = [{"code": "accident_risk", "weight": 4.0, "label": "Risco de acidente físico"}]
    signals = [{"technique": "transits", "domain": "saude_rotina",
                "polarity": "challenging", "weight": 0.9,
                "evidence": {"aspect": "square"}}]
    result = classify_event_subtype("health", signals, rule_hits, [], {})
    assert result == "acidente_fisico"


def test_acidente_emocional_classification():
    rule_hits = [{"code": "psychological_transformation", "weight": 4.0,
                  "label": "Crise psicológica intensa"}]
    signals = [{"technique": "transits", "domain": "psicologico_espiritual",
                "polarity": "challenging", "weight": 0.8,
                "evidence": {"aspect": "opposition"}}]
    result = classify_event_subtype("health", signals, rule_hits, [], {})
    assert result == "acidente_emocional"


def test_acidente_fisico_in_subtype_definitions():
    assert "acidente_fisico" in SUBTYPE_DEFINITIONS
    sd = SUBTYPE_DEFINITIONS["acidente_fisico"]
    assert sd["category"] == "health"
    assert "accident_risk" in sd["priority_rule_codes"]


def test_acidente_emocional_in_subtype_definitions():
    assert "acidente_emocional" in SUBTYPE_DEFINITIONS
    sd = SUBTYPE_DEFINITIONS["acidente_emocional"]
    assert sd["category"] == "health"
    assert "psychological_transformation" in sd["priority_rule_codes"]


def test_acidente_fisico_subtype_text():
    signals = [{"technique": "transits", "label": "Marte sq Saturno", "weight": 4.0,
                "evidence": {"aspect": "square"}}]
    rule_hits = [{"code": "accident_risk", "weight": 4.5, "label": "Risco físico elevado"}]
    result = build_subtype_text(
        "acidente_fisico",
        signals=signals,
        rule_hits=rule_hits,
        reference_date=date(2026, 6, 1),
        user_context={},
        independent_signals=2,
    )
    assert result["subtype_label"] == "Acidente ou risco físico"
    assert "acidente" in result["subtype_what"].lower() or "físico" in result["subtype_what"].lower()


# ---------------------------------------------------------------------------
# Task 8: pregnancy_window → filhos
# ---------------------------------------------------------------------------

def test_filhos_triggered_by_pregnancy_window():
    rule_hits = [{"code": "pregnancy_window", "weight": 4.0, "label": "Janela de gravidez"}]
    signals = [{"technique": "transits", "domain": "relacionamentos",
                "polarity": "supportive", "weight": 0.8, "evidence": {}}]
    result = classify_event_subtype("relationships", signals, rule_hits, [], {})
    assert result == "filhos"


def test_filhos_definition_has_pregnancy_window():
    sd = SUBTYPE_DEFINITIONS["filhos"]
    assert "pregnancy_window" in sd["rule_codes"]


# ---------------------------------------------------------------------------
# Task 10: format_assertive_when_label used in formatted_block
# ---------------------------------------------------------------------------

def test_subtype_formatted_block_has_assertive_when():
    signals = [{"technique": "transits", "label": "Marte sq Saturno", "weight": 3.0,
                "evidence": {"aspect": "square"}}]
    rule_hits = [{"code": "breakup", "weight": 4.0, "label": "Ruptura"}]
    result = build_subtype_text(
        "separacao_abrupta",
        signals=signals,
        rule_hits=rule_hits,
        reference_date=date(2026, 6, 1),
        user_context={},
        independent_signals=2,
        time_window={"start": "2026-01-05", "end": "2026-02-28", "peak": "2026-01-20"},
    )
    block = result["subtype_formatted_block"]
    assert "janeiro de 2026" in block or "janeiro" in block
    assert "20 de janeiro" in block
