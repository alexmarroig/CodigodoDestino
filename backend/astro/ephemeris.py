from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import swisseph as swe

PLANETS = {
    "sun": swe.SUN,
    "moon": swe.MOON,
    "mercury": swe.MERCURY,
    "venus": swe.VENUS,
    "mars": swe.MARS,
    "jupiter": swe.JUPITER,
    "saturn": swe.SATURN,
}


@dataclass(frozen=True)
class EphemerisResult:
    utc_datetime: str
    julian_day: float
    planets: dict[str, dict[str, float]]
    angles: dict[str, float]
    houses: dict[str, object]


def julian_day_from_utc(dt_utc: datetime) -> float:
    dt = dt_utc.astimezone(timezone.utc)
    hour = dt.hour + dt.minute / 60 + dt.second / 3600 + dt.microsecond / 3_600_000_000
    return swe.julday(dt.year, dt.month, dt.day, hour, swe.GREG_CAL)


def calculate_ephemeris(dt_utc: datetime, lat: float, lon: float, house_system: str = "P") -> EphemerisResult:
    dt = dt_utc.astimezone(timezone.utc)
    jd = julian_day_from_utc(dt)

    planets: dict[str, dict[str, float]] = {}
    for name, pid in PLANETS.items():
        calc, _ = swe.calc_ut(jd, pid, swe.FLG_SWIEPH | swe.FLG_SPEED)
        planets[name] = {"longitude": round(calc[0] % 360.0, 6)}

    house_code = house_system.encode("ascii")
    cusps, ascmc = swe.houses(jd, lat, lon, house_code)
    houses = [round(c, 6) for c in cusps]
    angles = {
        "ascendant": round(ascmc[0], 6),
        "midheaven": round(ascmc[1], 6),
    }

    return EphemerisResult(
        utc_datetime=dt.isoformat().replace("+00:00", "Z"),
        julian_day=jd,
        planets=planets,
        angles=angles,
        houses={"system": house_system, "cusps": houses},
    )
