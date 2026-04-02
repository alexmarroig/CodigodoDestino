from __future__ import annotations

import hashlib
import json
from typing import List, Dict, Any

from openai import OpenAI

from core.cache import CacheClient
from core.config import settings

# -----------------------------------
# CONFIG
# -----------------------------------

PROMPT_META = {
    "style": "narrativa",
    "technical_terms": False,
    "language": "pt-BR",
    "version": "v2",
}


# -----------------------------------
# BUILD PROMPT (ESTRUTURADO)
# -----------------------------------

def build_narrative_prompt(events: List[Dict]) -> Dict[str, Any]:

    sorted_events = sorted(
        events,
        key=lambda e: (e["time_window"]["start"], -e["score"]),
    )

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

    prompt_text = (
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
        "prompt": prompt_text,
        "events_used": sorted_events,
    }


# -----------------------------------
# CACHE KEY
# -----------------------------------

def _llm_cache_key(prompt: str, model: str) -> str:
    raw = json.dumps(
        {
            "prompt": prompt,
            "model": model,
            "temperature": 0,
            "max_tokens": 550,
        },
        ensure_ascii=False,
    )
    return f"llm:{model}:{hashlib.sha256(raw.encode()).hexdigest()}"


# -----------------------------------
# OPENROUTER CALL
# -----------------------------------

def _call_openrouter(prompt: str, model: str) -> Dict[str, Any]:
    client = OpenAI(
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
    )

    response = client.chat.completions.create(
        model=model,
        temperature=0,
        max_tokens=550,
        messages=[
            {
                "role": "system",
                "content": "Você escreve narrativas claras, diretas e envolventes em português.",
            },
            {"role": "user", "content": prompt},
        ],
        extra_headers={
            "HTTP-Referer": settings.openrouter_site_url,
            "X-Title": settings.openrouter_app_name,
        },
    )

    return {
        "text": response.choices[0].message.content or "",
        "model": model,
        "usage": {
            "input_tokens": getattr(response.usage, "prompt_tokens", 0) if response.usage else 0,
            "output_tokens": getattr(response.usage, "completion_tokens", 0) if response.usage else 0,
        },
    }


# -----------------------------------
# MAIN FUNCTION
# -----------------------------------

def generate_narrative_with_cache(
    prompt_data: Dict[str, Any],
    cache: CacheClient,
) -> Dict[str, Any]:

    if not settings.openrouter_api_key:
        return {
            "text": "",
            "model": "disabled",
            "cached": False,
            "usage": {"input_tokens": 0, "output_tokens": 0},
        }

    prompt = prompt_data["prompt"]

    primary_key = _llm_cache_key(prompt, settings.openrouter_model)

    cached = cache.get_cache(primary_key)
    if cached:
        return {**cached, "cached": True}

    try:
        result = _call_openrouter(prompt, settings.openrouter_model)

        cache.set_cache(primary_key, result, settings.llm_cache_ttl)

        return {**result, "cached": False}

    except Exception:
        fallback_key = _llm_cache_key(prompt, settings.openrouter_fallback_model)

        cached_fallback = cache.get_cache(fallback_key)
        if cached_fallback:
            return {**cached_fallback, "cached": True}

        fallback_result = _call_openrouter(prompt, settings.openrouter_fallback_model)

        cache.set_cache(fallback_key, fallback_result, settings.llm_cache_ttl)

        return {**fallback_result, "cached": False}