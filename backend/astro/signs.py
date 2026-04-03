from __future__ import annotations

from dataclasses import dataclass

SIGNS_PT = [
    "Aries",
    "Touro",
    "Gemeos",
    "Cancer",
    "Leao",
    "Virgem",
    "Libra",
    "Escorpiao",
    "Sagitario",
    "Capricornio",
    "Aquario",
    "Peixes",
]

SIGNS_EN = [
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces",
]


@dataclass(frozen=True)
class SignPosition:
    longitude: float
    sign: str
    sign_en: str
    sign_index: int
    degree_in_sign: float
    degree: int
    minute: int
    second: int
    formatted: str


def normalize_longitude(longitude: float) -> float:
    normalized = longitude % 360.0
    if normalized >= 360.0:
        normalized = 0.0
    return round(normalized, 6)


def _degrees_to_dms(value: float) -> tuple[int, int, int]:
    degree = int(value)
    minutes_float = (value - degree) * 60.0
    minute = int(minutes_float)
    second = int(round((minutes_float - minute) * 60.0))

    if second == 60:
        second = 0
        minute += 1
    if minute == 60:
        minute = 0
        degree += 1

    return degree, minute, second


def longitude_to_sign(longitude: float) -> SignPosition:
    normalized = normalize_longitude(longitude)
    sign_index = int(normalized // 30.0)
    degree_in_sign = round(normalized - (sign_index * 30.0), 6)
    degree, minute, second = _degrees_to_dms(degree_in_sign)

    return SignPosition(
        longitude=normalized,
        sign=SIGNS_PT[sign_index],
        sign_en=SIGNS_EN[sign_index],
        sign_index=sign_index,
        degree_in_sign=degree_in_sign,
        degree=degree,
        minute=minute,
        second=second,
        formatted=f"{SIGNS_PT[sign_index]} {degree}deg{minute:02d}'{second:02d}\"",
    )
