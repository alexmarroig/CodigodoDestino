from __future__ import annotations

from datetime import date, datetime
from typing import Any

from engine.certainty import CERTAINTY_LABELS, apply_certainty_prefix, certainty_from_signal_count
from engine.date_formatting import format_date_pt, format_time_window_label
from engine.predictive_insights import build_predictive_insights, format_prediction_block

SECTION_DEFINITIONS = [
    {"id": "central_reading", "title": "Leitura central", "order": 1},
    {"id": "personality", "title": "Personalidade real", "order": 2},
    {"id": "core_wound", "title": "Ferida principal", "order": 3},
    {"id": "emotional_pattern", "title": "Padrão emocional", "order": 4},
    {"id": "relationships", "title": "Relações", "order": 5},
    {"id": "family", "title": "Família", "order": 6},
    {"id": "money", "title": "Dinheiro", "order": 7},
    {"id": "career", "title": "Carreira", "order": 8},
    {"id": "life_timeline", "title": "Linha temporal", "order": 9},
    {"id": "future_events", "title": "Eventos futuros", "order": 10},
    {"id": "critical_cycles", "title": "Ciclos críticos", "order": 11},
    {"id": "conclusion", "title": "Conclusão final", "order": 12},
]

LIFE_BANDS = [
    ("childhood", "Infância", 0, 12),
    ("adolescence", "Adolescência", 13, 19),
    ("twenties_early", "20 a 25 anos", 20, 25),
    ("late_twenties", "26 a 30 anos", 26, 30),
    ("early_thirties", "31 a 35 anos", 31, 35),
    ("late_thirties", "36 a 42 anos", 36, 42),
    ("maturity", "Maturidade", 43, 120),
]

WOUND_RULE_CODES = {
    "emotional_low",
    "emotional_cut",
    "deep_emotional_break",
    "psychological_transformation",
    "emotional_bond",
}

EMOTIONAL_RULE_CODES = {
    "emotional_low",
    "emotional_cut",
    "conflict_relationship",
    "intense_relationship",
    "psychological_transformation",
}


def _parse_birth_date(payload: dict[str, Any]) -> date | None:
    raw = payload.get("date")
    if raw is None:
        return None
    if isinstance(raw, date):
        return raw
    if hasattr(raw, "isoformat"):
        return raw
    return date.fromisoformat(str(raw))


def _age_on(reference: date, birth: date) -> int:
    years = reference.year - birth.year
    if (reference.month, reference.day) < (birth.month, birth.day):
        years -= 1
    return max(0, years)


def _sign_label(computed: dict[str, Any], planet: str) -> str | None:
    signs = computed.get("astrology", {}).get("signs", {})
    entry = signs.get(planet) or signs.get(planet.lower()) or signs.get(planet.capitalize())
    if not entry:
        return None
    return str(entry.get("sign") or entry.get("formatted") or "").strip() or None


def _context_placeholders(user_context: dict[str, Any]) -> dict[str, str]:
    status = str(user_context.get("relationship_status") or "unknown")
    partner = str(user_context.get("current_partner_role") or "unknown")
    children = user_context.get("has_children")
    partner_label = {
        "girlfriend": "sua namorada",
        "boyfriend": "seu namorado",
        "wife": "sua esposa",
        "husband": "seu marido",
        "partner": "seu parceiro",
    }.get(partner, "seu parceiro")

    status_phrase = {
        "single": "você está solteiro(a)",
        "dating": "você está namorando",
        "engaged": "você está noivo(a)",
        "married": "você está casado(a)",
        "separated": "você está separado(a)",
        "divorced": "você está divorciado(a)",
        "widowed": "você é viúvo(a)",
    }.get(status, "seu vínculo afetivo atual está em aberto")

    children_phrase = ""
    if children is True:
        children_phrase = " e tem filhos"
    elif children is False:
        children_phrase = " e não tem filhos"

    return {
        "partner_role": partner_label,
        "relationship_status": status_phrase + children_phrase,
        "living_situation": str(user_context.get("living_situation") or "").strip(),
        "current_city": str(user_context.get("current_city") or "").strip(),
    }


