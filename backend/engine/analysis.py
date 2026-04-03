from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict
from datetime import date, datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from astro.aspects import ASPECTS, angular_distance
from astro.ephemeris import calculate_ephemeris
from astro.signs import longitude_to_sign
from astro.time import local_to_utc, utc_isoformat_z

THEME_MAP = {
    1: "identidade",
    2: "financeiro",
    3: "comunicacao",
    4: "familia_lar",
    5: "criatividade_afetos",
    6: "saude_rotina",
    7: "relacionamentos",
    8: "crises_recursos",
    9: "expansao_sentido",
    10: "carreira_status",
    11: "amigos_rede",
    12: "psicologico_espiritual",
}

DOMAIN_LABELS = {
    "identidade": "identidade",
    "financeiro": "financeiro",
    "comunicacao": "comunicacao",
    "familia_lar": "familia e lar",
    "criatividade_afetos": "criatividade e afetos",
    "saude_rotina": "saude e rotina",
    "relacionamentos": "relacionamentos",
    "crises_recursos": "crises e recursos compartilhados",
    "expansao_sentido": "expansao, estudos e proposito",
    "carreira_status": "carreira e status",
    "amigos_rede": "amigos e rede",
    "psicologico_espiritual": "psicologico e recolhimento",
}

TECHNIQUE_WEIGHTS = {
    "profections": 1.0,
    "solar_return": 0.95,
    "transits": 0.74,
    "progressions": 0.7,
    "solar_arc": 0.76,
    "numerology": 0.35,
}

ASPECT_STRENGTH = {
    "conjunction": 0.92,
    "opposition": 0.84,
    "square": 0.8,
    "trine": 0.64,
    "sextile": 0.5,
}

PLANET_STRENGTH = {
    "sun": 0.74,
    "moon": 0.75,
    "mercury": 0.55,
    "venus": 0.62,
    "mars": 0.78,
    "jupiter": 0.72,
    "saturn": 0.85,
    "uranus": 0.72,
    "neptune": 0.68,
    "pluto": 0.9,
}

SIGN_RULERS = {
    "aries": "mars",
    "taurus": "venus",
    "gemini": "mercury",
    "cancer": "moon",
    "leo": "sun",
    "virgo": "mercury",
    "libra": "venus",
    "scorpio": "mars",
    "sagittarius": "jupiter",
    "capricorn": "saturn",
    "aquarius": "saturn",
    "pisces": "jupiter",
}

PLANET_SPEED_WINDOWS = {
    "moon": 3,
    "sun": 7,
    "mercury": 9,
    "venus": 10,
    "mars": 14,
    "jupiter": 45,
    "saturn": 65,
    "uranus": 120,
    "neptune": 150,
    "pluto": 180,
}

NUMEROLOGY_DOMAIN_MAP = {
    1: "identidade",
    2: "relacionamentos",
    3: "comunicacao",
    4: "estrutura",
    5: "expansao_sentido",
    6: "familia_lar",
    7: "psicologico_espiritual",
    8: "carreira_status",
    9: "fechamentos",
    11: "psicologico_espiritual",
    22: "carreira_status",
    33: "amigos_rede",
}

QUALITY_CONFIG = {
    "A": {
        "label": "hora exata",
        "confidence_modifier": 1.0,
        "can_use_houses": True,
        "can_use_angles": True,
    },
    "B": {
        "label": "janela de horario",
        "confidence_modifier": 0.8,
        "can_use_houses": True,
        "can_use_angles": False,
    },
    "C": {
        "label": "horario desconhecido",
        "confidence_modifier": 0.58,
        "can_use_houses": False,
        "can_use_angles": False,
    },
}

WINDOW_TIMES = {
    "morning": "09:00:00",
    "afternoon": "15:00:00",
    "evening": "21:00:00",
}

ANGLE_DOMAIN_MAP = {
    "ascendant": "identidade",
    "descendant": "relacionamentos",
    "midheaven": "carreira_status",
    "imum_coeli": "familia_lar",
}

