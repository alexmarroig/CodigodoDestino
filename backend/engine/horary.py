from __future__ import annotations

from dataclasses import asdict
from datetime import date
from typing import Any

from astro.aspects import angular_distance
from astro.ephemeris import calculate_ephemeris
from astro.signs import longitude_to_sign
from astro.time import convert_with_metadata, local_to_utc
from engine.analysis import SIGN_RULERS, THEME_MAP, get_house_from_longitude

QUESTION_HOUSE_MAP = {
    "carreira": 10,
    "emprego": 10,
    "trabalho": 10,
    "dinheiro": 2,
    "finance": 2,
    "amor": 7,
    "relacao": 7,
    "casamento": 7,
    "volta": 7,
    "familia": 4,
    "casa": 4,
    "mudanca": 4,
    "saude": 6,
    "corpo": 6,
    "rotina": 6,
    "amizade": 11,
    "amigos": 11,
}

MAJOR_ASPECTS = {
    "conjunction": 0.0,
    "sextile": 60.0,
    "square": 90.0,
    "trine": 120.0,
    "opposition": 180.0,
}


def _find_aspect(longitude_a: float, longitude_b: float, orb_limit: float) -> dict[str, Any] | None:
    distance = angular_distance(longitude_a, longitude_b)
    best: dict[str, Any] | None = None
    for aspect_name, target in MAJOR_ASPECTS.items():
        orb = abs(distance - target)
        if orb > orb_limit:
            continue
        if best is None or orb < float(best["orb"]):
            best = {
                "aspect": aspect_name,
                "target_angle": target,
                "orb": round(orb, 6),
            }
    return best


def _question_house(question: str) -> int:
    normalized = question.lower()
    for keyword, house in QUESTION_HOUSE_MAP.items():
        if keyword in normalized:
            return house
    return 7


def _strictures(ephemeris: dict[str, Any], orb_degrees: float) -> list[dict[str, Any]]:
    strictures: list[dict[str, Any]] = []
    asc_sign = longitude_to_sign(float(ephemeris["angles"]["ascendant"]))
    moon_sign = longitude_to_sign(float(ephemeris["planets"]["moon"]["longitude"]))

    if asc_sign.degree_in_sign < 3:
        strictures.append(
            {
                "code": "early_ascendant",
                "message": "Ascendente em grau inicial sugere que a situacao ainda esta muito crua.",
            }
        )
    if asc_sign.degree_in_sign > 27:
        strictures.append(
            {
                "code": "late_ascendant",
                "message": "Ascendente em grau final sugere que o processo ja esta muito adiantado.",
            }
        )
    if moon_sign.degree_in_sign > 27:
        strictures.append(
            {
                "code": "late_moon",
                "message": "Lua em fim de signo indica mudanca de contexto ou leitura mais instavel.",
            }
        )

    moon_longitude = float(ephemeris["planets"]["moon"]["longitude"])
    moon_has_major_application = False
    for planet_name, planet_data in ephemeris["planets"].items():
        if planet_name == "moon":
            continue
        if _find_aspect(moon_longitude, float(planet_data["longitude"]), orb_degrees) is not None:
            moon_has_major_application = True
            break
    if not moon_has_major_application:
        strictures.append(
            {
                "code": "void_of_course_moon",
                "message": "A Lua nao forma aspecto maior imediato, o que enfraquece conclusoes definitivas.",
            }
        )

    return strictures


