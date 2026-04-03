from uuid import uuid4

from fastapi.testclient import TestClient

from api.main import app
from db.models import User, UserRuleWeight
from db.session import SessionLocal, initialize_database


def _create_user() -> int:
    initialize_database()
    session = SessionLocal()
    try:
        user = User(email=f"teste-{uuid4()}@example.com")
        session.add(user)
        session.commit()
        session.refresh(user)
        return int(user.id)
    finally:
        session.close()


def test_mapa_endpoint_keeps_compatibility(monkeypatch) -> None:
    monkeypatch.setattr(
        "core.pipeline.generate_narrative_with_cache",
        lambda prompt_data, cache: {
            "text": "Leitura local de teste.",
            "strategy": "template",
            "strategy_reason": "test",
            "complexity_score": 0.2,
            "prompt_event_count": len(prompt_data["events_used"]),
        },
    )

    client = TestClient(app)
    response = client.post(
        "/mapa",
        json={
            "date": "1995-03-10",
            "time": "14:30",
            "lat": -23.55,
            "lon": -46.63,
            "timezone": "America/Sao_Paulo",
            "reference_date": "2026-04-02",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "computed" in data
    assert "events" in data
    assert "narrative" in data
    assert "analysis" in data
    assert "profile_quality" in data
    assert "confidence" in data
    assert "uncertainties" in data
    assert "techniques_used" in data
    assert "forecast_360" in data
    assert "timeline" in data
    assert "life_episodes" in data
    assert "turning_points" in data
    assert "exact_timing" in data
    assert "life_events" in data
    assert "life_story" in data
    assert "feedback_questions" in data
    assert "user_rule_overrides" in data
    assert "proposito" in data["forecast_360"]


def test_mapa_allows_unknown_birth_time(monkeypatch) -> None:
    monkeypatch.setattr(
        "core.pipeline.generate_narrative_with_cache",
        lambda prompt_data, cache: {
            "text": "Leitura local de teste.",
            "strategy": "template",
            "strategy_reason": "test",
            "complexity_score": 0.2,
            "prompt_event_count": len(prompt_data["events_used"]),
        },
    )

    client = TestClient(app)
    response = client.post(
        "/mapa",
        json={
            "date": "1995-03-10",
            "lat": -23.55,
            "lon": -46.63,
            "timezone": "America/Sao_Paulo",
            "birth_time_precision": "unknown",
            "reference_date": "2026-04-02",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["profile_quality"]["code"] == "C"
    assert data["profile_quality"]["can_use_houses"] is False


def test_horaria_endpoint_returns_judgment() -> None:
    client = TestClient(app)
    response = client.post(
        "/horaria",
        json={
            "question": "Ele volta a falar comigo?",
            "date": "2026-04-02",
            "time": "14:30",
            "lat": -23.55,
            "lon": -46.63,
            "timezone": "America/Sao_Paulo",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["judgment"] in {"tende a sim", "tende a nao", "indeterminado"}
    assert "testimonies_for" in data
    assert "testimonies_against" in data


def test_life_event_endpoint_saves_feedback() -> None:
    client = TestClient(app)
    response = client.post(
        "/life-event",
        json={
            "event_type": "relationship_start",
            "event_date": "2024-08-10",
            "description": "Comecei um relacionamento importante.",
            "birth_date": "1995-03-10",
            "birth_time": "14:30",
            "birth_lat": -23.55,
            "birth_lon": -46.63,
            "birth_timezone": "America/Sao_Paulo",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "event" in data
    assert "learning" in data


def test_feedback_event_endpoint_learns_and_mapa_exposes_questions(monkeypatch) -> None:
    monkeypatch.setattr(
        "core.pipeline.generate_narrative_with_cache",
        lambda prompt_data, cache: {
            "text": "Leitura local de teste.",
            "strategy": "template",
            "strategy_reason": "test",
            "complexity_score": 0.2,
            "prompt_event_count": len(prompt_data["events_used"]),
        },
    )

    user_id = _create_user()
    client = TestClient(app)

    feedback_response = client.post(
        "/feedback-event",
        json={
            "user_id": user_id,
            "event_type": "career_change",
            "event_date": "2025-11-14",
            "real_intensity": 4,
            "predicted": True,
            "description": "Troquei de trabalho depois de muita pressao.",
            "birth_date": "1995-03-10",
            "birth_time": "14:30",
            "birth_lat": -23.55,
            "birth_lon": -46.63,
            "birth_timezone": "America/Sao_Paulo",
        },
    )

    assert feedback_response.status_code == 200
    feedback_data = feedback_response.json()
    assert feedback_data["ok"] is True
    assert feedback_data["learning"]["observed_events"] >= 1
    assert "feedback_event" in feedback_data
    assert "user_rule_overrides" in feedback_data

    session = SessionLocal()
    try:
        assert session.query(UserRuleWeight).filter(UserRuleWeight.user_id == user_id).count() >= 1
    finally:
        session.close()

    mapa_response = client.post(
        "/mapa",
        json={
            "user_id": user_id,
            "date": "1995-03-10",
            "time": "14:30",
            "lat": -23.55,
            "lon": -46.63,
            "timezone": "America/Sao_Paulo",
            "reference_date": "2026-04-02",
        },
    )

    assert mapa_response.status_code == 200
    mapa_data = mapa_response.json()
    assert "feedback_questions" in mapa_data
    assert "user_rule_overrides" in mapa_data
    assert isinstance(mapa_data["feedback_questions"], list)