POINT_DISPLAY_NAMES = {
    "sun": "Sol",
    "moon": "Lua",
    "mercury": "Mercurio",
    "venus": "Venus",
    "mars": "Marte",
    "jupiter": "Jupiter",
    "saturn": "Saturno",
    "uranus": "Urano",
    "neptune": "Netuno",
    "pluto": "Plutao",
    "ascendant": "Ascendente",
    "descendant": "Descendente",
    "midheaven": "MC",
    "imum_coeli": "IC",
    "vertex": "Vertex",
    "ASC": "Ascendente",
    "DSC": "Descendente",
    "MC": "MC",
    "IC": "IC",
}

ANGLE_SHORT_NAMES = {
    "ascendant": "ASC",
    "descendant": "DSC",
    "midheaven": "MC",
    "imum_coeli": "IC",
    "vertex": "Vertex",
}


def get_house_from_longitude(longitude: float, cusps: list[float]) -> int | None:
    if len(cusps) != 12:
        return None

    for index in range(12):
        start = cusps[index]
        end = cusps[(index + 1) % 12]
        if start < end:
            if start <= longitude < end:
                return index + 1
        elif longitude >= start or longitude < end:
            return index + 1
    return None


def _build_time_window(reference_date: date, days: int) -> dict[str, Any]:
    duration_days = max(1, days)
    return {
        "start": reference_date.isoformat(),
        "end": (reference_date + timedelta(days=duration_days - 1)).isoformat(),
        "peak": reference_date.isoformat(),
        "duration_days": duration_days,
        "precision": "day",
    }


def assess_profile_quality(payload: dict[str, Any]) -> dict[str, Any]:
    assumptions: list[str] = []

    birth_time_precision = str(payload.get("birth_time_precision") or "").strip().lower()
    birth_time_window = str(payload.get("birth_time_window") or "").strip().lower() or None
    original_time = payload.get("time")

    if birth_time_precision not in {"exact", "window", "unknown"}:
        birth_time_precision = "exact" if original_time else "unknown"

    if birth_time_precision == "window":
        if birth_time_window not in WINDOW_TIMES:
            birth_time_window = "morning"
            assumptions.append("Janela de horario ausente; usando manha como referencia tecnica.")
        effective_time = WINDOW_TIMES[birth_time_window]
        quality_code = "B"
        assumptions.append(
            "Casas e angulos ficam com confianca reduzida porque o horario nao e exato."
        )
    elif birth_time_precision == "unknown":
        effective_time = "12:00:00"
        quality_code = "C"
        assumptions.append(
            "Horario desconhecido; tecnicas dependentes de casas e angulos foram degradadas."
        )
    else:
        effective_time = original_time.isoformat() if hasattr(original_time, "isoformat") else str(original_time)
        quality_code = "A"

    config = QUALITY_CONFIG[quality_code]
    return {
        "code": quality_code,
        "label": config["label"],
        "birth_time_precision": birth_time_precision,
        "birth_time_window": birth_time_window,
        "effective_time": effective_time,
        "assumptions": assumptions,
        "confidence_modifier": config["confidence_modifier"],
        "can_use_houses": config["can_use_houses"],
        "can_use_angles": config["can_use_angles"],
    }


def _planet_house_map(planets: dict[str, dict[str, Any]], houses: list[float]) -> dict[str, int | None]:
    return {
        planet_name: get_house_from_longitude(float(planet_data["longitude"]), houses)
        for planet_name, planet_data in planets.items()
    }


def _signal_label(planet_a: str, aspect: str, planet_b: str) -> str:
    translated = {
        "conjunction": "conjuncao",
        "opposition": "oposicao",
        "square": "quadratura",
        "trine": "trigono",
        "sextile": "sextil",
    }
    left = POINT_DISPLAY_NAMES.get(planet_a, planet_a.title())
    right = POINT_DISPLAY_NAMES.get(planet_b, planet_b.title())
    return f"{left} em {translated.get(aspect, aspect)} com {right}"


def _infer_domain(
    preferred_house: int | None,
    fallback_house: int | None,
    fallback_domain: str = "identidade",
) -> str:
    if preferred_house is not None:
        return THEME_MAP.get(preferred_house, fallback_domain)
    if fallback_house is not None:
        return THEME_MAP.get(fallback_house, fallback_domain)
    return fallback_domain


