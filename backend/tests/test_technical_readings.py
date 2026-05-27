from datetime import date

from engine.portuguese_text import polish_portuguese
from engine.technical_readings import build_signal_reading, format_technical_block


def test_polish_portuguese_adds_accents() -> None:
    assert "não" in polish_portuguese("nao da para evitar")
    assert "você" in polish_portuguese("voce decide")
    assert "está" in polish_portuguese("O mapa esta pressionado")
    assert "evitável" in polish_portuguese("Parcialmente evitavel")


def test_polish_portuguese_translates_english_planets() -> None:
    assert "Netuno" in polish_portuguese("Neptune em oposicao com Venus")
    assert "Plutão" in polish_portuguese("Pluto square Moon")
    assert "Vênus" in polish_portuguese("transito de Venus na casa 7")


def test_build_signal_reading_includes_aspect_and_when() -> None:
    reading = build_signal_reading(
        {
            "technique": "transits",
            "label": "Saturno em quadratura com Lua",
            "weight": 0.9,
            "polarity": "challenging",
            "time_window": {"start": "2026-05-01", "end": "2026-05-20", "peak": "2026-05-10"},
            "evidence": {
                "aspect": "square",
                "planet_a": "saturn",
                "planet_b": "moon",
                "phase": "applying",
                "orb": 1.2,
                "transit_house": 7,
            },
        },
        reference_date=date(2026, 4, 4),
        category_key="rupture",
    )
    assert "quadratura" in reading["aspect_line"].lower()
    assert "10 de maio de 2026" in reading["when"]
    assert reading["when"].count("10 de maio de 2026") == 1
    assert "anular" in reading["avoidability"] or "evitável" in reading["avoidability"]

    block = format_technical_block([reading])
    assert "Aspecto:" in block
    assert "Quando:" in block
