from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List

import swisseph as swe

# -----------------------------------
# CONFIGURAÇÃO SWISS EPHEMERIS
# -----------------------------------

swe.set_ephe_path("./ephe")

FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED  # 🔥 removido SIDEREAL (evita erro)

PLANETS = {
    "sun": swe.SUN,
    "moon": swe.MOON,
    "mercury": swe.MERCURY,
    "venus": swe.VENUS,
    "mars": swe.MARS,
    "jupiter": swe.JUPITER,
    "saturn": swe.SATURN,
}

SIGNS = [
    "aries", "taurus", "gemini", "cancer",
    "leo", "virgo", "libra", "scorpio",
    "sagittarius", "capricorn", "aquarius", "pisces"
]

# -----------------------------------
# TYPES
# -----------------------------------

@dataclass(frozen=True)
class EphemerisResult:
    utc_datetime: str
    julian_day: float
    planets: Dict[str, Dict[str, float | str]]
    angles: Dict[str, float]
    houses: Dict[str, List[float] | str]

# -----------------------------------
# UTILS
# -----------------------------------

def _normalize(deg: float) -> float:
    return round(deg % 360.0, 6)


def _get_sign(longitude: float) -> str:
    index = int(longitude // 30)
    return SIGNS[index]


def julian_day_from_utc(dt_utc: datetime) -> float:
    dt = dt_utc.astimezone(timezone.utc)

    hour = (
        dt.hour
        + dt.minute / 60
        + dt.second / 3600
        + dt.microsecond / 3_600_000_000
    )

    return swe.julday(dt.year, dt.month, dt.day, hour, swe.GREG_CAL)

# -----------------------------------
# CORE ENGINE
# -----------------------------------

def calculate_ephemeris(
    dt_utc: datetime,
    lat: float,
    lon: float,
    house_system: str = "P",
) -> EphemerisResult:

    dt = dt_utc.astimezone(timezone.utc)
    jd = julian_day_from_utc(dt)

    # -------------------------
    # PLANETAS
    # -------------------------

    planets: Dict[str, Dict[str, float | str]] = {}

    for name, pid in PLANETS.items():
        try:
            calc, ret = swe.calc_ut(jd, pid, FLAGS)
        except Exception as exc:
            raise RuntimeError(f"Erro ao calcular planeta {name}") from exc

        if ret < 0:
            raise RuntimeError(f"Erro Swiss Ephemeris em {name}")

        longitude = _normalize(calc[0])

        planets[name] = {
            "longitude": longitude,
            "sign": _get_sign(longitude),
            "speed": round(calc[3], 6),
            "retrograde": calc[3] < 0,
        }

    # -------------------------
    # CASAS + ÂNGULOS
    # -------------------------

    try:
        house_code = house_system.encode("ascii")
        cusps, ascmc = swe.houses(jd, lat, lon, house_code)
    except Exception as exc:
        raise RuntimeError("Erro ao calcular casas") from exc

    houses = [_normalize(c) for c in cusps]

    angles = {
        "ascendant": _normalize(ascmc[0]),
        "midheaven": _normalize(ascmc[1]),
    }

    # -------------------------
    # RESULTADO FINAL
    # -------------------------

    return EphemerisResult(
        utc_datetime=dt.isoformat().replace("+00:00", "Z"),
        julian_day=jd,
        planets=planets,
        angles=angles,
        houses={
            "system": house_system,
            "cusps": houses,
        },
    )