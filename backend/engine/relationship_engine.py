from __future__ import annotations

from typing import Any


def _score_probability(score: float, scale: float = 10.0) -> float:
    return round(max(0.05, min(0.97, score / scale)), 2)


def detect_relationship_events(
    analysis: dict[str, Any],
    rule_hits: list[dict[str, Any]],
) -> dict[str, Any]:
    relevant_hits = [
        hit
        for hit in rule_hits
        if hit["domain"] in {"relacionamentos", "criatividade_afetos"}
        or hit["code"]
        in {
            "relationship_start",
            "love_expansion",
            "relationship_test",
            "relationship_block",
            "intense_relationship",
            "sudden_love",
            "conflict_relationship",
            "emotional_bond",
            "marriage_window",
            "commitment",
            "breakup",
            "sudden_break",
            "emotional_cut",
            "deep_emotional_break",
        }
    ]

    marriage_score = sum(
        float(hit["weight"])
        for hit in relevant_hits
        if hit["code"] in {"marriage_window", "commitment", "love_expansion", "relationship_start"}
    )
    bonding_score = sum(
        float(hit["weight"])
        for hit in relevant_hits
        if hit["code"] in {"emotional_bond", "relationship_start", "love_expansion", "intense_relationship"}
    )
    breakup_score = sum(
        float(hit["weight"])
        for hit in relevant_hits
        if hit["code"] in {"breakup", "sudden_break", "deep_emotional_break", "emotional_cut"}
    )
    tension_score = sum(
        float(hit["weight"])
        for hit in relevant_hits
        if hit["code"] in {"relationship_test", "relationship_block", "conflict_relationship", "intense_relationship"}
    )

    marriage_probability = _score_probability(marriage_score, 9.0)
    bonding_probability = _score_probability(bonding_score, 8.5)
    breakup_probability = _score_probability(breakup_score + (tension_score * 0.35), 9.5)
    tension_probability = _score_probability(tension_score, 8.5)

    if breakup_probability >= 0.68 and breakup_probability > marriage_probability:
        summary = (
            "O campo afetivo entra em fase de corte real: vinculos frageis tendem a rachar, "
            "e o que estiver desgastado pode pedir ruptura, afastamento ou redefinicao dura."
        )
        advice = "Nao force permanencia onde a realidade ja mostrou esgotamento. Nomeie o problema antes de decidir."
    elif marriage_probability >= 0.68 or bonding_probability >= 0.72:
        summary = (
            "Existe uma janela concreta de aprofundamento afetivo. Relacoes com base real tendem "
            "a caminhar para compromisso, alinhamento mais serio ou formalizacao."
        )
        advice = "Observe consistencia, disponibilidade e reciprocidade. Se a base existir, este e um periodo de consolidacao."
    elif tension_probability >= 0.55:
        summary = (
            "Relacionamentos entram em prova: o tema nao e ausencia de sentimento, mas limite, maturidade "
            "e a capacidade de sustentar o que se promete."
        )
        advice = "Converse sobre expectativa, tempo e limite. Evite romantizar sinais de incompatibilidade."
    else:
        summary = (
            "A vida afetiva esta ativa, mas ainda mais em ajuste do que em desfecho fechado. "
            "O que comeca agora ainda passa por teste antes de se definir."
        )
        advice = "Diminua leitura ansiosa e aumente observacao do comportamento repetido."

    peak_dates = [
        peak
        for peak in [hit.get("time_window", {}).get("peak") for hit in relevant_hits]
        if peak
    ][:3]

    return {
        "key": "relacionamento",
        "marriage_probability": marriage_probability,
        "bonding_probability": bonding_probability,
        "breakup_probability": breakup_probability,
        "tension_probability": tension_probability,
        "summary": summary,
        "advice": advice,
        "signals": [hit["label"] for hit in relevant_hits[:5]],
        "peak_dates": peak_dates,
        "rule_count": len(relevant_hits),
        "current_theme": (
            "formalizacao"
            if marriage_probability >= breakup_probability and marriage_probability >= 0.6
            else "ruptura"
            if breakup_probability >= 0.6
            else "teste"
        ),
        "why_now": " + ".join(hit["label"] for hit in relevant_hits[:3]) or "Sinais relacionais ainda em formacao.",
    }
