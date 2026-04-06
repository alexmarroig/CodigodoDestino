from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Context-aware scenario maps
# ---------------------------------------------------------------------------
# Each domain has scenario templates that vary depending on user context.
# Keys: domain → tone → context_key → {scenarios, impact, risk, action}
# When no user context is provided, "default" is used.
# ---------------------------------------------------------------------------

RELATIONSHIP_SCENARIOS: dict[str, dict[str, Any]] = {
    "supportive": {
        "single": {
            "scenarios": [
                "Conhecer alguém com potencial real de relacionamento — em evento social, trabalho ou apresentação de amigos.",
                "Retomada de contato com alguém do passado que volta com intenção clara.",
                "Abertura emocional que permite aceitar convites e propostas que antes seriam ignorados.",
            ],
            "impact": "Possibilidade concreta de iniciar um relacionamento que tem base para durar.",
            "risk": "Idealizar a pessoa nova e ignorar sinais de incompatibilidade por carência.",
            "action": "Aceite convites, frequente ambientes novos, mas observe consistência antes de se comprometer.",
        },
        "married": {
            "scenarios": [
                "Fase de reaproximação real com o parceiro — conversas que resolvem pendências antigas.",
                "Momento favorável para planejar algo juntos: viagem, mudança ou projeto de família.",
                "Melhora na comunicação e na vida íntima do casal.",
            ],
            "impact": "Fortalecimento do vínculo e maior clareza sobre o futuro da relação.",
            "risk": "Acomodar-se achando que tudo se resolverá sozinho sem investir no diálogo.",
            "action": "Proponha uma conversa franca sobre planos e expectativas. Aproveite a janela para resolver o que travava.",
        },
        "separated": {
            "scenarios": [
                "Procura do ex-parceiro com proposta de reaproximação ou resolução pendente.",
                "Conhecer alguém novo que traz leveza e perspectiva diferente.",
                "Encerramento emocional de ciclo anterior que libera para novo começo.",
            ],
            "impact": "Clareza sobre seguir adiante ou revisitar o que ficou pendente.",
            "risk": "Voltar por saudade sem que os problemas reais tenham mudado.",
            "action": "Avalie propostas com base em fatos, não em emoção. Se for alguém novo, vá devagar.",
        },
        "default": {
            "scenarios": [
                "Abertura para novos vínculos ou fortalecimento dos existentes.",
                "Conversas que trazem clareza sobre o que a pessoa quer de um relacionamento.",
            ],
            "impact": "Mudança positiva na vida afetiva.",
            "risk": "Confundir empolgação passageira com certeza de longo prazo.",
            "action": "Esteja presente, observe reciprocidade e não force ritmo.",
        },
    },
    "challenging": {
        "single": {
            "scenarios": [
                "Rejeição ou frustração em tentativa de aproximação.",
                "Solidão que pesa mais do que o normal e gera decisões impulsivas.",
                "Envolvimento com pessoa indisponível ou incompatível.",
            ],
            "impact": "Desgaste emocional e possível isolamento.",
            "risk": "Aceitar qualquer coisa por desespero ou se fechar completamente.",
            "action": "Não force conexões. Use esse período para entender o que realmente quer antes de buscar alguém.",
        },
        "married": {
            "scenarios": [
                "Discussão séria que expõe problemas antigos do casamento.",
                "Distanciamento emocional ou físico do parceiro.",
                "Descoberta de algo que muda a percepção sobre a relação.",
            ],
            "impact": "Crise que obriga a decidir entre ajustar ou encerrar.",
            "risk": "Tomar decisão definitiva no calor da emoção.",
            "action": "Converse antes de agir. Se necessário, busque mediação profissional.",
        },
        "separated": {
            "scenarios": [
                "Cobrança legal ou emocional do ex-parceiro.",
                "Dificuldade em seguir adiante por questões não resolvidas.",
                "Pressão familiar para retomar ou desistir definitivamente.",
            ],
            "impact": "Tensão emocional que afeta outras áreas da vida.",
            "risk": "Deixar a situação arrastar sem tomar posição clara.",
            "action": "Resolva pendências práticas (documentos, divisão de bens) antes de lidar com o emocional.",
        },
        "default": {
            "scenarios": [
                "Tensão ou desgaste em vínculo importante.",
                "Necessidade de rever limites e expectativas em relação afetiva.",
            ],
            "impact": "Período de ajuste forçado na vida relacional.",
            "risk": "Reagir por impulso e agravar o conflito.",
            "action": "Fale sobre o que incomoda com clareza, sem ultimatos.",
        },
    },
    "mixed": {
        "default": {
            "scenarios": [
                "Sinais contraditórios na relação: momentos de aproximação seguidos de distância.",
                "Dúvida entre manter ou encerrar um vínculo.",
            ],
            "impact": "Instabilidade emocional até que uma decisão seja tomada.",
            "risk": "Ficar paralisado entre duas opções e perder o momento de agir.",
            "action": "Defina um prazo interno para observar e depois decidir com base no que aconteceu, não no que espera.",
        },
    },
}