def _section(
    *,
    section_id: str,
    title: str,
    summary: str,
    body: str,
    certainty_level: str = "tendency",
    evidence: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "id": section_id,
        "title": title,
        "summary": summary.strip(),
        "body": body.strip(),
        "certainty_level": certainty_level,
        "certainty_label": CERTAINTY_LABELS.get(certainty_level, CERTAINTY_LABELS["tendency"]),
        "evidence": list(evidence or [])[:6],
    }


def _format_date_window(window: dict[str, Any] | None, reference_date: date | None = None) -> str:
    return format_time_window_label(window, reference_date=reference_date)


def _prediction_body(event: dict[str, Any], reference_date: date | None = None) -> str:
    if event.get("formatted_block"):
        return str(event["formatted_block"])
    patched = dict(event)
    if reference_date is not None and patched.get("time_window"):
        patched = {
            **patched,
            "time_window": {
                **dict(patched["time_window"]),
                "formatted_label": _format_date_window(patched["time_window"], reference_date),
            },
        }
    return format_prediction_block(patched)


def _strongest_predictive(predictive: dict[str, Any]) -> dict[str, Any] | None:
    events = list(predictive.get("detected_events") or [])
    if events:
        return events[0]
    watchlist = list(predictive.get("watchlist") or [])
    return watchlist[0] if watchlist else None


def _build_central_reading(
    narrative: dict[str, Any],
    predictive: dict[str, Any],
    user_context: dict[str, Any],
    reference_date: date,
) -> dict[str, Any]:
    lead = _strongest_predictive(predictive)
    placeholders = _context_placeholders(user_context)

    if lead:
        certainty = certainty_from_signal_count(lead["independent_signals"])
        when = _format_date_window(lead.get("time_window"), reference_date)
        scenario = str(lead.get("primary_scenario") or (lead.get("possible_scenarios") or [""])[0])
        summary = f"{lead['event_type']} — {when}."
        body = _prediction_body(lead, reference_date)
        if placeholders["relationship_status"]:
            body += f"\n\nContexto atual: {placeholders['relationship_status'].capitalize()}."
        if lead.get("impact"):
            body += f"\n\nImpacto: {lead['impact']}"
    elif narrative.get("text"):
        narrative_text = str(narrative.get("text") or "").strip()
        summary = narrative_text.split("\n\n")[0][:280]
        body = narrative_text[:1800]
        certainty = "tendency"
    else:
        summary = "O mapa ainda não fecha um eixo dominante com força total."
        body = (
            "Os sinais estão se organizando. Observe repetição de tema nas próximas semanas "
            "antes de tratar qualquer leitura como destino fechado."
        )
        certainty = "chance"

    evidence = []
    if lead:
        evidence.extend(lead.get("signals", [])[:3])
        evidence.extend(lead.get("rule_hits", [])[:2])
        if lead.get("astro_reason"):
            evidence.append(str(lead["astro_reason"])[:180])

    return _section(
        section_id="central_reading",
        title="Leitura central",
        summary=summary,
        body=body,
        certainty_level=certainty,
        evidence=evidence,
    )


def _build_personality(computed: dict[str, Any], numerology: dict[str, Any]) -> dict[str, Any]:
    sun = _sign_label(computed, "Sun") or _sign_label(computed, "sun")
    moon = _sign_label(computed, "Moon") or _sign_label(computed, "moon")
    asc = _sign_label(computed, "Asc") or _sign_label(computed, "asc")

    parts = []
    if sun:
        parts.append(
            f"Sol em {sun} (astrologia): você se apresenta com essa postura e precisa ser visto do seu jeito."
        )
    if moon:
        parts.append(
            f"Lua em {moon} (astrologia): por dentro, você reage com sensibilidade a abandono, controle ou excesso de exigência."
        )
    if asc:
        parts.append(
            f"Ascendente em {asc} (astrologia): na prática, as pessoas te leem assim antes de te conhecer de verdade."
        )

    life_path = numerology.get("life_path_number")
    personal_year = dict(numerology.get("personal_year") or {})
    if life_path:
        parts.append(
            f"Caminho de vida {life_path} (numerologia): repete padrão até você assumir o que não quer mais repetir."
        )
    if personal_year.get("value"):
        parts.append(
            f"Ano pessoal {personal_year['value']} (numerologia): reforça o tema central deste ciclo de vida."
        )

    body = " ".join(parts) if parts else (
        "Sem hora exata, a leitura de personalidade fica mais genérica. "
        "Ainda assim, o mapa mostra alguém que reage forte quando sente perda de controle emocional."
    )
    return _section(
        section_id="personality",
        title="Personalidade real",
        summary=parts[0] if parts else "Identidade em reconstrução.",
        body=body,
        certainty_level="tendency",
    )


