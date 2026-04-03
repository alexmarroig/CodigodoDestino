from __future__ import annotations

from dataclasses import asdict
from datetime import date, datetime
from typing import Any

from sqlalchemy.orm import Session

from astro.aspects import calculate_aspects
from astro.ephemeris import calculate_ephemeris
from astro.time import convert_with_metadata, local_to_utc
from core.errors import AppError
from db.models import UserLifeEvent
from db.session import SessionLocal, initialize_database
from engine.analysis import assess_profile_quality, build_multilayer_analysis
from engine.learning_engine import summarize_learning
from engine.rules_engine import build_specialized_insights
from numerologia.core import life_path_number, personal_year


def _build_birth_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "date": payload["birth_date"],
        "time": payload.get("birth_time"),
        "lat": payload["birth_lat"],
        "lon": payload["birth_lon"],
        "timezone": payload["birth_timezone"],
        "orb_degrees": payload.get("orb_degrees", 6.0),
        "house_system": payload.get("house_system", "P"),
        "birth_time_precision": payload.get("birth_time_precision"),
        "birth_time_window": payload.get("birth_time_window"),
        "reference_date": payload["event_date"],
    }


def _serialize_life_event(model: UserLifeEvent) -> dict[str, Any]:
    return {
        "id": model.id,
        "user_id": model.user_id,
        "event_type": model.event_type,
        "event_date": model.event_date.isoformat(),
        "description": model.description,
        "transits": model.transits,
        "progressions": model.progressions,
        "solar_arc": model.solar_arc,
        "rule_hits": model.rule_hits,
        "special_analysis": model.special_analysis,
        "created_at": model.created_at.isoformat() if model.created_at else None,
    }


def save_life_event(payload: dict[str, Any], db: Session) -> dict[str, Any]:
    initialize_database()
    birth_payload = _build_birth_payload(payload)
    profile_quality = assess_profile_quality(birth_payload)

    event_time = payload.get("event_time") or profile_quality["effective_time"]
    event_timezone = payload.get("event_timezone") or payload["birth_timezone"]
    event_lat = payload.get("event_lat") or payload["birth_lat"]
    event_lon = payload.get("event_lon") or payload["birth_lon"]

    utc_metadata = convert_with_metadata(
        birth_payload["date"],
        profile_quality["effective_time"],
        birth_payload["timezone"],
    )
    natal_utc = local_to_utc(
        birth_payload["date"],
        profile_quality["effective_time"],
        birth_payload["timezone"],
    )
    natal_ephemeris = calculate_ephemeris(
        natal_utc,
        float(birth_payload["lat"]),
        float(birth_payload["lon"]),
        str(birth_payload["house_system"]),
    )
    positions = {planet: float(data["longitude"]) for planet, data in natal_ephemeris.planets.items()}
    natal_aspects = calculate_aspects(positions, float(birth_payload["orb_degrees"]))

    numerology = {
        "birth_date": birth_payload["date"],
        "life_path_number": life_path_number(birth_payload["date"]),
        "personal_year": personal_year(birth_payload["date"], str(payload["event_date"])),
    }

    analysis_payload = {
        **birth_payload,
        "reference_date": payload["event_date"],
        "time": str(event_time),
        "timezone": event_timezone,
        "lat": float(event_lat),
        "lon": float(event_lon),
    }

    analysis = build_multilayer_analysis(
        payload=analysis_payload,
        utc_metadata=asdict(utc_metadata),
        natal_ephemeris={
            "utc_datetime": natal_ephemeris.utc_datetime,
            "julian_day": natal_ephemeris.julian_day,
            "planets": natal_ephemeris.planets,
            "angles": natal_ephemeris.angles,
            "houses": natal_ephemeris.houses,
        },
        natal_aspects=natal_aspects,
        numerology=numerology,
        reference_date=date.fromisoformat(str(payload["event_date"])),
        profile_quality=profile_quality,
    )
    specialized = build_specialized_insights(analysis)

    model = UserLifeEvent(
        user_id=payload.get("user_id"),
        event_type=str(payload["event_type"]),
        event_date=date.fromisoformat(str(payload["event_date"])),
        description=payload.get("description"),
        natal_input=birth_payload,
        transits=list(analysis.get("transits", {}).get("aspects", [])),
        progressions=list(analysis.get("progressions", {}).get("aspects", [])),
        solar_arc=list(analysis.get("solar_arc", {}).get("aspects", [])),
        rule_hits=list(specialized.get("rule_hits", [])),
        special_analysis={
            "relationship": specialized.get("relationship", {}),
            "financial": specialized.get("financial", {}),
            "purpose": specialized.get("purpose", {}),
        },
    )

    del db
    persistence_session = SessionLocal()
    try:
        persistence_session.add(model)
        persistence_session.commit()
        persistence_session.refresh(model)
    except Exception as exc:
        persistence_session.rollback()
        initialize_database()
        persistence_session.close()
        persistence_session = SessionLocal()
        persistence_session.add(model)
        try:
            persistence_session.commit()
            persistence_session.refresh(model)
        except Exception as retry_exc:
            persistence_session.rollback()
            raise AppError(
                code="life_event_persist_error",
                message="Nao foi possivel salvar o evento de vida.",
                status_code=500,
            ) from retry_exc

    stored_events = []
    if payload.get("user_id") is not None:
        stored_events = [
            _serialize_life_event(item)
            for item in persistence_session.query(UserLifeEvent)
            .filter(UserLifeEvent.user_id == payload.get("user_id"))
            .order_by(UserLifeEvent.event_date.asc())
            .all()
        ]

    try:
        return {
            "ok": True,
            "event": _serialize_life_event(model),
            "analysis_snapshot": {
                "relationship": specialized.get("relationship", {}),
                "financial": specialized.get("financial", {}),
                "purpose": specialized.get("purpose", {}),
                "rule_hits": specialized.get("rule_hits", [])[:12],
            },
            "learning": summarize_learning(stored_events),
        }
    finally:
        persistence_session.close()
