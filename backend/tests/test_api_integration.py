from fastapi.testclient import TestClient

from api.main import app


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
