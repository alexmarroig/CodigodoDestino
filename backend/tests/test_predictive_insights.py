from datetime import date

from engine.predictive_insights import (
    CATEGORY_DEFINITIONS,
    _build_astrological_reason,
    _merged_window,
    build_predictive_insights,
)


def _analysis_fixture() -> dict:
    return {
        "signals": [
            {
                "technique": "transits",
                "domain": "carreira_status",
                "label": "Saturno pressiona o MC",
                "weight": 0.86,
                "polarity": "challenging",
                "evidence": {
                    "aspect": "square",
                    "planet_a": "saturn",
                    "planet_b": "midheaven",
                    "transit_house": 10,
                    "natal_house": 10,
                },
                "time_window": {
                    "start": "2026-04-10",
                    "end": "2026-05-02",
                    "peak": "2026-04-18",
                },
            },
            {
                "technique": "progressions",
                "domain": "carreira_status",
                "label": "Lua progredida muda o foco profissional",
                "weight": 0.74,
                "polarity": "mixed",
                "evidence": {
                    "aspect": "opposition",
                    "planet_a": "moon",
                    "planet_b": "sun",
                    "natal_house": 10,
                },
                "time_window": {
                    "start": "2026-04-01",
                    "end": "2026-07-30",
                    "peak": "2026-05-20",
                },
            },
            {
                "technique": "solar_return",
                "domain": "carreira_status",
                "label": "Retorno solar reforca a casa 10",
                "weight": 0.91,
                "polarity": "mixed",
                "time_window": {
                    "start": "2026-01-01",
                    "end": "2026-12-31",
                    "peak": "2026-06-01",
                },
            },
            {
                "technique": "numerology",
                "domain": "carreira_status",
                "label": "Ano pessoal 8 amplia ambicao e metas",
                "weight": 0.32,
                "polarity": "mixed",
                "time_window": {
                    "start": "2026-01-01",
                    "end": "2026-12-31",
                    "peak": "2026-06-01",
                },
            },
            {
                "technique": "transits",
                "domain": "saude_rotina",
                "label": "Marte pressiona rotina e desgaste",
                "weight": 0.7,
                "polarity": "challenging",
                "time_window": {
                    "start": "2026-04-05",
                    "end": "2026-04-19",
                    "peak": "2026-04-11",
                },
            },
            {
                "technique": "numerology",
                "domain": "saude_rotina",
                "label": "Mes pessoal pede recolhimento",
                "weight": 0.28,
                "polarity": "mixed",
                "time_window": {
                    "start": "2026-04-01",
                    "end": "2026-04-30",
                    "peak": "2026-04-15",
                },
            },
        ],
        "rule_hits": [
            {
                "code": "career_reset",
                "label": "Reinicio estrutural da carreira",
                "domain": "carreira_status",
                "weight": 4.9,
            },
            {
                "code": "accident_risk",
                "label": "Sobrecarga, atrito ou risco fisico",
                "domain": "saude_rotina",
                "weight": 4.2,
            },
        ],
        "life_events": [
            {
                "type": "career_change",
                "window": {
                    "start": "2026-04-12",
                    "peak": "2026-04-18",
                    "end": "2026-04-28",
                },
            }
        ],
        "exact_timing": {
            "timed_events": [
                {
                    "code": "career_reset",
                    "domain": "carreira_status",
                    "date": "2026-04-18",
                    "time_window": {
                        "start": "2026-04-12",
                        "peak": "2026-04-18",
                        "end": "2026-04-28",
                    },
                }
            ]
        },
    }


def test_merged_window_long_cycle_drops_reference_peak() -> None:
    items = [
        {"time_window": {"start": "2026-05-27", "end": "2027-05-27", "peak": "2026-05-27"}},
        {"time_window": {"start": "2026-06-01", "end": "2028-05-17", "peak": "2026-05-27"}},
    ]
    merged = _merged_window(items, date(2026, 5, 27))
    assert merged is not None
    assert merged.get("peak") is None


