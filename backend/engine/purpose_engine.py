from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from engine.analysis import DOMAIN_LABELS, THEME_MAP

PURPOSE_NUMEROLOGY_MAP = {
    1: "identidade",
    2: "relacionamentos",
    3: "comunicacao",
    4: "carreira_status",
    5: "expansao_sentido",
    6: "familia_lar",
    7: "psicologico_espiritual",
    8: "carreira_status",
    9: "expansao_sentido",
    11: "psicologico_espiritual",
    22: "carreira_status",
    33: "amigos_rede",
}

PLANET_PURPOSE_WEIGHTS = {
    "sun": 3.0,
    "moon": 1.8,
    "mercury": 1.0,
    "venus": 1.0,
    "mars": 1.4,
    "jupiter": 2.1,
    "saturn": 2.2,
}


def analyze_life_purpose(analysis: dict[str, Any]) -> dict[str, Any]:
    domain_scores: defaultdict[str, float] = defaultdict(float)
    evidence: list[str] = []

    natal_planet_houses = dict(analysis.get("natal", {}).get("planet_houses", {}))
    for planet_name, house in natal_planet_houses.items():
        if house is None:
            continue
        domain = THEME_MAP.get(int(house))
        if not domain:
            continue
        weight = PLANET_PURPOSE_WEIGHTS.get(planet_name, 0.6)
        domain_scores[domain] += weight
        if planet_name in {"sun", "jupiter", "saturn"}:
            evidence.append(f"{planet_name.title()} natal aponta para {DOMAIN_LABELS.get(domain, domain)}")

    profections = dict(analysis.get("profections", {}))
    activated_domain = profections.get("activated_domain")
    if activated_domain:
        domain_scores[str(activated_domain)] += 2.6
        evidence.append(
            f"Profeccao anual ativa {DOMAIN_LABELS.get(str(activated_domain), str(activated_domain))}"
        )

    solar_return = dict(analysis.get("solar_return", {}))
    for dominant_house in list(solar_return.get("dominant_houses", []) or [])[:2]:
        domain = str(dominant_house["domain"])
        domain_scores[domain] += 2.1 - (0.3 * len(evidence))
        evidence.append(f"Retorno solar concentra energia em {DOMAIN_LABELS.get(domain, domain)}")

    numerology = dict(analysis.get("numerology", {}))
    life_path_number = int(numerology.get("life_path_number", 0) or 0)
    numerology_domain = PURPOSE_NUMEROLOGY_MAP.get(life_path_number)
    if numerology_domain:
        domain_scores[numerology_domain] += 1.2
        evidence.append(f"Caminho de vida {life_path_number} reforca {DOMAIN_LABELS.get(numerology_domain, numerology_domain)}")

    if not domain_scores:
        return {
            "summary": "O proposito ainda nao aparece com densidade suficiente para uma leitura mais fina.",
            "current_focus": "O ciclo atual ainda esta mais reativo do que direcional.",
            "long_arc": "Vale observar repeticao de temas antes de tirar conclusoes maiores.",
            "focus_domains": [],
            "evidence": [],
        }

    ranked = Counter(domain_scores).most_common(3)
    focus_domains = [domain for domain, _ in ranked]
    primary = focus_domains[0]
    secondary = focus_domains[1] if len(focus_domains) > 1 else None

    summary = (
        f"Seu eixo de proposito tende a ganhar forma em {DOMAIN_LABELS.get(primary, primary)}"
        + (
            f", com segunda camada em {DOMAIN_LABELS.get(secondary, secondary)}."
            if secondary
            else "."
        )
    )
    current_focus = (
        f"No ciclo atual, esse proposito pede escolhas mais concretas em {DOMAIN_LABELS.get(activated_domain, primary)}."
        if activated_domain
        else f"No ciclo atual, o chamado fica mais claro em {DOMAIN_LABELS.get(primary, primary)}."
    )
    long_arc = (
        f"A longo prazo, seu caminho cresce quando voce transforma {DOMAIN_LABELS.get(primary, primary)} em algo visivel, "
        f"sustentavel e com utilidade real."
    )

    return {
        "summary": summary,
        "current_focus": current_focus,
        "long_arc": long_arc,
        "focus_domains": focus_domains,
        "evidence": evidence[:5],
        "life_path_number": life_path_number,
    }
