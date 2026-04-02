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


# -----------------------------------
# TYPES
# -----------------------------------

@dataclass(frozen=True)
class SignPosition:
    input_longitude: float
    sign: str
    sign_index: int
    degree_in_sign: float
    formatted: str


# -----------------------------------
# UTILS
# -----------------------------------

def normalize_longitude(longitude: float) -> float:
    """
    Normaliza longitude para faixa 0–360.
    """
    lon = longitude % 360.0

    # evita 360 virar índice inválido
    if lon == 360.0:
        lon = 0.0

    return lon


def _deg_to_dms(degree_float: float) -> tuple[int, int, int]:
    """
    Converte grau decimal em grau/minuto/segundo sem overflow.
    """
    degree_int = int(degree_float)
    minutes_float = (degree_float - degree_int) * 60

    minute = int(minutes_float)
    seconds_float = (minutes_float - minute) * 60
    second = int(seconds_float)

    # evita overflow tipo 29°59'60"
    if second == 60:
        second = 0
        minute += 1

    if minute == 60:
        minute = 0
        degree_int += 1

    return degree_int, minute, second


# -----------------------------------
# CORE
# -----------------------------------

def longitude_to_sign(longitude: float) -> SignPosition:
    lon = normalize_longitude(longitude)

    sign_index = int(lon // 30.0)
    degree_in_sign = lon - sign_index * 30.0

    deg, minute, second = _deg_to_dms(degree_in_sign)

    return SignPosition(
        input_longitude=round(lon, 6),
        sign=SIGNS_PT[sign_index],
        sign_index=sign_index,
        degree_in_sign=round(degree_in_sign, 6),
        formatted=f"{SIGNS_PT[sign_index]} {deg}°{minute:02d}'{second:02d}\"",
    )