CAREER_SCENARIOS: dict[str, dict[str, Any]] = {
    "supportive": {
        "employed": {
            "scenarios": [
                "Promoção, aumento ou reconhecimento formal no trabalho.",
                "Convite para projeto importante ou mudança de área dentro da empresa.",
                "Visibilidade profissional que atrai novas propostas.",
            ],
            "impact": "Avanço concreto na carreira com melhora de posição ou salário.",
            "risk": "Assumir mais do que consegue sustentar por empolgação.",
            "action": "Aceite oportunidades com critério. Negocie condições antes de dizer sim.",
        },
        "unemployed": {
            "scenarios": [
                "Surgimento de vaga ou oportunidade através de contato inesperado.",
                "Entrevista que avança rápido e gera proposta concreta.",
                "Início de atividade freelance ou projeto próprio que gera renda.",
            ],
            "impact": "Retorno ao mercado de trabalho ou início de nova fonte de renda.",
            "risk": "Aceitar a primeira oferta sem avaliar se é sustentável.",
            "action": "Ative sua rede de contatos agora. Atualize currículo e esteja disponível para entrevistas rápidas.",
        },
        "self_employed": {
            "scenarios": [
                "Entrada de cliente importante ou contrato de maior valor.",
                "Expansão do negócio: novo serviço, mercado ou parceria.",
                "Reconhecimento público que gera indicações orgânicas.",
            ],
            "impact": "Crescimento real do faturamento e da base de clientes.",
            "risk": "Crescer sem estrutura e comprometer a qualidade.",
            "action": "Invista em estrutura antes de escalar. Formalize acordos por escrito.",
        },
        "default": {
            "scenarios": [
                "Momento favorável para movimentação profissional.",
                "Oportunidade de crescimento ou mudança de direção na carreira.",
            ],
            "impact": "Avanço profissional visível.",
            "risk": "Deixar a janela passar por indecisão.",
            "action": "Tome iniciativa profissional agora — proponha, candidate-se, negocie.",
        },
    },
    "challenging": {
        "employed": {
            "scenarios": [
                "Pressão no trabalho: cobrança excessiva, prazos apertados ou conflito com chefia.",
                "Risco de demissão, reestruturação ou mudança forçada de função.",
                "Ambiente de trabalho tóxico que se agrava.",
            ],
            "impact": "Instabilidade profissional que pode levar a mudança forçada.",
            "risk": "Pedir demissão por impulso sem ter alternativa.",
            "action": "Documente situações, atualize currículo e comece a buscar alternativas em paralelo.",
        },
        "unemployed": {
            "scenarios": [
                "Fase de portas fechadas: entrevistas sem retorno, propostas canceladas.",
                "Pressão financeira que aumenta a urgência de encontrar trabalho.",
                "Desmotivação e questionamento sobre a própria capacidade.",
            ],
            "impact": "Período difícil que testa a resiliência e exige ajuste de estratégia.",
            "risk": "Aceitar condições muito abaixo do aceitável por desespero.",
            "action": "Revise sua abordagem de busca. Considere áreas ou formatos diferentes. Peça ajuda.",
        },
        "self_employed": {
            "scenarios": [
                "Perda de cliente importante ou queda brusca de faturamento.",
                "Problema operacional grave: inadimplência, processo ou quebra de contrato.",
                "Sobrecarga que compromete saúde e qualidade do serviço.",
            ],
            "impact": "Crise no negócio que exige ação imediata.",
            "risk": "Ignorar os sinais e continuar operando no vermelho.",
            "action": "Corte custos não essenciais, renegocie dívidas e busque orientação financeira profissional.",
        },
        "default": {
            "scenarios": [
                "Pressão profissional que exige reposicionamento.",
                "Risco de perda de estabilidade no trabalho.",
            ],
            "impact": "Mudança forçada na carreira.",
            "risk": "Reagir sem planejamento.",
            "action": "Proteja sua posição atual enquanto prepara alternativas.",
        },
    },
    "mixed": {
        "default": {
            "scenarios": [
                "Oportunidade misturada com risco: proposta boa mas com condições incertas.",
                "Mudança de emprego que pode ser positiva ou desestabilizadora.",
            ],
            "impact": "Transição profissional com resultado dependente de como for conduzida.",
            "risk": "Decidir rápido demais sem avaliar os riscos reais.",
            "action": "Analise a proposta com calma. Peça prazo para responder e consulte alguém de confiança.",
        },
    },
}

