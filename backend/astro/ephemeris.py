from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List

import swisseph as swe

# -----------------------------------
# CONFIGURAÇÃO SWISS EPHEMERIS
# -----------------------------------

# Ajuste conforme seu ambiente (ex: ./ephe ou /usr/share/ephe)
swe.set_ephe_path("./ephe")

FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL

PLANETS = {
    "sun": swe.SUN,
    "moon": swe.MOON,
    "mercury": swe.MERCURY,
    "venus": swe.VENUS,
    "mars": swe.MARS,
    "jupiter": swe.JUPITER,
    "saturn": swe.SATURN,
}


# -----------------------------------
# TYPES
# -----------------------------------

@dataclass(frozen=True)
class EphemerisResult:
    utc_datetime: str
    julian_day: float
    planets: Dict[str, Dict[str, float]]
    angles: Dict[str, float]
    houses: Dict[str, List[float] | str]


# -----------------------------------
# UTILS
# -----------------------------------

def _round(value: float) -> float:
    return round(value % 360.0, 6)


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
# CORE
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

    planets: Dict[str, Dict[str, float]] = {}

    for name, pid in PLANETS.items():
        try:
            calc, ret = swe.calc_ut(jd, pid, FLAGS)
        except Exception as exc:
            raise RuntimeError(f"Erro ao calcular planeta {name}") from exc

        if ret < 0:
            raise RuntimeError(f"Swiss Ephemeris erro em {name}")

        planets[name] = {
            "longitude": _round(calc[0]),
            "speed": round(calc[3], 6),
        }

    # -------------------------
    # CASAS + ÂNGULOS
    # -------------------------

    try:
        house_code = house_system.encode("ascii")
        cusps, ascmc = swe.houses(jd, lat, lon, house_code)
    except Exception as exc:
        raise RuntimeError("Erro ao calcular casas") from exc

    houses = [_round(c) for c in cusps]

    angles = {
        "ascendant": _round(ascmc[0]),
        "midheaven": _round(ascmc[1]),
    }

    # -------------------------
    # RESULTADO
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