from __future__ import annotations

from datetime import date, datetime
from typing import Any

from engine.analysis import DOMAIN_LABELS
from engine.certainty import (
    CERTAINTY_LABELS,
    apply_certainty_prefix,
    certainty_from_signal_count,
)

CATEGORY_DEFINITIONS = [
    {
        "key": "health",
        "event_type": "Saude, doenca ou acidente",
        "domains": {"saude_rotina", "psicologico_espiritual"},
        "allowed_polarities": {"challenging", "mixed"},
        "rule_codes": {
            "accident_risk",
            "emotional_low",
            "psychological_transformation",
        },
        "life_event_types": {"crisis"},
    },
    {
        "key": "career",
        "event_type": "Emprego, carreira ou perda de trabalho",
        "domains": {"carreira_status"},
        "allowed_polarities": {"supportive", "challenging", "mixed"},
        "rule_codes": {
            "career_block",
            "career_reset",
            "career_transformation",
            "career_growth",
            "career_change",
            "career_pressure",
            "authority_conflict",
        },
        "life_event_types": {"career_change"},
    },
    {
        "key": "relationships",
        "event_type": "Relacionamento, namoro ou casamento",
        "domains": {"relacionamentos", "criatividade_afetos"},
        "allowed_polarities": {"supportive", "challenging", "mixed"},
        "rule_codes": {
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
        },
        "life_event_types": {"marriage"},
    },
    {
        "key": "rupture",
        "event_type": "Briga, ruptura ou separacao",
        "domains": {"relacionamentos", "familia_lar", "psicologico_espiritual"},
        "allowed_polarities": {"challenging", "mixed"},
        "rule_codes": {
            "breakup",
            "sudden_break",
            "emotional_cut",
            "deep_emotional_break",
            "relationship_block",
            "relationship_test",
        },
        "life_event_types": {"breakup", "crisis"},
    },
    {
        "key": "major_transitions",
        "event_type": "Grande mudanca de vida",
        "domains": {
            "identidade",
            "crises_recursos",
            "psicologico_espiritual",
            "expansao_sentido",
            "carreira_status",
        },
        "allowed_polarities": {"supportive", "challenging", "mixed"},
        "rule_codes": {
            "career_change",
            "career_reset",
            "career_transformation",
            "financial_transformation",
            "extreme_conflict",
            "psychological_transformation",
        },
        "life_event_types": {"life_change", "career_change", "crisis"},
    },
]

PROBABILITY_LEVELS = {
    1: "Descartar",
    2: "Baixa",
    3: "Moderada",
    4: "Alta",
}

