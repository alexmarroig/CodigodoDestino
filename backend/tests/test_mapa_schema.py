from datetime import date

from api.schemas import MapaRequest


def test_mapa_request_accepts_living_situation_enum() -> None:
    req = MapaRequest(
        date=date(1990, 5, 27),
        lat=-23.55,
        lon=-46.63,
        timezone="America/Sao_Paulo",
        user_context={"living_situation": "alone"},
    )
    assert req.user_context is not None
    assert req.user_context.living_situation == "alone"


def test_mapa_request_normalizes_portuguese_living_situation() -> None:
    req = MapaRequest(
        date=date(1990, 5, 27),
        lat=-23.55,
        lon=-46.63,
        timezone="America/Sao_Paulo",
        user_context={"living_situation": "Mora sozinho(a)"},
    )
    assert req.user_context is not None
    assert req.user_context.living_situation == "alone"
