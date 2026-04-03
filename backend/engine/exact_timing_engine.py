from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from astro.aspects import angular_distance
from astro.ephemeris import calculate_ephemeris

ASPECT_MAP = {
    "conjunction": 0,
    "square": 90,
    "opposition": 180,
    "trine": 120,
    "sextile": 60,
}


def is_applying(prev_angle: float, current_angle: float, target: float) -> bool:
    prev_diff = abs(prev_angle - target)
    curr_diff = abs(current_angle - target)
    return curr_diff < prev_diff


def _local_scan_datetime(reference_date: date, local_time: str, timezone_name: str) -> datetime:
    return datetime.fromisoformat(f"{reference_date.isoformat()}T{local_time}").replace(
        tzinfo=ZoneInfo(timezone_name)
    )


def _point_longitude(snapshot: dict[str, Any], point_name: str) -> float | None:
    if point_name in snapshot["planets"]:
        return float(snapshot["planets"][point_name]["longitude"])

    angle_aliases = {
        "ASC": "ascendant",
        "DSC": "descendant",
        "MC": "midheaven",
        "IC": "imum_coeli",
        "VERTEX": "vertex",
    }
    resolved = angle_aliases.get(point_name, point_name)
    if resolved in snapshot["angles"]:
        return float(snapshot["angles"][resolved])
    return None


def _natal_point_longitude(natal_ephemeris: dict[str, Any], point_name: str) -> float | None:
    if point_name in natal_ephemeris["planets"]:
        return float(natal_ephemeris["planets"][point_name]["longitude"])

    angle_aliases = {
        "ASC": "ascendant",
        "DSC": "descendant",
        "MC": "midheaven",
        "IC": "imum_coeli",
        "VERTEX": "vertex",
    }
    resolved = angle_aliases.get(point_name, point_name)
    if resolved in natal_ephemeris["angles"]:
        return float(natal_ephemeris["angles"][resolved])
    return None


def build_daily_scan(
    *,
    payload: dict[str, Any],
    start_date: date,
    days: int,
) -> list[dict[str, Any]]:
    local_time = str(payload.get("time") or payload.get("effective_time") or "12:00:00")
    timezone_name = str(payload["timezone"])
    lat = float(payload["lat"])
    lon = float(payload["lon"])
    house_system = str(payload["house_system"])

    snapshots: list[dict[str, Any]] = []
    for offset in range(days):
        current_date = start_date + timedelta(days=offset)
        local_dt = _local_scan_datetime(current_date, local_time, timezone_name)
        utc_dt = local_dt.astimezone(ZoneInfo("UTC"))
        ephemeris = calculate_ephemeris(utc_dt, lat, lon, house_system)
        snapshots.append(
            {
                "date": current_date,
                "planets": ephemeris.planets,
                "angles": ephemeris.angles,
            }
        )
    return snapshots


