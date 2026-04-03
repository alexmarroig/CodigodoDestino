from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from engine.exact_timing_engine import (
    cluster_events_by_date,
    detect_critical_periods,
    detect_timed_events,
)
from engine.financial_engine import detect_financial_cycles
from engine.life_events_engine import full_life_event_analysis
from engine.purpose_engine import analyze_life_purpose
from engine.relationship_engine import detect_relationship_events

POINT_ALIASES = {
    "ascendant": "ASC",
    "descendant": "DSC",
    "midheaven": "MC",
    "imum_coeli": "IC",
    "vertex": "VERTEX",
}

RULES = [
    {"planet_a": "saturn", "aspect": "square", "planet_b": "sun", "code": "career_block", "weight": 4.0, "domain": "carreira_status", "polarity": "challenging", "label": "Pressao de carreira e autoridade"},
    {"planet_a": "saturn", "aspect": "conjunction", "planet_b": "MC", "code": "career_reset", "weight": 5.0, "domain": "carreira_status", "polarity": "challenging", "label": "Reinicio estrutural da carreira"},
    {"planet_a": "pluto", "aspect": "conjunction", "planet_b": "MC", "code": "career_transformation", "weight": 5.0, "domain": "carreira_status", "polarity": "challenging", "label": "Transformacao profunda da direcao profissional"},
    {"planet_a": "jupiter", "aspect": "trine", "planet_b": "MC", "code": "career_growth", "weight": 3.5, "domain": "carreira_status", "polarity": "supportive", "label": "Expansao de carreira e visibilidade"},
    {"planet_a": "mars", "aspect": "square", "planet_b": "MC", "code": "career_conflict", "weight": 3.0, "domain": "carreira_status", "polarity": "challenging", "label": "Conflito ou pressa na carreira"},
    {"planet_a": "uranus", "aspect": "conjunction", "planet_b": "MC", "code": "career_change", "weight": 5.0, "domain": "carreira_status", "polarity": "mixed", "label": "Mudanca brusca de rumo profissional"},
    {"planet_a": "saturn", "aspect": "opposition", "planet_b": "MC", "code": "career_pressure", "weight": 4.0, "domain": "carreira_status", "polarity": "challenging", "label": "Pressao publica ou profissional"},
    {"planet_a": "sun", "aspect": "square", "planet_b": "saturn", "code": "authority_conflict", "weight": 3.0, "domain": "carreira_status", "polarity": "challenging", "label": "Atrito com cobranca e autoridade"},
    {"planet_a": "venus", "aspect": "conjunction", "planet_b": "venus", "code": "relationship_start", "weight": 4.0, "domain": "relacionamentos", "polarity": "supportive", "label": "Abertura para novo vinculo"},
    {"planet_a": "jupiter", "aspect": "conjunction", "planet_b": "venus", "code": "love_expansion", "weight": 4.2, "domain": "relacionamentos", "polarity": "supportive", "label": "Expansao afetiva e acolhimento"},
    {"planet_a": "saturn", "aspect": "opposition", "planet_b": "venus", "code": "relationship_test", "weight": 5.0, "domain": "relacionamentos", "polarity": "challenging", "label": "Teste serio de relacao"},
    {"planet_a": "saturn", "aspect": "square", "planet_b": "venus", "code": "relationship_block", "weight": 5.0, "domain": "relacionamentos", "polarity": "challenging", "label": "Bloqueio ou distancia afetiva"},
    {"planet_a": "pluto", "aspect": "square", "planet_b": "venus", "code": "intense_relationship", "weight": 4.8, "domain": "relacionamentos", "polarity": "mixed", "label": "Relacao intensa e transformadora"},
    {"planet_a": "uranus", "aspect": "conjunction", "planet_b": "venus", "code": "sudden_love", "weight": 4.8, "domain": "relacionamentos", "polarity": "mixed", "label": "Aproximacao repentina ou imprevisivel"},
    {"planet_a": "mars", "aspect": "square", "planet_b": "venus", "code": "conflict_relationship", "weight": 3.2, "domain": "relacionamentos", "polarity": "challenging", "label": "Atrito, ciúme ou friccao afetiva"},
    {"planet_a": "moon", "aspect": "conjunction", "planet_b": "venus", "code": "emotional_bond", "weight": 3.0, "domain": "relacionamentos", "polarity": "supportive", "label": "Vinculo emocional ganha corpo"},
    {"planet_a": "jupiter", "aspect": "trine", "planet_b": "venus", "code": "marriage_window", "weight": 5.0, "domain": "relacionamentos", "polarity": "supportive", "label": "Janela de compromisso ou casamento"},
    {"planet_a": "saturn", "aspect": "trine", "planet_b": "venus", "code": "commitment", "weight": 5.0, "domain": "relacionamentos", "polarity": "supportive", "label": "Compromisso e estabilizacao"},
    {"planet_a": "uranus", "aspect": "square", "planet_b": "venus", "code": "breakup", "weight": 5.0, "domain": "relacionamentos", "polarity": "challenging", "label": "Ruptura afetiva ou quebra brusca"},
    {"planet_a": "uranus", "aspect": "opposition", "planet_b": "venus", "code": "sudden_break", "weight": 5.0, "domain": "relacionamentos", "polarity": "challenging", "label": "Quebra repentina de vinculo"},
    {"planet_a": "saturn", "aspect": "opposition", "planet_b": "moon", "code": "emotional_cut", "weight": 4.0, "domain": "relacionamentos", "polarity": "challenging", "label": "Esfriamento emocional forte"},
    {"planet_a": "pluto", "aspect": "square", "planet_b": "moon", "code": "deep_emotional_break", "weight": 5.0, "domain": "relacionamentos", "polarity": "challenging", "label": "Ruptura emocional profunda"},
    {"planet_a": "jupiter", "aspect": "conjunction", "planet_b": "venus", "code": "financial_gain", "weight": 4.0, "domain": "financeiro", "polarity": "supportive", "label": "Entrada ou ganho financeiro"},
    {"planet_a": "jupiter", "aspect": "trine", "planet_b": "venus", "code": "money_flow", "weight": 3.2, "domain": "financeiro", "polarity": "supportive", "label": "Fluxo de dinheiro melhora"},
    {"planet_a": "saturn", "aspect": "square", "planet_b": "venus", "code": "financial_restriction", "weight": 5.0, "domain": "financeiro", "polarity": "challenging", "label": "Restricao ou aperto financeiro"},
    {"planet_a": "pluto", "aspect": "conjunction", "planet_b": "venus", "code": "financial_transformation", "weight": 5.0, "domain": "crises_recursos", "polarity": "mixed", "label": "Reestruturacao profunda de recursos"},
    {"planet_a": "uranus", "aspect": "conjunction", "planet_b": "venus", "code": "unexpected_money", "weight": 4.0, "domain": "financeiro", "polarity": "mixed", "label": "Dinheiro inesperado ou instavel"},
    {"planet_a": "mars", "aspect": "square", "planet_b": "venus", "code": "financial_loss", "weight": 4.0, "domain": "financeiro", "polarity": "challenging", "label": "Perda, gasto ou pressa financeira"},
    {"planet_a": "mars", "aspect": "square", "planet_b": "saturn", "code": "accident_risk", "weight": 5.0, "domain": "saude_rotina", "polarity": "challenging", "label": "Sobrecarga, atrito ou risco fisico"},
    {"planet_a": "mars", "aspect": "opposition", "planet_b": "pluto", "code": "extreme_conflict", "weight": 5.0, "domain": "transicoes", "polarity": "challenging", "label": "Conflito extremo e pressao de virada"},
    {"planet_a": "saturn", "aspect": "square", "planet_b": "moon", "code": "emotional_low", "weight": 4.0, "domain": "psicologico_espiritual", "polarity": "challenging", "label": "Baixa emocional e peso psiquico"},
    {"planet_a": "pluto", "aspect": "conjunction", "planet_b": "moon", "code": "psychological_transformation", "weight": 5.0, "domain": "psicologico_espiritual", "polarity": "mixed", "label": "Transformacao emocional profunda"},
]

