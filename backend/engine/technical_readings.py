from __future__ import annotations

from typing import Any

from engine.astro_confirmation import is_self_aspect as _is_self_aspect, score_signal
from engine.date_formatting import format_date_pt, format_time_window_label
from engine.portuguese_text import polish_portuguese

ASPECT_NAMES_PT = {
    "conjunction": "conjunção",
    "opposition": "oposição",
    "square": "quadratura",
    "trine": "trígono",
    "sextile": "sextil",
}

PLANET_NAMES_PT = {
    "Sun": "Sol",
    "Moon": "Lua",
    "Mercury": "Mercúrio",
    "Venus": "Vênus",
    "Mars": "Marte",
    "Jupiter": "Júpiter",
    "Saturn": "Saturno",
    "Uranus": "Urano",
    "Neptune": "Netuno",
    "Pluto": "Plutão",
    "Asc": "Ascendente",
    "Mc": "Meio-Céu",
    "Chiron": "Quíron",
    "North Node": "Nodo Norte",
    "South Node": "Nodo Sul",
    "True Node": "Nodo Norte",
    "Lilith": "Lilith",
}


def _translate_planet(raw: str) -> str:
    clean = raw.replace("_", " ").strip()
    return PLANET_NAMES_PT.get(clean, PLANET_NAMES_PT.get(clean.title(), clean.title() if clean else clean))

ASPECT_MEANINGS = {
    "conjunction": "une e intensifica os dois pontos — o tema explode ou se concentra",
    "opposition": "puxa confronto, polarização ou decisão entre dois polos",
    "square": "gera atrito, pressão e necessidade de ajuste imediato",
    "trine": "facilita fluxo e oportunidade, se você agir",
    "sextile": "abre porta de oportunidade moderada",
}

PHASE_LABELS = {
    "applying": "aproximando do exato",
    "separating": "afastando do exato",
}

TECHNIQUE_LABELS = {
    "transits": "Trânsito",
    "progressions": "Progressão",
    "solar_return": "Retorno solar",
    "solar_arc": "Arco solar",
    "profections": "Profeccão anual",
    "numerology": "Numerologia",
}

CATEGORY_AVOIDABILITY = {
    "health": "Parcialmente evitável: repouso, ritmo e cuidado reduzem o impacto.",
    "career": "Parcialmente evitável: decisão antecipada melhora o desfecho.",
    "relationships": "Parcialmente evitável: conversa clara e limite mudam o resultado.",
    "rupture": "Parcialmente evitável: limite consciente pode frear, mas o ciclo não some.",
    "major_transitions": "Não evitável como ciclo; dá para escolher como atravessar.",
    "finance": "Parcialmente evitável: planejamento antecipado reduz o impacto de perdas e consolida ganhos.",
}

PROBABILITY_QUALITY = {
    "Alta": "forte",
    "Moderada": "moderada",
    "Baixa": "baixa",
    "Descartar": "fraca",
}


def _avoidability_for_signal(signal: dict[str, Any], category_key: str) -> str:
    technique = str(signal.get("technique") or "")
    polarity = str(signal.get("polarity") or "mixed")
    if technique in {"solar_return", "profections", "progressions", "solar_arc"}:
        return "Ciclo estrutural: não se cancela; prepara-se e conduz com consciência."
    if technique == "numerology":
        return "Ciclo numerológico: não se apaga; muda-se a resposta prática."
    if polarity == "supportive":
        return "Aspecto favorável: não precisa evitar; use o timing para agir."
    if polarity == "challenging":
        return "Aspecto tenso: não dá para anular, mas dá para reduzir dano com atitude."
    return CATEGORY_AVOIDABILITY.get(category_key, "Parcialmente evitável com escolha consciente.")


def _house_phrase(house: int | None) -> str:
    if house is None:
        return ""
    themes = {
        1: "identidade",
        2: "dinheiro",
        3: "comunicação",
        4: "família",
        5: "afeto",
        6: "rotina e saúde",
        7: "parcerias",
        8: "crises e recursos compartilhados",
        9: "expansão",
        10: "carreira",
        11: "rede e amigos",
        12: "inconsciente e encerramentos",
    }
    return f" Casa {house} ({themes.get(house, 'vida')})."


