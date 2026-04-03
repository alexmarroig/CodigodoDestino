from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime
from typing import Any

from engine.analysis import DOMAIN_LABELS

EVENT_TYPE_BY_DOMAIN = {
    "identidade": "identity_shift",
    "financeiro": "financial_recalibration",
    "comunicacao": "communication_turn",
    "familia_lar": "family_home_activation",
    "criatividade_afetos": "creative_romantic_activation",
    "saude_rotina": "health_routine_pressure",
    "relacionamentos": "relationship_transition",
    "crises_recursos": "shared_resources_change",
    "expansao_sentido": "expansion_and_learning",
    "carreira_status": "career_transition",
    "amigos_rede": "network_reconfiguration",
    "psicologico_espiritual": "inner_restructuring",
}

EVENT_TONE_TEMPLATES = {
    "carreira_status": {
        "supportive": {
            "description": "O eixo profissional ganha tracao e pede movimento mais deliberado.",
            "effect": "Tende a aparecer como visibilidade, redefinicao de metas e negociacoes mais relevantes.",
            "advice": [
                "Escolha uma prioridade profissional e sustente-a por algumas semanas.",
                "Negocie com base em fatos e nao apenas em expectativa.",
            ],
        },
        "challenging": {
            "description": "Ha pressao real sobre carreira e posicionamento publico.",
            "effect": "Isso costuma se manifestar como cobrancas, necessidade de reposicionamento e decisoes estruturais.",
            "advice": [
                "Evite agir por desgaste momentaneo.",
                "Reorganize prioridades antes de assumir novas cargas.",
            ],
        },
        "mixed": {
            "description": "Carreira e reputacao entram em fase sensivel de ajuste.",
            "effect": "O periodo mistura oportunidade e pressao, pedindo calibracao fina das escolhas.",
            "advice": [
                "Separe o que e urgencia do que e direcao de longo prazo.",
                "Revise estrategia antes de ampliar compromisso.",
            ],
        },
    },
    "relacionamentos": {
        "supportive": {
            "description": "Os vinculos entram em fase mais aberta a alinhamento e reaproximacao.",
            "effect": "Pode aparecer como conversas produtivas, redefinicao de combinados e maior clareza afetiva.",
            "advice": [
                "Fale com franqueza, mas sem transformar tudo em ultimato.",
                "Observe reciprocidade antes de aprofundar promessa.",
            ],
        },
        "challenging": {
            "description": "Relacionamentos pedem maturidade e ajuste de expectativa.",
            "effect": "A tendencia e expor desequilibrios, silencios mal resolvidos ou desgaste acumulado.",
            "advice": [
                "Converse sobre o que esta implicito.",
                "Nao tente resolver carencia com pressa.",
            ],
        },
        "mixed": {
            "description": "O campo relacional esta ativo, mas ainda instavel.",
            "effect": "Ha ao mesmo tempo desejo de aproximação e necessidade de rever limites.",
            "advice": [
                "Va para a conversa com um objetivo claro.",
                "Nao leia ambiguidade como confirmacao nem como rejeicao imediata.",
            ],
        },
    },
    "familia_lar": {
        "supportive": {
            "description": "A base emocional e domestica pede consolidacao.",
            "effect": "Surge mais vontade de organizar a casa, proteger energia e fortalecer senso de raiz.",
            "advice": [
                "Fortaleça o que te da base antes de expandir para fora.",
                "Resolva uma pendencia domestica concreta.",
            ],
        },
        "challenging": {
            "description": "Lar, familia e base emocional entram em fase de maior sensibilidade.",
            "effect": "Isso pode se traduzir em tensao familiar, desconforto com ambiente ou necessidade de reorganizar a base.",
            "advice": [
                "Nao adie uma conversa domestica importante.",
                "Proteja sua energia antes de absorver o caos de terceiros.",
            ],
        },
        "mixed": {
            "description": "A vida privada pede revisao de estrutura e afeto.",
            "effect": "O periodo exige equilibrar cuidado, limites e senso de pertencimento.",
            "advice": [
                "Nomeie o que esta faltando na base.",
                "Ajuste rotina e limites antes de buscar controle externo.",
            ],
        },
    },
    "saude_rotina": {
        "supportive": {
            "description": "Rotina e autocuidado podem ser reorganizados com mais eficiencia.",
            "effect": "A fase favorece pequenos ajustes que geram melhora consistente.",
            "advice": [
                "Simplifique a rotina antes de tentar otimizar tudo.",
                "Trate energia e descanso como parte da estrategia.",
            ],
        },
        "challenging": {
            "description": "Ha sinais de pressao sobre rotina, corpo e capacidade de sustentacao.",
            "effect": "Isso costuma aparecer como desgaste, aculo de tarefas e maior vulnerabilidade fisica ou emocional.",
            "advice": [
                "Reduza excesso de carga antes que o corpo cobre.",
                "Se algo persistir, busque suporte profissional adequado.",
            ],
        },
        "mixed": {
            "description": "O campo de saude e rotina pede recalibracao, nao improviso.",
            "effect": "O periodo oscila entre desejo de produzir mais e necessidade de respeitar limite.",
            "advice": [
                "Organize o essencial antes de aceitar novas demandas.",
                "Observe sinais recorrentes de cansaco ou irritacao.",
            ],
        },
    },
}