def _safe_datetime_combine(raw_date: date, raw_time: str, timezone_name: str) -> datetime:
    parsed_time = time.fromisoformat(raw_time)
    return datetime.combine(raw_date, parsed_time, tzinfo=ZoneInfo(timezone_name))


def _find_aspect(
    planet_a: str,
    planet_b: str,
    longitude_a: float,
    longitude_b: float,
    orb_limit: float,
) -> tuple[str, float, float] | None:
    distance = angular_distance(longitude_a, longitude_b)
    best_name: str | None = None
    best_target = 0.0
    best_orb = orb_limit + 1.0

    for aspect_name, target in ASPECTS.items():
        orb = abs(distance - target)
        if orb <= orb_limit and orb < best_orb:
            best_name = aspect_name
            best_target = target
            best_orb = orb

    if best_name is None:
        return None
    return best_name, best_target, round(best_orb, 6)


def _phase_from_next_day(
    aspect_name: str,
    next_longitude: float,
    natal_longitude: float,
    current_orb: float,
) -> str:
    target_angle = ASPECTS[aspect_name]
    next_distance = angular_distance(next_longitude, natal_longitude)
    next_orb = abs(next_distance - target_angle)
    return "applying" if next_orb < current_orb else "separating"


def _signal_weight(
    *,
    technique: str,
    aspect: str | None,
    planet_a: str | None,
    orb: float | None,
    phase: str | None,
    quality_modifier: float,
) -> float:
    base = TECHNIQUE_WEIGHTS[technique]
    if aspect is not None:
        base *= ASPECT_STRENGTH.get(aspect, 0.45)
    if planet_a is not None:
        base *= PLANET_STRENGTH.get(planet_a, 0.55)
    if orb is not None:
        base *= max(0.42, 1 - (orb / 10.0))
    if phase == "applying":
        base *= 1.08
    elif phase == "separating":
        base *= 0.93
    return round(base * quality_modifier, 3)


def _signal_polarity(aspect: str | None, planet_a: str | None) -> str:
    if aspect in {"square", "opposition"}:
        return "challenging"
    if aspect in {"trine", "sextile"}:
        return "supportive"
    if planet_a in {"saturn", "mars", "pluto"}:
        return "challenging"
    if planet_a == "jupiter":
        return "supportive"
    return "mixed"


def _find_solar_return_datetime(
    natal_sun_longitude: float,
    reference_date: date,
    timezone_name: str,
    lat: float,
    lon: float,
    house_system: str,
) -> datetime:
    local_anchor = datetime(reference_date.year, reference_date.month, reference_date.day, tzinfo=ZoneInfo(timezone_name))
    start = local_anchor.astimezone(ZoneInfo("UTC")) - timedelta(days=2)
    best_dt = start
    best_distance = 999.0

    for hours in range(0, 24 * 5):
        candidate = start + timedelta(hours=hours)
        ephemeris = calculate_ephemeris(candidate, lat, lon, house_system)
        distance = angular_distance(
            float(ephemeris.planets["sun"]["longitude"]),
            natal_sun_longitude,
        )
        if distance < best_distance:
            best_distance = distance
            best_dt = candidate

    refine_start = best_dt - timedelta(hours=1)
    for minutes in range(0, 121, 5):
        candidate = refine_start + timedelta(minutes=minutes)
        ephemeris = calculate_ephemeris(candidate, lat, lon, house_system)
        distance = angular_distance(
            float(ephemeris.planets["sun"]["longitude"]),
            natal_sun_longitude,
        )
        if distance < best_distance:
            best_distance = distance
            best_dt = candidate

    return best_dt


def _progressed_datetime(birth_utc: datetime, reference_utc: datetime) -> datetime:
    age_in_years = max(
        0.0,
        (reference_utc - birth_utc).total_seconds() / (365.2425 * 24 * 60 * 60),
    )
    return birth_utc + timedelta(days=age_in_years)


def _age_years(birth_date: date, reference_date: date) -> int:
    age = reference_date.year - birth_date.year
    if (reference_date.month, reference_date.day) < (birth_date.month, birth_date.day):
        age -= 1
    return max(0, age)


