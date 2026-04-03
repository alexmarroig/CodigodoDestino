from engine.horary import analyze_horary


def test_horary_returns_structured_judgment() -> None:
    result = analyze_horary(
        {
            "question": "Vou conseguir essa vaga de emprego?",
            "date": "2026-04-02",
            "time": "14:30:00",
            "lat": -23.55,
            "lon": -46.63,
            "timezone": "America/Sao_Paulo",
            "orb_degrees": 4.0,
            "house_system": "P",
        }
    )

    assert result["domain"] == "carreira_status"
    assert "is_radical" in result
    assert "strictures" in result
    assert "significators" in result
    assert result["judgment"] in {"tende a sim", "tende a nao", "indeterminado"}
    assert result["confidence"]["level"] in {"high", "medium", "low"}
