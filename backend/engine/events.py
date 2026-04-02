from __future__ import annotations

from datetime import date


def _has_aspect(aspects: list[dict], a: str, b: str, aspect: str) -> bool:
    for item in aspects:
        if {item["planet_a"], item["planet_b"]} == {a, b} and item["aspect"] == aspect:
            return True
    return False


def generate_events(aspects: list[dict], houses: list[float], numerology: dict) -> list[dict]:
    events: list[dict] = []

    if _has_aspect(aspects, "venus", "mars", "square"):
        events.append(
            {
                "id": "evt_rel_001",
                "evento": "Fase de tensão e ajustes em vínculos afetivos",
                "categoria": "relacionamento",
                "intensidade": "alta",
                "score": 0.86,
                "drivers": ["venus_square_mars"],
                "time_window": {"start": str(date.today()), "end": str(date.today())},
            }
        )

    saturn_long = None
    for asp in aspects:
        if "saturn" in {asp["planet_a"], asp["planet_b"]} and asp["aspect"] in {"square", "opposition"}:
            saturn_long = 1
            break
    if saturn_long and len(houses) == 12:
        events.append(
            {
                "id": "evt_rel_002",
                "evento": "Período de responsabilidade e definição em relacionamentos",
                "categoria": "relacionamento",
                "intensidade": "média",
                "score": 0.72,
                "drivers": ["saturn_hard_aspect"],
                "time_window": {"start": str(date.today()), "end": str(date.today())},
            }
        )

    if numerology.get("life_path_number") == 1:
        events.append(
            {
                "id": "evt_pers_001",
                "evento": "Janela favorável para protagonismo e decisões independentes",
                "categoria": "desenvolvimento_pessoal",
                "intensidade": "média",
                "score": 0.64,
                "drivers": ["life_path_1"],
                "time_window": {"start": str(date.today()), "end": str(date.today())},
            }
        )

    if not events:
        events.append(
            {
                "id": "evt_gen_001",
                "evento": "Ciclo estável com progresso gradual",
                "categoria": "geral",
                "intensidade": "baixa",
                "score": 0.4,
                "drivers": ["no_major_triggers"],
                "time_window": {"start": str(date.today()), "end": str(date.today())},
            }
        )

    return events
