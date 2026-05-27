"""
Fatalistic prediction subtyping for CodigodoDestino.

Maps rule codes and signals to specific event subtypes (e.g. separação abrupta vs
afastamento, doença leve vs crise, emprego novo vs perda) and produces precise
Portuguese text with dates using the "Quando / O que / Por que / Dá para evitar"
structure.

Sub-types require minimum conditions:
  - min_techniques: independent techniques for watchlist inclusion
  - fatalistic_threshold: techniques required for "vai acontecer" language
  - At least one matching rule code (priority_rule_codes score 10×)
"""

from __future__ import annotations

from datetime import date
from typing import Any

from engine.astro_confirmation import (
    classify_career_finance_subtype,
    classify_family_subtype,
    classify_health_subtype,
    classify_relationship_conflict_subtype,
    filter_generational_pairs,
    filter_self_aspects,
    is_generational_outer_pair as _is_generational_outer_pair,
    is_self_aspect as _ac_is_self_aspect,
    score_signal,
)
from engine.astro_provenance import (
    build_astro_provenance,
    build_human_por_que_from_provenance,
    format_provenance_technical_block,
)
from engine.cluster_convergence import compute_cluster_metrics
from engine.certainty import resolve_certainty
from engine.signal_enrichment import (
    format_brady_por_que_line,
    has_hard_slow_transit,
    soft_aspect_opportunity_note,
    subtype_requires_hard_aspect,
)
from engine.date_formatting import format_assertive_when_label, format_date_pt, format_time_window_label, parse_iso_date
from engine.portuguese_text import polish_portuguese

# ---------------------------------------------------------------------------
# Planet translation and signal helpers
# ---------------------------------------------------------------------------

_PLANET_NAMES_PT: dict[str, str] = {
    "Sun": "Sol", "Moon": "Lua", "Mercury": "Mercúrio", "Venus": "Vênus",
    "Mars": "Marte", "Jupiter": "Júpiter", "Saturn": "Saturno",
    "Uranus": "Urano", "Neptune": "Netuno", "Pluto": "Plutão",
    "Asc": "Ascendente", "Mc": "Meio-Céu", "Chiron": "Quíron",
    "North Node": "Nodo Norte", "South Node": "Nodo Sul",
    "True Node": "Nodo Norte", "Lilith": "Lilith",
}

# Fast-moving planets whose transits qualify as "fast movers" for briga calibration
_FAST_MOVERS: frozenset[str] = frozenset({"sun", "moon", "mercury", "venus", "mars"})
# Planets that produce meaningful relational conflict in house 7
_CONFLICT_PLANETS: frozenset[str] = frozenset({"mars", "saturn", "uranus", "pluto"})
# Rule codes that independently justify briga_grave
_CONFLICT_RULE_CODES: frozenset[str] = frozenset(
    {"conflict_relationship", "extreme_conflict", "breakup", "sudden_break"}
)
# Window duration above which assertive "briga grave" language is softened
_LONG_WINDOW_DAYS: int = 90


def _pt_planet(raw: str) -> str:
    """Translate a raw planet key to Portuguese."""
    clean = raw.replace("_", " ").strip()
    return _PLANET_NAMES_PT.get(
        clean, _PLANET_NAMES_PT.get(clean.title(), clean.title() if clean else clean)
    )


def _is_self_aspect(signal: dict[str, Any]) -> bool:
    """Return True when a signal has the same planet on both sides (e.g. Pluto/Pluto).

    Generational progressions like progressed Pluto conjunct natal Pluto are not
    individually meaningful and should be filtered from primary explanations.
    Delegates to astro_confirmation.is_self_aspect for consistency.
    """
    return _ac_is_self_aspect(signal)


def _meaningful_signals_for_display(
    signals: list[dict[str, Any]],
    *,
    subtype_key: str | None = None,
) -> list[dict[str, Any]]:
    """Signals for por_que / bullets: no self-aspects, no outer–outer generational pairs."""
    cleaned = filter_generational_pairs(signals)
    if subtype_key in {
        "separacao_termino", "separacao_abrupta", "briga_forte", "briga_grave",
        "afastamento_emocional", "afastamento", "ciume_posse",
    }:
        from engine.signal_enrichment import HARD_ASPECTS

        slow_hard = [
            s for s in cleaned
            if str(s.get("technique") or "") == "transits"
            and str((s.get("evidence") or {}).get("aspect") or "") in HARD_ASPECTS
            and (
                str((s.get("evidence") or {}).get("planet_a") or "").replace("_", " ").lower()
                in {"saturn", "uranus", "neptune", "pluto"}
                or str((s.get("evidence") or {}).get("planet_b") or "").replace("_", " ").lower()
                in {"saturn", "uranus", "neptune", "pluto"}
            )
        ]
        if slow_hard:
            cleaned = [
                s for s in cleaned
                if not (
                    str(s.get("technique") or "") == "transits"
                    and str((s.get("evidence") or {}).get("planet_a") or "").replace("_", " ").lower()
                    in _FAST_MOVERS
                    and str((s.get("evidence") or {}).get("planet_b") or "").replace("_", " ").lower()
                    in {"jupiter", "sun", "moon", "mercury", "venus"}
                )
            ] or cleaned
    return sorted(cleaned, key=lambda s: (-score_signal(s), str(s.get("label") or "")))


def _has_fast_mover_transit(signals: list[dict[str, Any]]) -> bool:
    """Return True if at least one transit involves a fast-moving planet."""
    for s in signals:
        if str(s.get("technique") or "") != "transits":
            continue
        pa = str((s.get("evidence") or {}).get("planet_a") or "").replace("_", " ").lower()
        if pa in _FAST_MOVERS:
            return True
    return False


def _has_conflict_planet_in_7_or_rule(
    signals: list[dict[str, Any]],
    rule_hits: list[dict[str, Any]],
) -> bool:
    """Return True when Mars/Saturn/Uranus/Pluto activates house 7, or a conflict rule fires."""
    for s in signals:
        ev = s.get("evidence") or {}
        house = ev.get("transit_house") or ev.get("natal_house")
        pa = str(ev.get("planet_a") or "").replace("_", " ").lower()
        if house == 7 and pa in _CONFLICT_PLANETS:
            return True
    for h in rule_hits:
        if str(h.get("code") or "") in _CONFLICT_RULE_CODES:
            return True
    return False


def _window_duration_days(time_window: dict[str, Any] | None) -> int:
    """Return the span in days between start and end of a time window dict."""
    if not time_window:
        return 0
    start = parse_iso_date(time_window.get("start"))
    end = parse_iso_date(time_window.get("end"))
    if start and end:
        return max(0, (end - start).days)
    return 0


# ---------------------------------------------------------------------------
# Tense aspect helper
# ---------------------------------------------------------------------------

_TENSE_ASPECTS: frozenset[str] = frozenset({"square", "opposition", "conjunction"})


def _has_tense_aspect(signals: list[dict[str, Any]]) -> bool:
    """Return True if any signal carries a tense planetary aspect."""
    for s in signals:
        if str((s.get("evidence") or {}).get("aspect") or "") in _TENSE_ASPECTS:
            return True
    return False


def _primary_source_label(signals: list[dict[str, Any]]) -> str:
    """Return 'astrologia' unless all signals are numerology-based."""
    for s in signals:
        if str(s.get("technique") or "") != "numerology":
            return "astrologia"
    return "numerologia" if signals else "astrologia"


_TECHNIQUE_LABELS_PT: dict[str, str] = {
    "transits": "Trânsito",
    "progressions": "Progressão",
    "solar_return": "Retorno solar",
    "solar_arc": "Arco solar",
    "profections": "Profecção anual",
    "numerology": "Numerologia",
}

_HOUSE_THEMES: dict[int, str] = {
    1: "identidade", 2: "dinheiro", 3: "comunicação", 4: "família",
    5: "afeto", 6: "rotina e saúde", 7: "parcerias",
    8: "crises e recursos compartilhados", 9: "expansão", 10: "carreira",
    11: "rede e amigos", 12: "inconsciente e encerramentos",
}

_ASPECT_NAMES_PT: dict[str, str] = {
    "conjunction": "conjunção", "opposition": "oposição",
    "square": "quadratura", "trine": "trígono", "sextile": "sextil",
}


