from __future__ import annotations

from typing import Any


def _score_probability(score: float, scale: float = 10.0) -> float:
    return round(max(0.05, min(0.97, score / scale)), 2)


def detect_financial_cycles(
    analysis: dict[str, Any],
    rule_hits: list[dict[str, Any]],
) -> dict[str, Any]:
    relevant_hits = [
        hit
        for hit in rule_hits
        if hit["domain"] in {"financeiro", "crises_recursos"}
        or hit["code"]
        in {
            "financial_gain",
            "money_flow",
            "financial_restriction",
            "financial_transformation",
            "unexpected_money",
            "financial_loss",
        }
    ]

    growth_score = sum(
        float(hit["weight"])
        for hit in relevant_hits
        if hit["code"] in {"financial_gain", "money_flow", "unexpected_money"}
    )
    restriction_score = sum(
        float(hit["weight"])
        for hit in relevant_hits
        if hit["code"] in {"financial_restriction", "financial_loss"}
    )
    restructure_score = sum(
        float(hit["weight"])
        for hit in relevant_hits
        if hit["code"] in {"financial_transformation"}
    )
    volatility_score = sum(
        float(hit["weight"])
        for hit in relevant_hits
        if hit["code"] in {"unexpected_money", "financial_loss"}
    )

    growth_probability = _score_probability(growth_score, 8.5)
    restriction_probability = _score_probability(restriction_score, 8.5)
    restructure_probability = _score_probability(restructure_score + (restriction_score * 0.25), 9.0)
    volatility_probability = _score_probability(volatility_score, 8.0)

    if restriction_probability >= 0.65 and restriction_probability > growth_probability:
        summary = (
            "O dinheiro entra em fase de contencao real. O periodo pede corte de excesso, revisao de custos, "
            "mais criterio com risco e menos confianca em fluxo automatico."
        )
        advice = "Proteja caixa, renegocie o que pesar e evite ampliar gasto fixo sem previsibilidade."
        current_theme = "ajuste"
    elif growth_probability >= 0.68:
        summary = (
            "Ha janela concreta para destravar dinheiro, melhorar fluxo ou colher resultado de movimento anterior. "
            "O ganho tende a vir mais por expansao inteligente do que por impulso."
        )
        advice = "Aproveite abertura para organizar entradas, consolidar reserva e transformar ganho em estrutura."
        current_theme = "expansao"
    elif restructure_probability >= 0.58:
        summary = (
            "Financas entram em fase de reestruturacao. Nao e apenas ganhar ou perder: o ponto principal e mudar "
            "a forma como voce lida com valor, dependencia e controle de recursos."
        )
        advice = "Troque improviso por plano. O melhor movimento agora e reorganizar estrategia, nao apenas reagir."
        current_theme = "reestruturacao"
    else:
        summary = (
            "O dinheiro mostra oscilacao moderada. Ainda nao e um capitulo de virada total, mas ja pede "
            "mais atencao a fluxo, timing e disciplina."
        )
        advice = "Evite operar no escuro. Pequenos ajustes agora evitam pressao maior depois."
        current_theme = "observacao"

    peak_dates = [
        peak
        for peak in [hit.get("time_window", {}).get("peak") for hit in relevant_hits]
        if peak
    ][:3]

    return {
        "key": "financas",
        "growth_probability": growth_probability,
        "restriction_probability": restriction_probability,
        "restructure_probability": restructure_probability,
        "volatility_probability": volatility_probability,
        "summary": summary,
        "advice": advice,
        "signals": [hit["label"] for hit in relevant_hits[:5]],
        "peak_dates": peak_dates,
        "rule_count": len(relevant_hits),
        "current_theme": current_theme,
        "why_now": " + ".join(hit["label"] for hit in relevant_hits[:3]) or "Sinais financeiros ainda difusos.",
    }