TECHNIQUE_FACTORS = {
    "transits": 1.0,
    "progressions": 0.72,
    "solar_arc": 0.82,
}

TECHNIQUE_WINDOWS = {
    "transits": 28,
    "progressions": 120,
    "solar_arc": 210,
}

AREA_KEY_BY_DOMAIN = {
    "relacionamentos": "relacionamento",
    "criatividade_afetos": "relacionamento",
    "amigos_rede": "amizades",
    "familia_lar": "familia",
    "carreira_status": "carreira",
    "saude_rotina": "saude",
    "expansao_sentido": "viagens",
    "comunicacao": "viagens",
    "identidade": "transicoes",
    "crises_recursos": "transicoes",
    "psicologico_espiritual": "transicoes",
    "financeiro": "financas",
}


def _normalize_point(name: str | None) -> str | None:
    if name is None:
        return None
    lowered = str(name).strip().lower()
    return POINT_ALIASES.get(lowered, lowered.upper() if lowered in {"mc", "ic", "asc", "dsc"} else lowered)


def _fallback_time_window(reference_date: date, technique: str) -> dict[str, Any]:
    duration = TECHNIQUE_WINDOWS.get(technique, 30)
    end = reference_date + timedelta(days=duration - 1)
    peak = reference_date + timedelta(days=max(0, duration // 2))
    return {
        "start": reference_date.isoformat(),
        "end": end.isoformat(),
        "peak": peak.isoformat(),
        "duration_days": duration,
        "precision": "mixed" if duration > 30 else "day",
    }


def _aspect_sources(analysis: dict[str, Any]) -> list[tuple[str, list[dict[str, Any]]]]:
    return [
        ("transits", list(analysis.get("transits", {}).get("aspects", []))),
        ("progressions", list(analysis.get("progressions", {}).get("aspects", []))),
        ("solar_arc", list(analysis.get("solar_arc", {}).get("aspects", []))),
    ]


def build_rule_hits(analysis: dict[str, Any]) -> list[dict[str, Any]]:
    user_rule_overrides = dict(analysis.get("user_rule_overrides") or {})
    reference_date = date.fromisoformat(str(analysis["utc_reference"]["input_local"]["date"]))
    hits: list[dict[str, Any]] = []

    for technique, aspects in _aspect_sources(analysis):
        for aspect in aspects:
            planet_a = _normalize_point(aspect.get("planet_a"))
            planet_b = _normalize_point(aspect.get("planet_b"))
            aspect_name = str(aspect.get("aspect") or "")
            orb = float(aspect.get("orb") or 0.0)
            phase = str(aspect.get("phase") or "")
            orb_factor = max(0.62, 1 - (orb / 7.0))
            phase_factor = 1.08 if phase == "applying" else 0.94 if phase == "separating" else 1.0

            for rule in RULES:
                if planet_a != _normalize_point(rule["planet_a"]):
                    continue
                if planet_b != _normalize_point(rule["planet_b"]):
                    continue
                if aspect_name != str(rule["aspect"]):
                    continue

                base_weight = float(user_rule_overrides.get(str(rule["code"]), rule["weight"]))
                weight = round(base_weight * TECHNIQUE_FACTORS[technique] * orb_factor * phase_factor, 3)
                hits.append(
                    {
                        "technique": technique,
                        "code": rule["code"],
                        "domain": rule["domain"],
                        "polarity": rule["polarity"],
                        "label": rule["label"],
                        "weight": weight,
                        "planet_a": planet_a,
                        "planet_b": planet_b,
                        "aspect": aspect_name,
                        "orb": orb,
                        "phase": phase or "active",
                        "time_window": aspect.get("time_window") or _fallback_time_window(reference_date, technique),
                        "evidence": {
                            "planet_a": aspect.get("planet_a"),
                            "planet_b": aspect.get("planet_b"),
                            "aspect": aspect_name,
                            "orb": orb,
                            "phase": phase,
                        },
                    }
                )

    hits.sort(key=lambda item: (-float(item["weight"]), item["code"]))
    return hits


def build_specialized_insights(
    analysis: dict[str, Any],
    *,
    payload: dict[str, Any] | None = None,
    natal_ephemeris: dict[str, Any] | None = None,
    include_exact_timing: bool = False,
) -> dict[str, Any]:
    rule_hits = build_rule_hits(analysis)
    relationship = detect_relationship_events(analysis, rule_hits)
    financial = detect_financial_cycles(analysis, rule_hits)
    purpose = analyze_life_purpose(analysis)
    timed_events: list[dict[str, Any]] = []
    critical_periods: list[dict[str, Any]] = []
    life_events: list[dict[str, Any]] = []

    if include_exact_timing and payload is not None and natal_ephemeris is not None:
        reference_date = date.fromisoformat(str(payload["reference_date"]))
        timed_events = detect_timed_events(
            natal_ephemeris=natal_ephemeris,
            payload=payload,
            rules=RULES,
            start_date=reference_date,
            days=730,
        )
        for event in timed_events:
            event["area_key"] = AREA_KEY_BY_DOMAIN.get(str(event["domain"]), "transicoes")

        life_events = full_life_event_analysis(timed_events)
        critical_periods = detect_critical_periods(cluster_events_by_date(timed_events))
        relationship["exact_hits"] = [
            event for event in timed_events if event["area_key"] == "relacionamento"
        ][:6]
        financial["exact_hits"] = [
            event for event in timed_events if event["area_key"] == "financas"
        ][:6]
        relationship["critical_periods"] = [
            item
            for item in critical_periods
            if any(event["area_key"] == "relacionamento" for event in item["events"])
        ][:3]
        financial["critical_periods"] = [
            item
            for item in critical_periods
            if any(event["area_key"] == "financas" for event in item["events"])
        ][:3]

    return {
        "rule_hits": rule_hits,
        "relationship": relationship,
        "financial": financial,
        "purpose": purpose,
        "exact_timing": {
            "timed_events": timed_events,
            "critical_periods": critical_periods,
        },
        "life_events": life_events,
    }