def _build_core_wound(rule_hits: list[dict[str, Any]], user_context: dict[str, Any]) -> dict[str, Any]:
    wound_hits = [hit for hit in rule_hits if hit.get("code") in WOUND_RULE_CODES]
    father = user_context.get("father_status")
    mother = user_context.get("mother_status")
    father_rel = str(user_context.get("father_relationship") or "unknown")
    mother_rel = str(user_context.get("mother_relationship") or "unknown")

    lines = []
    if wound_hits:
        labels = [str(hit.get("label")) for hit in wound_hits[:2]]
        lines.append(
            "Seu mapa marca ferida emocional profunda: "
            + ", ".join(labels)
            + ". Isso não é fraqueza — é memória que ainda comanda reações."
        )
    else:
        lines.append(
            "A ferida principal não grita no mapa, mas aparece quando alguém some, muda de tom "
            "ou te coloca em segundo plano sem aviso."
        )

    if father_rel in {"distant", "conflict", "absent"} or father == "deceased":
        lines.append("Com o pai, há história de distância, peso ou figura que não sustentou como você precisava.")
    if mother_rel in {"distant", "conflict", "absent"} or mother == "deceased":
        lines.append("Com a mãe, o padrão aponta cuidado excessivo, cobrança ou ausência que ainda define limites.")

    if user_context.get("experienced_abandonment"):
        lines.append("O abandono emocional não é só passado: ele reaparece em vínculos até ser reconhecido.")

    certainty = "must" if len(wound_hits) >= 2 else "tendency"
    return _section(
        section_id="core_wound",
        title="Ferida principal",
        summary=lines[0][:200],
        body="\n\n".join(lines),
        certainty_level=certainty,
        evidence=[hit.get("label", "") for hit in wound_hits[:3]],
    )


def _build_emotional_pattern(
    analysis: dict[str, Any],
    domain_analysis: dict[str, Any],
) -> dict[str, Any]:
    domains = list(domain_analysis.get("domains") or [])
    psycho = next((d for d in domains if d.get("domain") == "psicologico_espiritual"), None)
    rule_hits = [
        hit for hit in analysis.get("rule_hits", [])
        if hit.get("code") in EMOTIONAL_RULE_CODES
    ]

    if psycho:
        summary = psycho.get("domain_label", "Emoção") + ": " + str(psycho.get("tone", "pressão emocional"))
        body = str(
            psycho.get("summary")
            or "Você alterna entre controle, silêncio e explosão quando sente que vai perder alguém ou algo importante."
        )
        certainty = "must" if psycho.get("converged") else "tendency"
    else:
        summary = "Instabilidade emocional aparece em ciclos, não o tempo todo."
        body = (
            "Quando o mapa aperta, você fecha, some ou reage forte. "
            "O padrão se repete em relação, família e trabalho até haver ruptura ou limite claro."
        )
        certainty = "tendency"

    return _section(
        section_id="emotional_pattern",
        title="Padrão emocional",
        summary=summary[:220],
        body=body,
        certainty_level=certainty,
        evidence=[hit.get("label", "") for hit in rule_hits[:3]],
    )


