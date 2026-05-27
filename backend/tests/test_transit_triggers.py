"""Tests for transit_triggers.py — fast-planet peaks inside slow windows."""

from __future__ import annotations

from datetime import date

from engine.transit_triggers import (
    find_trigger_peak_in_window,
    refine_signal_window_with_trigger,
)


def _snapshot(day: int, moon_lon: float) -> dict:
    return {
        "date": date(2026, 6, day),
        "planets": {
            "saturn": {"longitude": 350.0},
            "moon": {"longitude": moon_lon},
            "sun": {"longitude": 80.0},
        },
        "angles": {},
    }


def test_find_trigger_peak_finds_moon_crossing_square():
    natal = {"planets": {"venus": {"longitude": 90.0}}, "angles": {}}
    snapshots = [
        _snapshot(1, 60.0),
        _snapshot(2, 180.0),
        _snapshot(3, 92.0),
        _snapshot(4, 120.0),
    ]
    peak = find_trigger_peak_in_window(
        natal_ephemeris=natal,
        snapshots=snapshots,
        natal_point="venus",
        aspect_name="square",
    )
    assert peak == date(2026, 6, 2)


def test_refine_signal_adds_trigger_peak_for_slow_transit():
    signal = {
        "technique": "transits",
        "label": "Saturno em quadratura com Vênus",
        "time_window": {
            "start": "2026-06-01",
            "end": "2026-10-01",
            "peak": "2026-06-01",
            "duration_days": 65,
        },
        "evidence": {
            "aspect": "square",
            "planet_a": "saturn",
            "planet_b": "venus",
            "time_window": {
                "start": "2026-06-01",
                "end": "2026-10-01",
                "peak": "2026-06-01",
                "duration_days": 65,
            },
        },
    }
    natal = {"planets": {"venus": {"longitude": 90.0}}, "angles": {}}
    payload = {
        "date": "1990-01-01",
        "time": "12:00:00",
        "lat": -23.55,
        "lon": -46.63,
        "timezone": "America/Sao_Paulo",
        "house_system": "P",
        "reference_date": date(2026, 6, 1),
    }
    refined = refine_signal_window_with_trigger(
        signal,
        natal_ephemeris=natal,
        payload=payload,
        reference_date=date(2026, 6, 1),
        scan_days=7,
    )
    ev = refined.get("evidence") or {}
    assert ev.get("timing_mode") in {"pico_datado", "tema_no_periodo"}