def _enrich_por_que(
    signals: list[dict[str, Any]],
    rule_hits: list[dict[str, Any]],
    matching_rule_codes: set[str],
    *,
    subtype_key: str | None = None,
) -> str:
    """Build a rich por_que string: 'Técnica: aspecto planeta_a/planeta_b, Casa N (tema)'.

    Self-aspects (planet A == planet B, e.g. progressed Pluto conjunct natal Pluto) are
    excluded because generational positions carry no individual predictive meaning.
    """
    parts: list[str] = []

    meaningful_signals = _meaningful_signals_for_display(signals, subtype_key=subtype_key)
    for s in meaningful_signals[:3]:
        technique = _TECHNIQUE_LABELS_PT.get(str(s.get("technique") or ""), "Técnica")
        evidence = dict(s.get("evidence") or {})
        label = str(s.get("label") or "").strip()
        aspect = _ASPECT_NAMES_PT.get(str(evidence.get("aspect") or ""), "")
        planet_a = _pt_planet(str(evidence.get("planet_a") or ""))
        planet_b = _pt_planet(str(evidence.get("planet_b") or ""))
        house = evidence.get("transit_house") or evidence.get("natal_house")
        house_str = (
            f", Casa {house} ({_HOUSE_THEMES.get(int(house), 'vida')})"
            if isinstance(house, int)
            else ""
        )

        if aspect and planet_a:
            piece = f"{technique}: {aspect} {planet_a}"
            # Only add planet_b if it's different from planet_a
            if planet_b and planet_b.lower() != planet_a.lower():
                piece += f"/{planet_b}"
            piece += house_str
        elif label:
            piece = f"{technique}: {label}{house_str}"
        else:
            continue
        parts.append(piece)

    for h in rule_hits[:2]:
        if str(h.get("code", "")) in matching_rule_codes and h.get("label"):
            parts.append(f"Regra: {h['label']}")

    brady_lines: list[str] = []
    for s in meaningful_signals[:2]:
        brady = format_brady_por_que_line(dict((s.get("evidence") or {})))
        if brady and brady not in parts:
            brady_lines.append(brady)
    if brady_lines:
        parts = brady_lines + parts

    if not parts:
        return "Convergência técnica detectada no mapa."
    return "; ".join(parts)


def _human_por_que_deduped(
    signals: list[dict[str, Any]],
    rule_hits: list[dict[str, Any]],
    matching_rule_codes: set[str],
    *,
    subtype_key: str | None = None,
) -> str:
    """
    Compact, deduplicated por_que for surface display:
    - Groups identical aspect+planet patterns across techniques
    - Shows 'X técnicas confirmam' when the same pattern repeats
    - Max 2 patterns + 1 rule
    """
    meaningful = _meaningful_signals_for_display(signals, subtype_key=subtype_key)

    pattern_counts: dict[str, int] = {}
    pattern_house: dict[str, str] = {}

    for s in meaningful:
        evidence = dict(s.get("evidence") or {})
        label = str(s.get("label") or "").strip()
        aspect = _ASPECT_NAMES_PT.get(str(evidence.get("aspect") or ""), "")
        planet_a = _pt_planet(str(evidence.get("planet_a") or ""))
        planet_b = _pt_planet(str(evidence.get("planet_b") or ""))
        house = evidence.get("transit_house") or evidence.get("natal_house")

        if aspect and planet_a:
            p_b_part = f"/{planet_b}" if (planet_b and planet_b.lower() != planet_a.lower()) else ""
            key = f"{aspect} {planet_a}{p_b_part}"
        elif label:
            key = label
        else:
            continue

        pattern_counts[key] = pattern_counts.get(key, 0) + 1
        if isinstance(house, int) and key not in pattern_house:
            pattern_house[key] = f", Casa {house} ({_HOUSE_THEMES.get(house, 'vida')})"

    parts: list[str] = []
    for key, count in list(pattern_counts.items())[:2]:
        house_str = pattern_house.get(key, "")
        tech_note = f" ({count} técnicas confirmam)" if count > 1 else ""
        parts.append(f"{key}{house_str}{tech_note}")

    for h in rule_hits[:1]:
        if str(h.get("code", "")) in matching_rule_codes and h.get("label"):
            rule_label = str(h["label"])
            if rule_label not in " ".join(parts):
                parts.append(rule_label)

    if not parts:
        return "Convergência técnica detectada no mapa."
    return "; ".join(parts)


# ---------------------------------------------------------------------------
# Subtype definitions
# ---------------------------------------------------------------------------