def _build_relationships(
    relationship: dict[str, Any],
    predictive: dict[str, Any],
    user_context: dict[str, Any],
    reference_date: date,
) -> dict[str, Any]:
    placeholders = _context_placeholders(user_context)
    status = str(user_context.get("relationship_status") or "unknown")
    rel_events = [
        e for e in (*predictive.get("detected_events", []), *predictive.get("watchlist", []))
        if e.get("category_key") in {"relationships", "rupture"}
    ]
    lead = rel_events[0] if rel_events else None

    summary = str(relationship.get("summary") or "Relações em fase de definição ou desgaste.")
    body_parts = [summary]
    if placeholders["relationship_status"]:
        body_parts.append(f"Hoje: {placeholders['relationship_status']}.")
    if lead:
        certainty = certainty_from_signal_count(lead["independent_signals"])
        body_parts.append(_prediction_body(lead, reference_date))
    else:
        certainty = "tendency"
        if status in {"separated", "divorced", "widowed"}:
            body_parts.append(
                "O mapa confirma ciclo de encerramento afetivo seguido de reconstrução lenta — "
                "não de volta automática ao que já morreu."
            )
        elif status in {"married", "engaged", "dating"}:
            body_parts.append(
                f"A relação com {placeholders['partner_role']} entra em teste de verdade: "
                "ou aprofunda compromisso ou explode em conversa que não dá mais para adiar."
            )

    return _section(
        section_id="relationships",
        title="Relações",
        summary=summary[:220],
        body="\n\n".join(body_parts),
        certainty_level=certainty if lead else "tendency",
        evidence=list(relationship.get("signals") or [])[:4],
    )


def _build_family(
    user_context: dict[str, Any],
    related_people: list[dict[str, Any]],
    predictive: dict[str, Any],
    reference_date: date,
) -> dict[str, Any]:
    father = user_context.get("father_status")
    mother = user_context.get("mother_status")
    father_rel = str(user_context.get("father_relationship") or "unknown")
    mother_rel = str(user_context.get("mother_relationship") or "unknown")
    siblings = user_context.get("has_siblings")
    adoption = user_context.get("experienced_adoption")

    family_events = [
        e for e in predictive.get("detected_events", [])
        if "familia" in " ".join(e.get("domains", [])).lower()
        or e.get("category_key") == "rupture"
    ]

    lines = []
    if father == "deceased":
        lines.append("Figura paterna ausente no físico: o mapa puxa temas de herança emocional e responsabilidade precoce.")
    elif father_rel == "conflict":
        lines.append("Conflito ativo ou recente com figura paterna — discussão que muda dinâmica familiar.")
    elif father_rel == "distant":
        lines.append("Distância emocional com o pai: afastamento que parece normalizado mas ainda pesa.")

    if mother == "deceased":
        lines.append("Perda ou ausência materna marca raiz emocional e senso de lar.")
    elif mother_rel == "conflict":
        lines.append("Tensão com a mãe: cobrança, culpa ou cuidado que virou peso.")
    elif mother_rel == "close":
        lines.append("Vínculo forte com a mãe — às vezes útil, às vezes dependência que limita autonomia.")

    if siblings is True:
        lines.append("Irmãos entram no mapa como espelho de rivalidade, comparação ou aliança.")
    if adoption:
        lines.append("História de adoção ou família recomposta: busca de pertencimento que nunca fica totalmente quieto.")

    if family_events:
        lead = family_events[0]
        lines.append(_prediction_body(lead, reference_date))

    if not lines:
        lines.append(
            "Família aparece como campo de lealdade e limite: você repete padrões até romper com o que herdou."
        )

    related_names = [p.get("name") for p in related_people if p.get("relation") in {"father", "mother", "sibling", "child"}]
    evidence = [name for name in related_names if name][:3]

    return _section(
        section_id="family",
        title="Família",
        summary=lines[0][:220],
        body="\n\n".join(lines),
        certainty_level="tendency",
        evidence=evidence,
    )


def _build_money(financial: dict[str, Any], predictive: dict[str, Any], reference_date: date) -> dict[str, Any]:
    money_events = [
        e for e in predictive.get("detected_events", [])
        if e.get("category_key") in {"career", "major_transitions"}
        or "recursos" in " ".join(e.get("domains", [])).lower()
    ]
    summary = str(financial.get("summary") or "Dinheiro e segurança em ajuste.")
    body = summary
    if financial.get("why_now"):
        body += f"\n\n{financial['why_now']}"
    if money_events:
        lead = money_events[0]
        body += "\n\n" + _prediction_body(lead, reference_date)
    certainty = "must" if financial.get("restructure_probability", 0) > 0.6 else "tendency"
    return _section(
        section_id="money",
        title="Dinheiro",
        summary=summary[:220],
        body=body,
        certainty_level=certainty,
        evidence=list(financial.get("signals") or [])[:4],
    )


