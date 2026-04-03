from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import swisseph as swe

from core.config import settings

PRIMARY_FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED
FALLBACK_FLAGS = swe.FLG_MOSEPH | swe.FLG_SPEED

PLANETS = {
    "sun": swe.SUN,
    "moon": swe.MOON,
    "mercury": swe.MERCURY,
    "venus": swe.VENUS,
    "mars": swe.MARS,
    "jupiter": swe.JUPITER,
    "saturn": swe.SATURN,
    "uranus": swe.URANUS,
    "neptune": swe.NEPTUNE,
    "pluto": swe.PLUTO,
}


@dataclass(frozen=True)
class EphemerisResult:
    utc_datetime: str
    julian_day: float
    planets: dict[str, dict[str, Any]]
    angles: dict[str, float]
    houses: dict[str, Any]


def _configure_ephemeris_path() -> None:
    ephe_path = Path(settings.swisseph_path)
    ephe_path.mkdir(parents=True, exist_ok=True)
    swe.set_ephe_path(str(ephe_path))


def _normalize(value: float) -> float:
    return round(value % 360.0, 6)


def julian_day_from_utc(dt_utc: datetime) -> float:
    dt = dt_utc.astimezone(timezone.utc)
    hour = (
        dt.hour
        + (dt.minute / 60.0)
        + (dt.second / 3600.0)
        + (dt.microsecond / 3_600_000_000.0)
    )
    return swe.julday(dt.year, dt.month, dt.day, hour, swe.GREG_CAL)


def _calculate_planet(julian_day: float, planet_id: int, planet_name: str) -> dict[str, Any]:
    for flags in (PRIMARY_FLAGS, FALLBACK_FLAGS):
        try:
            values, ret_flag = swe.calc_ut(julian_day, planet_id, flags)
        except Exception:
            continue

        if ret_flag < 0:
            continue

        longitude_speed = round(values[3], 6)
        return {
            "longitude": _normalize(values[0]),
            "latitude": round(values[1], 6),
            "distance_au": round(values[2], 9),
            "speed_longitude": longitude_speed,
            "retrograde": longitude_speed < 0,
        }

    raise RuntimeError(f"Swiss Ephemeris failed for planet '{planet_name}'.")


def _calculate_houses(julian_day: float, lat: float, lon: float, house_system: str) -> tuple[list[float], dict[str, float]]:
    try:
        cusps, ascmc = swe.houses(julian_day, lat, lon, house_system.encode("ascii"))
    except Exception as exc:
        raise RuntimeError("Swiss Ephemeris failed while calculating houses.") from exc

    normalized_cusps = [_normalize(cusp) for cusp in list(cusps)]
    ascendant = _normalize(ascmc[0])
    midheaven = _normalize(ascmc[1])

    angles = {
        "ascendant": ascendant,
        "descendant": _normalize(ascendant + 180.0),
        "midheaven": midheaven,
        "imum_coeli": _normalize(midheaven + 180.0),
        "vertex": _normalize(ascmc[3]),
    }
    return normalized_cusps, angles


def calculate_ephemeris(
    dt_utc: datetime,
    lat: float,
    lon: float,
    house_system: str = "P",
) -> EphemerisResult:
    _configure_ephemeris_path()

    dt = dt_utc.astimezone(timezone.utc)
    julian_day = julian_day_from_utc(dt)

    planets = {
        name: _calculate_planet(julian_day, planet_id, name)
        for name, planet_id in PLANETS.items()
    }
    cusps, angles = _calculate_houses(julian_day, lat, lon, house_system)

    return EphemerisResult(
        utc_datetime=dt.isoformat().replace("+00:00", "Z"),
        julian_day=julian_day,
        planets=planets,
        angles=angles,
        houses={"system": house_system, "cusps": cusps},
    )