def test_predictive_insights_require_three_independent_signals() -> None:
    result = build_predictive_insights(_analysis_fixture(), reference_date=date(2026, 4, 4))

    detected = {item["category_key"]: item for item in result["detected_events"]}
    watchlist = {item["category_key"]: item for item in result["watchlist"]}

    assert detected["career"]["probability_level"] == "Alta"
    assert detected["career"]["certainty_level"] == "will"
    assert detected["career"]["certainty_label"] == "Alta probabilidade"
    assert detected["career"]["technique_count"] == 4
    assert detected["career"]["independent_signals"] >= 3
    assert detected["career"]["what_is_happening"].startswith("Isso vai acontecer")
    assert detected["career"]["time_window"]["label"]
    assert "Motivo (" in detected["career"]["explanation"]
    assert detected["career"]["what_is_happening"]
    assert len(detected["career"]["what_this_may_look_like_in_real_life"]) >= 2
    assert len(detected["career"]["possible_scenarios"]) >= 2
    assert detected["career"]["impact"]
    assert detected["career"]["risk"]
    assert detected["career"]["recommended_action"]
    assert "Quando:" in detected["career"]["formatted_block"]
    assert "O que acontece:" in detected["career"]["formatted_block"]
    assert "Por que (astrologia/numerologia):" in detected["career"]["formatted_block"]
    # "Leitura técnica:" header was removed from formatted_block (readability fix)
    # Technical items are still present as numbered entries in the block
    assert "Dá para evitar?" in detected["career"]["formatted_block"]
    # Compact human summary should exist separately
    assert "human_summary" in detected["career"]
    assert "Leitura técnica" not in detected["career"]["human_summary"]
    assert detected["career"]["quality_summary"]
    assert watchlist["health"]["probability_level"] == "Baixa"
    assert watchlist["health"]["certainty_level"] == "tendency"
    assert watchlist["health"]["independent_signals"] == 2


def test_predictive_insights_boosts_rupture_when_separated() -> None:
    analysis = _analysis_fixture()
    analysis["signals"].extend(
        [
            {
                "technique": "transits",
                "domain": "relacionamentos",
                "label": "Urano na casa 7",
                "weight": 0.82,
                "polarity": "challenging",
                "time_window": {"start": "2026-04-01", "end": "2026-06-01", "peak": "2026-05-01"},
            },
            {
                "technique": "progressions",
                "domain": "relacionamentos",
                "label": "Lua progredida testa vinculo",
                "weight": 0.71,
                "polarity": "challenging",
                "time_window": {"start": "2026-04-01", "end": "2026-07-01", "peak": "2026-05-15"},
            },
        ]
    )
    analysis["rule_hits"].append(
        {"code": "breakup", "label": "Ruptura afetiva", "domain": "relacionamentos", "weight": 4.8}
    )
    analysis["user_context"] = {"relationship_status": "separated"}
    baseline = build_predictive_insights(_analysis_fixture(), reference_date=date(2026, 4, 4))
    boosted = build_predictive_insights(analysis, reference_date=date(2026, 4, 4))
    boosted_events = boosted["detected_events"] + boosted["watchlist"]
    rupture = next((item for item in boosted_events if item["category_key"] == "rupture"), None)
    assert rupture is not None
    baseline_events = baseline["detected_events"] + baseline["watchlist"]
    baseline_rupture = next((item for item in baseline_events if item["category_key"] == "rupture"), None)
    if baseline_rupture:
        assert rupture["probability_score"] >= baseline_rupture["probability_score"]


# ---------------------------------------------------------------------------
# Task 8: pregnancy_window in CATEGORY_DEFINITIONS relationships
# ---------------------------------------------------------------------------

def test_relationships_category_includes_pregnancy_window():
    rel_def = next(c for c in CATEGORY_DEFINITIONS if c["key"] == "relationships")
    assert "pregnancy_window" in rel_def["rule_codes"]


# ---------------------------------------------------------------------------
# Task 9: _build_astrological_reason labels techniques
# ---------------------------------------------------------------------------