SUBTYPE_DEFINITIONS: dict[str, dict[str, Any]] = {
    # ─────────────────────────────────────────────────────────────────────────
    # RUPTURA — briga_grave / separacao_abrupta / afastamento
    # ─────────────────────────────────────────────────────────────────────────
    "briga_grave": {
        "label": "Briga grave",
        "category": "rupture",
        "rule_codes": {"relationship_test", "conflict_relationship", "extreme_conflict", "authority_conflict"},
        "priority_rule_codes": {"extreme_conflict"},
        "min_techniques": 2,
        "fatalistic_threshold": 3,
        "avoidability": (
            "Parcialmente evitável: parar a escalada exige ceder território antes que "
            "a discussão vire ponto de não retorno."
        ),
        "template": {
            "what": (
                "O mapa indica briga grave com {partner_role} ou alguém muito próximo. "
                "Não é desentendimento normal — é confronto que muda a relação de lugar."
            ),
            "when_note": (
                "O conflito tem mais força em {when_peak}. "
                "Antes disso, o desgaste já é visível."
            ),
            "scenarios": [
                "Uma conversa sobre limite, dinheiro ou lealdade escala sem controle e vira acusação direta.",
                "Desgaste acumulado explode na primeira brecha: tom errado, mensagem mal interpretada ou decisão unilateral.",
                "O confronto acontece mas ninguém cede — e o silêncio depois é pior que a briga.",
            ],
            "risk": (
                "Se não houver conversa honesta antes do pico, a briga pode virar "
                "afastamento prolongado ou separação."
            ),
            "action": (
                "Coloque o problema na mesa antes que ele escolha o momento de explodir. "
                "Limite claro agora evita explosão depois."
            ),
        },
    },

    "separacao_abrupta": {
        "label": "Separação abrupta",
        "category": "rupture",
        "rule_codes": {"breakup", "sudden_break", "intense_relationship"},
        "priority_rule_codes": {"breakup", "sudden_break"},
        "min_techniques": 2,
        "fatalistic_threshold": 3,
        "avoidability": (
            "Difícil de evitar quando Urano ou Plutão estão no eixo de Vênus — "
            "o ciclo quer ruptura. Dá para conduzir com dignidade."
        ),
        "template": {
            "what": (
                "Há risco real de separação abrupta com {partner_role} — corte que acontece rápido, "
                "sem muito aviso prévio, e que muda a estrutura de vida."
            ),
            "when_note": (
                "A ruptura tem mais força em {when_peak}. "
                "Se já existe desgaste ativo, pode vir antes disso."
            ),
            "scenarios": [
                "A relação com {partner_role} termina de forma abrupta — decisão tomada, não negociada.",
                "Um evento externo (descoberta, traição, revelação) força o corte antes de qualquer conversa planejada.",
                "Você decide sair antes que o desgaste vire humilhação ou dependência.",
            ],
            "risk": (
                "Se a separação vier sem preparo, o impacto em moradia, finanças e "
                "rede emocional é muito maior."
            ),
            "action": (
                "Prepare cenário de saída antes do pico. "
                "Questões práticas (moradia, finanças) devem ser pensadas agora."
            ),
        },
    },

    "afastamento": {
        "label": "Afastamento emocional",
        "category": "rupture",
        "rule_codes": {"emotional_cut", "deep_emotional_break", "relationship_block"},
        "priority_rule_codes": {"deep_emotional_break"},
        "min_techniques": 2,
        "fatalistic_threshold": 3,
        "avoidability": (
            "Parcialmente evitável: afastamento emocional pode ser reduzido com "
            "comunicação direta, mas o esfriamento do ciclo não desaparece."
        ),
        "template": {
            "what": (
                "O mapa mostra afastamento emocional progressivo com {partner_role} — "
                "não necessariamente separação formal, mas distância que cresce e "
                "muda a qualidade do vínculo."
            ),
            "when_note": (
                "O esfriamento é mais intenso em {when_peak}. "
                "Antes disso, o padrão de distância já está ativo."
            ),
            "scenarios": [
                "A relação com {partner_role} resfria: menos conversa, menos presença, menos iniciativa dos dois lados.",
                "Um familiar ou amigo próximo se afasta sem explicação clara, deixando peso e confusão.",
                "Você se fecha emocionalmente como proteção — e o outro interpreta como rejeição.",
            ],
            "risk": (
                "Se o afastamento não for nomeado, ele vira padrão permanente — "
                "e a relação fica em modo de sobrevivência."
            ),
            "action": (
                "Nomeie o afastamento em vez de esperar que passe. "
                "Pergunte o que mudou antes que o silêncio vire norma."
            ),
        },
    },

    # ─────────────────────────────────────────────────────────────────────────
    # RUPTURA ESPECÍFICA — separacao_termino / briga_forte / ciume_posse
    #                    / afastamento_emocional / conversa_seria / tensao_leve
    # ─────────────────────────────────────────────────────────────────────────

    "separacao_termino": {
        "label": "Separação ou término de vínculo",
        "category": "rupture",
        "rule_codes": {"breakup", "sudden_break", "intense_relationship", "emotional_cut", "deep_emotional_break"},
        "priority_rule_codes": {"breakup", "deep_emotional_break"},
        "min_techniques": 3,
        "fatalistic_threshold": 3,
        "avoidability": (
            "Difícil de evitar quando Saturno, Urano ou Plutão pressionam a Casa 7 — "
            "o ciclo quer encerramento. Dá para atravessar com dignidade e clareza."
        ),
        "template": {
            "what": (
                "O mapa indica pressão real de término ou encerramento do vínculo com "
                "{partner_role}. Não é briga passageira: são sinais lentos que pedem definição."
            ),
            "when_note": (
                "A pressão é mais intensa em {when_peak}. "
                "Se já existe desgaste, o processo pode começar antes disso."
            ),
            "scenarios": [
                "A relação com {partner_role} chega ao ponto de definição — continuar exige mudança real, ou encerrar.",
                "Saturno ou Plutão sobre a Casa 7 cobram maturidade: vínculos que não têm base real tendem a se desfazer.",
                "Uma conversa final define rumo com clareza — o que não serve mais é liberado.",
            ],
            "risk": (
                "Ignorar os sinais de encerramento pode atrasar o processo mas não o cancela — "
                "e a separação sem preparo é mais cara emocionalmente."
            ),
            "action": (
                "Examine o que ainda sustenta o vínculo. "
                "Se a resposta for hábito ou medo, o mapa está pedindo uma decisão honesta."
            ),
        },
    },

    "briga_forte": {
        "label": "Briga forte ou confronto direto",
        "category": "rupture",
        "rule_codes": {"conflict_relationship", "extreme_conflict", "relationship_test"},
        "priority_rule_codes": {"extreme_conflict", "conflict_relationship"},
        "min_techniques": 2,
        "fatalistic_threshold": 3,
        "avoidability": (
            "Parcialmente evitável: Marte não some do mapa, mas o confronto pode ser "
            "conduzido em vez de explodir. Limite claro antes do pico reduz o dano."
        ),
        "template": {
            "what": (
                "O mapa indica briga forte com {partner_role} ou pessoa próxima. "
                "Marte ativo gera pressão de confronto que dificilmente passa sem discussão direta."
            ),
            "when_note": (
                "O confronto tem mais força em {when_peak}. "
                "Antes disso, a tensão já está acumulando — e pode explodir em qualquer brecha."
            ),
            "scenarios": [
                "Discussão direta onde tom sobe, acusações aparecem e ninguém cede facilmente.",
                "Um ponto de atrito que existia há tempo explode no primeiro gatilho: palavras erradas, decisão unilateral.",
                "Confronto que define limite real — pode ser necessário, mas exige condução consciente.",
            ],
            "risk": (
                "Se a briga não tiver resolução, pode virar afastamento ou "
                "abrir ferida que demora muito para cicatrizar."
            ),
            "action": (
                "Escolha o momento e o tom. "
                "Confrontar com clareza é diferente de atacar no impulso — Marte tende ao segundo."
            ),
        },
    },

    "ciume_posse": {
        "label": "Ciúme, controle ou dinâmica possessiva",
        "category": "rupture",
        "rule_codes": {"intense_relationship", "conflict_relationship", "relationship_test", "emotional_bond"},
        "priority_rule_codes": {"intense_relationship"},
        "min_techniques": 2,
        "fatalistic_threshold": 3,
        "avoidability": (
            "Parcialmente evitável: a dinâmica de possessividade vem de dentro, "
            "não apenas do outro. Reconhecer isso muda o padrão."
        ),
        "template": {
            "what": (
                "O mapa ativa dinâmica de ciúme, controle ou possessividade intensa "
                "com {partner_role} — Plutão, Marte e Lua em tensão criam campo de intensidade "
                "que pode virar disputa de poder ou isolamento emocional."
            ),
            "when_note": "A intensidade é mais alta em {when_peak}.",
            "scenarios": [
                "Ciúme desproporcional a partir de insegurança — real ou projetada — que gera cobranças e vigilância.",
                "Controle sutil ou explícito: quem você vê, como se posiciona, onde vai.",
                "Dinâmica de posse onde os dois se prendem por intensidade, mesmo quando a relação não funciona mais.",
            ],
            "risk": (
                "Se o padrão possessivo não for nomeado, ele se normaliza e vira "
                "prisão emocional para os dois lados."
            ),
            "action": (
                "Nomeie a dinâmica com clareza — ciúme, controle ou medo de perder. "
                "A conversa que parece impossível é exatamente a que resolve."
            ),
        },
    },

    "afastamento_emocional": {
        "label": "Afastamento emocional gradual",
        "category": "rupture",
        "rule_codes": {"emotional_cut", "deep_emotional_break", "relationship_block"},
        "priority_rule_codes": {"deep_emotional_break"},
        "min_techniques": 2,
        "fatalistic_threshold": 3,
        "avoidability": (
            "Parcialmente evitável: Saturno resfria e cria distância, mas não força "
            "separação formal. Comunicação direta ainda muda o resultado."
        ),
        "template": {
            "what": (
                "O mapa mostra afastamento emocional com {partner_role} — "
                "Saturno ou pressão lenta sobre Vênus ou a Casa 7 cria distância que cresce "
                "sem confronto direto. Não é briga: é esfriamento."
            ),
            "when_note": (
                "O esfriamento é mais intenso em {when_peak}. "
                "Antes disso, os sinais de distância já estão ativos."
            ),
            "scenarios": [
                "A relação com {partner_role} resfria: menos presença, menos iniciativa, menos conexão real.",
                "Saturno sobre a Casa 7 ou Vênus cobra responsabilidade — quem não se compromete vai sendo deixado para trás.",
                "Você se fecha emocionalmente como proteção, e o outro interpreta como desinteresse.",
            ],
            "risk": (
                "Se o afastamento não for nomeado, ele vira padrão permanente — "
                "e a relação fica em modo de sobrevivência até um dos dois sair."
            ),
            "action": (
                "Nomeie o que mudou antes que o silêncio vire norma. "
                "Saturno responde a compromisso claro, não a esperança passiva."
            ),
        },
    },

    "conversa_seria": {
        "label": "Conversa séria ou definição verbal",
        "category": "rupture",
        "rule_codes": {"relationship_test", "conflict_relationship", "relationship_block"},
        "priority_rule_codes": set(),
        "min_techniques": 2,
        "fatalistic_threshold": 4,
        "avoidability": (
            "Evitável como conflito: Mercúrio ativo pede conversa, não briga. "
            "A conversa que parece difícil resolve mais do que o silêncio."
        ),
        "template": {
            "what": (
                "O mapa indica necessidade de conversa séria com {partner_role} — "
                "Mercúrio ativado aponta para definição verbal, esclarecimento ou "
                "alinhamento de expectativas. Não é briga: é diálogo que precisa acontecer."
            ),
            "when_note": "O momento mais propício para a conversa é em {when_peak}.",
            "scenarios": [
                "Uma conversa que vinha sendo adiada chega ao ponto de não poder mais ser ignorada.",
                "Mercúrio em tensão com Saturno ou Netuno aponta para mal-entendido que precisa de esclarecimento direto.",
                "Alinhamento verbal sobre limites, expectativas ou decisão importante que afeta os dois.",
            ],
            "risk": (
                "Se a conversa não acontecer, o mal-entendido se acumula e "
                "vira ressentimento ou afastamento silencioso."
            ),
            "action": (
                "Escolha o momento e diga o que precisa ser dito. "
                "Clareza agora evita explosão depois."
            ),
        },
    },

    "tensao_leve": {
        "label": "Tensão leve ou clima tenso passageiro",
        "category": "rupture",
        "rule_codes": {"relationship_test", "conflict_relationship"},
        "priority_rule_codes": set(),
        "min_techniques": 1,
        "fatalistic_threshold": 5,
        "avoidability": (
            "Evitável: trânsito rápido sem planeta lento — a tensão passa em dias. "
            "Não reage no impulso."
        ),
        "template": {
            "what": (
                "O mapa mostra tensão leve ou clima mais carregado com {partner_role} — "
                "trânsito rápido que passa em poucos dias. Não é briga grave nem separação: "
                "é irritação, desgaste ou sensibilidade elevada temporária."
            ),
            "when_note": "A tensão é mais perceptível em {when_peak}, mas tende a passar rapidamente.",
            "scenarios": [
                "Clima mais tenso do que o normal: palavras que saem erradas, irritação sem motivo claro.",
                "Sensibilidade elevada que faz pequenos atritos parecerem maiores do que são.",
                "Desentendimento passageiro que, se não for amplificado, não deixa rastro.",
            ],
            "risk": "Se você reagir no impulso durante o pico, o que seria desentendimento pode virar briga real.",
            "action": (
                "Aguarde o pico passar antes de tomar decisão sobre a relação. "
                "Trânsito rápido não define o vínculo."
            ),
        },
    },

    # ─────────────────────────────────────────────────────────────────────────
    # SAÚDE — doenca_leve / crise_saude / cronico
    # ─────────────────────────────────────────────────────────────────────────
    "doenca_leve": {
        "label": "Mal-estar ou esgotamento leve",
        "category": "health",
        "rule_codes": {"emotional_low"},
        "priority_rule_codes": set(),
        "min_techniques": 2,
        "fatalistic_threshold": 4,
        "avoidability": "Evitável com repouso e corte de excesso antes do pico.",
        "template": {
            "what": (
                "O mapa aponta desgaste acumulado que pode virar mal-estar físico: "
                "queda de imunidade, falta de sono ou disposição reduzida por alguns dias."
            ),
            "when_note": (
                "O período mais sensível é {when_peak}. "
                "Antes disso, o cansaço já está acumulando."
            ),
            "scenarios": [
                "Dias de baixa energia onde nada rende e qualquer esforço parece excessivo.",
                "Sono ruim, apetite alterado ou indisposição que exige reduzir o ritmo.",
                "Pequena gripe, resfriado ou processo inflamatório que obriga uma pausa.",
            ],
            "risk": "Se ignorado, pode virar afastamento ou crise mais séria.",
            "action": "Durma mais, coma bem e corte agenda não essencial nesse período.",
        },
    },

    "crise_saude": {
        "label": "Crise de saúde ou risco de acidente",
        "category": "health",
        "rule_codes": {"accident_risk", "extreme_conflict"},
        "priority_rule_codes": {"accident_risk"},
        "min_techniques": 2,
        "fatalistic_threshold": 3,
        "avoidability": (
            "Parcialmente evitável: o risco não some, mas cautela ao dirigir, "
            "evitar pressa e reduzir impulsividade diminuem a exposição."
        ),
        "template": {
            "what": (
                "O mapa indica pressão real de risco físico: Marte em ângulo tenso com Saturno "
                "ativa sobrecarga, atrito e probabilidade elevada de acidente ou "
                "crise de saúde mais séria."
            ),
            "when_note": "O risco é mais alto em {when_peak}. Atenção redobrada nesse período.",
            "scenarios": [
                "Acidente em trânsito, queda ou impacto físico por pressa, distração ou irritação.",
                "Crise de saúde que exige atendimento médico urgente — problema latente se manifesta.",
                "Sobrecarga extrema de trabalho e tensão que resulta em colapso físico ou emocional.",
            ],
            "risk": (
                "Ignorar os sinais de alerta pode resultar em afastamento longo, "
                "cirurgia ou consequência financeira."
            ),
            "action": (
                "Evite pressa no trânsito, não tome decisões impulsivas em momentos de "
                "irritação e antecipe consultas médicas se houver sintoma."
            ),
        },
    },

    "cronico": {
        "label": "Processo crônico ou transformação psicológica",
        "category": "health",
        "rule_codes": {"psychological_transformation", "emotional_low"},
        "priority_rule_codes": {"psychological_transformation"},
        "min_techniques": 2,
        "fatalistic_threshold": 3,
        "avoidability": (
            "Não evitável como ciclo: é transformação profunda. "
            "Dá para conduzir com apoio terapêutico."
        ),
        "template": {
            "what": (
                "O mapa aponta processo de transformação psicológica profunda — "
                "não é crise aguda, é um período de reorganização interna que afeta "
                "saúde, humor e percepção de identidade."
            ),
            "when_note": (
                "O processo está ativo durante {when_range}. "
                "O pico de intensidade ocorre em {when_peak}."
            ),
            "scenarios": [
                "Período de terapia, análise ou trabalho interior intenso que transforma padrões antigos.",
                "Sintoma físico sem causa orgânica clara — o corpo processando o que a mente não quer enfrentar.",
                "Fase de luto, desapego ou reconfiguração de identidade que leva meses.",
            ],
            "risk": (
                "Sem suporte, o processo pode virar depressão, isolamento ou "
                "uso de subterfúgios para não sentir."
            ),
            "action": (
                "Busque acompanhamento terapêutico, reduza exigências externas e "
                "permita que o processo aconteça sem forçar normalidade."
            ),
        },
    },

    "acidente_fisico": {
        "label": "Acidente ou risco físico",
        "category": "health",
        "rule_codes": {"accident_risk", "extreme_conflict"},
        "priority_rule_codes": {"accident_risk"},
        "min_techniques": 2,
        "fatalistic_threshold": 3,
        "avoidability": (
            "Parcialmente evitável: atenção redobrada no trânsito, evitar pressa e "
            "impulsividade reduz o risco — mas o período pede cautela real."
        ),
        "template": {
            "what": (
                "O mapa indica risco físico elevado: Marte em ângulo tenso ativa "
                "probabilidade real de acidente, queda, impacto ou lesão corporal."
            ),
            "when_note": "O risco é mais alto em {when_peak}. Atenção máxima nesse período.",
            "scenarios": [
                "Acidente no trânsito causado por pressa, distração ou irritação ao volante.",
                "Queda, impacto ou lesão física em atividade do dia a dia.",
                "Procedimento médico ou cirúrgico com complicação inesperada.",
            ],
            "risk": (
                "Ignorar os sinais de alerta pode resultar em afastamento prolongado, "
                "cirurgia ou consequência financeira séria."
            ),
            "action": (
                "Evite dirigir em estado de irritação, não tome decisões físicas "
                "impulsivas e antecipe consultas médicas se houver sintoma."
            ),
        },
    },

    "acidente_emocional": {
        "label": "Colapso ou trauma emocional",
        "category": "health",
        "rule_codes": {"emotional_low", "psychological_transformation", "deep_emotional_break"},
        "priority_rule_codes": {"psychological_transformation"},
        "min_techniques": 2,
        "fatalistic_threshold": 3,
        "avoidability": (
            "Não evitável como processo: o colapso emocional é transformação forçada. "
            "Dá para atravessar com suporte terapêutico."
        ),
        "template": {
            "what": (
                "O mapa aponta colapso ou trauma emocional: não é doença física, "
                "é ruptura interna que derruba funcionamento, humor e senso de identidade."
            ),
            "when_note": (
                "O período mais intenso é {when_peak}. "
                "Antes disso, os sinais de alerta já estão presentes."
            ),
            "scenarios": [
                "Crise de choro, paralisia emocional ou incapacidade temporária de funcionar normalmente.",
                "Revelação ou evento externo que abala estrutura psicológica construída por anos.",
                "Colapso de crença, propósito ou vínculo que sustentava a identidade.",
            ],
            "risk": (
                "Sem suporte, o trauma pode virar depressão, isolamento ou "
                "dissociação prolongada."
            ),
            "action": (
                "Busque acompanhamento terapêutico agora, não espere o colapso para pedir ajuda. "
                "Reduza exigências externas e permita que o processo aconteça."
            ),
        },
    },

    "risco_fisico_agudo": {
        "label": "Risco físico agudo",
        "category": "health",
        "rule_codes": {"accident_risk", "extreme_conflict"},
        "priority_rule_codes": {"accident_risk"},
        "min_techniques": 2,
        "fatalistic_threshold": 3,
        "avoidability": (
            "Parcialmente evitável: cautela no trânsito e redução de impulsividade "
            "diminuem exposição em dias-semanas de pico."
        ),
        "template": {
            "what": (
                "O mapa indica risco físico agudo (Marte/Urano tenso a corpo, ASC ou casas 6/8): "
                "acidente, lesão ou crise somática em janela curta — não processo crônico lento."
            ),
            "when_note": "Pico de risco em {when_peak} (dias a semanas).",
            "scenarios": [
                "Acidente por pressa, irritação ou distração no trânsito.",
                "Lesão súbita em atividade física ou trabalho sob pressão.",
                "Crise aguda que exige atendimento imediato.",
            ],
            "risk": "Ignorar o pico aumenta chance de afastamento ou complicação.",
            "action": "Evite pressa e impulsividade no pico; antecipe consulta se houver sintoma.",
        },
    },

    "doenca_cronica": {
        "label": "Doença ou limitação crônica",
        "category": "health",
        "rule_codes": {"psychological_transformation", "emotional_low"},
        "priority_rule_codes": set(),
        "min_techniques": 2,
        "fatalistic_threshold": 4,
        "avoidability": (
            "Ciclo prolongado: exige acompanhamento médico e rotina sustentável; "
            "não some com repouso de um fim de semana."
        ),
        "template": {
            "what": (
                "Saturno tenso nas casas 6/12 (ou ao regente da saúde) aponta processo "
                "crônico, limitação de energia ou doença de arrasto — não crise de um dia."
            ),
            "when_note": "Tema ativo em {when_range}; intensidade em {when_peak}.",
            "scenarios": [
                "Sintomas recorrentes que exigem investigação e rotina de tratamento.",
                "Esgotamento estrutural por excesso de responsabilidade.",
                "Reorganização forçada de hábitos por limitação física.",
            ],
            "risk": "Sem tratamento, o quadro cristaliza em padrão crônico.",
            "action": "Monte rotina médica e de sono; não normalize o cansaço como 'só estresse'.",
        },
    },

    "esgotamento_confusao": {
        "label": "Esgotamento e confusão (Netuno)",
        "category": "health",
        "rule_codes": {"emotional_low", "psychological_transformation"},
        "priority_rule_codes": set(),
        "min_techniques": 2,
        "fatalistic_threshold": 4,
        "avoidability": (
            "Reduzível com limites, sono e clareza de diagnóstico; "
            "evitar álcool, fuga e autodiagnóstico."
        ),
        "template": {
            "what": (
                "Netuno tenso ao Sol, ASC ou casa 6: névoa mental, esgotamento difuso, "
                "hipersensibilidade ou confusão entre cansaço físico e sobrecarga emocional."
            ),
            "when_note": "Névoa mais densa em {when_peak}.",
            "scenarios": [
                "Sono não reparador e dificuldade de concentração por semanas.",
                "Sensação de 'estar no automático' ou desorientado.",
                "Risco de mascarar problema orgânico com exaustão emocional.",
            ],
            "risk": "Sem limites, pode virar burnout ou uso de escape (substâncias, fuga).",
            "action": "Priorize sono, reduza estímulos e busque avaliação médica se persistir.",
        },
    },

    # ─────────────────────────────────────────────────────────────────────────
    # CARREIRA — emprego_novo / perda_emprego / pressao_carreira
    # ─────────────────────────────────────────────────────────────────────────
    "emprego_novo": {
        "label": "Emprego novo ou oportunidade profissional",
        "category": "career",
        "rule_codes": {"career_growth", "career_change", "career_transformation", "love_expansion"},
        "priority_rule_codes": {"career_growth"},
        "polarity_required": "supportive",
        "min_techniques": 2,
        "fatalistic_threshold": 3,
        "avoidability": "Não precisa evitar — precisa agir. A janela tem prazo.",
        "template": {
            "what": (
                "O mapa abre janela de oportunidade profissional concreta: "
                "nova posição, proposta de trabalho, promoção ou mudança de função."
            ),
            "when_note": (
                "A janela está mais aberta em {when_peak}. "
                "Depois disso, a oportunidade pode fechar ou mudar de forma."
            ),
            "scenarios": [
                "Proposta de emprego ou projeto novo aparece — e cobra resposta rápida.",
                "Promoção, expansão de responsabilidade ou mudança de cargo dentro da empresa atual.",
                "Transição de carreira que abre caminho novo mas exige reposicionamento e aprendizado.",
            ],
            "risk": (
                "Se você hesitar ou esperar por certeza total, "
                "a janela pode fechar antes de você decidir."
            ),
            "action": (
                "Atualize currículo, ative contatos e esteja pronto para negociar "
                "rapidamente quando a proposta aparecer."
            ),
        },
    },

    "perda_emprego": {
        "label": "Risco de demissão ou perda de emprego",
        "category": "career",
        "rule_codes": {"career_block", "career_reset", "authority_conflict"},
        "priority_rule_codes": {"career_reset"},
        "polarity_required": "challenging",
        "min_techniques": 2,
        "fatalistic_threshold": 3,
        "avoidability": (
            "Parcialmente evitável: se o ambiente já está instável, "
            "o ciclo tende a forçar saída. Prepare plano B agora."
        ),
        "template": {
            "what": (
                "O mapa indica risco real de perda de emprego, demissão ou saída forçada "
                "da posição atual — especialmente se o ambiente já está fragilizado."
            ),
            "when_note": (
                "O risco é mais alto em {when_peak}. "
                "Se houver sinais de instabilidade no trabalho antes disso, "
                "o processo pode começar antes."
            ),
            "scenarios": [
                "Demissão direta, corte de posição ou reestruturação que elimina sua função.",
                "Conflito com chefia ou empresa que torna o ambiente insustentável e força saída.",
                "Você decide sair antes de ser mandado embora — o ciclo empurra para novo começo.",
            ],
            "risk": (
                "Sem reserva financeira e currículo atualizado, "
                "a perda do emprego pode virar crise financeira séria."
            ),
            "action": (
                "Monte reserva emergencial imediatamente, atualize currículo e "
                "ative rede de contatos antes do pico do ciclo."
            ),
        },
    },

    "pressao_carreira": {
        "label": "Pressão profissional intensa",
        "category": "career",
        "rule_codes": {"career_pressure", "career_conflict", "authority_conflict", "career_block"},
        "priority_rule_codes": {"career_pressure", "career_conflict"},
        "min_techniques": 2,
        "fatalistic_threshold": 3,
        "avoidability": (
            "Parcialmente evitável: não dá para eliminar a pressão, "
            "mas dá para não deixar ela virar demissão ou colapso."
        ),
        "template": {
            "what": (
                "O mapa indica fase de pressão profissional intensa: cobranças aumentam, "
                "prazos apertam, conflito com autoridade cresce — "
                "sem necessariamente virar demissão."
            ),
            "when_note": "A pressão é mais intensa em {when_peak}. Prepare-se antes.",
            "scenarios": [
                "Chefe ou cliente aumenta cobrança de forma que parece injusta ou excessiva.",
                "Prazo impossível, meta inatingível ou mudança de regras que coloca você em desvantagem.",
                "Atrito com colega ou superior que exige escolha entre ceder ou confrontar.",
            ],
            "risk": (
                "Se a pressão não for gerenciada, pode virar burnout, "
                "pedido de demissão impulsivo ou conflito grave."
            ),
            "action": (
                "Documente tudo, negocie prazos com antecedência e "
                "não entre em confronto direto sem estratégia."
            ),
        },
    },

    "auditoria_carreira_ou_demissao": {
        "label": "Auditoria, corte ou demissão",
        "category": "career",
        "rule_codes": {"career_block", "career_reset", "authority_conflict", "career_pressure"},
        "priority_rule_codes": {"career_reset"},
        "polarity_required": "challenging",
        "min_techniques": 2,
        "fatalistic_threshold": 3,
        "avoidability": (
            "Prepare documentação e plano B; Saturno/Plutão no MC/10 exigem "
            "responsabilização estrutural, não só 'passar raiva'."
        ),
        "template": {
            "what": (
                "Saturno ou Plutão tenso no MC ou casa 10: auditoria, corte, demissão "
                "ou reestruturação que redefine status profissional."
            ),
            "when_note": "Pressão institucional mais forte em {when_peak}.",
            "scenarios": [
                "Revisão de metas com chefe ou RH que pode terminar em saída.",
                "Corte de equipe ou função eliminada na reorganização.",
                "Demissão após período de cobrança e prova de resultado.",
            ],
            "risk": "Sem reserva e rede ativa, vira crise financeira em cadeia.",
            "action": "Documente entregas, atualize currículo e ative contatos antes do pico.",
        },
    },

    "mudanca_abrupta_carreira": {
        "label": "Mudança abrupta de carreira",
        "category": "career",
        "rule_codes": {"career_change", "career_reset", "sudden_break"},
        "priority_rule_codes": {"career_change"},
        "min_techniques": 2,
        "fatalistic_threshold": 3,
        "avoidability": (
            "Urano no MC/ASC pede ruptura — dá para canalizar como salto planejado, "
            "não só demissão-surpresa."
        ),
        "template": {
            "what": (
                "Urano ativo no MC ou ASC: virada rápida de carreira, função ou imagem "
                "pública — muitas vezes sem aviso longo."
            ),
            "when_note": "Ruptura ou oportunidade súbita em {when_peak}.",
            "scenarios": [
                "Pedido de demissão impulsivo ou saída por insatisfação repentina.",
                "Proposta inesperada que muda cidade, setor ou modelo de trabalho.",
                "Reorganização que te coloca em papel totalmente novo.",
            ],
            "risk": "Decidir no impulso sem plano financeiro aumenta o custo da virada.",
            "action": "Separe o que é libertação do que é fuga; valide com prazo de 48h antes de cortar.",
        },
    },

    # ─────────────────────────────────────────────────────────────────────────
    # FINANÇAS — ganho_financeiro / perda_financeira
    # ─────────────────────────────────────────────────────────────────────────
    "ganho_financeiro": {
        "label": "Ganho ou entrada financeira",
        "category": "finance",
        "rule_codes": {"financial_gain", "money_flow", "unexpected_money"},
        "priority_rule_codes": {"financial_gain"},
        "min_techniques": 2,
        "fatalistic_threshold": 3,
        "avoidability": "Não precisa evitar. Use a janela para consolidar — não para gastar impulsivamente.",
        "template": {
            "what": (
                "O mapa indica entrada ou melhora financeira concreta: "
                "aumento, bônus, venda, herança ou oportunidade que traz dinheiro novo."
            ),
            "when_note": "A janela de entrada é mais favorável em {when_peak}.",
            "scenarios": [
                "Aumento de salário, bônus ou premiação que melhora a situação imediata.",
                "Venda de bem, recebimento de dívida ou entrada de dinheiro inesperado.",
                "Oportunidade de investimento ou negócio que traz retorno real.",
            ],
            "risk": (
                "Se não houver planejamento, o ganho vai embora antes de "
                "mudar a estrutura financeira."
            ),
            "action": (
                "Planeje onde vai o dinheiro antes de recebê-lo. "
                "Reserve parte, quite prioridade, depois gaste."
            ),
        },
    },

    "ganho_crescimento": {
        "label": "Ganho e crescimento (Júpiter)",
        "category": "finance",
        "rule_codes": {"financial_gain", "money_flow", "career_growth"},
        "priority_rule_codes": {"financial_gain", "career_growth"},
        "polarity_required": "supportive",
        "min_techniques": 2,
        "fatalistic_threshold": 3,
        "avoidability": "Exige dignidade e ausência de aflição forte a Júpiter; senão vira oportunidade fraca.",
        "template": {
            "what": (
                "Júpiter nas casas 2 ou 10 sem aflição pesada: expansão de renda, "
                "promoção ou entrada que aumenta margem real."
            ),
            "when_note": "Janela de crescimento em {when_peak}.",
            "scenarios": [
                "Aumento, bônus ou contrato melhor que amplia capacidade financeira.",
                "Negócio ou investimento com retorno visível no curto prazo.",
                "Reconhecimento profissional que abre porta de ganho.",
            ],
            "risk": "Ganho sem planejamento evapora; trígono fraco a receptor debilitado ilude.",
            "action": "Confirme se Júpiter não está apenas 'conforto ilusório'; planeje destino do recurso.",
        },
    },

    "aperto_financeiro": {
        "label": "Aperto financeiro (Saturno)",
        "category": "finance",
        "rule_codes": {"financial_restriction", "financial_loss", "career_block"},
        "priority_rule_codes": {"financial_restriction"},
        "polarity_required": "challenging",
        "min_techniques": 2,
        "fatalistic_threshold": 3,
        "avoidability": (
            "Contenção e renegociação antecipada reduzem dano; "
            "Saturno na casa 2 cobra disciplina, não milagre."
        ),
        "template": {
            "what": (
                "Saturno tenso na casa 2 ou ao regente financeiro: aperto, corte de gastos, "
                "dívida que vence ou queda de margem."
            ),
            "when_note": "Aperto mais intenso em {when_peak}.",
            "scenarios": [
                "Conta inesperada ou queda de renda que exige plano de corte.",
                "Renegociação de dívida ou adiamento de projeto por falta de caixa.",
                "Medo real de não fechar o mês — pede priorização brutal.",
            ],
            "risk": "Postergar o corte transforma aperto em inadimplência.",
            "action": "Liste gastos fixos, renegocie o que der e congele supérfluo antes do pico.",
        },
    },

    "perda_financeira": {
        "label": "Perda ou aperto financeiro",
        "category": "finance",
        "rule_codes": {"financial_restriction", "financial_loss", "financial_transformation"},
        "priority_rule_codes": {"financial_loss"},
        "min_techniques": 2,
        "fatalistic_threshold": 3,
        "avoidability": (
            "Parcialmente evitável: o ciclo aperta, mas dá para reduzir o impacto "
            "com corte de gastos e negociação antecipada."
        ),
        "template": {
            "what": (
                "O mapa indica aperto financeiro, perda de renda ou "
                "reestruturação forçada de gastos. "
                "O período pede menos risco e mais contenção."
            ),
            "when_note": "O aperto é mais intenso em {when_peak}. Prepare-se antes de chegar nessa data.",
            "scenarios": [
                "Perda de renda, corte de salário ou gasto inesperado que desequilibra o orçamento.",
                "Dívida que vence, investimento que não retorna ou custo imprevisto que compromete reserva.",
                "Reestruturação financeira forçada: precisa cortar, renegociar e reorganizar do zero.",
            ],
            "risk": (
                "Se não houver contenção prévia, o aperto pode virar "
                "dívida, dependência ou crise prolongada."
            ),
            "action": (
                "Corte gastos não essenciais agora, renegocie dívidas antes do vencimento "
                "e evite investimento de risco nesse período."
            ),
        },
    },

    # ─────────────────────────────────────────────────────────────────────────
    # RELACIONAMENTOS — compromisso / crise_afetiva / filhos
    # ─────────────────────────────────────────────────────────────────────────
    "compromisso": {
        "label": "Compromisso ou definição afetiva",
        "category": "relationships",
        "rule_codes": {"marriage_window", "commitment", "love_expansion", "relationship_start"},
        "priority_rule_codes": {"marriage_window", "commitment"},
        "min_techniques": 2,
        "fatalistic_threshold": 3,
        "avoidability": (
            "Não precisa evitar — é janela favorável. Mas requer ação: "
            "não espere o outro se comprometer sozinho."
        ),
        "template": {
            "what": (
                "O mapa abre janela de compromisso afetivo real: namoro oficial, noivado, "
                "casamento, morar junto ou conversa que define o futuro da relação."
            ),
            "when_note": (
                "A janela é mais forte em {when_peak}. "
                "Depois, pode perder força ou mudar de forma."
            ),
            "scenarios": [
                "A relação com {partner_role} avança para compromisso mais claro e formal.",
                "Alguém novo entra na vida e rapidamente vira foco emocional principal — relação séria, não passageira.",
                "Conversa definitiva com {partner_role} define rumo: crescer juntos ou encerrar.",
            ],
            "risk": (
                "Se você evitar a conversa de compromisso, a relação pode entrar em "
                "indefinição ou o outro pode perder interesse."
            ),
            "action": "Diga o que quer sem rodeios. A clareza agora constrói — a ambiguidade destrói.",
        },
    },

    "crise_afetiva": {
        "label": "Crise ou teste afetivo",
        "category": "relationships",
        "rule_codes": {"relationship_test", "relationship_block", "conflict_relationship", "intense_relationship"},
        "priority_rule_codes": {"relationship_test"},
        "min_techniques": 2,
        "fatalistic_threshold": 3,
        "avoidability": (
            "Parcialmente evitável: o teste vem, mas a forma como você responde "
            "define se a relação sobrevive ou quebra."
        ),
        "template": {
            "what": (
                "O mapa aponta crise ou teste afetivo com {partner_role}: "
                "a relação passa por pressão real que cobra posicionamento, maturidade e decisão."
            ),
            "when_note": "A crise tem mais força em {when_peak}.",
            "scenarios": [
                "Crise que expõe o que não estava funcionando — e obriga conversa difícil.",
                "Distância, ciúme, segredo ou traição que testa a base da relação.",
                "Relação intensa que cresce rápido demais e começa a cobrar preço alto.",
            ],
            "risk": (
                "Se a crise não for enfrentada diretamente, ela vira "
                "ressentimento silencioso ou separação não planejada."
            ),
            "action": (
                "Encare o problema de frente. "
                "Crise afetiva resolvida com clareza fortalece — ignorada, quebra."
            ),
        },
    },

    "filhos": {
        "label": "Filhos ou decisão sobre maternidade/paternidade",
        "category": "relationships",
        "rule_codes": {"love_expansion", "commitment", "emotional_bond", "marriage_window", "pregnancy_window"},
        "priority_rule_codes": {"pregnancy_window"},
        "min_techniques": 2,
        "fatalistic_threshold": 4,
        "avoidability": (
            "Não evitável como ciclo emocional. "
            "O tema de filhos aparece quando o mapa e o contexto de vida convergem."
        ),
        "template": {
            "what": (
                "O mapa ativa tema de filhos: gravidez, relação com filho(s) existente(s) "
                "ou decisão sobre maternidade/paternidade."
            ),
            "when_note": "O tema é mais ativo em {when_peak}.",
            "scenarios": [
                "Decisão sobre ter filhos ou engravidar — o ciclo favorece esse movimento.",
                "Relação com filho(s) entra em fase de mudança: adolescência, saída de casa ou reaproximação.",
                "Tema de guarda, criação ou responsabilidade parental demanda atenção.",
            ],
            "risk": (
                "Adiamento indefinido de decisões sobre filhos pode gerar "
                "arrependimento ou janela perdida."
            ),
            "action": (
                "Se o desejo está presente, o mapa suporta ação. "
                "Se há conflito com filho, abra o canal de conversa."
            ),
        },
    },

    # ─────────────────────────────────────────────────────────────────────────
    # GRANDES TRANSIÇÕES — família/lar e mudanca_local
    # ─────────────────────────────────────────────────────────────────────────
    "mudanca_residencia_radical": {
        "label": "Mudança radical de residência",
        "category": "major_transitions",
        "rule_codes": {"career_change", "financial_transformation", "career_reset"},
        "priority_rule_codes": set(),
        "min_techniques": 2,
        "fatalistic_threshold": 3,
        "avoidability": (
            "Urano/eclipse no eixo lar (IC/Lua) empurra mudança — "
            "planejar logística reduz caos."
        ),
        "template": {
            "what": (
                "Urano ou eixo IC/Lua ativado: mudança de casa, cidade ou país "
                "de forma rápida ou inesperada — ruptura do lar atual."
            ),
            "when_note": "Virada residencial em {when_peak}.",
            "scenarios": [
                "Mudança forçada por trabalho, aluguel ou ruptura familiar.",
                "Decisão súbita de trocar de cidade ou país.",
                "Imprevisto estrutural (obra, vizinho, financeiro) que exige sair.",
            ],
            "risk": "Mudança sem reserva financeira vira dupla crise (lar + dinheiro).",
            "action": "Feche custos e prazos por escrito; não assine pressionado no pico.",
        },
    },

    "reestruturacao_familiar_ou_luto": {
        "label": "Reestruturação familiar ou luto",
        "category": "major_transitions",
        "rule_codes": {"deep_emotional_break", "psychological_transformation", "emotional_cut"},
        "priority_rule_codes": {"deep_emotional_break"},
        "min_techniques": 2,
        "fatalistic_threshold": 3,
        "avoidability": (
            "Plutão no IC/Lua é processo profundo — apoio emocional e jurídico "
            "reduzem dano; distinto de Saturno 4 (cuidado prolongado)."
        ),
        "template": {
            "what": (
                "Plutão tenso no IC ou à Lua: reestruturação pesada da família, "
                "luto, herança conflituosa ou fim de capítulo doméstico."
            ),
            "when_note": "Processo mais denso em {when_peak}.",
            "scenarios": [
                "Separação sob o mesmo teto ou partilha de bens que redefine a família.",
                "Luto ou perda que reorganiza papéis em casa.",
                "Segredo ou crise de poder que muda a dinâmica familiar.",
            ],
            "risk": "Sem suporte, vira isolamento, litígio ou ressentimento crônico.",
            "action": "Busque mediação, terapia e assessoria jurídica cedo — não espere o pico.",
        },
    },

    "mudanca_local": {
        "label": "Mudança de casa ou cidade",
        "category": "major_transitions",
        "rule_codes": {"career_change", "financial_transformation", "psychological_transformation", "career_reset"},
        "priority_rule_codes": set(),
        "min_techniques": 2,
        "fatalistic_threshold": 3,
        "avoidability": (
            "Parcialmente evitável como escolha, mas o ciclo empurra para mudança. "
            "Resistir tem custo alto."
        ),
        "template": {
            "what": (
                "O mapa indica mudança de endereço, cidade ou país — "
                "seja por escolha, necessidade profissional ou ruptura da situação atual."
            ),
            "when_note": "A mudança tem mais força em {when_peak}.",
            "scenarios": [
                "Mudança de apartamento ou casa motivada por ruptura, nova etapa ou questão financeira.",
                "Transferência profissional ou nova oportunidade que exige mudar de cidade.",
                "Decisão de mudar de país ou região por reconstrução de vida.",
            ],
            "risk": (
                "Mudança não planejada financeiramente ou emocionalmente pode "
                "virar caos logístico e custo inesperado."
            ),
            "action": (
                "Pesquise antes, feche o contrato atual com antecedência e "
                "planeje a logística sem pressa."
            ),
        },
    },
}