def _build_career_section(
    forecast_360: dict[str, Any],
    predictive: dict[str, Any],
    reference_date: date,
) -> dict[str, Any]:
    areas = list(forecast_360.get("areas_da_vida") or [])
    career_area = next((a for a in areas if "carreira" in str(a.get("label", "")).lower()), None)
    career_events = [e for e in predictive.get("detected_events", []) if e.get("category_key") == "career"]

    if career_area:
        summary = str(career_area.get("what_tends_to_happen") or career_area.get("label"))
        peak_dates = [format_date_pt(item) for item in list(career_area.get("peak_dates") or [])[:2]]
        when_clause = f" Período mais sensível: {', '.join(peak_dates)}." if peak_dates else ""
        body = f"{summary}\n\n{career_area.get('why_now', '')}{when_clause}".strip()
        certainty = "must" if career_area.get("status") == "active" else "tendency"
    elif career_events:
        lead = career_events[0]
        summary = lead["event_type"]
        body = _prediction_body(lead, reference_date)
        certainty = certainty_from_signal_count(lead["independent_signals"])
    else:
        summary = "Carreira em observação — sem virada forte fechada agora."
        body = "O trabalho pede consistência. Grandes saltos dependem de janela que ainda está se formando."
        certainty = "chance"

    return _section(
        section_id="career",
        title="Carreira",
        summary=summary[:220],
        body=body,
        certainty_level=certainty,
    )


def _age_band_label(age: int) -> str:
    for _key, label, start, end in LIFE_BANDS:
        if start <= age <= end:
            return label
    return "Maturidade"


def _build_life_timeline(
    *,
    birth_date: date | None,
    reference_date: date,
    life_story: dict[str, Any],
    timeline: dict[str, Any],
    user_context: dict[str, Any],
    life_episodes: list[dict[str, Any]],
) -> dict[str, Any]:
    current_age = _age_on(reference_date, birth_date) if birth_date else None
    chapters = list(life_story.get("chapters") or [])
    periods = list(timeline.get("periods") or [])

    band_entries: dict[str, list[str]] = {band[0]: [] for band in LIFE_BANDS}

    context_events = []
    if user_context.get("major_loss_notes"):
        context_events.append(f"Perda declarada: {user_context['major_loss_notes']}")
    if user_context.get("major_trauma_notes"):
        context_events.append(f"Trauma declarado: {user_context['major_trauma_notes']}")
    if user_context.get("marked_separation"):
        context_events.append("Separação marcante já vivida — o mapa repete o medo de recomeço.")
    if user_context.get("experienced_betrayal"):
        context_events.append("Traição no passado — confiança demora a voltar.")
    if user_context.get("city_change"):
        context_events.append("Mudança de cidade alterou identidade e rede de apoio.")
    if user_context.get("country_change"):
        context_events.append("Mudança de país: ruptura de raiz e reconstrução de vida do zero.")
    if user_context.get("important_death"):
        context_events.append(f"Morte importante: {user_context['important_death']}")

    for note in context_events:
        if current_age is not None:
            if current_age <= 19:
                band_entries["adolescence"].append(note)
            elif current_age <= 30:
                band_entries["late_twenties"].append(note)
            else:
                band_entries["early_thirties"].append(note)
        else:
            band_entries["adolescence"].append(note)

    for chapter in chapters[:8]:
        headline = str(chapter.get("headline") or chapter.get("title") or "").strip()
        if not headline:
            continue
        age_hint = chapter.get("age")
        if isinstance(age_hint, (int, float)):
            band_key = next((b[0] for b in LIFE_BANDS if b[2] <= int(age_hint) <= b[3]), "maturity")
        elif current_age is not None:
            band_key = next((b[0] for b in LIFE_BANDS if b[2] <= current_age <= b[3]), "maturity")
        else:
            band_key = "maturity"
        band_entries[band_key].append(headline)

    for period in periods:
        if period.get("granularity") != "month":
            continue
        label = str(period.get("headline") or period.get("summary") or "").strip()
        if label and current_age is not None:
            band_key = next((b[0] for b in LIFE_BANDS if b[2] <= current_age <= b[3]), "maturity")
            band_entries[band_key].append(f"[Futuro próximo] {label}")
        if len([p for p in periods if p.get("granularity") == "month"]) > 0:
            break

    for episode in life_episodes[:4]:
        title = str(episode.get("title") or episode.get("headline") or "").strip()
        if title:
            band_entries["maturity"].append(title)

    lines = []
    for key, title, _start, _end in LIFE_BANDS:
        items = band_entries[key]
        if not items:
            if key == "childhood":
                lines.append(f"**{title}:** afastamento emocional precoce ou ambiente que exigiu amadurecer cedo.")
            continue
        lines.append(f"**{title}:**")
        for item in items[:3]:
            lines.append(f"• {item}")

    if current_age is not None:
        saturn_return = 27 <= current_age <= 31
        if saturn_return:
            lines.append(
                "**Retorno de Saturno (agora):** fase inevitável de ruptura e reconstrução — "
                "relações falsas caem, identidade antiga não cabe mais."
            )

    body = "\n".join(lines) if lines else (
        "A linha temporal pede mais dados de vida para cravar passado. "
        "O futuro próximo ainda aparece por ciclos mensais na seção de eventos."
    )
    summary = f"Você está na faixa de {_age_band_label(current_age)}." if current_age is not None else "Linha de vida em leitura."

    return _section(
        section_id="life_timeline",
        title="Linha temporal",
        summary=summary,
        body=body,
        certainty_level="tendency",
    )