DEFAULT_TONE_TEMPLATE = {
    "supportive": {
        "description": "Esse dominio entra em fase de maior abertura e movimentacao.",
        "effect": "A tendencia e ganhar clareza, oportunidade ou fluxo mais favoravel.",
        "advice": [
            "Aproveite a janela sem perder criterio.",
            "Transforme impulso em decisao pratica.",
        ],
    },
    "challenging": {
        "description": "Esse dominio entra em zona de maior tensao e exigencia.",
        "effect": "O periodo costuma pedir ajuste, limite ou reposicionamento antes de avancar.",
        "advice": [
            "Nao force uma resposta antes de entender a causa real.",
            "Diminua improviso e aumente criterio.",
        ],
    },
    "mixed": {
        "description": "Esse dominio esta ativo, mas com sinais mistos.",
        "effect": "Ha convergencia suficiente para marcar o tema, mas nao para cravar um unico desfecho.",
        "advice": [
            "Observe o que ganha repeticao nas proximas semanas.",
            "Trabalhe com cenarios em vez de certeza absoluta.",
        ],
    },
}


def _parse_iso_date(value: str) -> date:
    return datetime.fromisoformat(value).date()


def _window_bounds(signals: list[dict[str, Any]]) -> dict[str, Any]:
    starts = [_parse_iso_date(signal["time_window"]["start"]) for signal in signals]
    ends = [_parse_iso_date(signal["time_window"]["end"]) for signal in signals]
    start = min(starts)
    end = max(ends)
    duration = max(1, (end - start).days + 1)
    peak = start + ((end - start) // 2)
    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "peak": peak.isoformat(),
        "duration_days": duration,
        "precision": "mixed" if duration > 30 else "day",
    }


def _probability(total_weight: float, independent_techniques: int, quality_modifier: float) -> float:
    raw = 0.28 + (total_weight / 4.3) + (max(independent_techniques - 2, 0) * 0.07)
    return round(max(0.05, min(0.97, raw * quality_modifier)), 2)


def _intensity(total_weight: float) -> str:
    if total_weight >= 2.9:
        return "high"
    if total_weight >= 2.15:
        return "medium"
    return "low"


def _pick_tone(challenging_weight: float, supportive_weight: float) -> str:
    if challenging_weight > (supportive_weight + 0.25):
        return "challenging"
    if supportive_weight > (challenging_weight + 0.25):
        return "supportive"
    return "mixed"


def _top_labels(signals: list[dict[str, Any]], limit: int = 3) -> list[str]:
    ordered = sorted(signals, key=lambda item: (-float(item["weight"]), item["label"]))
    return [item["label"] for item in ordered[:limit]]


def _event_template(domain: str, tone: str) -> dict[str, Any]:
    templates = EVENT_TONE_TEMPLATES.get(domain, DEFAULT_TONE_TEMPLATE)
    return templates.get(tone, DEFAULT_TONE_TEMPLATE["mixed"])


