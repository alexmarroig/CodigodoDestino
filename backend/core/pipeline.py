from __future__ import annotations

from dataclasses import asdict
from datetime import date, datetime, timezone
from time import perf_counter
from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from astro.aspects import calculate_aspects
from astro.ephemeris import calculate_ephemeris
from astro.signs import longitude_to_sign
from astro.time import convert_with_metadata, local_to_utc
from core.cache import CacheClient
from core.config import settings
from core.errors import AppError
from core.serialization import stable_hash
from db.models import MapRequest
from db.session import SessionLocal, initialize_database
from engine.analysis import assess_profile_quality, build_multilayer_analysis, get_house_from_longitude
from engine.events import build_domain_analysis, generate_events, summarize_events
from engine.narrative import build_narrative_prompt, generate_narrative_with_cache
from numerologia.core import life_path_number, personal_year


def build_response_cache_key(payload: dict[str, Any]) -> str:
    return f"mapa:{stable_hash({**payload, 'engine_version': settings.engine_version})}"


def build_computed_cache_key(payload: dict[str, Any]) -> str:
    return f"computed:{stable_hash({**payload, 'engine_version': settings.engine_version})}"


def build_ephemeris_key(
    utc_datetime: str,
    lat: float,
    lon: float,
    house_system: str,
) -> str:
    raw = {
        "utc_datetime": utc_datetime,
        "lat": lat,
        "lon": lon,
        "house_system": house_system,
        "engine_version": settings.engine_version,
    }
    return f"ephemeris:{stable_hash(raw)}"


def _normalize_payload(payload: dict[str, Any], reference_date: date) -> dict[str, Any]:
    normalized = dict(payload)
    normalized["reference_date"] = reference_date.isoformat()
    normalized["house_system"] = str(normalized.get("house_system", "P")).upper()
    normalized["orb_degrees"] = float(normalized.get("orb_degrees", 6.0))
    normalized["lat"] = float(normalized["lat"])
    normalized["lon"] = float(normalized["lon"])
    if normalized.get("time") is not None:
        normalized["time"] = payload["time"].isoformat() if hasattr(payload["time"], "isoformat") else str(payload["time"])
    normalized["birth_time_precision"] = normalized.get("birth_time_precision")
    normalized["birth_time_window"] = normalized.get("birth_time_window")
    return normalized


def _hydrate_cached_response(cached_response: dict[str, Any], request_id: str, cache_enabled: bool) -> dict[str, Any]:
    cached_response["request_id"] = request_id
    cached_response.setdefault("metadata", {})
    cached_response["metadata"]["cache_hit"] = True
    cached_response["metadata"]["cache"] = {
        "full_response": True,
        "computed_snapshot": True,
        "ephemeris": True,
        "redis_enabled": cache_enabled,
    }
    if isinstance(cached_response.get("narrative"), dict):
        cached_response["narrative"]["cached"] = True
    return cached_response


def _persist_map_request(
    db: Session,
    payload: dict[str, Any],
    response: dict[str, Any],
) -> None:
    initialize_database()
    db_obj = MapRequest(
        user_id=payload.get("user_id"),
        input_data=payload,
        result=response,
        engine_version=settings.engine_version,
    )
    del db

    persistence_session = SessionLocal()
    try:
        persistence_session.add(db_obj)
        persistence_session.commit()
    except SQLAlchemyError:
        persistence_session.rollback()
        initialize_database()
        persistence_session.close()
        persistence_session = SessionLocal()
        persistence_session.add(db_obj)
        try:
            persistence_session.commit()
            return
        except SQLAlchemyError as retry_exc:
            persistence_session.rollback()
            raise AppError(
                code="database_error",
                message="Failed to persist mapa request in PostgreSQL.",
                status_code=500,
            ) from retry_exc
    finally:
        persistence_session.close()


def _natal_planet_houses(planets: dict[str, dict[str, Any]], houses: list[float]) -> dict[str, int | None]:
    return {
        planet_name: get_house_from_longitude(float(planet_data["longitude"]), houses)
        for planet_name, planet_data in planets.items()
    }


