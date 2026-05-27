"""
Brady-style cause-action-effect fields and hard-aspect gates for impactful events.
"""

from __future__ import annotations

from typing import Any

from engine.astro_confirmation import SLOW_PLANETS, TENSE_ASPECTS

HARD_ASPECTS: frozenset[str] = frozenset({"conjunction", "square", "opposition"})
SOFT_ASPECTS: frozenset[str] = frozenset({"trine", "sextile"})

MALEFICS: frozenset[str] = frozenset({"saturn", "mars", "uranus", "neptune", "pluto"})
BENEFICS: frozenset[str] = frozenset({"jupiter", "venus"})
LUMINARIES: frozenset[str] = frozenset({"sun", "moon"})

ASPECT_NATURE_PT: dict[str, str] = {
    "conjunction": "fusão intensa",
    "square": "choque e tensão",
    "opposition": "conflito ou polarização (muitas vezes com terceiros)",
    "trine": "fluxo facilitado",
    "sextile": "oportunidade leve",
}

_HOUSE_CAUSA_PT: dict[int, str] = {
    1: "identidade e corpo",
    2: "dinheiro e recursos",
    3: "comunicação e deslocamentos curtos",
    4: "lar e família",
    5: "afeto e criatividade",
    6: "rotina, saúde e trabalho diário",
    7: "parcerias e contratos",
    8: "crises, dívidas e transformação",
    9: "estudos, viagens e sentido",
    10: "carreira e status",
    11: "amigos e projetos coletivos",
    12: "inconsciente, isolamento e encerramentos",
}

# Subtypes that must not be fatalistic / drastic on soft aspects alone
_IMPACT_SUBTYPES_REQUIRING_HARD: frozenset[str] = frozenset({
    "crise_saude",
    "acidente_fisico",
    "risco_fisico_agudo",
    "separacao_abrupta",
    "separacao_termino",
    "briga_grave",
    "briga_forte",
    "perda_emprego",
    "auditoria_carreira_ou_demissao",
    "mudanca_abrupta_carreira",
    "perda_financeira",
    "mudanca_residencia_radical",
    "reestruturacao_familiar_ou_luto",
})


def aspect_nature_label(aspect: str | None) -> str:
    return ASPECT_NATURE_PT.get(str(aspect or ""), "ação mista")


def _norm_planet(name: str) -> str:
    return str(name or "").replace("_", " ").strip().lower()


def is_tense_conjunction(planet_a: str, planet_b: str) -> bool:
    """Conjunction is tense only with malefic or afflicted luminary pairing."""
    pa, pb = _norm_planet(planet_a), _norm_planet(planet_b)
    bodies = {pa, pb}
    if bodies & MALEFICS:
        return True
    if bodies <= LUMINARIES:
        return False
    if (bodies & LUMINARIES) and (bodies & MALEFICS):
        return True
    if (bodies & LUMINARIES) and (bodies & BENEFICS):
        return False
    return pa in MALEFICS or pb in MALEFICS


def is_tense_aspect(aspect: str, planet_a: str, planet_b: str) -> bool:
    asp = str(aspect or "")
    pa, pb = _norm_planet(planet_a), _norm_planet(planet_b)
    bodies = {pa, pb}
    fast_only = bodies <= (LUMINARIES | BENEFICS | frozenset({"mercury", "mars"}))
    if asp in {"square", "opposition"}:
        if fast_only and not (bodies & MALEFICS):
            return False
        return True
    if asp == "conjunction":
        return is_tense_conjunction(planet_a, planet_b)
    return False


def enrich_brady_evidence(evidence: dict[str, Any]) -> dict[str, Any]:
    """Add aspect_nature and Brady cause/action/effect keys to transit evidence."""
    enriched = dict(evidence)
    aspect = str(enriched.get("aspect") or "")
    enriched["aspect_nature"] = aspect_nature_label(aspect)

    transit_house = enriched.get("transit_house")
    natal_house = enriched.get("natal_house")
    if isinstance(transit_house, int):
        enriched["cause_house_theme"] = _HOUSE_CAUSA_PT.get(transit_house, "vida")
    if isinstance(natal_house, int):
        enriched["effect_house_theme"] = _HOUSE_CAUSA_PT.get(natal_house, "vida")

    return enriched


def enrich_transit_signal_evidence(signal: dict[str, Any]) -> dict[str, Any]:
    if str(signal.get("technique") or "") != "transits":
        return signal
    evidence = enrich_brady_evidence(dict(signal.get("evidence") or {}))
    updated = dict(signal)
    updated["evidence"] = evidence
    return updated


def format_brady_por_que_line(evidence: dict[str, Any]) -> str | None:
    """Portuguese 'Por quê' line: Causa → Ação → Efeito."""
    aspect = str(evidence.get("aspect") or "")
    if not aspect:
        return None

    cause_h = evidence.get("transit_house")
    effect_h = evidence.get("natal_house")
    nature = evidence.get("aspect_nature") or aspect_nature_label(aspect)

    cause_part = (
        f"Causa: Casa {cause_h} ({evidence.get('cause_house_theme', 'vida')})"
        if isinstance(cause_h, int)
        else "Causa: campo ativado pelo trânsito"
    )
    action_part = f"Ação: {nature}"
    effect_part = (
        f"Efeito: Casa {effect_h} ({evidence.get('effect_house_theme', 'vida')})"
        if isinstance(effect_h, int)
        else "Efeito: ponto natal ativado"
    )
    return f"{cause_part}; {action_part}; {effect_part}"


def has_hard_slow_transit(signals: list[dict[str, Any]]) -> bool:
    """True if a slow planet makes a hard aspect in transit signals."""
    for signal in signals:
        if str(signal.get("technique") or "") != "transits":
            continue
        ev = signal.get("evidence") or {}
        aspect = str(ev.get("aspect") or "")
        pa = str(ev.get("planet_a") or "")
        pb = str(ev.get("planet_b") or "")
        if not is_tense_aspect(aspect, pa, pb):
            continue
        pa_n = pa.replace("_", " ").lower()
        pb_n = pb.replace("_", " ").lower()
        if pa_n in SLOW_PLANETS or pb_n in SLOW_PLANETS:
            return True
    return False


def only_soft_slow_transits(signals: list[dict[str, Any]]) -> bool:
    """True when slow-planet transits exist but none are hard aspects."""
    has_slow = False
    has_hard_slow = False
    for signal in signals:
        if str(signal.get("technique") or "") != "transits":
            continue
        ev = signal.get("evidence") or {}
        pa = str(ev.get("planet_a") or "").replace("_", " ").lower()
        if pa not in SLOW_PLANETS:
            continue
        has_slow = True
        if str(ev.get("aspect") or "") in HARD_ASPECTS:
            has_hard_slow = True
    return has_slow and not has_hard_slow


def subtype_requires_hard_aspect(subtype_key: str) -> bool:
    return subtype_key in _IMPACT_SUBTYPES_REQUIRING_HARD


def soft_aspect_opportunity_note(signals: list[dict[str, Any]]) -> str | None:
    """Return a note when only soft aspects from slow planets are present."""
    if not only_soft_slow_transits(signals):
        return None
    return (
        "Janela de oportunidade ou fase de fluxo — sem aspecto tenso de planeta lento; "
        "não tratar como evento drástico inevitável."
    )