def _build_future_events(predictive: dict[str, Any], reference_date: date) -> dict[str, Any]:
    events = list(predictive.get("detected_events") or [])[:5]
    if not events:
        return _section(
            section_id="future_events",
            title="Eventos futuros",
            summary="Nenhum evento forte o suficiente para cravar agora.",
            body="Observe repetição de tema nas próximas semanas.",
            certainty_level="chance",
        )

    lines = []
    max_certainty = "chance"
    order = {"chance": 0, "tendency": 1, "must": 2, "will": 3}
    for event in events:
        certainty = certainty_from_signal_count(event["independent_signals"])
        if order[certainty] > order[max_certainty]:
            max_certainty = certainty
        lines.append(_prediction_body(event, reference_date))

    return _section(
        section_id="future_events",
        title="Eventos futuros",
        summary=events[0]["event_type"],
        body="\n\n".join(lines),
        certainty_level=max_certainty,
        evidence=events[0].get("signals", [])[:4],
    )


def _build_critical_cycles(
    *,
    birth_date: date | None,
    reference_date: date,
    turning_points: list[dict[str, Any]],
    forecast_360: dict[str, Any],
    numerology: dict[str, Any],
) -> dict[str, Any]:
    lines = []
    for point in turning_points[:6]:
        lines.append(f"• {format_date_pt(point.get('date'))}: {point.get('headline', point.get('summary', 'Virada'))}")

    critical = list(forecast_360.get("critical_periods") or [])
    for period in critical[:3]:
        lines.append(f"• Período crítico: {period.get('label', period.get('summary', ''))}")

    personal_year = numerology.get("personal_year", {})
    py_value = personal_year.get("value")
    if py_value == 9:
        lines.append("• Ano pessoal 9: encerramentos, perdas e desapego forçado.")
    elif py_value == 1:
        lines.append("• Ano pessoal 1: recomeço, nova identidade, reconstrução.")

    if birth_date:
        age = _age_on(reference_date, birth_date)
        if 27 <= age <= 31:
            lines.append("• Retorno de Saturno: destruição de estruturas falsas e amadurecimento forçado.")
        if 36 <= age <= 42:
            lines.append("• Ciclo de crise de meia-idade emocional: o que não serve mais precisa cair.")

    body = "\n".join(lines) if lines else "Ciclos críticos ainda em formação — sem pico único dominante."
    return _section(
        section_id="critical_cycles",
        title="Ciclos críticos",
        summary=lines[0].lstrip("• ")[:220] if lines else "Observe datas-chave.",
        body=body,
        certainty_level="must" if len(turning_points) >= 3 else "tendency",
    )


