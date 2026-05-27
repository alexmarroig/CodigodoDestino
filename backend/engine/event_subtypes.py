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

from engine.date_formatting import format_date_pt, format_time_window_label
from engine.portuguese_text import polish_portuguese

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
        "rule_codes": {"love_expansion", "commitment", "emotional_bond", "marriage_window"},
        "priority_rule_codes": set(),
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
    # GRANDES TRANSIÇÕES — mudanca_local (e fallback genérico)
    # ─────────────────────────────────────────────────────────────────────────
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
    # rupture (most specific first)
    "separacao_abrupta",
    "afastamento",
    "briga_grave",
    # health
    "crise_saude",
    "cronico",
    "doenca_leve",
    # career
    "perda_emprego",
    "emprego_novo",
    "pressao_carreira",
    # finance
    "perda_financeira",
    "ganho_financeiro",
    # relationships
    "filhos",
    "compromisso",
    "crise_afetiva",
    # major_transitions
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

    # Partner label
    partner = str(user_context.get("current_partner_role") or "unknown")
    partner_label = {
        "girlfriend": "sua namorada",
        "boyfriend": "seu namorado",
        "wife": "sua esposa",
        "husband": "seu marido",
        "partner": "seu parceiro",
    }.get(partner, "seu parceiro")

    # Date placeholders from time_window
    peak_raw = time_window.get("peak") if time_window else None
    start_raw = time_window.get("start") if time_window else None
    end_raw = time_window.get("end") if time_window else None

    when_peak = format_date_pt(peak_raw) if peak_raw else "período em formação"
    when_start = format_date_pt(start_raw) if start_raw else when_peak
    when_end = format_date_pt(end_raw) if end_raw else when_peak
    when_range = (
        format_time_window_label(time_window, reference_date=reference_date)
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
    matching_rule_codes = sd["rule_codes"]
    heavy_hits = [
        h for h in rule_hits
        if str(h.get("code", "")) in matching_rule_codes
        and float(h.get("weight", 0.0)) >= 3.5
    ]
    is_fatalistic = (
        independent_signals >= sd["fatalistic_threshold"]
        and len(heavy_hits) >= 1
    )

    # Build fields
    what = fill(template["what"])
    if is_fatalistic:
        what = f"Isso vai acontecer: {what}"

    when_note = fill(template.get("when_note", f"O período mais sensível é {when_range}."))
    scenarios = [fill(s) for s in template.get("scenarios", [])]
    risk = fill(template.get("risk", ""))
    action = fill(template.get("action", ""))
    avoidability = sd["avoidability"]

    # Build por_que from signal labels and rule hit labels
    signal_labels = [str(s.get("label", "")) for s in signals[:3] if s.get("label")]
    hit_labels = [
        str(h.get("label", ""))
        for h in rule_hits[:2]
        if h.get("label") and str(h.get("code", "")) in matching_rule_codes
    ]
    por_que_parts = signal_labels + hit_labels
    por_que = (
        "; ".join(por_que_parts)
        if por_que_parts
        else "Convergência técnica detectada no mapa."
    )

    primary_scenario = scenarios[0] if scenarios else what

    # Formatted block using standardized structure
    formatted_block = polish_portuguese(
        f"Quando: {when_range}\n\n"
        f"O que acontece: {primary_scenario}\n\n"
        f"Por que (astrologia/numerologia): {por_que}\n\n"
        f"Dá para evitar? {avoidability}\n\n"
        f"Risco: {risk}\n\n"
        f"Ação recomendada: {action}"
    )

    return {
        "subtype_key": subtype_key,
        "subtype_label": sd["label"],
        "subtype_what": what,
        "subtype_when_note": when_note,
        "subtype_scenarios": scenarios,
        "subtype_risk": risk,
        "subtype_action": action,
        "subtype_avoidability": avoidability,
        "subtype_por_que": por_que,
        "subtype_formatted_block": formatted_block,
        "is_fatalistic": is_fatalistic,
    }


# ---------------------------------------------------------------------------
# Helper: enriched prediction block combining base + subtype
# ---------------------------------------------------------------------------

def build_enriched_prediction_block(
    event: dict[str, Any],
    subtype_data: dict[str, Any],
) -> str:
    """
    Merge the base event's formatted_block with subtype-specific details.

    Returns a polished Portuguese prediction string.
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

    parts = [f"Quando: {when}", f"O que acontece ({subtype_label}): {what}"]
    if por_que:
        parts.append(f"Por que (astrologia/numerologia): {por_que}")
    if event.get("quality_summary"):
        parts.append(str(event["quality_summary"]))
    if event.get("technical_block"):
        parts.append(f"Leitura técnica:\n{event['technical_block']}")
    if avoidability:
        parts.append(f"Dá para evitar? {avoidability}")
    if risk:
        parts.append(f"Risco: {risk}")
    if action:
        parts.append(f"Ação recomendada: {action}")

    return polish_portuguese("\n\n".join(parts).strip())