# Evaluation priority: higher in list = preferred when scores are equal
_SUBTYPE_PRIORITY_ORDER: list[str] = [
    # rupture — confirmation-rulebook specific subtypes (most specific first)
    "separacao_termino",
    "briga_forte",
    "ciume_posse",
    "afastamento_emocional",
    "conversa_seria",
    "tensao_leve",
    # rupture — legacy generic subtypes (kept for backward compat)
    "separacao_abrupta",
    "afastamento",
    "briga_grave",
    # health (mais específico primeiro)
    "risco_fisico_agudo",
    "acidente_fisico",
    "crise_saude",
    "esgotamento_confusao",
    "doenca_cronica",
    "acidente_emocional",
    "cronico",
    "doenca_leve",
    # career
    "mudanca_abrupta_carreira",
    "auditoria_carreira_ou_demissao",
    "perda_emprego",
    "emprego_novo",
    "pressao_carreira",
    # finance
    "aperto_financeiro",
    "ganho_crescimento",
    "perda_financeira",
    "ganho_financeiro",
    # relationships
    "filhos",
    "compromisso",
    "crise_afetiva",
    # major_transitions
    "mudanca_residencia_radical",
    "reestruturacao_familiar_ou_luto",
    "mudanca_local",
]

# Pre-computed: category → ordered list of subtype keys
CATEGORY_SUBTYPES: dict[str, list[str]] = {}
for _sk, _sd in SUBTYPE_DEFINITIONS.items():
    _cat = _sd["category"]
    if _cat not in CATEGORY_SUBTYPES:
        CATEGORY_SUBTYPES[_cat] = []
    CATEGORY_SUBTYPES[_cat].append(_sk)


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def _polarity_balance(signals: list[dict[str, Any]]) -> str:
    """Return dominant polarity of signals: 'supportive', 'challenging', or 'mixed'."""
    counts: dict[str, int] = {}
    for s in signals:
        pol = str(s.get("polarity") or "mixed")
        counts[pol] = counts.get(pol, 0) + 1
    if not counts:
        return "mixed"
    return max(counts, key=lambda k: counts[k])


