from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from typing import Any

from openai import OpenAI

from core.cache import CacheClient
from core.config import settings
from core.serialization import json_dumps_text, stable_hash

PROMPT_META = {
    "style": "analise-multicamadas",
    "language": "pt-BR",
    "temperature": 0,
    "version": "v4",
}

INTENSITY_LABELS = {"high": "alta", "medium": "moderada", "low": "leve"}


@dataclass(frozen=True)
class NarrativePlan:
    strategy: str
    reason: str
    complexity_score: float
    selected_events: list[dict[str, Any]]
    selected_domains: list[dict[str, Any]]
    signature: str


@lru_cache(maxsize=1)
def _build_openai_client() -> OpenAI:
    return OpenAI(
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
    )


def _compact_event(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": event["id"],
        "title": event["title"],
        "domain": event["category"],
        "probability": event["probability"],
        "intensity": event["intensity"],
        "signals": event.get("signals", [])[:4],
        "time_window": event["time_window"],
        "counter_signals": event.get("counter_signals", [])[:2],
        "recommendations": event.get("recommendations", [])[:2],
    }


def _compact_domain(domain: dict[str, Any]) -> dict[str, Any]:
    return {
        "domain": domain["domain"],
        "domain_label": domain["domain_label"],
        "probability": domain["probability"],
        "tone": domain["tone"],
        "converged": domain["converged"],
        "independent_techniques": domain["independent_techniques"],
        "signal_labels": [signal["label"] for signal in domain["signals"][:4]],
        "time_window": domain["time_window"],
    }


