"""Rulebook classifiers for health, career/finance, and family subtypes."""

from __future__ import annotations

from engine.astro_confirmation import (
    classify_career_finance_subtype,
    classify_family_subtype,
    classify_health_subtype,
)


def _sig(planet_a: str, planet_b: str = "sun", aspect: str = "square", house: int | None = None) -> dict:
    ev: dict = {"planet_a": planet_a, "planet_b": planet_b, "aspect": aspect}
    if house is not None:
        ev["transit_house"] = house
    return {"technique": "transits", "evidence": ev}


def test_classify_health_risco_fisico_mars_house_6():
    signals = [_sig("mars", "moon", house=6)]
    assert classify_health_subtype(signals) == "risco_fisico_agudo"


def test_classify_health_cronico_saturn_house_12():
    signals = [_sig("saturn", "moon", house=12)]
    assert classify_health_subtype(signals) == "doenca_cronica"


def test_classify_health_esgotamento_neptune_angle():
    signals = [_sig("neptune", "sun", aspect="square")]
    assert classify_health_subtype(signals) == "esgotamento_confusao"


def test_classify_career_auditoria_saturn_mc_angle():
    signals = [_sig("saturn", "mc", aspect="square")]
    assert classify_career_finance_subtype(signals) == "auditoria_carreira_ou_demissao"


def test_classify_career_mudanca_abrupta_uranus():
    signals = [_sig("uranus", "midheaven", aspect="conjunction")]
    assert classify_career_finance_subtype(signals) == "mudanca_abrupta_carreira"


def test_classify_finance_aperto_saturn_house_2():
    signals = [_sig("saturn", "venus", house=2)]
    assert classify_career_finance_subtype(signals) == "aperto_financeiro"


def test_classify_finance_ganho_jupiter_house_10():
    signals = [_sig("jupiter", "sun", aspect="trine", house=10)]
    assert classify_career_finance_subtype(signals) == "ganho_crescimento"


def test_classify_family_pluto_moon_luto():
    signals = [_sig("pluto", "moon", aspect="square")]
    assert classify_family_subtype(signals) == "reestruturacao_familiar_ou_luto"


def test_classify_family_urano_mudanca_residencia():
    signals = [_sig("uranus", "moon", aspect="conjunction")]
    assert classify_family_subtype(signals) == "mudanca_residencia_radical"