def classify_event_subtype(
    category_key: str,
    category_signals: list[dict[str, Any]],
    rule_hits: list[dict[str, Any]],
    life_events: list[dict[str, Any]],
    user_context: dict[str, Any],
) -> str | None:
    """
    Classify the most specific subtype for a predicted event.

    Returns the subtype key string (e.g. 'separacao_abrupta') or None if no
    subtype matches.

    Scoring:
      - Each priority_rule_code match scores 10 points
      - Each normal rule_code match scores 1 point
      - Polarity alignment adds 0.5 bonus
      - Ties broken by position in _SUBTYPE_PRIORITY_ORDER (lower index wins)
    """
    available = CATEGORY_SUBTYPES.get(category_key, [])
    if not available:
        return None

    hit_codes = {str(h.get("code", "")) for h in rule_hits}
    dominant_polarity = _polarity_balance(category_signals)

    best_key: str | None = None
    best_score: float = -1.0
    best_priority: int = len(_SUBTYPE_PRIORITY_ORDER)

    for subtype_key in _SUBTYPE_PRIORITY_ORDER:
        if subtype_key not in available:
            continue
        sd = SUBTYPE_DEFINITIONS[subtype_key]

        priority_matches = len(hit_codes & sd.get("priority_rule_codes", set()))
        normal_matches = len(hit_codes & sd["rule_codes"])

        if normal_matches == 0 and priority_matches == 0:
            continue

        score: float = priority_matches * 10 + normal_matches

        # Small polarity bonus
        required_polarity = sd.get("polarity_required")
        if required_polarity and dominant_polarity == required_polarity:
            score += 0.5

        order_index = _SUBTYPE_PRIORITY_ORDER.index(subtype_key)

        # Prefer higher score; break ties with priority order (lower index = preferred)
        if score > best_score or (score == best_score and order_index < best_priority):
            best_score = score
            best_key = subtype_key
            best_priority = order_index

    # Context boost: filhos if user has / is planning children and relationships category
    if category_key == "relationships":
        has_children = user_context.get("has_children")
        planning_children = user_context.get("planning_children")
        if has_children or planning_children:
            filhos_sd = SUBTYPE_DEFINITIONS["filhos"]
            if len(hit_codes & filhos_sd["rule_codes"]) > 0:
                best_key = "filhos"

    # Context boost: mudanca_local if city/country change and major_transitions category
    if category_key == "major_transitions" and (
        user_context.get("city_change") or user_context.get("country_change")
    ):
        ml_sd = SUBTYPE_DEFINITIONS["mudanca_local"]
        if len(hit_codes & ml_sd["rule_codes"]) > 0:
            best_key = "mudanca_local"

    # Fatalism calibration (issue 9): briga_grave requires a conflict planet (Mars, Saturn,
    # Uranus, Pluto) in a transit, OR a conflict planet in house 7, OR an explicit conflict
    # rule code.  Sun/Moon/Mercury/Venus aspects alone (e.g. Sun square Jupiter) are not
    # sufficient — downgrade to crise_afetiva to avoid false positives from weak signals.
    if best_key == "briga_grave":
        has_conflict_transit = any(
            str((s.get("evidence") or {}).get("planet_a") or "").replace("_", " ").lower()
            in _CONFLICT_PLANETS
            for s in category_signals
            if str(s.get("technique") or "") == "transits"
        )
        if not has_conflict_transit and not _has_conflict_planet_in_7_or_rule(
            category_signals, rule_hits
        ):
            fallback = "crise_afetiva" if "crise_afetiva" in available else "afastamento"
            best_key = fallback

    _CAREER_RULEBOOK_SUBTYPES: frozenset[str] = frozenset({
        "mudanca_abrupta_carreira",
        "auditoria_carreira_ou_demissao",
        "perda_emprego",
        "pressao_carreira",
        "emprego_novo",
    })
    _FINANCE_RULEBOOK_SUBTYPES: frozenset[str] = frozenset({
        "aperto_financeiro",
        "ganho_crescimento",
        "ganho_financeiro",
        "perda_financeira",
    })

    if category_key == "health" and category_signals:
        health_subtype = classify_health_subtype(category_signals)
        if health_subtype and health_subtype in available:
            best_key = health_subtype

    if category_signals:
        career_finance_subtype = classify_career_finance_subtype(category_signals)
        if category_key == "career" and career_finance_subtype in _CAREER_RULEBOOK_SUBTYPES:
            if career_finance_subtype in available:
                best_key = career_finance_subtype
        if category_key == "finance" and career_finance_subtype in _FINANCE_RULEBOOK_SUBTYPES:
            if career_finance_subtype in available:
                best_key = career_finance_subtype

    if category_key == "major_transitions" and category_signals:
        family_subtype = classify_family_subtype(category_signals)
        if family_subtype and family_subtype in available:
            best_key = family_subtype

    # ── Confirmation-rulebook classifier override for rupture/relationships ──
    # For relationship conflict categories, delegate to the more specific
    # classify_relationship_conflict_subtype() from astro_confirmation.
    if category_key in {"rupture", "relationships"}:
        num_techniques = len({
            str(s.get("technique") or "")
            for s in category_signals
            if s.get("technique")
        })
        if category_signals or rule_hits:
            conflict_subtype = classify_relationship_conflict_subtype(
                signals=category_signals,
                rule_hits=rule_hits,
                num_techniques=num_techniques,
            )
            if conflict_subtype == "separacao_termino" and not has_hard_slow_transit(
                category_signals
            ):
                conflict_subtype = "afastamento_emocional"
            if category_key == "rupture":
                _CONFLICT_SUBTYPE_MAP: dict[str, str] = {
                    "separacao_termino": "separacao_termino",
                    "briga_forte": "briga_forte",
                    "ciume_posse": "ciume_posse",
                    "afastamento_emocional": "afastamento_emocional",
                    "conversa_seria": "conversa_seria",
                    "tensao_leve": "tensao_leve",
                }
                if conflict_subtype in _CONFLICT_SUBTYPE_MAP:
                    best_key = _CONFLICT_SUBTYPE_MAP[conflict_subtype]
            elif category_key == "relationships" and conflict_subtype == "conversa_seria":
                # For relationships category, apply conversa_seria only when
                # it doesn't override a stronger positive signal (commitment/filhos)
                if best_key not in {"compromisso", "filhos"}:
                    best_key = "conversa_seria"

    return best_key


