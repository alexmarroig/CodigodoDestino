from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from typing import Any

from astro.time import convert_with_metadata
from engine.analysis import THEME_MAP, build_multilayer_analysis
from engine.date_formatting import format_date_pt, format_month_range_pt, format_month_year_pt
from engine.events import build_domain_analysis, generate_events
from engine.rules_engine import build_specialized_insights
from numerologia.core import life_path_number, personal_year

AREA_DEFINITIONS = [
    {"key": "relacionamento", "label": "Relacionamentos", "houses": [5, 7], "domains": ["relacionamentos", "criatividade_afetos"]},
    {"key": "amizades", "label": "Amizades", "houses": [11], "domains": ["amigos_rede"]},
    {"key": "familia", "label": "Familia", "houses": [4], "domains": ["familia_lar"]},
    {"key": "carreira", "label": "Carreira", "houses": [10], "domains": ["carreira_status"]},
    {"key": "saude", "label": "Saude", "houses": [6], "domains": ["saude_rotina"]},
    {"key": "viagens", "label": "Viagens", "houses": [3, 9], "domains": ["expansao_sentido", "comunicacao"]},
    {"key": "transicoes", "label": "Transicoes", "houses": [1, 8, 12], "domains": ["identidade", "crises_recursos", "psicologico_espiritual"]},
    {"key": "financas", "label": "Financas", "houses": [2, 8], "domains": ["financeiro", "crises_recursos"]},
]

AREA_ADVICE = {
    "relacionamento": "Observe quem se aproxima, quem se afasta e onde a reciprocidade realmente existe.",
    "amizades": "Rede boa se fortalece com troca real, nao so com presenca ocasional.",
    "familia": "Organize a base antes de expandir outras frentes.",
    "carreira": "Decisoes estruturais pedem mais estrategia do que impulso.",
    "saude": "Respeite ritmo, descanso e sinais recorrentes do corpo e da rotina.",
    "viagens": "Movimento, estudo e deslocamentos ganham mais sentido quando tem direcao clara.",
    "transicoes": "Aceite que algumas viradas pedem desapego antes de abertura.",
    "financas": "Nao trate ajuste financeiro como derrota; trate como reposicionamento.",
}

HOUSE_LABELS = {
    1: "Casa 1 - Identidade",
    2: "Casa 2 - Dinheiro e valor",
    3: "Casa 3 - Movimento e comunicacao",
    4: "Casa 4 - Familia e base",
    5: "Casa 5 - Afeto e criatividade",
    6: "Casa 6 - Rotina e saude",
    7: "Casa 7 - Parcerias",
    8: "Casa 8 - Viradas e recursos compartilhados",
    9: "Casa 9 - Viagens e expansao",
    10: "Casa 10 - Carreira e status",
    11: "Casa 11 - Amigos e rede",
    12: "Casa 12 - Inconsciente e encerramentos",
}

HOUSE_DOMAIN_MAP = {domain: house for house, domain in THEME_MAP.items()}
AREA_BY_HOUSE = {
    house: [area["key"] for area in AREA_DEFINITIONS if house in area["houses"]]
    for house in range(1, 13)
}