def _build_astrology_snapshot(payload: dict[str, Any], cache: CacheClient) -> tuple[dict[str, Any], bool]:
    profile_quality = assess_profile_quality(payload)
    utc_metadata = convert_with_metadata(
        payload["date"],
        profile_quality["effective_time"],
        payload["timezone"],
    )
    utc_datetime = local_to_utc(
        payload["date"],
        profile_quality["effective_time"],
        payload["timezone"],
    )

    ephemeris_key = build_ephemeris_key(
        utc_metadata.utc_datetime,
        payload["lat"],
        payload["lon"],
        payload["house_system"],
    )
    cached_ephemeris = cache.get_cache(ephemeris_key)
    ephemeris_cache_hit = cached_ephemeris is not None

    if cached_ephemeris is None:
        ephemeris_result = calculate_ephemeris(
            utc_datetime,
            payload["lat"],
            payload["lon"],
            payload["house_system"],
        )
        cached_ephemeris = {
            "utc_datetime": ephemeris_result.utc_datetime,
            "julian_day": ephemeris_result.julian_day,
            "planets": ephemeris_result.planets,
            "angles": ephemeris_result.angles,
            "houses": ephemeris_result.houses,
        }
        cache.set_cache(ephemeris_key, cached_ephemeris, settings.ephemeris_cache_ttl)

    positions = {
        planet_name: float(planet_data["longitude"])
        for planet_name, planet_data in cached_ephemeris["planets"].items()
    }
    aspects = calculate_aspects(positions, payload["orb_degrees"])
    signs = {
        planet_name: asdict(longitude_to_sign(longitude))
        for planet_name, longitude in positions.items()
    }
    natal_houses = list(cached_ephemeris["houses"]["cusps"])
    planet_houses = _natal_planet_houses(cached_ephemeris["planets"], natal_houses)

    numerology = {
        "birth_date": payload["date"],
        "life_path_number": life_path_number(payload["date"]),
        "personal_year": personal_year(payload["date"], payload["reference_date"]),
    }

    analysis = build_multilayer_analysis(
        payload=payload,
        utc_metadata=asdict(utc_metadata),
        natal_ephemeris=cached_ephemeris,
        natal_aspects=aspects,
        numerology=numerology,
        reference_date=date.fromisoformat(payload["reference_date"]),
        profile_quality=profile_quality,
    )
    domain_bundle = build_domain_analysis(analysis)
    events = generate_events(analysis, date.fromisoformat(payload["reference_date"]))
    event_summary = summarize_events(events)

    analysis["domain_analysis"] = domain_bundle
    computed_snapshot = {
        "utc": asdict(utc_metadata),
        "astrology": {
            **cached_ephemeris,
            "signs": signs,
            "planet_houses": planet_houses,
        },
        "aspects": {
            "orb_degrees": payload["orb_degrees"],
            "aspects": aspects,
        },
        "numerology": numerology,
        "analysis": analysis,
        "events": events,
        "event_summary": event_summary,
        "profile_quality": profile_quality,
        "confidence": domain_bundle["confidence"],
        "uncertainties": domain_bundle["uncertainties"],
        "techniques_used": analysis["techniques_used"],
    }
    return computed_snapshot, ephemeris_cache_hit


def _resolve_computed_snapshot(
    payload: dict[str, Any],
    cache: CacheClient,
) -> tuple[dict[str, Any], bool, bool]:
    computed_key = build_computed_cache_key(payload)
    cached_snapshot = cache.get_cache(computed_key)
    if cached_snapshot is not None:
        return cached_snapshot, True, True

    computed_snapshot, ephemeris_cache_hit = _build_astrology_snapshot(payload, cache)
    cache.set_cache(computed_key, computed_snapshot, settings.computed_cache_ttl)
    return computed_snapshot, False, ephemeris_cache_hit


def run_pipeline(
    payload: dict[str, Any],
    db: Session,
    cache: CacheClient,
    request_id: str,
    reference_date: date,
) -> dict[str, Any]:
    started_at = perf_counter()
    normalized_payload = _normalize_payload(payload, reference_date)
    response_cache_key = build_response_cache_key(normalized_payload)

    cached_full = cache.get_cache(response_cache_key)
    if cached_full is not None:
        hydrated = _hydrate_cached_response(cached_full, request_id, cache.enabled)
        hydrated["metadata"]["performance"] = {
            "total_ms": round((perf_counter() - started_at) * 1000, 2),
            "narrative_strategy": hydrated.get("narrative", {}).get("strategy", "unknown"),
        }
        return hydrated

    computed_snapshot, computed_cache_hit, ephemeris_cache_hit = _resolve_computed_snapshot(
        normalized_payload,
        cache,
    )

    prompt_data = build_narrative_prompt(
        computed_snapshot["analysis"],
        computed_snapshot["events"],
        computed_snapshot["event_summary"],
        computed_snapshot["confidence"],
        computed_snapshot["uncertainties"],
    )
    narrative = generate_narrative_with_cache(prompt_data, cache)

    response = {
        "request_id": request_id,
        "input": normalized_payload,
        "computed": {
            "utc": computed_snapshot["utc"],
            "astrology": computed_snapshot["astrology"],
            "aspects": computed_snapshot["aspects"],
            "numerology": computed_snapshot["numerology"],
        },
        "analysis": computed_snapshot["analysis"],
        "profile_quality": computed_snapshot["profile_quality"],
        "confidence": computed_snapshot["confidence"],
        "uncertainties": computed_snapshot["uncertainties"],
        "techniques_used": computed_snapshot["techniques_used"],
        "events": computed_snapshot["events"],
        "event_summary": computed_snapshot["event_summary"],
        "narrative": narrative,
        "metadata": {
            "engine_version": settings.engine_version,
            "cache_hit": False,
            "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "cache": {
                "full_response": False,
                "computed_snapshot": computed_cache_hit,
                "ephemeris": ephemeris_cache_hit,
                "redis_enabled": cache.enabled,
            },
            "cost_control": {
                "narrative_strategy": narrative.get("strategy"),
                "strategy_reason": narrative.get("strategy_reason"),
                "complexity_score": narrative.get("complexity_score"),
                "prompt_event_count": narrative.get("prompt_event_count"),
            },
            "performance": {
                "total_ms": round((perf_counter() - started_at) * 1000, 2),
            },
        },
    }

    _persist_map_request(db, normalized_payload, response)
    cache.set_cache(response_cache_key, response, settings.map_cache_ttl)
    return response