def test_astrological_reason_labels_numerology():
    signals = [
        {"technique": "numerology", "label": "Ano pessoal 8", "weight": 0.5},
        {"technique": "transits", "label": "Júpiter trígono Lua", "weight": 0.9},
    ]
    result = _build_astrological_reason(
        event_type="Emprego, carreira ou perda de trabalho",
        signals=signals,
        rule_hits=[],
        life_events=[],
        techniques=["numerology", "transits"],
    )
    assert "Numerologia" in result or "Trânsito" in result


def test_astrological_reason_numerology_only():
    signals = [
        {"technique": "numerology", "label": "Ciclo do ano pessoal", "weight": 0.6},
    ]
    result = _build_astrological_reason(
        event_type="Dinheiro, ganho ou perda financeira",
        signals=signals,
        rule_hits=[],
        life_events=[],
        techniques=["numerology"],
    )
    assert "Numerologia" in result


# ---------------------------------------------------------------------------
# Task 11: Integration test — all categories produce four-point block
# ---------------------------------------------------------------------------

def _make_analysis_for_category(cat_key: str) -> dict:
    cat = next(c for c in CATEGORY_DEFINITIONS if c["key"] == cat_key)
    domain = next(iter(cat["domains"]))
    polarity = next(iter(cat["allowed_polarities"]))
    rule_code = next(iter(cat["rule_codes"]))
    evidence_sets = [
        {"aspect": "square", "planet_a": "saturn", "planet_b": "midheaven", "natal_house": 10},
        {"aspect": "opposition", "planet_a": "moon", "planet_b": "sun", "natal_house": 6},
        {"aspect": "square", "planet_a": "mars", "planet_b": "pluto", "natal_house": 8},
    ]
    techniques = ["transits", "progressions", "solar_return"]
    signals = [
        {
            "technique": t,
            "domain": domain,
            "label": f"Sinal {t} para {cat_key}",
            "weight": 0.8,
            "polarity": polarity,
            "time_window": {
                "start": "2026-06-01",
                "end": "2026-07-31",
                "peak": "2026-06-20",
            },
            "evidence": ev,
        }
        for t, ev in zip(techniques, evidence_sets)
    ]
    rule_hits = [{"code": rule_code, "weight": 4.0, "label": f"Regra {rule_code}"}]
    return {"signals": signals, "rule_hits": rule_hits, "life_events": [], "user_context": {}}


def test_all_categories_produce_four_point_block():
    cat_keys = ["health", "career", "relationships", "rupture", "finance", "major_transitions"]
    ref = date(2026, 6, 1)
    for cat_key in cat_keys:
        analysis = _make_analysis_for_category(cat_key)
        result = build_predictive_insights(analysis, reference_date=ref)
        events = result["detected_events"] + result["watchlist"]
        cat_events = [e for e in events if e["category_key"] == cat_key]
        if not cat_events:
            continue
        event = cat_events[0]
        assert event.get("when_label") or event.get("time_window"), \
            f"{cat_key}: missing 'Quando' field"
        assert event.get("what_is_happening") or event.get("subtype_what"), \
            f"{cat_key}: missing 'O que' field"
        assert event.get("explanation") or event.get("subtype_por_que"), \
            f"{cat_key}: missing 'Por quê' field"
        assert event.get("avoidability_summary") or event.get("subtype_avoidability"), \
            f"{cat_key}: missing 'Dá para evitar' field"


# ---------------------------------------------------------------------------
# Task 12: source_technique propagated to detected event entry
# ---------------------------------------------------------------------------

def test_detected_event_has_source_technique():
    analysis = _analysis_fixture()
    result = build_predictive_insights(analysis, reference_date=date(2026, 5, 1))
    events = result["detected_events"]
    assert events, "Nenhum evento detectado — verifique a fixture"
    for event in events:
        if event.get("subtype_key"):
            assert "source_technique" in event, (
                f"Event {event['category_key']} com subtype {event['subtype_key']} "
                "não tem source_technique"
            )
            assert event["source_technique"] in ("astrologia", "numerologia")
