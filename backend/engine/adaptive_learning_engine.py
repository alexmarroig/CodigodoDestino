from __future__ import annotations

from collections import defaultdict
from typing import Any

from sqlalchemy.orm import Session

from db.models import UserFeedbackEvent, UserRuleWeight


def extract_patterns(events: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    patterns: dict[str, dict[str, float]] = {}

    for event in events:
        intensity = max(1, int(event.get("real_intensity", 1)))
        for transit in list(event.get("transits", []) or []):
            key = f"{transit.get('planet_a')}_{transit.get('aspect')}_{transit.get('planet_b')}"
            bucket = patterns.setdefault(key, {"count": 0, "total_intensity": 0.0})
            bucket["count"] += 1
            bucket["total_intensity"] += intensity

        for hit in list(event.get("rule_hits", []) or []):
            code = str(hit.get("code") or "")
            if not code:
                continue
            bucket = patterns.setdefault(code, {"count": 0, "total_intensity": 0.0})
            bucket["count"] += 1
            bucket["total_intensity"] += intensity

    return patterns


def compute_pattern_score(pattern: dict[str, float]) -> float:
    count = max(1.0, float(pattern["count"]))
    avg_intensity = float(pattern["total_intensity"]) / count
    return round(count * avg_intensity, 2)


def update_rules(
    db: Session,
    *,
    user_id: int,
    patterns: dict[str, dict[str, float]],
) -> list[dict[str, Any]]:
    updated: list[dict[str, Any]] = []

    for key, data in patterns.items():
        score = min(compute_pattern_score(data), 10.0)
        average_intensity = round(float(data["total_intensity"]) / max(1, int(data["count"])), 2)
        record = (
            db.query(UserRuleWeight)
            .filter(UserRuleWeight.user_id == user_id, UserRuleWeight.rule_key == key)
            .one_or_none()
        )
        if record is None:
            record = UserRuleWeight(
                user_id=user_id,
                rule_key=key,
                weight=score,
                evidence_count=int(data["count"]),
                average_intensity=average_intensity,
            )
            db.add(record)
        else:
            record.weight = score
            record.evidence_count = int(data["count"])
            record.average_intensity = average_intensity

        updated.append(
            {
                "rule_key": key,
                "weight": score,
                "evidence_count": int(data["count"]),
                "average_intensity": average_intensity,
            }
        )

    db.commit()
    return sorted(updated, key=lambda item: (-float(item["weight"]), item["rule_key"]))[:12]


def get_user_rule_overrides(db: Session, user_id: int | None) -> dict[str, float]:
    if user_id is None:
        return {}

    rows = (
        db.query(UserRuleWeight)
        .filter(UserRuleWeight.user_id == user_id)
        .all()
    )
    return {row.rule_key: float(row.weight) for row in rows}


def learning_loop(db: Session, user_id: int) -> dict[str, Any]:
    rows = (
        db.query(UserFeedbackEvent)
        .filter(UserFeedbackEvent.user_id == user_id)
        .order_by(UserFeedbackEvent.event_date.asc())
        .all()
    )
    serialized = [
        {
            "event_type": row.event_type,
            "event_date": row.event_date.isoformat(),
            "real_intensity": row.real_intensity,
            "transits": row.transits,
            "rule_hits": row.rule_hits,
        }
        for row in rows
    ]
    patterns = extract_patterns(serialized)
    updated_rules = update_rules(db, user_id=user_id, patterns=patterns) if patterns else []
    return {
        "observed_events": len(serialized),
        "patterns": patterns,
        "updated_rules": updated_rules,
    }