def _domain_conflict(supportive_weight: float, challenging_weight: float) -> bool:
    if supportive_weight == 0 or challenging_weight == 0:
        return False
    return abs(supportive_weight - challenging_weight) <= 0.35


def build_domain_analysis(analysis: dict[str, Any]) -> dict[str, Any]:
    signals = list(analysis.get("signals", []))
    profile_quality = dict(analysis.get("profile_quality", {}))
    quality_modifier = float(profile_quality.get("confidence_modifier", 0.6))
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for signal in signals:
        grouped[str(signal["domain"])].append(signal)

    domain_analysis: list[dict[str, Any]] = []
    uncertainties: list[dict[str, Any]] = []

    for domain, domain_signals in grouped.items():
        techniques = sorted({str(signal["technique"]) for signal in domain_signals})
        independent_techniques = len(techniques)
        supportive = [
            signal
            for signal in domain_signals
            if signal.get("polarity") == "supportive"
        ]
        challenging = [
            signal
            for signal in domain_signals
            if signal.get("polarity") == "challenging"
        ]
        mixed = [
            signal
            for signal in domain_signals
            if signal.get("polarity") == "mixed"
        ]
        supportive_weight = round(sum(float(signal["weight"]) for signal in supportive), 3)
        challenging_weight = round(sum(float(signal["weight"]) for signal in challenging), 3)
        mixed_weight = round(sum(float(signal["weight"]) for signal in mixed), 3)
        total_weight = round(supportive_weight + challenging_weight + mixed_weight, 3)
        strong_signals = [
            signal for signal in domain_signals if float(signal["weight"]) >= 0.68
        ]
        converged = independent_techniques >= 3 or (
            len(strong_signals) >= 2 and total_weight >= 2.25
        )
        probability = _probability(total_weight, independent_techniques, quality_modifier)
        tone = _pick_tone(challenging_weight, supportive_weight)

        domain_entry = {
            "domain": domain,
            "domain_label": DOMAIN_LABELS.get(domain, domain.replace("_", " ")),
            "signal_count": len(domain_signals),
            "independent_techniques": techniques,
            "supportive_weight": supportive_weight,
            "challenging_weight": challenging_weight,
            "mixed_weight": mixed_weight,
            "total_weight": total_weight,
            "probability": probability,
            "intensity": _intensity(total_weight),
            "tone": tone,
            "converged": converged,
            "signals": domain_signals,
            "time_window": _window_bounds(domain_signals),
        }
        domain_analysis.append(domain_entry)

        if _domain_conflict(supportive_weight, challenging_weight):
            uncertainties.append(
                {
                    "domain": domain,
                    "kind": "mixed_testimonies",
                    "message": (
                        f"{DOMAIN_LABELS.get(domain, domain)} mostra sinais a favor e contra em peso parecido."
                    ),
                    "scenario_a": "O tema avanca se houver acao organizada e dialogo com a realidade.",
                    "scenario_b": "O tema emperra se a resposta vier no impulso ou sem criterio.",
                    "observables": [
                        "repeticao do mesmo tema em conversas ou tarefas",
                        "necessidade de rever limites ou prioridades",
                    ],
                }
            )
        elif not converged and independent_techniques >= 2:
            uncertainties.append(
                {
                    "domain": domain,
                    "kind": "insufficient_convergence",
                    "message": (
                        f"{DOMAIN_LABELS.get(domain, domain)} tem sinais relevantes, mas ainda nao convergentes o bastante."
                    ),
                    "scenario_a": "O dominio se confirma se novas evidencias surgirem nas proximas semanas.",
                    "scenario_b": "O dominio perde forca se o tema nao reaparecer de forma consistente.",
                    "observables": [
                        "novos gatilhos no mesmo dominio",
                        "persistencia do desconforto ou da oportunidade",
                    ],
                }
            )

    domain_analysis.sort(
        key=lambda item: (
            not item["converged"],
            -float(item["probability"]),
            item["domain"],
        )
    )

    converged_domains = [item for item in domain_analysis if item["converged"]]
    confidence_score = (
        sum(float(item["probability"]) for item in converged_domains) / len(converged_domains)
        if converged_domains
        else 0.32 * quality_modifier
    )
    confidence_level = "high" if confidence_score >= 0.74 else "medium" if confidence_score >= 0.5 else "low"
    confidence_reason = (
        "baseado em convergencia de tecnicas independentes"
        if converged_domains
        else "evidencias ainda insuficientes para convergencia forte"
    )

    return {
        "domains": domain_analysis,
        "uncertainties": uncertainties,
        "confidence": {
            "level": confidence_level,
            "score": round(confidence_score, 2),
            "reason": confidence_reason,
            "profile_quality": profile_quality.get("code", "C"),
        },
    }