FAMILY_SCENARIOS: dict[str, dict[str, Any]] = {
    "supportive": {
        "default": {
            "scenarios": [
                "Resolução de pendência familiar: conversa que destrava relação com parente.",
                "Mudança de casa ou reforma que melhora qualidade de vida.",
                "Reaproximação com familiar distante.",
            ],
            "impact": "Fortalecimento da base emocional e familiar.",
            "risk": "Assumir responsabilidades familiares além da sua capacidade.",
            "action": "Fortaleça os laços que importam. Resolva uma pendência doméstica concreta.",
        },
    },
    "challenging": {
        "father_absent": {
            "scenarios": [
                "Conflito com figura de autoridade: chefe, mentor ou homem mais velho.",
                "Cobrança institucional ou burocrática que pesa.",
                "Necessidade de assumir papel de liderança que não queria.",
            ],
            "impact": "Pressão vinda de quem representa autoridade na vida.",
            "risk": "Rebeldia contra autoridade sem avaliar consequências.",
            "action": "Separe a pessoa do papel. Resolva o problema prático, não o emocional.",
        },
        "mother_absent": {
            "scenarios": [
                "Sensação de falta de acolhimento ou suporte emocional.",
                "Crise em relação com mulher importante da vida (parceira, irmã, filha).",
                "Necessidade de cuidar de si mesmo em área que normalmente delega.",
            ],
            "impact": "Vulnerabilidade emocional que pede autocuidado ativo.",
            "risk": "Buscar acolhimento em fontes não confiáveis.",
            "action": "Identifique o que está faltando emocionalmente e busque suporte adequado — terapeuta, amigo de confiança.",
        },
        "with_children": {
            "scenarios": [
                "Problema de saúde, comportamento ou desempenho escolar de um filho.",
                "Tensão sobre decisões de criação com parceiro ou ex-parceiro.",
                "Gasto inesperado relacionado a filho.",
            ],
            "impact": "Aumento da carga mental e financeira ligada aos filhos.",
            "risk": "Negligenciar a própria saúde para atender aos filhos.",
            "action": "Resolva a demanda mais urgente e peça ajuda para o restante. Não tente fazer tudo sozinho.",
        },
        "default": {
            "scenarios": [
                "Tensão no ambiente doméstico: discussão, desconforto ou necessidade de reorganização.",
                "Problema com imóvel, mudança ou condições de moradia.",
            ],
            "impact": "Desestabilização da base emocional.",
            "risk": "Deixar o problema de casa afetar todas as outras áreas.",
            "action": "Enfrente a situação doméstica diretamente. Não adie.",
        },
    },
    "mixed": {
        "default": {
            "scenarios": [
                "Mudança de casa ou reorganização familiar que traz desafios e oportunidades.",
                "Necessidade de equilibrar cuidado com limites no ambiente familiar.",
            ],
            "impact": "Reestruturação da vida doméstica.",
            "risk": "Tentar controlar o que não depende só de você.",
            "action": "Adapte-se ao que está mudando. Proteja sua rotina e seu espaço.",
        },
    },
}