def build_signal_reading(signal: dict[str, Any], *, reference_date, category_key: str) -> dict[str, str]:
    technique = TECHNIQUE_LABELS.get(str(signal.get("technique")), str(signal.get("technique", "Sinal")))
    evidence = dict(signal.get("evidence") or {})
    time_window = dict(signal.get("time_window") or evidence.get("time_window") or {})
    when = format_time_window_label(time_window, reference_date=reference_date)
    peak = time_window.get("peak")
    peak_line = f" Exato mais provável: {format_date_pt(peak)}." if peak else ""

    if str(signal.get("technique")) == "numerology":
        meaning = "O ciclo numerológico reforça este tema no período indicado."
        title = str(signal.get("label") or "Sinal numerológico")
        return {
            "title": title,
            "aspect_line": "Numerologia (sem aspecto planetário)",
            "when": when + peak_line,
            "meaning": meaning,
            "avoidability": _avoidability_for_signal(signal, category_key),
            "formatted": polish_portuguese(
                f"{technique} — {title}. Quando: {when}.{peak_line} "
                f"Significado: {meaning} Dá para evitar? {_avoidability_for_signal(signal, category_key)}"
            ),
        }

    aspect = str(evidence.get("aspect") or "")
    aspect_pt = ASPECT_NAMES_PT.get(aspect, aspect or "aspecto")
    planet_a = _translate_planet(str(evidence.get("planet_a") or ""))
    planet_b = _translate_planet(str(evidence.get("planet_b") or ""))
    phase = PHASE_LABELS.get(str(evidence.get("phase") or ""), "")
    orb = evidence.get("orb")
    orb_line = f" Orbe {orb}°." if orb is not None else ""
    phase_line = f" Fase: {phase}." if phase else ""

    if aspect:
        if planet_a and planet_b and planet_a.lower() != planet_b.lower():
            aspect_line = f"{aspect_pt} entre {planet_a} e {planet_b}.{orb_line}{phase_line}"
        elif planet_a:
            aspect_line = f"{planet_a} em {aspect_pt}.{orb_line}{phase_line}"
        else:
            aspect_line = f"{aspect_pt}.{orb_line}{phase_line}"
        meaning = ASPECT_MEANINGS.get(aspect, "Ativa o tema com força no mapa.")
    else:
        aspect_line = str(signal.get("label") or "Sinal técnico")
        meaning = "Confirma o tema por técnica astrológica."

    house = evidence.get("transit_house") or evidence.get("natal_house")
    meaning += _house_phrase(house if isinstance(house, int) else None)

    title = str(signal.get("label") or aspect_line)
    avoid = _avoidability_for_signal(signal, category_key)

    return {
        "title": title,
        "aspect_line": aspect_line,
        "when": when + peak_line,
        "meaning": meaning.strip(),
        "avoidability": avoid,
        "formatted": polish_portuguese(
            f"{technique} — {aspect_line} Quando: {when}.{peak_line} "
            f"Significado: {meaning} Dá para evitar? {avoid}"
        ),
    }


def build_rule_reading(rule_hit: dict[str, Any]) -> dict[str, str]:
    label = str(rule_hit.get("label") or "Regra interpretativa")
    return {
        "title": label,
        "aspect_line": "Regra do motor interpretativo",
        "when": "Ativa enquanto os sinais técnicos convergem",
        "meaning": "Traduz o padrão astrológico em consequência humana direta.",
        "avoidability": "Parcialmente evitável: muda-se a resposta, não o ciclo.",
        "formatted": polish_portuguese(
            f"Regra interpretativa — {label}. "
            "Significado: traduz o padrão em evento concreto. "
            "Dá para evitar? Parcialmente, com escolha consciente."
        ),
    }


def build_technical_items(
    *,
    signals: list[dict[str, Any]],
    rule_hits: list[dict[str, Any]],
    reference_date,
    category_key: str,
    limit: int = 4,
) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    # Filter self-aspects before sorting — same-body progressions (Pluto/Pluto etc.)
    # carry no individual meaning and should not appear in the technical display.
    meaningful_signals = [s for s in signals if not _is_self_aspect(s)]
    sorted_signals = sorted(
        meaningful_signals,
        key=lambda item: (-score_signal(item), str(item.get("label", ""))),
    )
    for signal in sorted_signals[: max(1, limit - 1)]:
        items.append(build_signal_reading(signal, reference_date=reference_date, category_key=category_key))
    for hit in sorted(rule_hits, key=lambda item: -float(item.get("weight", 0.0)))[:1]:
        items.append(build_rule_reading(hit))
    return items[:limit]


def format_technical_block(items: list[dict[str, str]]) -> str:
    if not items:
        return ""
    lines: list[str] = []
    for index, item in enumerate(items, start=1):
        lines.append(f"{index}. {item['title']}")
        lines.append(f"   Aspecto: {item['aspect_line']}")
        lines.append(f"   Quando: {item['when']}")
        lines.append(f"   Significado: {item['meaning']}")
        lines.append(f"   Dá para evitar? {item['avoidability']}")
    return polish_portuguese("\n".join(lines))


def build_quality_summary(
    *,
    independent_signals: int,
    probability_level: str,
    techniques: list[str],
    has_peak: bool,
) -> str:
    technique_names = [TECHNIQUE_LABELS.get(name, name) for name in techniques[:4]]
    quality = PROBABILITY_QUALITY.get(probability_level, "moderada")
    peak_clause = " com data de pico" if has_peak else " sem pico exato fechado"
    techniques_clause = ", ".join(technique_names) if technique_names else "técnicas mistas"
    return polish_portuguese(
        f"Qualidade técnica {quality}: {independent_signals} técnicas independentes "
        f"({techniques_clause}){peak_clause}."
    )
