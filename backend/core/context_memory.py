from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from db.models import UserLifeEvent
from db.session import initialize_database


def _context_notes(user_context: dict[str, Any]) -> list[tuple[str, str]]:
    notes: list[tuple[str, str]] = []
    mapping = {
        "major_trauma_notes": "context_trauma",
        "major_loss_notes": "context_loss",
        "important_death": "context_death",
        "recurring_feeling": "context_feeling",
        "current_city": "context_city",
    }
    for field, event_type in mapping.items():
        value = user_context.get(field)
        if value:
            notes.append((event_type, str(value)[:1000]))

    flags = [
        ("marked_separation", "context_separation", "Separacao marcante declarada."),
        ("experienced_betrayal", "context_betrayal", "Traicao declarada no questionario."),
        ("experienced_depression", "context_depression", "Depressao declarada no questionario."),
        ("city_change", "context_move", "Mudanca de cidade declarada."),
        ("country_change", "context_move_country", "Mudanca de pais declarada."),
        ("financial_crisis", "context_finance", "Crise financeira declarada."),
        ("experienced_abandonment", "context_abandonment", "Abandono emocional declarado."),
        ("experienced_adoption", "context_adoption", "Adocao ou familia recomposta declarada."),
    ]
    for field, event_type, description in flags:
        if user_context.get(field):
            notes.append((event_type, description))
    return notes


def persist_user_context_memory(
  payload: dict[str, Any],
  db: Session,
) -> None:
    user_id = payload.get("user_id")
    user_context = dict(payload.get("user_context") or {})
    if not user_id or not user_context:
        return

    reference_date = payload.get("reference_date") or payload.get("date")
    if hasattr(reference_date, "isoformat"):
        event_date = reference_date
    else:
        from datetime import date

        event_date = date.fromisoformat(str(reference_date))

    initialize_database()
    notes = _context_notes(user_context)
    if not notes:
        return

    for event_type, description in notes:
        existing = (
            db.query(UserLifeEvent)
            .filter(
                UserLifeEvent.user_id == user_id,
                UserLifeEvent.event_type == event_type,
                UserLifeEvent.description == description,
            )
            .first()
        )
        if existing:
            continue
        db.add(
            UserLifeEvent(
                user_id=user_id,
                event_type=event_type,
                event_date=event_date,
                description=description,
                transits={},
                progressions={},
                solar_arc={},
                rule_hits=[],
                special_analysis={"source": "intake_questionnaire"},
            )
        )
    try:
        db.commit()
    except Exception:
        db.rollback()
