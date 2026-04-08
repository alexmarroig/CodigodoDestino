from __future__ import annotations
import logging
from typing import Any, Dict, List
from openai import OpenAI
from core.config import settings
from core.cache import CacheClient

logger = logging.getLogger(__name__)

def _build_openai_client() -> OpenAI:
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.openrouter_api_key,
    )

def _llm_cache_key(signature: str, model: str) -> str:
    return f"llm_narrative:{signature}:{model}"

def _call_openrouter(prompt: str, model: str) -> dict[str, Any]:
    client = _build_openai_client()

    system_prompt = (
        "Voce e um especialista senior em Product Design (Apple/Google) e Astrologia Psicologica Profunda. "
        "Sua tarefa e REESTRUTURAR o conteudo para uma experiencia premium de alto nivel.\n\n"
        "REGRAS DE OURO:\n"
        "1. LINGUAGEM: Humana, afirmativa, sem jargao astrologico, sem 'pode/talvez'. Frases curtas.\n"
        "2. ESTRUTURA: Entregue exatamente 6 blocos numerados:\n"
        "   1. SEU MOMENTO AGORA (Foco, desafio, oportunidade, estado emocional)\n"
        "   2. QUEM ESTA ENVOLVIDO (Tipo de pessoa, funcao, dinâmica e impacto)\n"
        "   3. LINHA DO TEMPO (Agora, Proximo Pico, Depois)\n"
        "   4. SCORES (0-10 para Amor, Carreira, Dinheiro e Saude)\n"
        "   5. ALERTAS (Riscos reais e pontos de sobrecarga)\n"
        "   6. DIRECAO PRATICA (Acao direta, decisao necessaria e o que evitar)\n\n"
        "3. CAMADAS: Use o formato:\n"
        "[TITULO]\n"
        "👉 Resumo brutal (1 linha)\n"
        "Explicacao simples (2-3 linhas)\n"
        "💡 O que isso pede de voce: (bullets)\n"
        "⚠️ Atencao: (bullets)\n\n"
        "NAO EXPLIQUE O QUE FEZ. APENAS ENTREGUE O RESULTADO."
    )

    response = client.chat.completions.create(
        model=model,
        temperature=0,
        max_tokens=settings.llm_max_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        extra_headers={
            "HTTP-Referer": settings.openrouter_site_url,
            "X-Title": settings.openrouter_app_name,
        },
    )

    text = response.choices[0].message.content or ""
    return {
        "text": text.strip(),
        "model": model,
        "provider": "openrouter",
        "usage": {
            "input_tokens": response.usage.prompt_tokens if response.usage else 0,
            "output_tokens": response.usage.completion_tokens if response.usage else 0,
        },
    }

def _build_local_fallback(
    events: list[dict[str, Any]],
    decision_results: dict[str, Any] | None = None,
    **kwargs,
) -> dict[str, Any]:
    # Compatibility with old signature for tests
    if decision_results is None:
        # Reconstruct minimal decision results from kwargs
        from engine.decision_motor import rank_events, identify_involved_person, calculate_scores
        from datetime import date
        res = rank_events(events, date.today())
        res["scores"] = calculate_scores(res["all_ranked"], date.today())
        if res["dominant"]:
            res["dominant"]["involved_person"] = identify_involved_person(res["dominant"])
        decision_results = res

    dominant = decision_results.get("dominant")
    scores = decision_results.get("scores", {})

    if not dominant:
        text = "O momento e de observacao. Nao ha convergencia clara para uma direcao forte agora."
    else:
        person = dominant.get("involved_person", {})
        rt = dominant.get("reality_translation", {})

        text = f"""
1. 🔮 SEU MOMENTO AGORA
👉 {rt.get('layer_1', 'Fase de ajustes importantes.')}

Explicação:
{rt.get('layer_2', 'O cenário pede atenção aos detalhes e paciência estratégica.')}

💡 O que isso pede de você:
- {rt.get('actions', ['Agir com critério'])[0]}
- Observar repetições de temas

2. 👤 QUEM ESTÁ ENVOLVIDO
👉 {person.get('type', 'Alguém próximo')}

Função: {person.get('role', 'Influência direta')}
Dinâmica: {person.get('dynamic', 'Testa limites')}
Impacto: {person.get('impact', 'Moderado')}

3. ⏳ LINHA DO TEMPO
AGORA: Fase de {dominant.get('tone', 'transição')}
PRÓXIMO PICO: {dominant.get('time_window', {}).get('peak', 'Em breve')}
DEPOIS: Consolidação dos ajustes

4. 📊 SCORES
Amor: {scores.get('amor', 5.0)}/10
Carreira: {scores.get('carreira', 5.0)}/10
Dinheiro: {scores.get('dinheiro', 5.0)}/10
Saúde: {scores.get('saude', 5.0)}/10

5. ⚠️ ALERTAS
- {rt.get('risks', ['Risco de agir por impulso'])[0]}

6. 🚀 DIREÇÃO PRÁTICA
- {rt.get('actions', ['Observar o cenário'])[0]}
- Evitar conclusões precipitadas
"""

    return {
        "text": text.strip(),
        "model": "local-fallback",
        "provider": "local-fallback",
        "strategy": "template",
    }

def build_narrative_prompt(
    analysis: dict[str, Any],
    events: list[dict[str, Any]],
    event_summary: dict[str, Any],
    confidence: dict[str, Any],
    uncertainties: list[dict[str, Any]],
    forecast_360: dict[str, Any] | None = None,
    timeline: dict[str, Any] | None = None,
    life_episodes: list[dict[str, Any]] | None = None,
    turning_points: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:

    confidence_level = confidence.get("level", "low")

    if confidence_level == "high":
        strategy = "llm"
        reason = "high-confidence-convergence"
    else:
        strategy = "template"
        reason = "template-cheaper-and-sufficient"

    return {
        "prompt": f"Analysis for {len(events)} events. Confidence: {confidence_level}.",
        "events_used": events,
        "domains_used": analysis.get("domain_analysis", {}).get("domains", []),
        "analysis_digest": {
            "confidence": confidence,
            "uncertainties": uncertainties,
            "forecast_360": forecast_360,
        },
        "plan": {
            "strategy": strategy,
            "signature": "premium_v1",
            "reason": reason,
            "complexity_score": 1.0 if strategy == "llm" else 0.3
        }
    }

def generate_narrative_with_cache(
    prompt_data: dict[str, Any],
    cache: CacheClient,
    decision_results: dict[str, Any],
) -> dict[str, Any]:
    prompt = str(prompt_data["prompt"])
    plan = dict(prompt_data["plan"])

    if plan["strategy"] != "llm" or not settings.openrouter_api_key:
        return {
            **_build_local_fallback(prompt_data["events_used"], decision_results),
            "cached": False,
        }

    cache_key = _llm_cache_key(plan["signature"], settings.openrouter_model)
    cached = cache.get_cache(cache_key)
    if cached:
        return {**cached, "cached": True}

    try:
        result = _call_openrouter(prompt, settings.openrouter_model)
        cache.set_cache(cache_key, result, settings.llm_cache_ttl)
        return {**result, "cached": False}
    except Exception:
        return {
            **_build_local_fallback(prompt_data["events_used"], decision_results),
            "cached": False,
        }