def _add_months(anchor: date, months: int) -> date:
    month_index = (anchor.month - 1) + months
    year = anchor.year + (month_index // 12)
    month = (month_index % 12) + 1
    day = min(anchor.day, 28)
    return date(year, month, day)


def generate_timeline(reference_date: date) -> list[dict[str, Any]]:
    periods: list[dict[str, Any]] = []

    for index in range(12):
        start = _add_months(reference_date, index)
        next_start = _add_months(reference_date, index + 1)
        periods.append(
            {
                "period_key": f"m{index + 1}",
                "label": format_month_year_pt(start),
                "granularity": "month",
                "horizon": "short" if index < 3 else "mid",
                "start": start,
                "end": next_start - timedelta(days=1),
            }
        )

    for index in range(4):
        start = _add_months(reference_date, 12 + (index * 3))
        next_start = _add_months(reference_date, 12 + ((index + 1) * 3))
        periods.append(
            {
                "period_key": f"q{index + 1}",
                "label": format_month_range_pt(start, next_start - timedelta(days=1)),
                "granularity": "quarter",
                "horizon": "long",
                "start": start,
                "end": next_start - timedelta(days=1),
            }
        )

    return periods


def _status_rank(status: str) -> int:
    return {"active": 3, "watch": 2, "quiet": 1}.get(status, 0)


def _status_phrase(status: str, intensity: str) -> str:
    if status == "active":
        return "entra em movimento claro" if intensity != "high" else "ganha forca concreta"
    if status == "watch":
        return "comeca a se desenhar"
    return "fica mais silencioso"


def _headline_from_period(period_label: str, coverage: list[dict[str, Any]]) -> str:
    active = [item for item in coverage if item["status"] == "active"]
    watch = [item for item in coverage if item["status"] == "watch"]
    ranked = sorted(active or watch, key=lambda item: (-float(item["probability"]), item["key"]))
    if not ranked:
        return f"{period_label}: o periodo segue sem convergencia forte."
    lead = ranked[0]
    return f"{period_label}: {lead['label'].lower()} {_status_phrase(lead['status'], lead['intensity'])}."


def _midpoint_date(start: str, end: str) -> str:
    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end)
    return (start_date + ((end_date - start_date) // 2)).isoformat()


def _dedupe_strings(values: list[str], limit: int = 6) -> list[str]:
    seen: list[str] = []
    for value in values:
        cleaned = str(value).strip()
        if not cleaned or cleaned in seen:
            continue
        seen.append(cleaned)
        if len(seen) >= limit:
            break
    return seen


def _build_house_summary(house: int, domain_label: str, status: str, label: str) -> str:
    base = HOUSE_LABELS[house]
    if status == "active":
        return f"{base} entra em fase forte em {label}, puxando {domain_label} com consequência prática."
    return f"{base} fica em observação em {label}, com sinais parciais em {domain_label}."


def _build_period_house_activity(period_domains: list[dict[str, Any]], period_label: str) -> list[dict[str, Any]]:
    activities: list[dict[str, Any]] = []
    for domain in period_domains:
        house = HOUSE_DOMAIN_MAP.get(domain["domain"])
        if house is None:
            continue
        status = "active" if domain["converged"] else "watch"
        activities.append(
            {
                "house": house,
                "domain": domain["domain"],
                "domain_label": domain["domain_label"],
                "status": status,
                "probability": round(float(domain["probability"]), 2),
                "confidence": "high" if domain["converged"] else "medium",
                "signals": [signal["label"] for signal in domain["signals"][:4]],
                "time_window": domain["time_window"],
                "summary": _build_house_summary(house, domain["domain_label"], status, period_label),
                "tone": domain["tone"],
            }
        )
    return activities


def _build_period_result(
    *,
    period: dict[str, Any],
    payload: dict[str, Any],
    natal_ephemeris: dict[str, Any],
    natal_aspects: list[dict[str, Any]],
    profile_quality: dict[str, Any],
) -> dict[str, Any]:
    analysis_payload = dict(payload)
    analysis_payload["reference_date"] = period["start"].isoformat()

    numerology = {
        "birth_date": payload["date"],
        "life_path_number": life_path_number(payload["date"]),
        "personal_year": personal_year(payload["date"], period["start"].isoformat()),
    }
    utc_metadata = convert_with_metadata(
        payload["date"],
        profile_quality["effective_time"],
        payload["timezone"],
    )
    analysis = build_multilayer_analysis(
        payload=analysis_payload,
        utc_metadata={
            "input_local": {
                "date": utc_metadata.input_local["date"],
                "time": utc_metadata.input_local["time"],
                "timezone": utc_metadata.input_local["timezone"],
            },
            "utc_datetime": utc_metadata.utc_datetime,
            "offset_applied": utc_metadata.offset_applied,
            "is_dst": utc_metadata.is_dst,
        },
        natal_ephemeris=natal_ephemeris,
        natal_aspects=natal_aspects,
        numerology=numerology,
        reference_date=period["start"],
        profile_quality=profile_quality,
    )
    specialized = build_specialized_insights(analysis)
    analysis["rule_hits"] = specialized["rule_hits"]
    analysis["relationship_analysis"] = specialized["relationship"]
    analysis["financial_analysis"] = specialized["financial"]
    analysis["purpose_analysis"] = specialized["purpose"]
    domain_bundle = build_domain_analysis(analysis)
    events = generate_events(analysis, period["start"])
    house_activity = _build_period_house_activity(domain_bundle["domains"], period["label"])
    strongest_coverage = max(
        domain_bundle["coverage"],
        key=lambda item: (_status_rank(item["status"]), float(item["probability"])),
        default=None,
    )
    turning_point_score = round(
        sum(float(item["probability"]) for item in domain_bundle["coverage"] if item["status"] == "active")
        + (len([item for item in domain_bundle["domains"] if item["converged"]]) * 0.18)
        + (len(events) * 0.07),
        2,
    )

    return {
        "period_key": period["period_key"],
        "label": period["label"],
        "granularity": period["granularity"],
        "horizon": period["horizon"],
        "start": period["start"].isoformat(),
        "end": period["end"].isoformat(),
        "peak": (
            (strongest_coverage.get("time_window") or {}).get("peak")
            if strongest_coverage
            else _midpoint_date(period["start"].isoformat(), period["end"].isoformat())
        ),
        "signals": _dedupe_strings(
            [signal for item in domain_bundle["coverage"] for signal in item.get("signals", [])],
            limit=8,
        ),
        "coverage": domain_bundle["coverage"],
        "domains": domain_bundle["domains"],
        "houses": house_activity,
        "confidence": domain_bundle["confidence"],
        "events": events,
        "turning_point_score": turning_point_score,
        "special_forecasts": {
            "relacionamento": specialized["relationship"],
            "financas": specialized["financial"],
            "purpose": specialized["purpose"],
        },
        "headline": _headline_from_period(period["label"], domain_bundle["coverage"]),
    }


def analyze_timeline(
    *,
    payload: dict[str, Any],
    natal_ephemeris: dict[str, Any],
    natal_aspects: list[dict[str, Any]],
    profile_quality: dict[str, Any],
    reference_date: date,
) -> list[dict[str, Any]]:
    periods = generate_timeline(reference_date)
    return [
        _build_period_result(
            period=period,
            payload=payload,
            natal_ephemeris=natal_ephemeris,
            natal_aspects=natal_aspects,
            profile_quality=profile_quality,
        )
        for period in periods
    ]


def _peak_dates(entries: list[dict[str, Any]]) -> list[str]:
    seen: list[str] = []
    for entry in sorted(entries, key=lambda item: (-float(item["probability"]), item["start"])):
        peak = (entry.get("time_window") or {}).get("peak")
        if peak and peak not in seen:
            seen.append(peak)
        if len(seen) == 3:
            break
    return seen


def _horizon_snapshot(entries: list[dict[str, Any]], label: str) -> dict[str, Any]:
    if not entries:
        return {
            "status": "quiet",
            "summary": f"{label} sem ativacao forte neste horizonte.",
            "period_label": None,
            "peak_date": None,
            "probability": 0.0,
        }

    strongest = max(entries, key=lambda item: (_status_rank(item["status"]), float(item["probability"])))
    peak_date = (strongest.get("time_window") or {}).get("peak")
    return {
        "status": strongest["status"],
        "summary": strongest["summary"],
        "period_label": strongest["label"],
        "peak_date": peak_date,
        "probability": round(float(strongest["probability"]), 2),
    }


def _aggregate_area_forecasts(timeline_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for period in timeline_results:
        special_forecasts = dict(period.get("special_forecasts") or {})
        for house_entry in period["houses"]:
            for area_key in AREA_BY_HOUSE.get(int(house_entry["house"]), []):
                special_entry = dict(special_forecasts.get(area_key, {}))
                grouped[area_key].append(
                    {
                        "house": house_entry["house"],
                        "status": house_entry["status"],
                        "probability": house_entry["probability"],
                        "confidence": house_entry["confidence"],
                        "summary": house_entry["summary"],
                        "signals": list(house_entry.get("signals", [])),
                        "time_window": house_entry["time_window"],
                        "label": period["label"],
                        "start": period["start"],
                        "end": period["end"],
                        "peak": period["peak"],
                        "period_key": period["period_key"],
                        "granularity": period["granularity"],
                        "horizon": period["horizon"],
                        "special": special_entry,
                        "turning_point_score": period.get("turning_point_score", 0.0),
                    }
                )

    forecasts: list[dict[str, Any]] = []
    for area in AREA_DEFINITIONS:
        entries = grouped.get(area["key"], [])
        strongest = max(entries, key=lambda item: (_status_rank(item["status"]), float(item["probability"])), default=None)
        strongest_special = dict((strongest or {}).get("special") or {})
        short_entries = [entry for entry in entries if entry["horizon"] == "short"]
        mid_entries = [entry for entry in entries if entry["granularity"] == "month"]
        long_entries = [entry for entry in entries if entry["horizon"] == "long"]
        timeline_hits = [
            {
                "period": entry["label"],
                "period_key": entry["period_key"],
                "status": entry["status"],
                "probability": round(float(entry["probability"]), 2),
                "summary": entry.get("special", {}).get("summary") or entry["summary"],
                "peak_date": (entry.get("time_window") or {}).get("peak") or entry.get("peak"),
                "house": entry["house"],
                "granularity": entry["granularity"],
                "horizon": entry["horizon"],
            }
            for entry in entries
        ]
        counter_signals = _dedupe_strings(
            [
                entry["summary"]
                for entry in entries
                if strongest
                and (
                    entry["status"] != strongest["status"]
                    or float(entry["probability"]) < max(0.0, float(strongest["probability"]) - 0.15)
                )
            ],
            limit=3,
        )
        forecasts.append(
            {
                "key": area["key"],
                "label": area["label"],
                "status": strongest["status"] if strongest else "quiet",
                "probability": round(float(strongest["probability"]), 2) if strongest else 0.0,
                "confidence": strongest["confidence"] if strongest else "low",
                "short_term": _horizon_snapshot(short_entries, area["label"]),
                "mid_term": _horizon_snapshot(mid_entries, area["label"]),
                "long_term": _horizon_snapshot(long_entries, area["label"]),
                "peak_dates": _peak_dates(entries),
                "what_tends_to_happen": (
                    strongest_special.get("summary")
                    or (strongest["summary"] if strongest else f"{area['label']} fica sem tendencia forte definida por enquanto.")
                ),
                "why_now": (
                    strongest_special.get("why_now")
                    or (
                        f"As casas {', '.join(str(house) for house in area['houses'])} ganharam mais movimento, "
                        f"com foco principal em casa {strongest['house']}."
                        if strongest
                        else "Sem convergencia tecnica suficiente neste momento."
                    )
                ),
                "advice": strongest_special.get("advice") or AREA_ADVICE[area["key"]],
                "signals": strongest_special.get("signals") or (strongest or {}).get("signals", []),
                "counter_signals": counter_signals,
                "special_focus": strongest_special or None,
                "timeline_hits": timeline_hits,
            }
        )

    return forecasts


def _aggregate_house_forecasts(timeline_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)

    for period in timeline_results:
        for house_entry in period["houses"]:
            house = int(house_entry["house"])
            grouped[house].append(
                {
                    "house": house,
                    "period_key": period["period_key"],
                    "label": period["label"],
                    "start": period["start"],
                    "end": period["end"],
                    "granularity": period["granularity"],
                    "horizon": period["horizon"],
                    "status": house_entry["status"],
                    "probability": round(float(house_entry["probability"]), 2),
                    "summary": house_entry["summary"],
                    "signals": list(house_entry.get("signals", [])),
                    "time_window": house_entry["time_window"],
                    "tone": house_entry["tone"],
                }
            )

    houses: list[dict[str, Any]] = []
    for house in range(1, 13):
        entries = grouped.get(house, [])
        strongest = max(entries, key=lambda item: (_status_rank(item["status"]), float(item["probability"])), default=None)
        houses.append(
            {
                "house": house,
                "label": HOUSE_LABELS[house],
                "domains": [THEME_MAP[house]],
                "status": strongest["status"] if strongest else "quiet",
                "probability": round(float(strongest["probability"]), 2) if strongest else 0.0,
                "confidence": "high" if strongest and strongest["status"] == "active" else "medium" if strongest else "low",
                "short_term": _horizon_snapshot([entry for entry in entries if entry["horizon"] == "short"], HOUSE_LABELS[house]),
                "mid_term": _horizon_snapshot([entry for entry in entries if entry["granularity"] == "month"], HOUSE_LABELS[house]),
                "long_term": _horizon_snapshot([entry for entry in entries if entry["horizon"] == "long"], HOUSE_LABELS[house]),
                "timeline_hits": [
                    {
                        "period": entry["label"],
                        "period_key": entry["period_key"],
                        "status": entry["status"],
                        "probability": round(float(entry["probability"]), 2),
                        "summary": entry["summary"],
                        "peak_date": (entry.get("time_window") or {}).get("peak"),
                    }
                    for entry in entries
                ],
                "peak_dates": _peak_dates(entries),
                "what_tends_to_happen": strongest["summary"] if strongest else f"{HOUSE_LABELS[house]} fica mais silenciosa neste ciclo.",
                "reading": (
                    f"{HOUSE_LABELS[house]} tende a ficar mais forte no ciclo, puxando {THEME_MAP[house].replace('_', ' ')} para o primeiro plano."
                    if strongest
                    else f"{HOUSE_LABELS[house]} segue mais quieta, sem um gatilho forte e continuo neste periodo."
                ),
                "signals": (strongest or {}).get("signals", []),
            }
        )

    return houses


def _build_life_episodes(area_forecasts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    episodes: list[dict[str, Any]] = []

    for area in area_forecasts:
        ordered_hits = [hit for hit in area["timeline_hits"] if hit["status"] != "quiet"]
        if not ordered_hits:
            continue

        clusters: list[list[dict[str, Any]]] = []
        current_cluster: list[dict[str, Any]] = []
        previous_period_key: str | None = None
        for hit in ordered_hits:
            current_prefix = str(hit["period_key"])[0]
            previous_prefix = previous_period_key[0] if previous_period_key else None
            contiguous = (
                previous_period_key is not None
                and current_prefix == previous_prefix
                and abs(int(str(hit["period_key"])[1:]) - int(str(previous_period_key)[1:])) <= 1
            )
            if not current_cluster or contiguous:
                current_cluster.append(hit)
            else:
                clusters.append(current_cluster)
                current_cluster = [hit]
            previous_period_key = str(hit["period_key"])
        if current_cluster:
            clusters.append(current_cluster)

        for cluster in clusters:
            first_hit = cluster[0]
            last_hit = cluster[-1]
            strongest = max(cluster, key=lambda item: (_status_rank(item["status"]), float(item["probability"])))
            cluster_peaks = _dedupe_strings(
                [str(hit.get("peak_date") or "") for hit in cluster if hit.get("peak_date")],
                limit=3,
            )
            episodes.append(
                {
                    "id": f"{area['key']}-{first_hit['period_key']}",
                    "title": f"{area['label']} entra em capitulo ativo",
                    "domain": area["key"],
                    "start": first_hit["period"],
                    "end": last_hit["period"],
                    "peak": cluster_peaks[0] if cluster_peaks else None,
                    "arc": "comeco -> intensificacao -> virada -> estabilizacao",
                    "summary": strongest["summary"],
                    "key_dates": cluster_peaks,
                }
            )

    episodes.sort(key=lambda item: (item["start"], item["domain"]))
    return episodes[:8]


def _build_turning_points(timeline_results: list[dict[str, Any]], area_forecasts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    turning_points: list[dict[str, Any]] = []

    ranked_periods = sorted(
        [period for period in timeline_results if float(period.get("turning_point_score", 0.0)) > 0],
        key=lambda item: (-float(item["turning_point_score"]), item["start"]),
    )
    for period in ranked_periods[:8]:
        lead = max(
            period["coverage"],
            key=lambda item: (_status_rank(item["status"]), float(item["probability"])),
            default=None,
        )
        if not lead:
            continue
        turning_points.append(
            {
                "date": period["peak"],
                "domain": lead["key"],
                "label": lead["label"],
                "probability": round(min(0.97, float(lead["probability"]) + (float(period["turning_point_score"]) * 0.03)), 2),
                "headline": lead["headline"] if "headline" in lead else f"{lead['label']} ganha ponto de virada",
                "summary": lead["summary"],
            }
        )

    for area in area_forecasts:
        for peak_date in area["peak_dates"][:1]:
            turning_points.append(
                {
                    "date": peak_date,
                    "domain": area["key"],
                    "label": area["label"],
                    "probability": round(float(area["probability"]), 2),
                    "headline": f"{area['label']} ganha pico de movimento",
                    "summary": area["what_tends_to_happen"],
                }
            )

    turning_points.sort(key=lambda item: (-float(item["probability"]), item["date"]))
    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for item in turning_points:
        marker = (item["domain"], item["date"])
        if marker in seen:
            continue
        seen.add(marker)
        deduped.append(item)
        if len(deduped) == 8:
            break
    return deduped


def _build_purpose_forecast(timeline_results: list[dict[str, Any]]) -> dict[str, Any]:
    purpose_entries = [
        dict(period.get("special_forecasts", {}).get("purpose") or {})
        for period in timeline_results
        if period.get("special_forecasts", {}).get("purpose")
    ]
    if not purpose_entries:
        return {
            "summary": "O proposito ainda nao apareceu com densidade suficiente para uma leitura mais fina.",
            "current_focus": "O ciclo atual ainda esta mais reativo do que direcional.",
            "long_arc": "Vale observar repeticao de temas antes de tirar conclusoes maiores.",
            "focus_domains": [],
            "evidence": [],
        }

    strongest = purpose_entries[0]
    focus_counts: dict[str, int] = defaultdict(int)
    evidence: list[str] = []
    for entry in purpose_entries:
        for domain in entry.get("focus_domains", [])[:2]:
            focus_counts[str(domain)] += 1
        for item in entry.get("evidence", [])[:3]:
            if item not in evidence:
                evidence.append(item)

    ranked_domains = sorted(focus_counts, key=lambda key: (-focus_counts[key], key))
    return {
        "summary": strongest.get("summary"),
        "current_focus": strongest.get("current_focus"),
        "long_arc": strongest.get("long_arc"),
        "focus_domains": ranked_domains[:3] or strongest.get("focus_domains", []),
        "evidence": evidence[:5],
    }


def _build_overview(area_forecasts: list[dict[str, Any]], turning_points: list[dict[str, Any]]) -> str:
    ranked = sorted(area_forecasts, key=lambda item: (_status_rank(item["status"]), float(item["probability"])), reverse=True)
    top = [item["label"].lower() for item in ranked[:3] if item["status"] != "quiet"]
    if not top:
        return "Os proximos meses seguem mais silenciosos, com movimentos graduais e sem um eixo dominante forte."

    turning = turning_points[0]["date"] if turning_points else None
    head = ", ".join(top)
    if turning:
        return f"Os próximos meses concentram movimento em {head}, com virada mais sensível em torno de {format_date_pt(turning)}."
    return f"Os próximos meses concentram movimento em {head}, exigindo leitura por etapas e não por um único evento."


def _build_timeline_horizon_summary(
    area_forecasts: list[dict[str, Any]],
    horizon_key: str,
    label: str,
) -> dict[str, Any]:
    horizon_entries = []
    for area in area_forecasts:
        horizon = dict(area.get(horizon_key) or {})
        horizon_entries.append(
            {
                "label": area["label"],
                "status": horizon.get("status", "quiet"),
                "probability": float(horizon.get("probability", 0.0)),
                "summary": horizon.get("summary") or f"{area['label']} segue sem destaque claro.",
                "peak_date": horizon.get("peak_date"),
            }
        )

    ranked = sorted(
        horizon_entries,
        key=lambda item: (_status_rank(item["status"]), item["probability"]),
        reverse=True,
    )
    lead = [item for item in ranked if item["status"] != "quiet"][:3]
    focus_areas = [item["label"] for item in lead]
    peak_dates = _dedupe_strings([str(item["peak_date"]) for item in lead if item.get("peak_date")], limit=3)
    summary = (
        " / ".join(item["summary"] for item in lead)
        if lead
        else f"{label} segue sem uma convergencia forte o bastante para cravar direcao."
    )
    return {
        "label": label,
        "summary": summary,
        "focus_areas": focus_areas,
        "peak_dates": peak_dates,
    }


def inject_exact_timing_into_forecast(
    forecast_360: dict[str, Any],
    exact_timing: dict[str, Any],
    life_events: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    timed_events = list(exact_timing.get("timed_events", []))
    critical_periods = list(exact_timing.get("critical_periods", []))
    clustered_life_events = list(life_events or [])
    if not timed_events and not critical_periods and not clustered_life_events:
        return forecast_360

    area_map = {area["key"]: area for area in forecast_360.get("areas_da_vida", [])}
    for event in timed_events:
        area = area_map.get(event.get("area_key"))
        if not area:
            continue
        special_focus = dict(area.get("special_focus") or {})
        exact_hits = list(special_focus.get("exact_hits") or [])
        exact_hits.append(event)
        exact_hits.sort(key=lambda item: (item["date"], -float(item["weight"])))
        special_focus["exact_hits"] = exact_hits[:6]
        area["special_focus"] = special_focus

        peak = str(event["time_window"]["peak"])
        if peak not in area["peak_dates"]:
            area["peak_dates"] = sorted([*area["peak_dates"], peak])[:5]

    turning_points = list(forecast_360.get("turning_points", []))
    for event in timed_events[:12]:
        turning_points.append(
            {
                "date": event["time_window"]["peak"],
                "domain": event["area_key"],
                "label": event["label"],
                "probability": min(0.97, round((float(event["weight"]) / 5.0), 2)),
                "headline": f"{event['label']} atinge pico exato",
                "summary": (
                    f"Janela entre {format_date_pt(event['time_window']['start'])} e "
                    f"{format_date_pt(event['time_window']['end'])}, "
                    f"com pico em {format_date_pt(event['time_window']['peak'])}."
                ),
            }
        )

    for event in clustered_life_events:
        turning_points.append(
            {
                "date": event["window"]["peak"],
                "domain": event["area_key"],
                "label": event["label"],
                "probability": min(0.97, round((float(event["strength"]) / 4.0), 2)),
                "headline": event["label"],
                "summary": event["summary"],
            }
        )

    turning_points.sort(key=lambda item: (-float(item["probability"]), item["date"]))
    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for item in turning_points:
        marker = (str(item["domain"]), str(item["date"]))
        if marker in seen:
            continue
        seen.add(marker)
        deduped.append(item)
        if len(deduped) == 10:
            break

    forecast_360["turning_points"] = deduped
    forecast_360["key_dates"] = [item["date"] for item in deduped]
    forecast_360["critical_periods"] = critical_periods
    forecast_360["life_events"] = clustered_life_events

    for event in clustered_life_events:
        area = area_map.get(event.get("area_key"))
        if not area:
            continue
        special_focus = dict(area.get("special_focus") or {})
        event_list = list(special_focus.get("life_events") or [])
        event_list.append(event)
        event_list.sort(key=lambda item: (item["window"]["peak"], -int(item["strength"])))
        special_focus["life_events"] = event_list[:4]
        area["special_focus"] = special_focus

    return forecast_360


def build_forecast_360(
    *,
    payload: dict[str, Any],
    natal_ephemeris: dict[str, Any],
    natal_aspects: list[dict[str, Any]],
    profile_quality: dict[str, Any],
    reference_date: date,
) -> dict[str, Any]:
    timeline_results = analyze_timeline(
        payload=payload,
        natal_ephemeris=natal_ephemeris,
        natal_aspects=natal_aspects,
        profile_quality=profile_quality,
        reference_date=reference_date,
    )
    area_forecasts = _aggregate_area_forecasts(timeline_results)
    house_forecasts = _aggregate_house_forecasts(timeline_results)
    life_episodes = _build_life_episodes(area_forecasts)
    turning_points = _build_turning_points(timeline_results, area_forecasts)
    purpose_forecast = _build_purpose_forecast(timeline_results)

    return {
        "summary": _build_overview(area_forecasts, turning_points),
        "areas_da_vida": area_forecasts,
        "casas": house_forecasts,
        "proposito": purpose_forecast,
        "timelines": {
            "short_term": _build_timeline_horizon_summary(area_forecasts, "short_term", "proximas 6 a 8 semanas"),
            "mid_term": _build_timeline_horizon_summary(area_forecasts, "mid_term", "proximos 12 meses"),
            "long_term": _build_timeline_horizon_summary(area_forecasts, "long_term", "tendencia de 2 a 3 anos"),
        },
        "key_dates": [item["date"] for item in turning_points],
        "timeline": {"periods": timeline_results},
        "life_episodes": life_episodes,
        "turning_points": turning_points,
    }
