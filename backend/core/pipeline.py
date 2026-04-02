from __future__ import annotations

import hashlib
import json
from typing import Any

from sqlalchemy.orm import Session

from astro.aspects import calculate_aspects
from astro.ephemeris import calculate_ephemeris
from astro.signs import longitude_to_sign
from astro.time import convert_with_metadata, local_to_utc
from core.cache import CacheClient
from core.config import settings
from db.models import MapRequest
from engine.events import generate_events
from engine.narrative import build_narrative_prompt, generate_narrative_with_cache
from numerologia.core import life_path_number, personal_year


def build_cache_key(payload: dict[str, Any]) -> str:
    serialized = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return f"v2:mapa:{hashlib.sha256(serialized.encode('utf-8')).hexdigest()}"


def build_ephemeris_key(utc_datetime: str, lat: float, lon: float, house_system: str) -> str:
    raw = f"{utc_datetime}|{lat}|{lon}|{house_system}"
    return f"v2:ephemeris:{hashlib.sha256(raw.encode('utf-8')).hexdigest()}"


def run_pipeline(payload: dict[str, Any], db: Session, cache: CacheClient, request_id: str) -> dict[str, Any]:
    cache_key = build_cache_key(payload)
    cached_full = cache.get_cache(cache_key)
    if cached_full is not None:
        return cached_full

    utc_meta = convert_with_metadata(payload["date"], payload["time"], payload["timezone"])
    utc_dt = local_to_utc(payload["date"], payload["time"], payload["timezone"])
    ephemeris_key = build_ephemeris_key(utc_meta.utc_datetime, payload["lat"], payload["lon"], payload["house_system"])

    cached_ephemeris = cache.get_cache(ephemeris_key)
    if cached_ephemeris is None:
        eph = calculate_ephemeris(utc_dt, payload["lat"], payload["lon"], payload["house_system"])
        cached_ephemeris = {
            "utc_datetime": eph.utc_datetime,
            "julian_day": eph.julian_day,
            "planets": eph.planets,
            "angles": eph.angles,
            "houses": eph.houses,
        }
        cache.set_cache(ephemeris_key, cached_ephemeris, settings.ephemeris_cache_ttl)

    positions = {planet: data["longitude"] for planet, data in cached_ephemeris["planets"].items()}
    aspects = calculate_aspects(positions, payload["orb_degrees"])
    signs = {planet: longitude_to_sign(long).__dict__ for planet, long in positions.items()}

    reference_date = payload["reference_date"]
    numerology = {
        "birth_date": payload["date"],
        "life_path_number": life_path_number(payload["date"]),
        "personal_year": personal_year(payload["date"], reference_date),
    }

    events = generate_events(aspects, cached_ephemeris["houses"]["cusps"], numerology, reference_date)
    prompt = build_narrative_prompt(events)
    narrative = generate_narrative_with_cache(prompt, cache)

    response = {
        "request_id": request_id,
        "input": payload,
        "computed": {
            "utc": utc_meta.__dict__,
            "astrology": {**cached_ephemeris, "signs": signs},
            "aspects": {"orb_degrees": payload["orb_degrees"], "aspects": aspects},
            "numerology": numerology,
        },
        "events": events,
        "narrative": narrative,
        "metadata": {
            "engine_version": settings.engine_version,
            "generated_at": f"{reference_date}T00:00:00Z",
        },
        "narrative_prompt": prompt,
    }

    db_obj = MapRequest(
        user_id=payload.get("user_id"),
        input_data=payload,
        result=response,
        engine_version=settings.engine_version,
    )
    db.add(db_obj)
    db.commit()

    cache.set_cache(cache_key, response, settings.map_cache_ttl)
    return response