REALITY_TEMPLATES = {
    "health": {
        "what": "Ha pressao real sobre corpo, rotina e estabilidade emocional. O periodo pode trazer doenca leve, esgotamento ou risco maior de acidente se houver imprudencia.",
        "scenarios": [
            "Carga acumulada de trabalho, familia ou estudo derruba sono, foco e disposicao ate o corpo pedir pausa.",
            "Stress, queda imunologica ou um mal-estar obriga a reduzir compromissos por alguns dias.",
            "Se houver pressa, distração ou irritacao ao volante, aumenta o risco de acidente em transito ou pequenos incidentes.",
        ],
        "impact": "A rotina perde rendimento e pode exigir corte de agenda, repouso ou reorganizacao pratica.",
        "risk": "Se isso for ignorado, o quadro pode virar afastamento, erro serio, piora emocional ou acidente evitavel.",
        "action": "Reduza excesso, respeite sinais do corpo, evite dirigir ou agir no impulso quando estiver esgotado e procure ajuda profissional se o sintoma persistir.",
    },
    "career": {
        "what": "Ha mudanca concreta na vida profissional. O periodo pode trazer oportunidade nova, pressao por resultado, troca de funcao ou perda de emprego se a estrutura atual ja estiver fragil.",
        "scenarios": [
            "Chefe, cliente ou empresa pressiona mais e obriga uma decisao sobre sair, ficar ou mudar de posicao.",
            "Surge proposta de trabalho, projeto ou promocao, mas ela cobra responsabilidade maior ou reposicionamento rapido.",
            "Se o ambiente ja esta instavel, cresce a chance de corte, desgaste forte ou saida forçada.",
        ],
        "impact": "Carreira, renda, rotina e imagem publica podem mudar no mesmo bloco de tempo.",
        "risk": "Se voce empurrar a decisao, pode perder tempo, dinheiro e margem de negociacao.",
        "action": "Trate isso como fase de decisao profissional. Atualize curriculo, documente fatos, negocie com clareza e nao espere a situacao piorar para agir.",
    },
    "relationships": {
        "what": "Relacionamentos entram em fase de definicao. O periodo favorece namoro serio, noivado, casamento ou uma conversa decisiva com {partner_role} sobre o futuro.",
        "scenarios": [
            "A relacao com {partner_role} avanca para compromisso mais claro, como oficializacao, morar junto ou casamento.",
            "Alguem novo entra e rapidamente vira foco emocional principal.",
            "Uma conversa objetiva com {partner_role} define se a relacao vai crescer ou parar de vez.",
        ],
        "impact": "A vida afetiva ganha rumo mais claro: compromisso, mudanca de status ou encerramento de indefinicao.",
        "risk": "Se voce evitar a conversa certa, a relacao pode entrar em desgaste, ciúme, promessa vazia ou triangulo emocional.",
        "action": "Diga o que quer, observe atitude concreta do outro e diferencie paixao momentanea de projeto real de vida.",
    },
    "rupture": {
        "what": "Ha risco alto de briga seria, corte emocional ou separacao. Isso pode acontecer com {partner_role}, ex, familia ou alguem muito proximo.",
        "scenarios": [
            "A relacao com {partner_role} chega ao limite depois de desgaste, frieza ou conflito repetido.",
            "Uma conversa pesada com pai, mae ou familiar abre distancia, magoa ou afastamento mais direto.",
            "Voce decide parar de tolerar uma situacao que ja vinha consumindo sua paz.",
        ],
        "impact": "Vinculos mudam de lugar rapidamente e isso mexe com rotina, moradia, apoio emocional e senso de estabilidade.",
        "risk": "Se for empurrado com a barriga, o conflito pode virar humilhacao, perda de confianca ou separacao mais dura.",
        "action": "Conduza a conversa com clareza, prepare limite e nao espere o problema se resolver sozinho.",
    },
    "major_transitions": {
        "what": "Esta e uma fase de virada grande. Trabalho, dinheiro, identidade, cidade, rotina ou relacoes podem mudar juntos no mesmo ciclo.",
        "scenarios": [
            "Uma mudanca de carreira puxa ajuste financeiro, afetivo e pessoal ao mesmo tempo.",
            "Voce fecha um capitulo antigo e comeca outro com prioridades bem diferentes.",
            "A pressao externa obriga uma decisao que muda o jeito de viver, trabalhar ou se posicionar.",
        ],
        "impact": "O mapa da vida muda de verdade: direcao, compromissos, dinheiro e estabilidade emocional entram em rearranjo.",
        "risk": "Se voce reagir tarde, a mudanca vem de forma caotica e mais cara.",
        "action": "Assuma que esta em virada de vida, corte o que nao sustenta mais e escolha uma direcao antes que o contexto escolha por voce.",
    },
}


def _parse_iso_date(value: str | None) -> date | None:
    if not value:
        return None
    return datetime.fromisoformat(value).date()


def _merged_window(items: list[dict[str, Any]], reference_date: date) -> dict[str, Any] | None:
    starts = [_parse_iso_date(item.get("time_window", {}).get("start")) for item in items]
    ends = [_parse_iso_date(item.get("time_window", {}).get("end")) for item in items]
    peaks = [_parse_iso_date(item.get("time_window", {}).get("peak")) for item in items]
    starts = [item for item in starts if item is not None]
    ends = [item for item in ends if item is not None]
    peaks = [item for item in peaks if item is not None]

    if not starts or not ends:
        return None

    start = min(starts)
    end = max(ends)
    peak = min(
        peaks or [start],
        key=lambda item: abs((item - reference_date).days),
    )
    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "peak": peak.isoformat(),
        "duration_days": max(1, (end - start).days + 1),
    }


