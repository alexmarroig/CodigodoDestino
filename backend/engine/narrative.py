from __future__ import annotations


def build_narrative_prompt(events: list[dict]) -> dict[str, object]:
    bullets = []
    for e in events:
        bullets.append(
            f"- Evento: {e['evento']} | Categoria: {e['categoria']} | Intensidade: {e['intensidade']} | Período: {e['time_window']['start']} a {e['time_window']['end']}"
        )

    prompt = (
        "Crie uma narrativa em português (pt-BR) com linguagem simples, sem termos técnicos de astrologia. "
        "Organize em ordem temporal, destacando intensidade de cada evento e possíveis atitudes práticas.\n"
        + "\n".join(bullets)
    )
    return {
        "prompt_meta": {"style": "narrativa", "technical_terms": False, "language": "pt-BR"},
        "prompt": prompt,
    }