HEALTH_SCENARIOS: dict[str, dict[str, Any]] = {
    "supportive": {
        "default": {
            "scenarios": [
                "Período bom para iniciar dieta, exercício ou tratamento que estava adiando.",
                "Melhora de disposição física e mental.",
                "Resultado positivo de exame ou tratamento em andamento.",
            ],
            "impact": "Ganho de saúde e disposição que impacta outras áreas da vida.",
            "risk": "Exagerar e se sobrecarregar achando que está invencível.",
            "action": "Aproveite a janela para estabelecer hábitos. Comece pequeno e mantenha.",
        },
    },
    "challenging": {
        "default": {
            "scenarios": [
                "Sintoma físico que precisa de atenção: dor persistente, cansaço extremo, lesão.",
                "Crise de ansiedade, insônia ou esgotamento emocional.",
                "Acidente doméstico ou no trabalho. Atenção redobrada no trânsito.",
            ],
            "impact": "Parada forçada que obriga a desacelerar e cuidar de si.",
            "risk": "Ignorar sintomas e continuar no mesmo ritmo até colapsar.",
            "action": "Marque exames pendentes. Reduza carga. Se algo persistir por mais de uma semana, procure médico.",
        },
    },
    "mixed": {
        "default": {
            "scenarios": [
                "Rotina instável que alterna entre produtividade e esgotamento.",
                "Necessidade de ajuste no ritmo de trabalho e descanso.",
            ],
            "impact": "Corpo pedindo recalibração.",
            "risk": "Empurrar com a barriga até o corpo cobrar.",
            "action": "Organize o essencial e elimine excessos na agenda.",
        },
    },
}

FINANCIAL_SCENARIOS: dict[str, dict[str, Any]] = {
    "supportive": {
        "default": {
            "scenarios": [
                "Entrada de dinheiro extra: bônus, comissão, venda ou recebimento atrasado.",
                "Oportunidade de investimento ou negócio com retorno provável.",
                "Renegociação favorável de dívida ou contrato.",
            ],
            "impact": "Melhora concreta da situação financeira.",
            "risk": "Gastar tudo antes de garantir reserva.",
            "action": "Separe uma parte para reserva antes de qualquer gasto. Formalize acordos por escrito.",
        },
    },
    "challenging": {
        "default": {
            "scenarios": [
                "Gasto inesperado: conserto, multa, conta médica ou emergência.",
                "Atraso de pagamento ou calote de cliente.",
                "Perda de renda por demissão, fim de contrato ou queda de faturamento.",
            ],
            "impact": "Aperto financeiro que exige corte e reorganização.",
            "risk": "Contrair dívida cara (cartão, cheque especial) para cobrir o rombo.",
            "action": "Corte gastos não essenciais imediatamente. Renegocie antes de atrasar. Busque renda alternativa.",
        },
    },
    "mixed": {
        "default": {
            "scenarios": [
                "Dinheiro entra mas com condição: investimento de risco, proposta com pegadinha.",
                "Necessidade de gastar para ganhar — sem garantia de retorno.",
            ],
            "impact": "Período de decisão financeira com risco real.",
            "risk": "Apostar tudo em uma oportunidade sem plano B.",
            "action": "Analise friamente. Nunca invista o que não pode perder.",
        },
    },
}

GENERIC_SCENARIOS: dict[str, dict[str, Any]] = {
    "supportive": {
        "default": {
            "scenarios": [
                "Movimento positivo nessa área da vida — abertura, clareza ou oportunidade.",
                "Resolução de algo que estava pendente ou travado.",
            ],
            "impact": "Avanço visível e tangível.",
            "risk": "Deixar a janela passar por inércia.",
            "action": "Aproveite o momento e tome uma decisão prática.",
        },
    },
    "challenging": {
        "default": {
            "scenarios": [
                "Pressão ou tensão que força ajuste nessa área.",
                "Situação que expõe uma fragilidade ou problema ignorado.",
            ],
            "impact": "Desconforto que obriga a mudar algo.",
            "risk": "Resistir à mudança e prolongar o desconforto.",
            "action": "Encare o problema de frente. Quanto antes agir, menor o desgaste.",
        },
    },
    "mixed": {
        "default": {
            "scenarios": [
                "Sinais mistos: oportunidade com risco, ou movimento com incerteza.",
                "Resultado depende de como a situação for conduzida.",
            ],
            "impact": "Fase de transição com desfecho em aberto.",
            "risk": "Paralisar por medo de errar.",
            "action": "Observe por algumas semanas e depois decida com base no que aconteceu.",
        },
    },
}

