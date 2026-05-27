from __future__ import annotations

from datetime import date, datetime
from typing import Any

from engine.analysis import DOMAIN_LABELS
from engine.certainty import (
    CERTAINTY_LABELS,
    apply_certainty_prefix,
    certainty_from_signal_count,
)
from engine.date_formatting import format_time_window_label, parse_iso_date
from engine.event_subtypes import (
    build_subtype_text,
    classify_event_subtype,
)
from engine.portuguese_text import polish_portuguese
from engine.technical_readings import (
    CATEGORY_AVOIDABILITY,
    build_quality_summary,
    build_technical_items,
    format_technical_block,
)

CATEGORY_DEFINITIONS = [
    {
        "key": "health",
        "event_type": "Saúde, doença ou acidente",
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
            "pregnancy_window",
        },
        "life_event_types": {"marriage"},
    },
    {
        "key": "rupture",
        "event_type": "Briga, ruptura ou separação",
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
        "event_type": "Grande mudança de vida",
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
    {
        "key": "finance",
        "event_type": "Dinheiro, ganho ou perda financeira",
        "domains": {"financeiro", "crises_recursos"},
        "allowed_polarities": {"supportive", "challenging", "mixed"},
        "rule_codes": {
            "financial_gain",
            "money_flow",
            "financial_restriction",
            "financial_transformation",
            "unexpected_money",
            "financial_loss",
        },
        "life_event_types": {"financial_change"},
    },
]

PROBABILITY_LEVELS = {
    1: "Descartar",
    2: "Baixa",
    3: "Moderada",
    4: "Alta",
}

TECHNIQUE_LABELS = {
    "transits": "Trânsito",
    "progressions": "Progressão",
    "solar_return": "Retorno solar",
    "solar_arc": "Arco solar",
    "profections": "Profeccão anual",
    "numerology": "Numerologia",
}

CATEGORY_CONCRETE_EVENT = {
    "health": "Episódio concreto de saúde: esgotamento, queda de imunidade ou risco de acidente",
    "career": "Mudança concreta no trabalho: promoção, troca de função, demissão ou proposta nova",
    "relationships": "Definição afetiva concreta: compromisso, casamento, morar junto ou conversa final com {partner_role}",
    "rupture": "Ruptura concreta: briga grave, corte emocional ou separação com {partner_role}",
    "major_transitions": "Virada de vida concreta: mudança de carreira, cidade, status ou estrutura familiar",
    "finance": "Mudança financeira concreta: entrada de dinheiro, perda de renda, aperto ou reestruturação de gastos",
}

