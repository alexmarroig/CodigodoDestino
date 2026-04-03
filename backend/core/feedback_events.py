from __future__ import annotations

from dataclasses import asdict
from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from astro.aspects import calculate_aspects
from astro.ephemeris import calculate_ephemeris
from astro.time import convert_with_metadata, local_to_utc
from core.errors import AppError
from core.life_events import _build_birth_payload
from db.models import UserFeedbackEvent, UserRuleWeight
from db.session import SessionLocal, initialize_database
from engine.adaptive_learning_engine import get_user_rule_overrides, learning_loop
from engine.analysis import assess_profile_quality, build_multilayer_analysis
from engine.rules_engine import build_specialized_insights
from numerologia.core import life_path_number, personal_year


def _serialize_feedback_event(model: UserFeedbackEvent) -> dict[str, Any]:
    return {
        "id": model.id,
        "user_id": model.user_id,
        "event_type": model.event_type,
        "event_date": model.event_date.isoformat(),
        "predicted": model.predicted,
        "real_intensity": model.real_intensity,
        "description": model.description,
        "transits": model.transits,
        "progressions": model.progressions,
        "solar_arc": model.solar_arc,
        "rule_hits": model.rule_hits,
        "created_at": model.created_at.isoformat() if model.created_at else None,
    }


def save_feedback_event(payload: dict[str, Any], db: Session) -> dict[str, Any]:
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
        "user_id": payload.get("user_id"),
    }

    persistence_session = SessionLocal()
    try:
        user_rule_overrides = get_user_rule_overrides(persistence_session, payload.get("user_id"))
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
        analysis["user_rule_overrides"] = user_rule_overrides
        specialized = build_specialized_insights(analysis)

        model = UserFeedbackEvent(
            user_id=payload.get("user_id"),
            event_type=str(payload["event_type"]),
            event_date=date.fromisoformat(str(payload["event_date"])),
            predicted=bool(payload.get("predicted", False)),
            real_intensity=int(payload.get("real_intensity", 3)),
            description=payload.get("description"),
            natal_input=birth_payload,
            transits=list(analysis.get("transits", {}).get("aspects", [])),
            progressions=list(analysis.get("progressions", {}).get("aspects", [])),
            solar_arc=list(analysis.get("solar_arc", {}).get("aspects", [])),
            rule_hits=list(specialized.get("rule_hits", [])),
        )

        persistence_session.add(model)
        persistence_session.commit()
        persistence_session.refresh(model)
    except Exception as exc:
        persistence_session.rollback()
        initialize_database()
        persistence_session.close()
        persistence_session = SessionLocal()
        try:
            user_rule_overrides = get_user_rule_overrides(persistence_session, payload.get("user_id"))
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
            analysis["user_rule_overrides"] = user_rule_overrides
            specialized = build_specialized_insights(analysis)
            model = UserFeedbackEvent(
                user_id=payload.get("user_id"),
                event_type=str(payload["event_type"]),
                event_date=date.fromisoformat(str(payload["event_date"])),
                predicted=bool(payload.get("predicted", False)),
                real_intensity=int(payload.get("real_intensity", 3)),
                description=payload.get("description"),
                natal_input=birth_payload,
                transits=list(analysis.get("transits", {}).get("aspects", [])),
                progressions=list(analysis.get("progressions", {}).get("aspects", [])),
                solar_arc=list(analysis.get("solar_arc", {}).get("aspects", [])),
                rule_hits=list(specialized.get("rule_hits", [])),
            )
            persistence_session.add(model)
            persistence_session.commit()
            persistence_session.refresh(model)
        except Exception as retry_exc:
            persistence_session.rollback()
            raise AppError(
                code="feedback_event_persist_error",
                message="Nao foi possivel salvar o feedback astrologico.",
                status_code=500,
            ) from retry_exc

    try:
        learning = (
            learning_loop(persistence_session, int(payload["user_id"]))
            if payload.get("user_id") is not None
            else {"observed_events": 0, "patterns": {}, "updated_rules": []}
        )
        refreshed_overrides = get_user_rule_overrides(persistence_session, payload.get("user_id"))
        strongest_rules = (
            persistence_session.query(UserRuleWeight)
            .filter(UserRuleWeight.user_id == payload.get("user_id"))
            .order_by(UserRuleWeight.weight.desc(), UserRuleWeight.rule_key.asc())
            .limit(12)
            .all()
            if payload.get("user_id") is not None
            else []
        )

        return {
            "ok": True,
            "feedback_event": _serialize_feedback_event(model),
            "analysis_snapshot": {
                "relationship": specialized.get("relationship", {}),
                "financial": specialized.get("financial", {}),
                "purpose": specialized.get("purpose", {}),
                "rule_hits": specialized.get("rule_hits", [])[:12],
            },
            "learning": learning,
            "user_rule_overrides": refreshed_overrides,
            "strongest_rules": [
                {
                    "rule_key": row.rule_key,
                    "weight": float(row.weight),
                    "evidence_count": int(row.evidence_count),
                    "average_intensity": float(row.average_intensity),
                }
                for row in strongest_rules
            ],
        }
    finally:
        persistence_session.close()