def _relative_timeframe(reference_date: date, window: dict[str, Any] | None) -> str:
    if not window:
        return "tempo ainda em formacao"

    start = _parse_iso_date(window["start"]) or reference_date
    end = _parse_iso_date(window["end"]) or start
    days_to_start = max(0, (start - reference_date).days)
    duration_days = max(1, (end - start).days + 1)

    if days_to_start <= 7 and duration_days <= 14:
        return "proximas 1 a 2 semanas"
    if days_to_start <= 14 and duration_days <= 28:
        return "proximas 2 a 4 semanas"
    if days_to_start <= 30 and duration_days <= 60:
        return "dentro de 1 a 2 meses"
    if days_to_start <= 60 and duration_days <= 120:
        return "dentro de 2 a 4 meses"
    if days_to_start <= 120 and duration_days <= 240:
        return "dentro de 6 a 8 meses"
    return "ao longo dos proximos 12 a 24 meses"


def _explanation(
    *,
    event_type: str,
    signals: list[dict[str, Any]],
    rule_hits: list[dict[str, Any]],
    life_events: list[dict[str, Any]],
) -> str:
    lead_labels = [item["label"] for item in sorted(signals, key=lambda item: -float(item["weight"]))[:3]]
    rule_labels = [item["label"] for item in sorted(rule_hits, key=lambda item: -float(item["weight"]))[:2]]
    life_labels = [item["type"] for item in life_events[:1]]
    evidence = lead_labels + rule_labels + life_labels
    evidence = evidence[:4]

    if not evidence:
        return f"{event_type} tem sinais aparecendo, mas ainda sem forca suficiente para uma previsao firme."

    return f"Ha convergencia real de sinais neste tema. Principais confirmacoes: {', '.join(evidence)}."


def _sort_signals(signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        signals,
        key=lambda item: (
            -float(item.get("weight", 0.0)),
            item.get("technique", ""),
            item.get("label", ""),
        ),
    )


def _category_priority_boost(category_key: str, user_context: dict[str, Any]) -> float:
    status = str(user_context.get("relationship_status") or "unknown")
    boosts = {
        "rupture": {
            "separated": 0.35,
            "divorced": 0.35,
            "widowed": 0.2,
        },
        "relationships": {
            "dating": 0.25,
            "engaged": 0.3,
            "married": 0.3,
            "single": 0.15,
        },
        "health": {},
        "career": {},
        "major_transitions": {
            "separated": 0.15,
            "divorced": 0.15,
        },
    }
    return boosts.get(category_key, {}).get(status, 0.0)


def _personalize_template_text(text: str, placeholders: dict[str, str]) -> str:
    result = text
    for key, value in placeholders.items():
        if value:
            result = result.replace(f"{{{key}}}", value)
    return result


def _build_context_placeholders(user_context: dict[str, Any]) -> dict[str, str]:
    partner = str(user_context.get("current_partner_role") or "unknown")
    partner_label = {
        "girlfriend": "sua namorada",
        "boyfriend": "seu namorado",
        "wife": "sua esposa",
        "husband": "seu marido",
        "partner": "seu parceiro",
    }.get(partner, "seu parceiro")
    return {"partner_role": partner_label}


def _build_human_translation(
    category_key: str,
    time_label: str,
    *,
    independent_signals: int,
    user_context: dict[str, Any],
) -> dict[str, Any]:
    template = REALITY_TEMPLATES[category_key]
    placeholders = _build_context_placeholders(user_context)
    certainty = certainty_from_signal_count(independent_signals)
    what = _personalize_template_text(template["what"], placeholders)
    what = apply_certainty_prefix(what, certainty)
    scenarios = [_personalize_template_text(item, placeholders) for item in template["scenarios"][:3]]
    if category_key == "rupture" and user_context.get("father_status") == "deceased":
        scenarios = [
            item for item in scenarios
            if "pai" not in item.lower() or "mae" in item.lower()
        ] or scenarios
    return {
        "what_is_happening": what,
        "what_this_may_look_like_in_real_life": scenarios[:2],
        "possible_scenarios": scenarios,
        "impact": _personalize_template_text(template["impact"], placeholders),
        "risk": _personalize_template_text(template["risk"], placeholders),
        "recommended_action": _personalize_template_text(template["action"], placeholders),
        "certainty_level": certainty,
        "certainty_label": CERTAINTY_LABELS[certainty],
        "formatted_block": (
            f"Janela de tempo:\n{time_label}\n\n"
            f"O que esta acontecendo:\n{what}\n\n"
            "Como isso pode aparecer na vida real:\n"
            + "\n".join(f"* {item}" for item in scenarios[:2])
            + "\n\n"
            f"Impacto:\n{template['impact']}\n\n"
            f"Risco:\n{template['risk']}\n\n"
            f"Acao recomendada:\n{template['action']}"
        ),
    }