REALITY_TEMPLATES = {
    "health": {
        "what": "Há pressão real sobre corpo, rotina e estabilidade emocional. O período pode trazer doença leve, esgotamento ou risco maior de acidente se houver imprudência.",
        "scenarios": [
            "Carga acumulada de trabalho, família ou estudo derruba sono, foco e disposição até o corpo pedir pausa.",
            "Estresse, queda imunológica ou mal-estar obriga a reduzir compromissos por alguns dias.",
            "Se houver pressa, distração ou irritação ao volante, aumenta o risco de acidente em trânsito ou pequenos incidentes.",
        ],
        "impact": "A rotina perde rendimento e pode exigir corte de agenda, repouso ou reorganização prática.",
        "risk": "Se isso for ignorado, o quadro pode virar afastamento, erro sério, piora emocional ou acidente evitável.",
        "action": "Reduza excesso, respeite sinais do corpo, evite dirigir ou agir no impulso quando estiver esgotado e procure ajuda profissional se o sintoma persistir.",
    },
    "career": {
        "what": "Há mudança concreta na vida profissional. O período pode trazer oportunidade nova, pressão por resultado, troca de função ou perda de emprego se a estrutura atual já estiver frágil.",
        "scenarios": [
            "Chefe, cliente ou empresa pressiona mais e obriga uma decisão sobre sair, ficar ou mudar de posição.",
            "Surge proposta de trabalho, projeto ou promoção, mas ela cobra responsabilidade maior ou reposicionamento rápido.",
            "Se o ambiente já está instável, cresce a chance de corte, desgaste forte ou saída forçada.",
        ],
        "impact": "Carreira, renda, rotina e imagem pública podem mudar no mesmo bloco de tempo.",
        "risk": "Se você empurrar a decisão, pode perder tempo, dinheiro e margem de negociação.",
        "action": "Trate isso como fase de decisão profissional. Atualize currículo, documente fatos, negocie com clareza e não espere a situação piorar para agir.",
    },
    "relationships": {
        "what": "Relacionamentos entram em fase de definição. O período favorece namoro sério, noivado, casamento ou conversa decisiva com {partner_role} sobre o futuro.",
        "scenarios": [
            "A relação com {partner_role} avança para compromisso mais claro, como oficialização, morar junto ou casamento.",
            "Alguém novo entra e rapidamente vira foco emocional principal.",
            "Uma conversa objetiva com {partner_role} define se a relação vai crescer ou parar de vez.",
        ],
        "impact": "A vida afetiva ganha rumo mais claro: compromisso, mudança de status ou encerramento de indefinição.",
        "risk": "Se você evitar a conversa certa, a relação pode entrar em desgaste, ciúme, promessa vazia ou triângulo emocional.",
        "action": "Diga o que quer, observe atitude concreta do outro e diferencie paixão momentânea de projeto real de vida.",
    },
    "rupture": {
        "what": "Há risco alto de briga séria, corte emocional ou separação. Isso pode acontecer com {partner_role}, ex, família ou alguém muito próximo.",
        "scenarios": [
            "A relação com {partner_role} chega ao limite depois de desgaste, frieza ou conflito repetido.",
            "Uma conversa pesada com pai, mãe ou familiar abre distância, mágoa ou afastamento mais direto.",
            "Você decide parar de tolerar uma situação que já vinha consumindo sua paz.",
        ],
        "impact": "Vínculos mudam de lugar rapidamente e isso mexe com rotina, moradia, apoio emocional e senso de estabilidade.",
        "risk": "Se for empurrado com a barriga, o conflito pode virar humilhação, perda de confiança ou separação mais dura.",
        "action": "Conduza a conversa com clareza, prepare limite e não espere o problema se resolver sozinho.",
    },
    "major_transitions": {
        "what": "Esta é uma fase de virada grande. Trabalho, dinheiro, identidade, cidade, rotina ou relações podem mudar juntos no mesmo ciclo.",
        "scenarios": [
            "Uma mudança de carreira puxa ajuste financeiro, afetivo e pessoal ao mesmo tempo.",
            "Você fecha um capítulo antigo e começa outro com prioridades bem diferentes.",
            "A pressão externa obriga uma decisão que muda o jeito de viver, trabalhar ou se posicionar.",
        ],
        "impact": "O mapa da vida muda de verdade: direção, compromissos, dinheiro e estabilidade emocional entram em rearranjo.",
        "risk": "Se você reagir tarde, a mudança vem de forma caótica e mais cara.",
        "action": "Assuma que está em virada de vida, corte o que não sustenta mais e escolha uma direção antes que o contexto escolha por você.",
    },
    "finance": {
        "what": "Há movimento concreto no campo financeiro. O período pode trazer entrada de dinheiro, aperto de renda, gasto inesperado ou reestruturação forçada de gastos.",
        "scenarios": [
            "Entrada de dinheiro — aumento, bônus, venda ou recebimento — melhora a situação e cobra planejamento imediato.",
            "Aperto, corte de renda ou gasto inesperado que desequilibra o orçamento e exige contenção rápida.",
            "Reestruturação financeira: dívida vence, investimento cobra decisão ou renda muda de fonte.",
        ],
        "impact": "Dinheiro, segurança e margem de decisão mudam de tamanho no mesmo bloco de tempo.",
        "risk": "Ganho sem planejamento some. Aperto sem contenção vira dívida. Os dois exigem ação rápida.",
        "action": "Antes de gastar qualquer entrada, defina destino. Antes do aperto virar crise, corte o supérfluo e renegocie o que der.",
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
    return format_time_window_label(window, reference_date=reference_date)


def _build_astrological_reason(
    *,
    event_type: str,
    signals: list[dict[str, Any]],
    rule_hits: list[dict[str, Any]],
    life_events: list[dict[str, Any]],
    techniques: list[str],
) -> str:
    parts: list[str] = []

    for signal in _sort_signals(signals)[:3]:
        technique = TECHNIQUE_LABELS.get(str(signal.get("technique")), str(signal.get("technique", "Sinal")))
        label = str(signal.get("label") or "").strip()
        if label:
            parts.append(f"{technique}: {label}")

    for hit in sorted(rule_hits, key=lambda item: -float(item.get("weight", 0.0)))[:2]:
        label = str(hit.get("label") or "").strip()
        if label:
            parts.append(f"Regra interpretativa: {label}")

    if life_events:
        parts.append(f"Evento de vida previsto: {event_type.lower()}")

    technique_names = [TECHNIQUE_LABELS.get(name, name) for name in techniques[:4]]
    if technique_names and not parts:
        return (
            f"Convergência entre {', '.join(technique_names)} aponta {event_type.lower()}, "
            "mas ainda sem detalhe técnico suficiente."
        )

    if not parts:
        return f"{event_type} aparece no mapa, mas ainda sem convergência técnica forte."

    convergence = ", ".join(technique_names) if technique_names else "múltiplas técnicas"
    return (
        f"Motivo ({convergence}): "
        + "; ".join(parts)
        + "."
    )


def _explanation(
    *,
    event_type: str,
    signals: list[dict[str, Any]],
    rule_hits: list[dict[str, Any]],
    life_events: list[dict[str, Any]],
    techniques: list[str] | None = None,
) -> str:
    return _build_astrological_reason(
        event_type=event_type,
        signals=signals,
        rule_hits=rule_hits,
        life_events=life_events,
        techniques=techniques or [],
    )


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
        "finance": {},
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


def _human_por_que_from_items(technical_items: list[dict[str, str]]) -> str:
    """Build a compact, readable por_que from pre-processed technical items."""
    parts: list[str] = []
    for item in technical_items[:2]:
        aspect_line = item.get("aspect_line", "").strip()
        meaning = item.get("meaning", "").strip()
        if "Regra" in aspect_line or not aspect_line:
            if item.get("title"):
                parts.append(str(item["title"]))
            continue
        if meaning:
            meaning_short = meaning.split(".")[0]
            parts.append(f"{aspect_line.rstrip('.')} — {meaning_short}")
        else:
            parts.append(aspect_line.rstrip("."))
    return "; ".join(parts) if parts else ""


def _build_human_translation(
    category_key: str,
    time_label: str,
    *,
    independent_signals: int,
    user_context: dict[str, Any],
    astro_reason: str,
    technical_items: list[dict[str, str]],
    quality_summary: str,
) -> dict[str, Any]:
    template = REALITY_TEMPLATES[category_key]
    placeholders = _build_context_placeholders(user_context)
    certainty = certainty_from_signal_count(independent_signals)
    what = apply_certainty_prefix(_personalize_template_text(template["what"], placeholders), certainty)
    scenarios = [_personalize_template_text(item, placeholders) for item in template["scenarios"][:3]]
    if category_key == "rupture" and user_context.get("father_status") == "deceased":
        scenarios = [
            item for item in scenarios
            if "pai" not in item.lower() or "mae" in item.lower()
        ] or scenarios
    primary_scenario = scenarios[0] if scenarios else CATEGORY_CONCRETE_EVENT[category_key]
    technical_block = format_technical_block(technical_items)
    avoidability = CATEGORY_AVOIDABILITY.get(category_key, "Parcialmente evitável com escolha consciente.")

    # Compact human-readable por_que (no raw codes, no duplication)
    human_por_que = _human_por_que_from_items(technical_items)
    por_que_line = f"Por quê: {human_por_que}\n" if human_por_que else ""

    # 3-5 line human summary for surface display
    human_summary = polish_portuguese(
        f"O que: {primary_scenario}\n"
        f"Quando: {time_label}\n"
        f"{por_que_line}"
        f"Evitar: {avoidability}"
    )

    # Full technical block for accordion (no "Leitura técnica:" header)
    formatted_block = polish_portuguese(
        f"Quando: {time_label}\n\n"
        f"O que acontece: {primary_scenario}\n\n"
        f"Por que (astrologia/numerologia): {astro_reason}\n\n"
        f"{quality_summary}\n\n"
        f"{technical_block}\n\n"
        f"Dá para evitar? {avoidability}\n\n"
        f"Impacto: {_personalize_template_text(template['impact'], placeholders)}\n\n"
        f"Risco: {_personalize_template_text(template['risk'], placeholders)}\n\n"
        f"Ação recomendada: {_personalize_template_text(template['action'], placeholders)}"
    )

    return {
        "what_is_happening": what,
        "primary_scenario": primary_scenario,
        "when_label": time_label,
        "astro_reason": astro_reason,
        "technical_items": technical_items,
        "technical_block": technical_block,
        "quality_summary": quality_summary,
        "avoidability_summary": avoidability,
        "what_this_may_look_like_in_real_life": scenarios[:2],
        "possible_scenarios": scenarios,
        "impact": _personalize_template_text(template["impact"], placeholders),
        "risk": _personalize_template_text(template["risk"], placeholders),
        "recommended_action": _personalize_template_text(template["action"], placeholders),
        "certainty_level": certainty,
        "certainty_label": CERTAINTY_LABELS[certainty],
        "human_summary": human_summary,
        "formatted_block": formatted_block,
    }


def format_prediction_block(event: dict[str, Any]) -> str:
    window = dict(event.get("time_window") or {})
    when = str(window.get("formatted_label") or window.get("label") or event.get("when_label") or "período em formação")
    scenario = str(event.get("primary_scenario") or (event.get("possible_scenarios") or [""])[0] or event.get("what_is_happening") or "")
    reason = str(event.get("astro_reason") or event.get("explanation") or "")
    parts = [
        f"Quando: {when}",
        f"O que acontece: {scenario}",
        f"Por que (astrologia/numerologia): {reason}",
    ]
    if event.get("quality_summary"):
        parts.append(str(event["quality_summary"]))
    if event.get("avoidability_summary"):
        parts.append(f"Dá para evitar? {event['avoidability_summary']}")
    return polish_portuguese("\n\n".join(parts).strip())


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
        time_label = _relative_timeframe(reference_date, time_window)
        if time_window is not None:
            time_window = {
                **time_window,
                "label": time_label,
                "formatted_label": time_label,
            }
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
            "time_window": time_window or {"label": time_label, "formatted_label": time_label},
            "when_label": time_label,
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
                techniques=techniques,
            ),
            "domains": sorted(
                {
                    DOMAIN_LABELS.get(str(signal["domain"]), str(signal["domain"]).replace("_", " "))
                    for signal in category_signals
                }
            ),
        }
        technical_items = build_technical_items(
            signals=category_signals,
            rule_hits=category_rule_hits,
            reference_date=reference_date,
            category_key=definition["key"],
        )
        quality_summary = build_quality_summary(
            independent_signals=independent_signals,
            probability_level=probability_level,
            techniques=techniques,
            has_peak=bool(time_window and time_window.get("peak")),
        )
        entry.update(
            _build_human_translation(
                definition["key"],
                time_label,
                independent_signals=independent_signals,
                user_context=user_context,
                astro_reason=entry["explanation"],
                technical_items=technical_items,
                quality_summary=quality_summary,
            )
        )

        # Classify and attach subtype-specific text
        subtype_key = classify_event_subtype(
            category_key=definition["key"],
            category_signals=category_signals,
            rule_hits=category_rule_hits,
            life_events=category_life_events,
            user_context=user_context,
        )
        if subtype_key:
            subtype_data = build_subtype_text(
                subtype_key=subtype_key,
                signals=category_signals,
                rule_hits=category_rule_hits,
                reference_date=reference_date,
                user_context=user_context,
                independent_signals=independent_signals,
                time_window=time_window,
            )
            entry.update(subtype_data)
            # Override avoidability with subtype-specific text when available
            if subtype_data.get("subtype_avoidability"):
                entry["avoidability_summary"] = subtype_data["subtype_avoidability"]
            # Override formatted_block with enriched subtype version if available
            if subtype_data.get("subtype_formatted_block"):
                entry["subtype_formatted_block"] = subtype_data["subtype_formatted_block"]

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