def _build_conclusion(sections: list[dict[str, Any]], predictive: dict[str, Any], reference_date: date) -> dict[str, Any]:
    lead = _strongest_predictive(predictive)
    central = next((s for s in sections if s["id"] == "central_reading"), None)
    future = next((s for s in sections if s["id"] == "future_events"), None)

    parts = []
    if central:
        parts.append(central["summary"])
    if lead:
        certainty = certainty_from_signal_count(lead["independent_signals"])
        parts.append(
            f"O eixo mais forte agora: {lead['event_type']} "
            f"{_format_date_window(lead.get('time_window'), reference_date)}."
        )
    if future:
        parts.append(future["summary"])

    body = (
        "Seu mapa não pede otimismo vazio. Ele aponta ruptura, escolha e reconstrução. "
        "O que se repete na sua vida não é acaso — é padrão. "
        "A próxima virada exige decisão antes que o contexto decida por você."
    )
    if lead:
        certainty = certainty_from_signal_count(lead["independent_signals"])
        body = apply_certainty_prefix(
            f"O destino mais provável agora passa por {lead['event_type'].lower()}. "
            "Ignorar isso custa tempo, dinheiro e paz.",
            certainty,
        )

    return _section(
        section_id="conclusion",
        title="Conclusão final",
        summary=" ".join(parts)[:280] if parts else "Destino em movimento — leia as seções anteriores como um só fio.",
        body=body,
        certainty_level=lead and certainty_from_signal_count(lead["independent_signals"]) or "tendency",
    )


def build_destiny_sections(
    *,
    payload: dict[str, Any],
    computed: dict[str, Any],
    analysis: dict[str, Any],
    narrative: dict[str, Any],
    forecast_360: dict[str, Any],
    timeline: dict[str, Any],
    life_episodes: list[dict[str, Any]],
    turning_points: list[dict[str, Any]],
    reference_date: date,
) -> list[dict[str, Any]]:
    user_context = dict(analysis.get("user_context") or payload.get("user_context") or {})
    related_people = list(analysis.get("related_people") or payload.get("related_people") or [])
    predictive = dict(analysis.get("predictive_insights") or {})
    if not predictive.get("detected_events") and not predictive.get("watchlist"):
        predictive = build_predictive_insights(analysis, reference_date=reference_date)

    domain_analysis = dict(analysis.get("domain_analysis") or {})
    birth_date = _parse_birth_date(payload)
    numerology = dict(computed.get("numerology") or {})

    sections: list[dict[str, Any]] = []

    sections.append(_build_central_reading(narrative, predictive, user_context, reference_date))
    sections.append(_build_personality(computed, numerology))
    sections.append(_build_core_wound(list(analysis.get("rule_hits") or []), user_context))
    sections.append(_build_emotional_pattern(analysis, domain_analysis))
    sections.append(
        _build_relationships(
            dict(analysis.get("relationship_analysis") or {}),
            predictive,
            user_context,
            reference_date,
        )
    )
    sections.append(_build_family(user_context, related_people, predictive, reference_date))
    sections.append(_build_money(dict(analysis.get("financial_analysis") or {}), predictive, reference_date))
    sections.append(_build_career_section(forecast_360, predictive, reference_date))
    sections.append(
        _build_life_timeline(
            birth_date=birth_date,
            reference_date=reference_date,
            life_story=dict(analysis.get("life_story") or {}),
            timeline=timeline,
            user_context=user_context,
            life_episodes=life_episodes,
        )
    )
    sections.append(_build_future_events(predictive, reference_date))
    sections.append(
        _build_critical_cycles(
            birth_date=birth_date,
            reference_date=reference_date,
            turning_points=turning_points,
            forecast_360=forecast_360,
            numerology=numerology,
        )
    )
    sections.append(_build_conclusion(sections, predictive, reference_date))

    for index, definition in enumerate(SECTION_DEFINITIONS):
        if index < len(sections):
            sections[index]["order"] = definition["order"]

    return sections
