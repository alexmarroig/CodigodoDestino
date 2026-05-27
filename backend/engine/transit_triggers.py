"""
Fast-planet trigger scan for slow transit windows (Hand/Brady timing hierarchy).

When Saturn/Uranus/Neptune/Pluto (etc.) hold a long window, Sun/Moon/Mercury/Mars
crossing the same natal degree within the window pinpoints a dated peak.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from astro.aspects import ASPECTS, angular_distance

from engine.exact_timing_engine import build_daily_scan

_SLOW_WINDOW_DAYS: dict[str, int] = {
    "jupiter": 45,
    "saturn": 65,
    "uranus": 120,
    "neptune": 150,
    "pluto": 180,
}


def _build_time_window(reference_date: date, days: int) -> dict[str, Any]:
    duration_days = max(1, days)
    return {
        "start": reference_date.isoformat(),
        "end": (reference_date + timedelta(days=duration_days - 1)).isoformat(),
        "peak": reference_date.isoformat(),
        "duration_days": duration_days,
        "precision": "day",
    }

SLOW_TRANSIT_PLANETS: frozenset[str] = frozenset(
    {"jupiter", "saturn", "uranus", "neptune", "pluto"}
)
TRIGGER_PLANETS: frozenset[str] = frozenset({"sun", "moon", "mercury", "mars"})
MIN_SLOW_WINDOW_DAYS: int = 21
TRIGGER_ORB_DEGREES: float = 1.5
DEFAULT_SCAN_DAYS: int = 14
MAX_SCAN_DAYS: int = 60


def _norm(name: str) -> str:
    return name.replace("_", " ").strip().lower()


def _natal_longitude(natal_ephemeris: dict[str, Any], point: str) -> float | None:
    p = _norm(point)
    planets = natal_ephemeris.get("planets") or {}
    if p in planets:
        return float(planets[p]["longitude"])
    angle_map = {
        "asc": "ascendant",
        "mc": "midheaven",
        "dsc": "descendant",
        "ic": "imum_coeli",
    }
    resolved = angle_map.get(p, p)
    angles = natal_ephemeris.get("angles") or {}
    if resolved in angles:
        return float(angles[resolved])
    return None


def find_trigger_peak_in_window(
    *,
    natal_ephemeris: dict[str, Any],
    snapshots: list[dict[str, Any]],
    natal_point: str,
    aspect_name: str,
    slow_transit_planet: str | None = None,
) -> date | None:
    """
    Return the first date in snapshots when a trigger planet hits the slow aspect angle
    to the natal point (within TRIGGER_ORB_DEGREES).
    """
    natal_lon = _natal_longitude(natal_ephemeris, natal_point)
    if natal_lon is None:
        return None

    target_angle = ASPECTS.get(aspect_name)
    if target_angle is None:
        return None

    best_date: date | None = None
    best_orb = TRIGGER_ORB_DEGREES + 1.0

    for snapshot in snapshots:
        snap_date = snapshot.get("date")
        if not isinstance(snap_date, date):
            continue
        for trigger in TRIGGER_PLANETS:
            if slow_transit_planet and _norm(trigger) == _norm(slow_transit_planet):
                continue
            planets = snapshot.get("planets") or {}
            if trigger not in planets:
                continue
            transit_lon = float(planets[trigger]["longitude"])
            distance = angular_distance(transit_lon, natal_lon)
            orb = abs(distance - target_angle)
            if orb <= TRIGGER_ORB_DEGREES and orb < best_orb:
                best_orb = orb
                best_date = snap_date

    return best_date


def _relative_trigger_label(trigger_date: date, reference_date: date) -> str:
    delta = (trigger_date - reference_date).days
    if delta <= 0:
        return "hoje"
    if delta <= 7:
        return "esta semana"
    if delta <= 14:
        return "nas próximas duas semanas"
    return trigger_date.isoformat()


def refine_signal_window_with_trigger(
    signal: dict[str, Any],
    *,
    natal_ephemeris: dict[str, Any],
    payload: dict[str, Any],
    reference_date: date,
    scan_days: int = DEFAULT_SCAN_DAYS,
) -> dict[str, Any]:
    """
    If signal is a long slow-planet transit, scan for fast triggers and tighten peak.
    """
    if str(signal.get("technique") or "") != "transits":
        return signal

    evidence = dict(signal.get("evidence") or {})
    slow_planet = _norm(str(evidence.get("planet_a") or ""))
    if slow_planet not in SLOW_TRANSIT_PLANETS:
        return signal

    window = dict(signal.get("time_window") or evidence.get("time_window") or {})
    duration = int(window.get("duration_days") or _SLOW_WINDOW_DAYS.get(slow_planet, 21))
    if duration < MIN_SLOW_WINDOW_DAYS:
        return signal

    natal_point = str(evidence.get("planet_b") or "")
    aspect_name = str(evidence.get("aspect") or "")
    if not natal_point or not aspect_name:
        return signal

    effective_scan = min(max(scan_days, duration), MAX_SCAN_DAYS)
    snapshots = build_daily_scan(
        payload={**payload, "reference_date": reference_date},
        start_date=reference_date,
        days=effective_scan,
    )
    trigger_date = find_trigger_peak_in_window(
        natal_ephemeris=natal_ephemeris,
        snapshots=snapshots,
        natal_point=natal_point,
        aspect_name=aspect_name,
        slow_transit_planet=slow_planet,
    )
    if trigger_date is None:
        evidence["timing_mode"] = "tema_no_periodo"
        updated = dict(signal)
        updated["evidence"] = evidence
        return updated

    trigger_label = _relative_trigger_label(trigger_date, reference_date)
    tightened = _build_time_window(trigger_date, max(3, min(7, duration // 10 or 3)))
    tightened["peak"] = trigger_date.isoformat()
    tightened["precision"] = "trigger"
    tightened["trigger_planet_scan"] = True
    tightened["trigger_label"] = trigger_label

    evidence["timing_mode"] = "pico_datado"
    evidence["trigger_peak"] = trigger_date.isoformat()
    evidence["trigger_label"] = trigger_label
    evidence["time_window"] = tightened

    updated = dict(signal)
    updated["time_window"] = tightened
    updated["evidence"] = evidence
    if "tema sensível" not in str(signal.get("label") or "").lower():
        updated["label"] = (
            f"{signal.get('label', '')} — pico {trigger_label}"
        ).strip(" —")
    return updated


def refine_slow_transit_windows(
    signals: list[dict[str, Any]],
    *,
    natal_ephemeris: dict[str, Any],
    payload: dict[str, Any],
    reference_date: date,
) -> list[dict[str, Any]]:
    return [
        refine_signal_window_with_trigger(
            s,
            natal_ephemeris=natal_ephemeris,
            payload=payload,
            reference_date=reference_date,
        )
        for s in signals
    ]