def find_exact_hit(
    *,
    natal_ephemeris: dict[str, Any],
    snapshots: list[dict[str, Any]],
    planet_a: str,
    planet_b: str,
    aspect_degree: float,
    activation_orb: float = 2.5,
) -> dict[str, Any] | None:
    natal_longitude = _natal_point_longitude(natal_ephemeris, planet_b)
    if natal_longitude is None:
        return None

    active_days: list[dict[str, Any]] = []
    smallest_orb = 999.0
    best_index = -1

    for index, snapshot in enumerate(snapshots):
        transit_longitude = _point_longitude(snapshot, planet_a)
        if transit_longitude is None:
            continue
        angle = angular_distance(transit_longitude, natal_longitude)
        orb = abs(angle - aspect_degree)
        if orb <= activation_orb:
            active_days.append(
                {
                    "index": index,
                    "date": snapshot["date"],
                    "angle": angle,
                    "orb": round(orb, 6),
                }
            )
        if orb < smallest_orb:
            smallest_orb = orb
            best_index = index

    if best_index < 0 or smallest_orb > 1.5:
        return None

    cluster = [item for item in active_days if abs(item["index"] - best_index) <= 21]
    if not cluster:
        peak_snapshot = snapshots[best_index]
        cluster = [
            {
                "index": best_index,
                "date": peak_snapshot["date"],
                "angle": angular_distance(
                    float(_point_longitude(peak_snapshot, planet_a) or 0.0),
                    natal_longitude,
                ),
                "orb": round(smallest_orb, 6),
            }
        ]

    cluster.sort(key=lambda item: item["index"])
    peak = min(cluster, key=lambda item: float(item["orb"]))
    prev_angle = cluster[0]["angle"] if len(cluster) == 1 else cluster[max(0, cluster.index(peak) - 1)]["angle"]
    applying = is_applying(prev_angle, peak["angle"], aspect_degree)

    return {
        "start": cluster[0]["date"].isoformat(),
        "peak": peak["date"].isoformat(),
        "end": cluster[-1]["date"].isoformat(),
        "exact_date": peak["date"].isoformat(),
        "orb": round(float(peak["orb"]), 4),
        "applying": applying,
        "duration_days": max(1, (cluster[-1]["date"] - cluster[0]["date"]).days + 1),
        "precision": "day",
    }


def detect_timed_events(
    *,
    natal_ephemeris: dict[str, Any],
    payload: dict[str, Any],
    rules: list[dict[str, Any]],
    start_date: date,
    days: int = 730,
) -> list[dict[str, Any]]:
    snapshots = build_daily_scan(payload=payload, start_date=start_date, days=days)
    events: list[dict[str, Any]] = []

    for rule in rules:
        aspect_degree = ASPECT_MAP.get(str(rule["aspect"]))
        if aspect_degree is None:
            continue
        result = find_exact_hit(
            natal_ephemeris=natal_ephemeris,
            snapshots=snapshots,
            planet_a=str(rule["planet_a"]).upper() if str(rule["planet_a"]).upper() in {"ASC", "DSC", "MC", "IC"} else str(rule["planet_a"]),
            planet_b=str(rule["planet_b"]).upper() if str(rule["planet_b"]).upper() in {"ASC", "DSC", "MC", "IC"} else str(rule["planet_b"]),
            aspect_degree=aspect_degree,
        )
        if result is None:
            continue

        events.append(
            {
                "type": rule["code"],
                "domain": rule["domain"],
                "planet_a": rule["planet_a"],
                "planet_b": rule["planet_b"],
                "aspect": rule["aspect"],
                "label": rule["label"],
                "date": result["exact_date"],
                "orb": result["orb"],
                "weight": float(rule["weight"]),
                "time_window": {
                    "start": result["start"],
                    "peak": result["peak"],
                    "end": result["end"],
                    "duration_days": result["duration_days"],
                    "precision": result["precision"],
                },
                "applying": result["applying"],
                "intensity": "high" if float(rule["weight"]) >= 4.5 else "medium" if float(rule["weight"]) >= 3.0 else "low",
            }
        )

    events.sort(key=lambda item: (item["date"], -float(item["weight"]), item["type"]))
    return events


def cluster_events_by_date(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    clusters: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for event in events:
        month_key = str(event["date"])[:7]
        clusters[month_key].append(event)

    return [
        {
            "month": month,
            "events": sorted(items, key=lambda item: (-float(item["weight"]), item["date"])),
            "total_weight": round(sum(float(item["weight"]) for item in items), 2),
        }
        for month, items in sorted(clusters.items())
    ]


def detect_critical_periods(clusters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    critical: list[dict[str, Any]] = []

    for cluster in clusters:
        total_weight = float(cluster["total_weight"])
        if total_weight < 10:
            continue
        critical.append(
            {
                "month": cluster["month"],
                "intensity": "high" if total_weight >= 14 else "medium",
                "total_weight": round(total_weight, 2),
                "events": cluster["events"][:6],
                "headline": f"{cluster['month']} concentra varios gatilhos exatos no mesmo periodo.",
            }
        )

    return critical