def generate_events(
    analysis: dict[str, Any],
    reference_date: date,
) -> list[dict[str, Any]]:
    domain_bundle = build_domain_analysis(analysis)
    events: list[dict[str, Any]] = []

    for rank_seed, item in enumerate(domain_bundle["domains"], start=1):
        if not item["converged"]:
            continue

        supporting_signals = [
            signal for signal in item["signals"] if signal.get("polarity") == "supportive"
        ]
        challenging_signals = [
            signal for signal in item["signals"] if signal.get("polarity") == "challenging"
        ]
        template = _event_template(item["domain"], item["tone"])
        probability = float(item["probability"])
        title = template["description"]
        cause = " + ".join(_top_labels(item["signals"]))
        counter_signals = _top_labels(
            supporting_signals if item["tone"] == "challenging" else challenging_signals
        )
        recommendations = list(template["advice"])
        tags = sorted({item["domain"], *item["independent_techniques"]})
        time_window = item["time_window"]
        event_id = f"{EVENT_TYPE_BY_DOMAIN.get(item['domain'], 'domain_activation')}_{time_window['start']}"

        events.append(
            {
                "id": event_id,
                "type": EVENT_TYPE_BY_DOMAIN.get(item["domain"], "domain_activation"),
                "event": title,
                "title": title,
                "summary": template["effect"],
                "category": item["domain"],
                "domains": [item["domain"]],
                "probability": probability,
                "intensity": item["intensity"],
                "score": probability,
                "priority": max(1, min(100, int(round(probability * 100)))),
                "confidence": probability,
                "signals": _top_labels(item["signals"], limit=5),
                "description": title,
                "cause": cause,
                "effect": template["effect"],
                "advice": " ".join(recommendations),
                "recommendations": recommendations,
                "time_window": time_window,
                "counter_signals": counter_signals,
                "drivers": [
                    {
                        "kind": signal["kind"],
                        "code": signal["technique"],
                        "weight": signal["weight"],
                        "evidence": signal["evidence"],
                    }
                    for signal in sorted(
                        item["signals"],
                        key=lambda signal: (-float(signal["weight"]), signal["label"]),
                    )[:5]
                ],
                "tags": tags,
                "context": {
                    "domain_label": item["domain_label"],
                    "independent_techniques": item["independent_techniques"],
                    "supportive_weight": item["supportive_weight"],
                    "challenging_weight": item["challenging_weight"],
                    "mixed_weight": item["mixed_weight"],
                    "profile_quality": analysis.get("profile_quality", {}).get("code", "C"),
                },
                "narrative_hint": (
                    f"{title} Causa: {cause}. Efeito esperado: {template['effect']}"
                ),
                "rank": rank_seed,
                "generated_for": reference_date.isoformat(),
            }
        )

    events.sort(
        key=lambda event: (
            event["time_window"]["start"],
            -int(event["priority"]),
            event["id"],
        )
    )
    for rank, event in enumerate(events, start=1):
        event["rank"] = rank
    return events


def summarize_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    category_counts = Counter(event["category"] for event in events)
    intensity_counts = Counter(event["intensity"] for event in events)
    top_tags = Counter(tag for event in events for tag in event.get("tags", []))

    return {
        "total": len(events),
        "categories": dict(category_counts),
        "intensity_breakdown": dict(intensity_counts),
        "top_event_ids": [event["id"] for event in events[:3]],
        "top_tags": [tag for tag, _ in top_tags.most_common(5)],
        "average_score": round(
            sum(float(event["score"]) for event in events) / len(events),
            3,
        )
        if events
        else 0.0,
        "highest_priority": max((event["priority"] for event in events), default=0),
    }