# ---------------------------------------------------------------------------
# Text builder
# ---------------------------------------------------------------------------

def build_subtype_text(
    subtype_key: str,
    signals: list[dict[str, Any]],
    rule_hits: list[dict[str, Any]],
    reference_date: date,
    user_context: dict[str, Any],
    independent_signals: int = 0,
    time_window: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build human-readable, subtype-specific prediction text.

    Returns a dict with keys:
      subtype_key, subtype_label, subtype_what, subtype_when_note,
      subtype_scenarios, subtype_risk, subtype_action, subtype_avoidability,
      subtype_por_que, subtype_formatted_block, is_fatalistic
    """
    sd = SUBTYPE_DEFINITIONS.get(subtype_key)
    if sd is None:
        return {}

    template = sd["template"]

    # Partner label — rupture subtypes use a broader default unless the user has an
    # explicit partner role, to avoid falsely personalising "briga com sua esposa" when
    # the Casa 7 signal is about partnership/business conflict in general.
    partner = str(user_context.get("current_partner_role") or "unknown")
    relationship_status = str(user_context.get("relationship_status") or "unknown")
    _rupture_subtypes = {
        "briga_grave", "separacao_abrupta", "afastamento", "crise_afetiva",
        "separacao_termino", "briga_forte", "ciume_posse", "afastamento_emocional",
        "conversa_seria", "tensao_leve",
    }
    _broad_default = (
        "seu parceiro, sócio ou vínculo 1-a-1"
        if subtype_key in _rupture_subtypes and partner == "unknown"
        else "seu parceiro"
    )
    partner_label = {
        "girlfriend": "sua namorada",
        "boyfriend": "seu namorado",
        "wife": "sua esposa",
        "husband": "seu marido",
        "partner": "seu parceiro",
    }.get(partner, _broad_default)

    # Date placeholders from time_window
    peak_raw = time_window.get("peak") if time_window else None
    start_raw = time_window.get("start") if time_window else None
    end_raw = time_window.get("end") if time_window else None

    when_peak = format_date_pt(peak_raw) if peak_raw else "período em formação"
    when_start = format_date_pt(start_raw) if start_raw else when_peak
    when_end = format_date_pt(end_raw) if end_raw else when_peak
    when_range = (
        format_assertive_when_label(time_window, reference_date=reference_date)
        if time_window
        else "período em formação"
    )

    def fill(text: str) -> str:
        return (
            text
            .replace("{partner_role}", partner_label)
            .replace("{when_peak}", when_peak)
            .replace("{when_start}", when_start)
            .replace("{when_end}", when_end)
            .replace("{when_range}", when_range)
        )

    # Fatalistic determination: needs fatalistic_threshold independent techniques
    # AND at least one matching rule code with weight ≥ 3.5
    # AND the time window must be short (≤ 90 days) — long cycles get broad language.
    matching_rule_codes = sd["rule_codes"]
    heavy_hits = [
        h for h in rule_hits
        if str(h.get("code", "")) in matching_rule_codes
        and float(h.get("weight", 0.0)) >= 3.5
    ]
    window_days = _window_duration_days(time_window)
    is_long_window = window_days > _LONG_WINDOW_DAYS
    is_fatalistic = (
        independent_signals >= sd["fatalistic_threshold"]
        and len(heavy_hits) >= 1
        and _has_tense_aspect(signals)
        and not is_long_window  # 2-year cycles don't justify assertive language
    )

    if subtype_requires_hard_aspect(subtype_key) and not has_hard_slow_transit(signals):
        is_fatalistic = False

    _gain_subtypes = frozenset({"ganho_crescimento", "ganho_financeiro", "emprego_novo"})
    if subtype_key in _gain_subtypes:
        has_real_gain_support = any(
            (s.get("evidence") or {}).get("natal_dignity_supports_gain")
            for s in signals
        )
        only_illusory = any(
            s.get("dignity_downgrade") == "conforto_ilusorio" for s in signals
        ) and not has_real_gain_support
        if only_illusory:
            is_fatalistic = False

    # Build fields — long windows use softened language regardless of subtype
    if is_long_window and subtype_key in {"briga_grave", "separacao_abrupta"}:
        # Wide cycle: say the theme is sensitive, not that a specific fight will happen
        long_start = format_date_pt(start_raw) if start_raw else when_range
        long_end = format_date_pt(end_raw) if end_raw else when_range
        what = (
            f"Entre {long_start} e {long_end}, o tema de parceria e vínculo 1-a-1 fica sensível — "
            f"possível tensão, briga ou momento de definição com {partner_label}. "
            f"O ciclo é longo; o momento exato depende de outros ativadores."
        )
    else:
        what = fill(template["what"])
        if is_fatalistic:
            what = f"Isso vai acontecer: {what}"

    when_note = fill(template.get("when_note", f"O período mais sensível é {when_range}."))
    soft_note = soft_aspect_opportunity_note(signals)
    if soft_note and subtype_requires_hard_aspect(subtype_key):
        when_note = f"{when_note} {soft_note}"
    scenarios = [fill(s) for s in template.get("scenarios", [])]
    risk = fill(template.get("risk", ""))
    action = fill(template.get("action", ""))
    avoidability = sd["avoidability"]

    # Build por_que with technique labels, aspect names, and house context
    por_que = _enrich_por_que(
        signals, rule_hits, matching_rule_codes, subtype_key=subtype_key
    )

    source_technique = _primary_source_label(signals)

    primary_scenario = scenarios[0] if scenarios else what

    # Compact human summary for surface display (3–5 lines, no technical repetition)
    category_key = str(sd.get("category") or "rupture")
    cluster_metrics = compute_cluster_metrics(signals, rule_hits)
    certainty_level = resolve_certainty(
        independent_signals,
        signals,
        category_key=category_key,
        theme_convergence=int(cluster_metrics.get("theme_convergence") or 0),
        has_hard_slow=has_hard_slow_transit(signals),
    )
    provenance = build_astro_provenance(
        signals=signals,
        rule_hits=rule_hits,
        time_window=time_window,
        certainty_level=certainty_level,
        category_key=category_key,
        cluster_metrics=cluster_metrics,
    )
    human_por_que = build_human_por_que_from_provenance(provenance) or _human_por_que_deduped(
        signals, rule_hits, matching_rule_codes, subtype_key=subtype_key
    )
    subtype_human_summary = polish_portuguese(
        f"O quê: {primary_scenario}\n"
        f"Quando: {when_range}\n"
        f"Por quê: {human_por_que}\n"
        f"Evitar: {avoidability}"
    )

    # Full technical block for accordion
    provenance_block = format_provenance_technical_block(provenance)
    formatted_block = polish_portuguese(
        f"Quando: {when_range}\n\n"
        f"O que acontece: {primary_scenario}\n\n"
        f"Por que (astrologia/numerologia): {por_que}\n\n"
        f"{provenance_block}\n\n"
        f"Dá para evitar? {avoidability}\n\n"
        f"Risco: {risk}\n\n"
        f"Ação recomendada: {action}"
    )

    return {
        "subtype_key": subtype_key,
        "subtype_label": sd["label"],
        "source_technique": source_technique,
        "subtype_what": what,
        "subtype_when_note": when_note,
        "subtype_scenarios": scenarios,
        "subtype_risk": risk,
        "subtype_action": action,
        "subtype_avoidability": avoidability,
        "subtype_por_que": por_que,
        "subtype_human_summary": subtype_human_summary,
        "subtype_formatted_block": formatted_block,
        "is_fatalistic": is_fatalistic,
        "astro_provenance": provenance,
        "certainty_level": certainty_level,
        "cluster_metrics": cluster_metrics,
    }


# ---------------------------------------------------------------------------
# Helper: enriched prediction block combining base + subtype
# ---------------------------------------------------------------------------

def build_enriched_prediction_block(
    event: dict[str, Any],
    subtype_data: dict[str, Any],
) -> str:
    """
    Merge base + subtype into full technical block for accordion display.

    Returns a polished Portuguese string with all details.
    """
    if not subtype_data:
        return str(event.get("formatted_block") or "")

    when = str(
        event.get("when_label")
        or (event.get("time_window") or {}).get("formatted_label")
        or subtype_data.get("subtype_when_note")
        or "período em formação"
    )
    what = str(subtype_data.get("subtype_what") or event.get("what_is_happening") or "")
    por_que = str(subtype_data.get("subtype_por_que") or event.get("explanation") or "")
    avoidability = str(subtype_data.get("subtype_avoidability") or event.get("avoidability_summary") or "")
    risk = str(subtype_data.get("subtype_risk") or event.get("risk") or "")
    action = str(subtype_data.get("subtype_action") or event.get("recommended_action") or "")
    subtype_label = str(subtype_data.get("subtype_label") or "")

    parts: list[str] = [f"Quando: {when}", f"O que acontece ({subtype_label}): {what}"]
    if por_que:
        parts.append(f"Por que (astrologia/numerologia): {por_que}")
    if event.get("quality_summary"):
        parts.append(str(event["quality_summary"]))
    if avoidability:
        parts.append(f"Dá para evitar? {avoidability}")
    if risk:
        parts.append(f"Risco: {risk}")
    if action:
        parts.append(f"Ação recomendada: {action}")

    return polish_portuguese("\n\n".join(parts).strip())