# Map domain keys to their scenario banks
DOMAIN_SCENARIO_MAP: dict[str, dict[str, dict[str, Any]]] = {
    "relacionamentos": RELATIONSHIP_SCENARIOS,
    "criatividade_afetos": RELATIONSHIP_SCENARIOS,
    "carreira_status": CAREER_SCENARIOS,
    "familia_lar": FAMILY_SCENARIOS,
    "saude_rotina": HEALTH_SCENARIOS,
    "financeiro": FINANCIAL_SCENARIOS,
    "crises_recursos": FINANCIAL_SCENARIOS,
}


# ---------------------------------------------------------------------------
# Context key resolution
# ---------------------------------------------------------------------------

def _resolve_context_key(domain: str, tone: str, user_context: dict[str, Any] | None) -> str:
    """Pick the most specific context key available for this domain + tone + user context."""
    if user_context is None:
        return "default"

    if domain in ("relacionamentos", "criatividade_afetos"):
        status = user_context.get("relationship_status")
        if status in ("married",):
            return "married"
        if status in ("separated", "divorced"):
            return "separated"
        if status in ("single", "dating"):
            return "single"

    elif domain == "carreira_status":
        status = user_context.get("employment_status")
        if status == "employed":
            return "employed"
        if status == "unemployed":
            return "unemployed"
        if status == "self_employed":
            return "self_employed"

    elif domain == "familia_lar":
        if tone == "challenging":
            if user_context.get("father_present") is False:
                return "father_absent"
            if user_context.get("mother_present") is False:
                return "mother_absent"
            if user_context.get("has_children") is True:
                return "with_children"

    return "default"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def translate_event_to_reality(
    event: dict[str, Any],
    user_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Enrich a single ForecastEvent with concrete real-life translation.

    Returns a dict with keys:
        scenarios  — list[str]
        impact     — str
        risk       — str
        action     — str
    """
    domain = str(event.get("category", ""))
    tone = _infer_tone_from_event(event)
    scenario_bank = DOMAIN_SCENARIO_MAP.get(domain, GENERIC_SCENARIOS)

    tone_bank = scenario_bank.get(tone, scenario_bank.get("mixed", GENERIC_SCENARIOS["mixed"]))
    context_key = _resolve_context_key(domain, tone, user_context)

    entry = tone_bank.get(context_key) or tone_bank.get("default") or GENERIC_SCENARIOS.get(tone, GENERIC_SCENARIOS["mixed"])["default"]

    return {
        "scenarios": list(entry["scenarios"]),
        "impact": entry["impact"],
        "risk": entry["risk"],
        "action": entry["action"],
    }


def enrich_events_with_reality(
    events: list[dict[str, Any]],
    user_context: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Add ``reality_translation`` key to each event in-place and return the list."""
    ctx = _normalize_user_context(user_context)
    for event in events:
        event["reality_translation"] = translate_event_to_reality(event, ctx)
    return events


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _infer_tone_from_event(event: dict[str, Any]) -> str:
    """Derive tone from event context weights."""
    ctx = event.get("context", {})
    sup = float(ctx.get("supportive_weight", 0))
    chal = float(ctx.get("challenging_weight", 0))
    if chal > (sup + 0.25):
        return "challenging"
    if sup > (chal + 0.25):
        return "supportive"
    return "mixed"


def _normalize_user_context(raw: Any) -> dict[str, Any] | None:
    if raw is None:
        return None
    if isinstance(raw, dict):
        return raw
    # Pydantic model or dataclass
    if hasattr(raw, "model_dump"):
        return raw.model_dump(exclude_none=True)
    if hasattr(raw, "__dict__"):
        return {k: v for k, v in raw.__dict__.items() if v is not None}
    return None