def _angle_aspects(
    source_longitude: float,
    targets: dict[str, float],
    orb_limit: float,
) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for angle_name, target_longitude in targets.items():
        match = _find_aspect(angle_name, angle_name, source_longitude, target_longitude, orb_limit)
        if match is None:
            continue
        aspect_name, target_angle, orb = match
        matches.append(
            {
                "target": angle_name,
                "aspect": aspect_name,
                "target_angle": target_angle,
                "orb": orb,
            }
        )
    return matches


def build_multilayer_analysis(
    *,
    payload: dict[str, Any],
    utc_metadata: dict[str, Any],
    natal_ephemeris: dict[str, Any],
    natal_aspects: list[dict[str, Any]],
    numerology: dict[str, Any],
    reference_date: date,
    profile_quality: dict[str, Any],
) -> dict[str, Any]:
    houses = list(natal_ephemeris["houses"]["cusps"])
    natal_planet_houses = _planet_house_map(natal_ephemeris["planets"], houses)
    natal_angle_signs = {
        angle_name: asdict(longitude_to_sign(longitude))
        for angle_name, longitude in natal_ephemeris["angles"].items()
    }

    reference_utc = local_to_utc(
        payload["reference_date"],
        profile_quality["effective_time"],
        payload["timezone"],
    )
    next_day_utc = reference_utc + timedelta(days=1)

    current_chart = calculate_ephemeris(
        reference_utc,
        payload["lat"],
        payload["lon"],
        payload["house_system"],
    )
    next_day_chart = calculate_ephemeris(
        next_day_utc,
        payload["lat"],
        payload["lon"],
        payload["house_system"],
    )

    current_planet_houses = (
        _planet_house_map(current_chart.planets, houses)
        if profile_quality["can_use_houses"]
        else {planet_name: None for planet_name in current_chart.planets}
    )

    transit_signals: list[dict[str, Any]] = []
    transit_aspects: list[dict[str, Any]] = []
    for transit_planet, transit_data in current_chart.planets.items():
        for natal_planet, natal_data in natal_ephemeris["planets"].items():
            aspect_match = _find_aspect(
                transit_planet,
                natal_planet,
                float(transit_data["longitude"]),
                float(natal_data["longitude"]),
                float(payload["orb_degrees"]),
            )
            if aspect_match is None:
                continue

            aspect_name, target_angle, orb = aspect_match
            phase = _phase_from_next_day(
                aspect_name,
                float(next_day_chart.planets[transit_planet]["longitude"]),
                float(natal_data["longitude"]),
                orb,
            )
            preferred_house = current_planet_houses.get(transit_planet)
            fallback_house = natal_planet_houses.get(natal_planet)
            domain = _infer_domain(preferred_house, fallback_house)
            duration = PLANET_SPEED_WINDOWS.get(transit_planet, 21)
            weight = _signal_weight(
                technique="transits",
                aspect=aspect_name,
                planet_a=transit_planet,
                orb=orb,
                phase=phase,
                quality_modifier=float(profile_quality["confidence_modifier"]),
            )
            polarity = _signal_polarity(aspect_name, transit_planet)

            transit_aspect = {
                "planet_a": transit_planet,
                "planet_b": natal_planet,
                "aspect": aspect_name,
                "target_angle": target_angle,
                "orb": orb,
                "phase": phase,
                "domain": domain,
                "transit_house": preferred_house,
                "natal_house": fallback_house,
                "time_window": _build_time_window(reference_date, duration),
                "weight": weight,
            }
            transit_aspects.append(transit_aspect)
            transit_signals.append(
                {
                    "technique": "transits",
                    "domain": domain,
                    "label": _signal_label(transit_planet, aspect_name, natal_planet),
                    "weight": weight,
                    "polarity": polarity,
                    "phase": phase,
                    "kind": "aspect",
                    "time_window": transit_aspect["time_window"],
                    "evidence": transit_aspect,
                }
            )

        if profile_quality["can_use_angles"]:
            for angle_name, angle_longitude in natal_ephemeris["angles"].items():
                aspect_match = _find_aspect(
                    transit_planet,
                    angle_name,
                    float(transit_data["longitude"]),
                    float(angle_longitude),
                    float(payload["orb_degrees"]),
                )
                if aspect_match is None:
                    continue

                aspect_name, target_angle, orb = aspect_match
                phase = _phase_from_next_day(
                    aspect_name,
                    float(next_day_chart.planets[transit_planet]["longitude"]),
                    float(angle_longitude),
                    orb,
                )
                domain = ANGLE_DOMAIN_MAP.get(angle_name, "identidade")
                duration = PLANET_SPEED_WINDOWS.get(transit_planet, 21)
                weight = _signal_weight(
                    technique="transits",
                    aspect=aspect_name,
                    planet_a=transit_planet,
                    orb=orb,
                    phase=phase,
                    quality_modifier=float(profile_quality["confidence_modifier"]),
                )
                polarity = _signal_polarity(aspect_name, transit_planet)
                angle_code = ANGLE_SHORT_NAMES.get(angle_name, angle_name)

                transit_aspect = {
                    "planet_a": transit_planet,
                    "planet_b": angle_code,
                    "aspect": aspect_name,
                    "target_angle": target_angle,
                    "orb": orb,
                    "phase": phase,
                    "domain": domain,
                    "transit_house": current_planet_houses.get(transit_planet),
                    "natal_house": None,
                    "target_kind": "angle",
                    "time_window": _build_time_window(reference_date, duration),
                    "weight": weight,
                }
                transit_aspects.append(transit_aspect)
                transit_signals.append(
                    {
                        "technique": "transits",
                        "domain": domain,
                        "label": _signal_label(transit_planet, aspect_name, angle_code),
                        "weight": weight,
                        "polarity": polarity,
                        "phase": phase,
                        "kind": "angle_aspect",
                        "time_window": transit_aspect["time_window"],
                        "evidence": {
                            **transit_aspect,
                            "angle_name": angle_name,
                        },
                    }
                )

    birth_date = date.fromisoformat(payload["date"])
    profected_house = (_age_years(birth_date, reference_date) % 12) + 1
    profected_longitude = houses[profected_house - 1]
    profected_sign = asdict(longitude_to_sign(profected_longitude))
    profected_domain = THEME_MAP[profected_house]
    profections = {
        "age": _age_years(birth_date, reference_date),
        "activated_house": profected_house,
        "activated_domain": profected_domain,
        "activated_sign": profected_sign,
        "lord_of_year": SIGN_RULERS[profected_sign["sign_en"]],
        "time_window": _build_time_window(date(reference_date.year, 1, 1), 365),
        "signal": {
            "technique": "profections",
            "domain": profected_domain,
            "label": f"Profeccao anual ativa a casa {profected_house}",
            "weight": round(
                TECHNIQUE_WEIGHTS["profections"] * float(profile_quality["confidence_modifier"]),
                3,
            ),
            "polarity": "mixed",
            "phase": "active",
            "kind": "annual_theme",
            "time_window": _build_time_window(date(reference_date.year, 1, 1), 365),
            "evidence": {
                "activated_house": profected_house,
                "activated_sign": profected_sign["sign"],
                "lord_of_year": SIGN_RULERS[profected_sign["sign_en"]],
            },
        },
    }

    solar_return_data: dict[str, Any]
    solar_return_signals: list[dict[str, Any]] = []
    if profile_quality["can_use_houses"]:
        solar_return_dt = _find_solar_return_datetime(
            float(natal_ephemeris["planets"]["sun"]["longitude"]),
            date(reference_date.year, birth_date.month, birth_date.day),
            payload["timezone"],
            payload["lat"],
            payload["lon"],
            payload["house_system"],
        )
        solar_return_chart = calculate_ephemeris(
            solar_return_dt,
            payload["lat"],
            payload["lon"],
            payload["house_system"],
        )
        sr_houses = list(solar_return_chart.houses["cusps"])
        sr_planet_houses = _planet_house_map(solar_return_chart.planets, sr_houses)
        counts = Counter(
            house
            for planet_name, house in sr_planet_houses.items()
            if house is not None and planet_name in {"sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"}
        )
        dominant_house_counts = counts.most_common(2)
        angle_hits = []
        for planet_name, planet_data in solar_return_chart.planets.items():
            for angle_name, angle_longitude in solar_return_chart.angles.items():
                orb = angular_distance(float(planet_data["longitude"]), angle_longitude)
                if orb <= 8:
                    angle_hits.append({"planet": planet_name, "angle": angle_name, "orb": round(orb, 6)})

        for rank, (house_number, count) in enumerate(dominant_house_counts, start=1):
            domain = THEME_MAP[house_number]
            solar_return_signals.append(
                {
                    "technique": "solar_return",
                    "domain": domain,
                    "label": f"Retorno solar concentra foco na casa {house_number}",
                    "weight": round(
                        (TECHNIQUE_WEIGHTS["solar_return"] - ((rank - 1) * 0.12))
                        * float(profile_quality["confidence_modifier"]),
                        3,
                    ),
                    "polarity": "mixed",
                    "phase": "annual",
                    "kind": "annual_theme",
                    "time_window": _build_time_window(date(reference_date.year, 1, 1), 365),
                    "evidence": {
                        "house": house_number,
                        "domain": domain,
                        "planet_count": count,
                    },
                }
            )

        solar_return_data = {
            "available": True,
            "utc_datetime": utc_isoformat_z(solar_return_dt),
            "planet_houses": sr_planet_houses,
            "dominant_houses": [
                {
                    "house": house_number,
                    "domain": THEME_MAP[house_number],
                    "planet_count": count,
                }
                for house_number, count in dominant_house_counts
            ],
            "angle_hits": angle_hits,
        }
    else:
        solar_return_data = {
            "available": False,
            "reason": "quality_c_blocks_house_based_solar_return",
        }

    birth_local_dt = _safe_datetime_combine(
        birth_date,
        profile_quality["effective_time"],
        payload["timezone"],
    )
    birth_utc = birth_local_dt.astimezone(ZoneInfo("UTC"))
    progressed_utc = _progressed_datetime(birth_utc, reference_utc)
    progressed_chart = calculate_ephemeris(
        progressed_utc,
        payload["lat"],
        payload["lon"],
        payload["house_system"],
    )
    progressed_signals: list[dict[str, Any]] = []
    progressed_aspects: list[dict[str, Any]] = []
    for progressed_planet, progressed_data in progressed_chart.planets.items():
        for natal_planet, natal_data in natal_ephemeris["planets"].items():
            aspect_match = _find_aspect(
                progressed_planet,
                natal_planet,
                float(progressed_data["longitude"]),
                float(natal_data["longitude"]),
                1.0,
            )
            if aspect_match is None:
                continue
            aspect_name, target_angle, orb = aspect_match
            domain = _infer_domain(
                natal_planet_houses.get(natal_planet),
                natal_planet_houses.get(progressed_planet),
            )
            weight = _signal_weight(
                technique="progressions",
                aspect=aspect_name,
                planet_a=progressed_planet,
                orb=orb,
                phase="exact",
                quality_modifier=float(profile_quality["confidence_modifier"]),
            )
            evidence = {
                "planet_a": progressed_planet,
                "planet_b": natal_planet,
                "aspect": aspect_name,
                "target_angle": target_angle,
                "orb": orb,
            }
            progressed_aspects.append(evidence)
            progressed_signals.append(
                {
                    "technique": "progressions",
                    "domain": domain,
                    "label": f"Progressao de {progressed_planet.title()} ativa {natal_planet.title()}",
                    "weight": weight,
                    "polarity": _signal_polarity(aspect_name, progressed_planet),
                    "phase": "background",
                    "kind": "progression",
                    "time_window": _build_time_window(reference_date, 120),
                    "evidence": evidence,
                }
            )

    age_years = _age_years(birth_date, reference_date)
    solar_arc_signals: list[dict[str, Any]] = []
    solar_arc_aspects: list[dict[str, Any]] = []
    directed_points = {
        **{
            planet_name: (float(planet_data["longitude"]) + age_years) % 360.0
            for planet_name, planet_data in natal_ephemeris["planets"].items()
        },
        **{
            angle_name: (float(longitude) + age_years) % 360.0
            for angle_name, longitude in natal_ephemeris["angles"].items()
            if profile_quality["can_use_angles"]
        },
    }

    target_points = {
        **{name: float(data["longitude"]) for name, data in natal_ephemeris["planets"].items()},
        **{
            angle_name: float(longitude)
            for angle_name, longitude in natal_ephemeris["angles"].items()
            if profile_quality["can_use_angles"]
        },
    }

    for directed_name, directed_longitude in directed_points.items():
        for target_name, target_longitude in target_points.items():
            aspect_match = _find_aspect(
                directed_name,
                target_name,
                directed_longitude,
                target_longitude,
                1.0,
            )
            if aspect_match is None:
                continue
            aspect_name, target_angle, orb = aspect_match
            domain = (
                ANGLE_DOMAIN_MAP.get(target_name)
                if target_name in ANGLE_DOMAIN_MAP
                else _infer_domain(natal_planet_houses.get(target_name), None)
            )
            weight = _signal_weight(
                technique="solar_arc",
                aspect=aspect_name,
                planet_a=directed_name if directed_name in PLANET_STRENGTH else None,
                orb=orb,
                phase="exact",
                quality_modifier=float(profile_quality["confidence_modifier"]),
            )
            evidence = {
                "planet_a": directed_name,
                "planet_b": target_name,
                "aspect": aspect_name,
                "target_angle": target_angle,
                "orb": orb,
            }
            solar_arc_aspects.append(evidence)
            solar_arc_signals.append(
                {
                    "technique": "solar_arc",
                    "domain": domain,
                    "label": f"Arco solar de {directed_name.title()} toca {target_name.title()}",
                    "weight": weight,
                    "polarity": _signal_polarity(aspect_name, directed_name if directed_name in PLANET_STRENGTH else None),
                    "phase": "structural",
                    "kind": "solar_arc",
                    "time_window": _build_time_window(reference_date, 180),
                    "evidence": evidence,
                }
            )

    personal_year = numerology["personal_year"]
    numerology_domain = NUMEROLOGY_DOMAIN_MAP.get(int(personal_year["value"]), "identidade")
    numerology_signal = {
        "technique": "numerology",
        "domain": numerology_domain,
        "label": f"Ano pessoal {personal_year['value']} reforca {numerology_domain.replace('_', ' ')}",
        "weight": round(
            TECHNIQUE_WEIGHTS["numerology"] * float(profile_quality["confidence_modifier"]),
            3,
        ),
        "polarity": "mixed",
        "phase": "annual",
        "kind": "numerology",
        "time_window": _build_time_window(date(reference_date.year, 1, 1), 365),
        "evidence": {
            "life_path_number": numerology["life_path_number"],
            "personal_year": personal_year,
        },
    }

    signals = [
        profections["signal"],
        *solar_return_signals,
        *transit_signals,
        *progressed_signals,
        *solar_arc_signals,
        numerology_signal,
    ]

    techniques_used = [
        technique_name
        for technique_name, is_used in (
            ("natal", True),
            ("transits", bool(transit_signals)),
            ("profections", True),
            ("solar_return", solar_return_data.get("available", False)),
            ("progressions", bool(progressed_signals)),
            ("solar_arc", bool(solar_arc_signals)),
            ("numerology", True),
        )
        if is_used
    ]

    return {
        "profile_quality": profile_quality,
        "theme_map": THEME_MAP,
        "natal": {
            "planet_houses": natal_planet_houses,
            "angles": natal_ephemeris["angles"],
            "angle_signs": natal_angle_signs,
            "aspects": natal_aspects,
        },
        "transits": {
            "reference_utc": utc_isoformat_z(reference_utc),
            "planet_houses": current_planet_houses,
            "aspects": transit_aspects,
        },
        "profections": profections,
        "solar_return": solar_return_data,
        "progressions": {
            "progressed_utc": utc_isoformat_z(progressed_utc),
            "aspects": progressed_aspects,
        },
        "solar_arc": {
            "age_years": age_years,
            "aspects": solar_arc_aspects,
        },
        "numerology": {
            **numerology,
            "method": {
                "life_path": "pitagorico-reduzindo-todos-os-digitos",
                "personal_year": "dia-mes-nascimento + ano de referencia",
            },
        },
        "signals": signals,
        "techniques_used": techniques_used,
        "utc_reference": utc_metadata,
    }