def analyze_horary(payload: dict[str, Any]) -> dict[str, Any]:
    utc_metadata = convert_with_metadata(payload["date"], payload["time"], payload["timezone"])
    question_utc = local_to_utc(payload["date"], payload["time"], payload["timezone"])
    ephemeris = calculate_ephemeris(
        question_utc,
        payload["lat"],
        payload["lon"],
        payload["house_system"],
    )
    chart = {
        "utc": asdict(utc_metadata),
        "planets": ephemeris.planets,
        "angles": ephemeris.angles,
        "houses": ephemeris.houses,
    }

    question_house = _question_house(payload["question"])
    question_house_domain = THEME_MAP.get(question_house, "relacionamentos")
    asc_sign = asdict(longitude_to_sign(float(ephemeris.angles["ascendant"])))
    quesited_sign = asdict(longitude_to_sign(float(ephemeris.houses["cusps"][question_house - 1])))
    querent_ruler = SIGN_RULERS[asc_sign["sign_en"]]
    quesited_ruler = SIGN_RULERS[quesited_sign["sign_en"]]
    moon_longitude = float(ephemeris.planets["moon"]["longitude"])
    querent_longitude = float(ephemeris.planets[querent_ruler]["longitude"])
    quesited_longitude = float(ephemeris.planets[quesited_ruler]["longitude"])

    strictures = _strictures(chart, float(payload["orb_degrees"]))
    querent_aspect = _find_aspect(
        querent_longitude,
        quesited_longitude,
        float(payload["orb_degrees"]),
    )
    moon_aspect = _find_aspect(
        moon_longitude,
        quesited_longitude,
        float(payload["orb_degrees"]),
    )

    testimonies_for: list[dict[str, Any]] = []
    testimonies_against: list[dict[str, Any]] = []

    if querent_aspect is not None:
        testimony = {
            "label": f"{querent_ruler.title()} em {querent_aspect['aspect']} com {quesited_ruler.title()}",
            "weight": 0.95 - float(querent_aspect["orb"]) / 10,
            "evidence": querent_aspect,
        }
        if querent_aspect["aspect"] in {"trine", "sextile", "conjunction"}:
            testimonies_for.append(testimony)
        else:
            testimonies_against.append(testimony)

    if moon_aspect is not None:
        testimony = {
            "label": f"Lua em {moon_aspect['aspect']} com {quesited_ruler.title()}",
            "weight": 0.82 - float(moon_aspect["orb"]) / 10,
            "evidence": moon_aspect,
        }
        if moon_aspect["aspect"] in {"trine", "sextile", "conjunction"}:
            testimonies_for.append(testimony)
        else:
            testimonies_against.append(testimony)

    if strictures:
        testimonies_against.append(
            {
                "label": "Consideracoes antes do julgamento enfraquecem certeza.",
                "weight": 0.45,
                "evidence": {"strictures": [item["code"] for item in strictures]},
            }
        )

    for_weight = round(sum(float(item["weight"]) for item in testimonies_for), 3)
    against_weight = round(sum(float(item["weight"]) for item in testimonies_against), 3)
    is_radical = len(strictures) == 0

    if not is_radical and abs(for_weight - against_weight) < 0.35:
        judgment = "indeterminado"
        uncertainty_reason = "O mapa tem restricoes e os testemunhos estao equilibrados."
    elif for_weight > against_weight + 0.25:
        judgment = "tende a sim"
        uncertainty_reason = "Ha mais testimonios favoraveis do que contrarios."
    elif against_weight > for_weight + 0.25:
        judgment = "tende a nao"
        uncertainty_reason = "Ha mais testimonios contrarios do que favoraveis."
    else:
        judgment = "indeterminado"
        uncertainty_reason = "Os testimonios ainda nao convergem o bastante."

    confidence_score = max(0.2, min(0.92, 0.45 + abs(for_weight - against_weight) * 0.35 - (0.12 * len(strictures))))
    confidence_level = "high" if confidence_score >= 0.74 else "medium" if confidence_score >= 0.5 else "low"

    return {
        "question": payload["question"],
        "domain": question_house_domain,
        "chart": chart,
        "is_radical": is_radical,
        "strictures": strictures,
        "significators": {
            "querent_house": 1,
            "querent_sign": asc_sign,
            "querent_ruler": querent_ruler,
            "quesited_house": question_house,
            "quesited_domain": question_house_domain,
            "quesited_sign": quesited_sign,
            "quesited_ruler": quesited_ruler,
            "moon": "moon",
        },
        "testimonies_for": testimonies_for,
        "testimonies_against": testimonies_against,
        "judgment": judgment,
        "confidence": {
            "level": confidence_level,
            "score": round(confidence_score, 2),
        },
        "uncertainty_reason": uncertainty_reason,
    }
