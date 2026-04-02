from __future__ import annotations

from dataclasses import dataclass

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


@dataclass(frozen=True)
class SignPosition:
    input_longitude: float
    sign: str
    sign_index: int
    degree_in_sign: float
    formatted: str


def normalize_longitude(longitude: float) -> float:
    return longitude % 360.0


def longitude_to_sign(longitude: float) -> SignPosition:
    lon = normalize_longitude(longitude)
    sign_index = int(lon // 30.0)
    degree_in_sign = lon - sign_index * 30.0
    degree_int = int(degree_in_sign)
    minute = int(round((degree_in_sign - degree_int) * 60))
    return SignPosition(
        input_longitude=round(lon, 6),
        sign=SIGNS_PT[sign_index],
        sign_index=sign_index,
        degree_in_sign=round(degree_in_sign, 6),
        formatted=f"{SIGNS_PT[sign_index]} {degree_int}°{minute:02d}'",
    )