def _select_events_for_prompt(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ranked = sorted(
        events,
        key=lambda item: (
            -float(item["probability"]),
            item["time_window"]["start"],
            item["id"],
        ),
    )
    return [_compact_event(event) for event in ranked[: settings.max_events_in_prompt]]


def _select_domains_for_prompt(domain_analysis: dict[str, Any]) -> list[dict[str, Any]]:
    domains = list(domain_analysis.get("domains", []))
    ranked = sorted(
        domains,
        key=lambda item: (
            not item["converged"],
            -float(item["probability"]),
            item["domain"],
        ),
    )
    return [_compact_domain(item) for item in ranked[: max(settings.max_events_in_prompt, 3)]]


def _calculate_complexity_score(
    events: list[dict[str, Any]],
    domain_analysis: dict[str, Any],
    uncertainties: list[dict[str, Any]],
) -> float:
    if not events and not domain_analysis.get("domains"):
        return 0.0

    high_intensity_count = sum(1 for event in events if event["intensity"] == "high")
    average_probability = (
        sum(float(event["probability"]) for event in events) / len(events)
        if events
        else 0.0
    )
    domain_diversity = min(1.0, len(domain_analysis.get("domains", [])) / 4)
    uncertainty_load = min(1.0, len(uncertainties) / 3)

    score = (
        (average_probability * 0.45)
        + (high_intensity_count * 0.16)
        + (domain_diversity * 0.2)
        + (uncertainty_load * 0.1)
    )
    return round(min(1.0, score), 3)


def _should_use_llm(
    events: list[dict[str, Any]],
    confidence: dict[str, Any],
    complexity_score: float,
) -> tuple[bool, str]:
    if confidence.get("level") == "high":
        return True, "high-confidence-convergence"
    high_intensity_count = sum(1 for event in events if event["intensity"] == "high")
    if (
        confidence.get("level") == "medium"
        and high_intensity_count >= max(2, settings.llm_min_high_intensity_events)
    ):
        return True, "high-intensity-events"
    if confidence.get("level") != "low" and complexity_score >= settings.llm_complexity_threshold:
        return True, "complexity-threshold"
    return False, "template-cheaper-and-sufficient"


def _build_signature(
    selected_events: list[dict[str, Any]],
    selected_domains: list[dict[str, Any]],
    strategy: str,
) -> str:
    return stable_hash(
        {
            "strategy": strategy,
            "events": selected_events,
            "domains": selected_domains,
        }
    )


def _build_narrative_plan(
    analysis: dict[str, Any],
    events: list[dict[str, Any]],
    confidence: dict[str, Any],
    uncertainties: list[dict[str, Any]],
) -> NarrativePlan:
    selected_events = _select_events_for_prompt(events)
    selected_domains = _select_domains_for_prompt(analysis.get("domain_analysis", {}))
    complexity_score = _calculate_complexity_score(
        selected_events,
        analysis.get("domain_analysis", {}),
        uncertainties,
    )
    use_llm, reason = _should_use_llm(selected_events, confidence, complexity_score)
    strategy = "llm" if use_llm else "template"
    signature = _build_signature(selected_events, selected_domains, strategy)

    return NarrativePlan(
        strategy=strategy,
        reason=reason,
        complexity_score=complexity_score,
        selected_events=selected_events,
        selected_domains=selected_domains,
        signature=signature,
    )


def build_narrative_prompt(
    analysis: dict[str, Any],
    events: list[dict[str, Any]],
    event_summary: dict[str, Any],
    confidence: dict[str, Any],
    uncertainties: list[dict[str, Any]],
) -> dict[str, Any]:
    plan = _build_narrative_plan(analysis, events, confidence, uncertainties)
    prompt_payload = {
        "profile_quality": analysis.get("profile_quality", {}),
        "confidence": confidence,
        "event_summary": event_summary,
        "macro_theme": {
            "profections": analysis.get("profections", {}),
            "solar_return": analysis.get("solar_return", {}),
        },
        "domains": plan.selected_domains,
        "events": plan.selected_events,
        "uncertainties": uncertainties[:3],
        "techniques_used": analysis.get("techniques_used", []),
        "numerology": analysis.get("numerology", {}),
    }

    prompt_lines = [
        "Voce e um analista astrologico e numerologico profissional.",
        "Nao invente dados e nao afirme certezas absolutas.",
        "Use pt-BR direto, maduro e pratico.",
        "So conclua com firmeza onde houver convergencia real de tecnicas.",
        "Quando houver sinais mistos, diga isso explicitamente e mostre o que observar.",
        "",
        "JSON DE ANALISE:",
        json_dumps_text(prompt_payload, sort_keys=True),
        "",
        "FORMATO OBRIGATORIO:",
        "1. Resumo do periodo em 1 paragrafo.",
        "2. Tema do ano explicando por que esse tema foi ativado.",
        "3. Dominios principais com causa -> efeito -> orientacao pratica.",
        "4. Incertezas e o que observar.",
        "5. Nota curta de responsabilidade.",
    ]

    return {
        "prompt_meta": PROMPT_META,
        "prompt": "\n".join(prompt_lines),
        "events_used": plan.selected_events,
        "domains_used": plan.selected_domains,
        "analysis_digest": prompt_payload,
        "plan": asdict(plan),
    }


def _llm_cache_key(signature: str, model: str) -> str:
    return f"llm:{model}:{signature}"


def _call_openrouter(prompt: str, model: str) -> dict[str, Any]:
    client = _build_openai_client()

    response = client.chat.completions.create(
        model=model,
        temperature=0,
        max_tokens=settings.llm_max_tokens,
        messages=[
            {
                "role": "system",
                "content": (
                    "Voce escreve leituras claras, especificas e prudentes em portugues do Brasil, "
                    "sempre conectando evidencia, janela temporal e orientacao pratica."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        extra_headers={
            "HTTP-Referer": settings.openrouter_site_url,
            "X-Title": settings.openrouter_app_name,
        },
    )

    message_content = response.choices[0].message.content or ""
    if isinstance(message_content, list):
        text = "".join(
            part.text
            for part in message_content
            if hasattr(part, "text") and isinstance(part.text, str)
        )
    else:
        text = str(message_content)
    usage = response.usage

    return {
        "text": text.strip(),
        "model": model,
        "provider": "openrouter",
        "usage": {
            "input_tokens": getattr(usage, "prompt_tokens", 0) if usage else 0,
            "output_tokens": getattr(usage, "completion_tokens", 0) if usage else 0,
        },
    }


def _build_local_fallback(
    events: list[dict[str, Any]],
    domains: list[dict[str, Any]],
    confidence: dict[str, Any],
    uncertainties: list[dict[str, Any]],
    plan: dict[str, Any],
    *,
    reason_override: str | None = None,
) -> dict[str, Any]:
    if not events:
        text = (
            "O periodo nao mostra convergencia suficiente para previsoes fortes. "
            "Neste momento, a leitura mais honesta e observar repeticao de temas antes de concluir direcao."
        )
    else:
        lead_event = events[0]
        lead_domain = domains[0]["domain_label"] if domains else lead_event["domain"]
        secondary_clause = ""
        if len(events) > 1:
            secondary_titles = ", ".join(event["title"].lower() for event in events[1:3])
            secondary_clause = f" Ao fundo, tambem aparecem {secondary_titles}."

        uncertainty_clause = ""
        if uncertainties:
            uncertainty_clause = (
                f" Ainda assim, ha incerteza em {uncertainties[0]['domain'].replace('_', ' ')}, "
                "entao vale observar se o tema se repete antes de cravar desfecho."
            )

        text = (
            f"O eixo mais ativo agora e {lead_domain}, com intensidade "
            f"{INTENSITY_LABELS.get(str(lead_event['intensity']), str(lead_event['intensity']))}. "
            f"{lead_event['description']} Isso tende a se manifestar como {lead_event['effect'].lower()} "
            f"As orientacoes mais uteis agora sao: {' '.join(lead_event.get('recommendations', [])[:2])}."
            f"{secondary_clause}{uncertainty_clause} "
            f"O nivel de confianca geral desta leitura esta em {confidence.get('level', 'low')}."
        )

    return {
        "text": text,
        "model": "local-fallback",
        "provider": "local-fallback",
        "usage": {"input_tokens": 0, "output_tokens": 0},
        "strategy": "template",
        "requested_strategy": plan["strategy"],
        "strategy_reason": reason_override or plan["reason"],
        "complexity_score": plan["complexity_score"],
        "prompt_event_count": len(events),
    }


def generate_narrative_with_cache(
    prompt_data: dict[str, Any],
    cache: CacheClient,
) -> dict[str, Any]:
    prompt = str(prompt_data["prompt"])
    events = list(prompt_data["events_used"])
    domains = list(prompt_data["domains_used"])
    confidence = dict(prompt_data["analysis_digest"]["confidence"])
    uncertainties = list(prompt_data["analysis_digest"]["uncertainties"])
    plan = dict(prompt_data["plan"])

    if plan["strategy"] != "llm":
        return {
            **_build_local_fallback(events, domains, confidence, uncertainties, plan),
            "cached": False,
        }

    if not settings.openrouter_api_key:
        return {
            **_build_local_fallback(
                events,
                domains,
                confidence,
                uncertainties,
                plan,
                reason_override="openrouter-disabled",
            ),
            "cached": False,
        }

    primary_cache_key = _llm_cache_key(plan["signature"], settings.openrouter_model)
    cached_primary = cache.get_cache(primary_cache_key)
    if cached_primary is not None:
        return {**cached_primary, "cached": True}

    try:
        primary_result = _call_openrouter(prompt, settings.openrouter_model)
        enriched_primary = {
            **primary_result,
            "strategy": plan["strategy"],
            "requested_strategy": plan["strategy"],
            "strategy_reason": plan["reason"],
            "complexity_score": plan["complexity_score"],
            "prompt_event_count": len(events),
        }
        cache.set_cache(primary_cache_key, enriched_primary, settings.llm_cache_ttl)
        return {**enriched_primary, "cached": False}
    except Exception:
        fallback_cache_key = _llm_cache_key(plan["signature"], settings.openrouter_fallback_model)
        cached_fallback = cache.get_cache(fallback_cache_key)
        if cached_fallback is not None:
            return {**cached_fallback, "cached": True}

        try:
            fallback_result = _call_openrouter(prompt, settings.openrouter_fallback_model)
            enriched_fallback = {
                **fallback_result,
                "strategy": plan["strategy"],
                "requested_strategy": plan["strategy"],
                "strategy_reason": plan["reason"],
                "complexity_score": plan["complexity_score"],
                "prompt_event_count": len(events),
            }
            cache.set_cache(fallback_cache_key, enriched_fallback, settings.llm_cache_ttl)
            return {**enriched_fallback, "cached": False}
        except Exception:
            return {
                **_build_local_fallback(
                    events,
                    domains,
                    confidence,
                    uncertainties,
                    plan,
                    reason_override="openrouter-failed-fallback",
                ),
                "cached": False,
            }
