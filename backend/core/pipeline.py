from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone, date
from typing import Any, Dict

from sqlalchemy.orm import Session

from astro.aspects import calculate_aspects
from astro.ephemeris import calculate_ephemeris
from astro.signs import longitude_to_sign
from astro.time import convert_with_metadata, local_to_utc
from core.cache import CacheClient
from core.config import settings
from db.models import MapRequest
from engine.events import generate_events
from engine.narrative import build_narrative_prompt
from numerologia.core import life_path_number, personal_year


# -----------------------------------
# HASH UTILS
# -----------------------------------

def _hash(data: Any) -> str:
    serialized = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


# -----------------------------------
# CACHE KEYS
# -----------------------------------

def build_cache_key(payload: Dict[str, Any]) -> str:
    enriched = {
        **payload,
        "engine_version": settings.engine_version,
    }
    return f"mapa:{_hash(enriched)}"


def build_ephemeris_key(utc_datetime: str, lat: float, lon: float, house_system: str) -> str:
    raw = f"{utc_datetime}|{lat}|{lon}|{house_system}|v1"
    return f"ephemeris:{hashlib.sha256(raw.encode()).hexdigest()}"


def build_interpretation_key(events: list[dict]) -> str:
    """
    🔥 HASH SEMÂNTICO (ESSENCIAL)
    """
    signature = [
        {
            "drivers": e["drivers"],
            "intensity": e["intensity"],
            "category": e["category"],
        }
        for e in events
    ]
    return f"interp:{_hash(signature)}"


# -----------------------------------
# CORE
# -----------------------------------

def run_pipeline(
    payload: Dict[str, Any],
    db: Session,
    cache: CacheClient,
    request_id: str,
    reference_date: date,
) -> Dict[str, Any]:

    # -------------------------
    # NORMALIZAÇÃO
    # -------------------------

    payload = {**payload, "reference_date": reference_date.isoformat()}

    cache_key = build_cache_key(payload)

    # -------------------------
    # CACHE COMPLETO
    # -------------------------

    cached_full = cache.get_cache(cache_key)
    if cached_full:
        return cached_full

    # -------------------------
    # UTC
    # -------------------------

    utc_meta = convert_with_metadata(payload["date"], payload["time"], payload["timezone"])
    utc_dt = local_to_utc(payload["date"], payload["time"], payload["timezone"])

    # -------------------------
    # EPHEMERIS CACHE
    # -------------------------

    ephemeris_key = build_ephemeris_key(
        utc_meta.utc_datetime,
        payload["lat"],
        payload["lon"],
        payload.get("house_system", "P"),
    )

    cached_ephemeris = cache.get_cache(ephemeris_key)

    if not cached_ephemeris:
        eph = calculate_ephemeris(
            utc_dt,
            payload["lat"],
            payload["lon"],
            payload.get("house_system", "P"),
        )

        cached_ephemeris = {
            "utc_datetime": eph.utc_datetime,
            "julian_day": eph.julian_day,
            "planets": eph.planets,
            "angles": eph.angles,
            "houses": eph.houses,
        }

        cache.set_cache(ephemeris_key, cached_ephemeris)

    # -------------------------
    # ASPECTOS
    # -------------------------

    positions = {
        planet: data["longitude"]
        for planet, data in cached_ephemeris["planets"].items()
    }

    aspects = calculate_aspects(positions, payload.get("orb_degrees", 6))

    # -------------------------
    # SIGNOS
    # -------------------------

    signs = {
        planet: longitude_to_sign(long).__dict__
        for planet, long in positions.items()
    }

    # -------------------------
    # NUMEROLOGIA
    # -------------------------

    numerology = {
        "birth_date": payload["date"],
        "life_path_number": life_path_number(payload["date"]),
        "personal_year": personal_year(payload["date"], reference_date),
    }

    # -------------------------
    # EVENTOS
    # -------------------------

    events = generate_events(
        aspects,
        cached_ephemeris["houses"]["cusps"],
        numerology,
        reference_date,
    )

    # -------------------------
    # 🔥 INTERPRETATION CACHE
    # -------------------------

    interpretation_key = build_interpretation_key(events)
    cached_prompt = cache.get_cache(interpretation_key)

    if cached_prompt:
        prompt = cached_prompt
    else:
        prompt = build_narrative_prompt(events)
        cache.set_cache(interpretation_key, prompt)

    # -------------------------
    # RESPONSE
    # -------------------------

    response = {
        "request_id": request_id,
        "input": payload,
        "computed": {
            "utc": utc_meta.__dict__,
            "astrology": {
                **cached_ephemeris,
                "signs": signs,
            },
            "aspects": {
                "orb_degrees": payload.get("orb_degrees", 6),
                "aspects": aspects,
            },
            "numerology": numerology,
        },
        "events": events,
        "narrative_prompt": prompt,
        "metadata": {
            "engine_version": settings.engine_version,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    }

    # -------------------------
    # DB SAVE
    # -------------------------

    db_obj = MapRequest(
        user_id=payload.get("user_id"),
        input_data=payload,
        result=response,
        engine_version=settings.engine_version,
    )

    db.add(db_obj)
    db.commit()

    # -------------------------
    # CACHE FINAL
    # -------------------------

    cache.set_cache(cache_key, response)

    return response
