from __future__ import annotations

from dataclasses import dataclass

# -----------------------------------
# CONSTANTES
# -----------------------------------

SIGNS_PT = [
    "Áries",
    "Touro",
    "Gêmeos",
    "Câncer",
    "Leão",
    "Virgem",
    "Libra",
    "Escorpião",
    "Sagitário",
    "Capricórnio",
    "Aquário",
    "Peixes",
]

SIGNS_EN = [
    "aries", "taurus", "gemini", "cancer",
    "leo", "virgo", "libra", "scorpio",
    "sagittarius", "capricorn", "aquarius", "pisces"
]

# -----------------------------------
# TYPES
# -----------------------------------

@dataclass(frozen=True)
class SignPosition:
    longitude: float              # 0–360 normalizado
    sign: str                     # "Áries"
    sign_en: str                  # "aries"
    sign_index: int               # 0–11
    degree_in_sign: float         # 0–30
    degree: int
    minute: int
    second: int
    formatted: str                # "Áries 10°23'15\""


# -----------------------------------
# UTILS
# -----------------------------------

def normalize_longitude(longitude: float) -> float:
    lon = longitude % 360.0

    # proteção extrema contra 360 exato
    if lon >= 360.0:
        lon = 0.0

    return round(lon, 6)


def _deg_to_dms(degree_float: float) -> tuple[int, int, int]:
    degree_int = int(degree_float)

    minutes_float = (degree_float - degree_int) * 60
    minute = int(minutes_float)

    seconds_float = (minutes_float - minute) * 60
    second = int(seconds_float)

    # correções de overflow
    if second >= 60:
        second = 0
        minute += 1

    if minute >= 60:
        minute = 0
        degree_int += 1

    return degree_int, minute, second


# -----------------------------------
# CORE
# -----------------------------------

def longitude_to_sign(longitude: float) -> SignPosition:
    lon = normalize_longitude(longitude)

    sign_index = int(lon // 30.0)
    degree_in_sign = lon - (sign_index * 30.0)

    deg, minute, second = _deg_to_dms(degree_in_sign)

    return SignPosition(
        longitude=lon,
        sign=SIGNS_PT[sign_index],
        sign_en=SIGNS_EN[sign_index],
        sign_index=sign_index,
        degree_in_sign=round(degree_in_sign, 6),
        degree=deg,
        minute=minute,
        second=second,
        formatted=f"{SIGNS_PT[sign_index]} {deg}°{minute:02d}'{second:02d}\"",
    )