def build_predictive_insights(
    analysis: dict[str, Any],
    *,
    reference_date: date,
) -> dict[str, Any]:
    user_context = dict(analysis.get("user_context") or {})
    signals = list(analysis.get("signals", []))
    rule_hits = list(analysis.get("rule_hits", []))
    life_events = list(analysis.get("life_events", []))
    exact_timed_events = list(analysis.get("exact_timing", {}).get("timed_events", []))

    detected_events: list[dict[str, Any]] = []
    watchlist: list[dict[str, Any]] = []

    for definition in CATEGORY_DEFINITIONS:
        category_signals = [
            signal
            for signal in signals
            if signal.get("domain") in definition["domains"]
            and signal.get("polarity") in definition["allowed_polarities"]
        ]
        category_rule_hits = [
            hit
            for hit in rule_hits
            if hit.get("code") in definition["rule_codes"]
            or hit.get("domain") in definition["domains"]
        ]
        category_life_events = [
            event
            for event in life_events
            if event.get("type") in definition["life_event_types"]
        ]
        category_timed_events = [
            event
            for event in exact_timed_events
            if event.get("code") in definition["rule_codes"]
            or event.get("domain") in definition["domains"]
        ]

        techniques = sorted({str(signal["technique"]) for signal in category_signals})
        independent_signals = len(techniques)
        probability_level = PROBABILITY_LEVELS.get(min(independent_signals, 4), "High")

        if independent_signals <= 1:
            continue

        merged_items = [
            *category_signals,
            *[
                {"time_window": event.get("window") or event.get("time_window", {})}
                for event in category_life_events
            ],
            *[
                {"time_window": event.get("time_window", {})}
                for event in category_timed_events
            ],
        ]
        time_window = _merged_window(merged_items, reference_date)
        priority_boost = _category_priority_boost(definition["key"], user_context)
        probability_score = round(
            min(
                0.95,
                (
                    (independent_signals * 0.19)
                    + (sum(float(signal["weight"]) for signal in category_signals[:4]) * 0.08)
                    + priority_boost
                ),
            ),
            2,
        )
        certainty_level = certainty_from_signal_count(independent_signals)
        entry = {
            "category_key": definition["key"],
            "event_type": definition["event_type"],
            "probability_level": probability_level,
            "certainty_level": certainty_level,
            "certainty_label": CERTAINTY_LABELS[certainty_level],
            "independent_signals": independent_signals,
            "probability_score": probability_score,
            "time_window": {
                **(time_window or {}),
                "label": _relative_timeframe(reference_date, time_window),
            },
            "techniques": techniques,
            "signals": [signal["label"] for signal in _sort_signals(category_signals)[:4]],
            "rule_hits": [hit["label"] for hit in category_rule_hits[:3]],
            "exact_dates": [
                event.get("date")
                or event.get("window", {}).get("peak")
                for event in [*category_timed_events[:2], *category_life_events[:2]]
                if event.get("date") or event.get("window", {}).get("peak")
            ],
            "explanation": _explanation(
                event_type=definition["event_type"],
                signals=category_signals,
                rule_hits=category_rule_hits,
                life_events=category_life_events,
            ),
            "domains": sorted(
                {
                    DOMAIN_LABELS.get(str(signal["domain"]), str(signal["domain"]).replace("_", " "))
                    for signal in category_signals
                }
            ),
        }
        entry.update(
            _build_human_translation(
                definition["key"],
                entry["time_window"]["label"],
                independent_signals=independent_signals,
                user_context=user_context,
            )
        )

        if independent_signals >= 3:
            detected_events.append(entry)
        else:
            watchlist.append(entry)

    detected_events.sort(
        key=lambda item: (
            item["probability_level"] != "High",
            -float(item["probability_score"]),
            item["event_type"],
        )
    )
    watchlist.sort(key=lambda item: (-float(item["probability_score"]), item["event_type"]))

    return {
        "detected_events": detected_events,
        "watchlist": watchlist,
        "summary": {
            "detected_count": len(detected_events),
            "watchlist_count": len(watchlist),
            "strongest_category": detected_events[0]["event_type"] if detected_events else None,
        },
    }
