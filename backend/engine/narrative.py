from __future__ import annotations

from typing import List, Dict, Any


# -----------------------------------
# CONFIG
# -----------------------------------

PROMPT_META = {
    "style": "narrativa",
    "technical_terms": False,
    "language": "pt-BR",
    "version": "v1",
}


# -----------------------------------
# CORE
# -----------------------------------

def build_narrative_prompt(events: List[Dict]) -> Dict[str, Any]:
    """
    Constrói prompt estruturado para LLM (sem chamada externa).
    Determinístico e pronto para cache.
    """

    # -------------------------
    # NORMALIZAÇÃO
    # -------------------------

    sorted_events = sorted(
        events,
        key=lambda e: (e["time_window"]["start"], -e["score"]),
    )

    # -------------------------
    # BULLETS
    # -------------------------

    bullets: List[str] = []

    for e in sorted_events:
        bullets.append(
            (
                f"- Evento: {e['event']} | "
                f"Categoria: {e['category']} | "
                f"Intensidade: {e['intensity']} | "
                f"Período: {e['time_window']['start']} até {e['time_window']['end']}"
            )
        )

    # -------------------------
    # PROMPT
    # -------------------------

    prompt = (
        "Você é um especialista em interpretação simbólica.\n"
        "Crie uma narrativa em português (pt-BR), clara, direta e sem termos técnicos de astrologia.\n\n"
        "Regras:\n"
        "- Organize os eventos em ordem temporal\n"
        "- Destaque intensidade (leve, moderada, alta)\n"
        "- Explique causas e possíveis consequências\n"
        "- Sugira atitudes práticas\n"
        "- NÃO use termos técnicos (ex: conjunção, quadratura, etc)\n\n"
        "Eventos:\n"
        + "\n".join(bullets)
    )

    return {
        "prompt_meta": PROMPT_META,
        "prompt": prompt,
        "events_used": sorted_events,  # útil para debug/cache
    }