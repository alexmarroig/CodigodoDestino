from __future__ import annotations

import hashlib
import json
from typing import Any

from openai import OpenAI

from core.cache import CacheClient
from core.config import settings


def build_narrative_prompt(events: list[dict]) -> str:
    lines: list[str] = [
        "Crie uma narrativa em português sem termos técnicos.",
        "Organize por tempo e intensidade.",
        "Eventos:",
    ]
    for event in events:
        lines.append(
            f"- {event['event']} | categoria={event['category']} | intensidade={event['intensity']} | periodo={event['time_window']['start']}"
        )
    return "\n".join(lines)


def _llm_cache_key(prompt: str, model: str) -> str:
    raw = json.dumps({"prompt": prompt, "model": model, "temperature": 0, "max_tokens": 550}, ensure_ascii=False)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"llm:{model}:{digest}"


def _call_openrouter(prompt: str, model: str) -> dict[str, Any]:
    client = OpenAI(api_key=settings.openrouter_api_key, base_url=settings.openrouter_base_url)
    response = client.chat.completions.create(
        model=model,
        temperature=0,
        max_tokens=550,
        messages=[
            {"role": "system", "content": "Você escreve narrativas claras, sem termos técnicos, em português."},
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


def generate_narrative_with_cache(prompt: str, cache: CacheClient) -> dict[str, Any]:
    if not settings.openrouter_api_key:
        return {"text": "", "model": "disabled", "cached": False, "usage": {"input_tokens": 0, "output_tokens": 0}}

    primary_key = _llm_cache_key(prompt, settings.openrouter_model)
    cached = cache.get_cache(primary_key)
    if cached is not None:
        return {**cached, "cached": True}

    try:
        result = _call_openrouter(prompt, settings.openrouter_model)
        cache.set_cache(primary_key, result, settings.llm_cache_ttl)
        return {**result, "cached": False}
    except Exception:
        fallback_key = _llm_cache_key(prompt, settings.openrouter_fallback_model)
        cached_fallback = cache.get_cache(fallback_key)
        if cached_fallback is not None:
            return {**cached_fallback, "cached": True}
        fallback_result = _call_openrouter(prompt, settings.openrouter_fallback_model)
        cache.set_cache(fallback_key, fallback_result, settings.llm_cache_ttl)
        return {**fallback_result, "cached": False}
