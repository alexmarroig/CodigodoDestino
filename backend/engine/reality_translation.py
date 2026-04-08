from __future__ import annotations
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# Scenario Banks (Refactored for Human Reality & 4-Layer Structure)
# ---------------------------------------------------------------------------

RELATIONSHIP_SCENARIOS = {
    "supportive": {
        "default": {
            "layer_1": "Uma abertura importante para conexão e entendimento.",
            "layer_2": "O clima favorece conversas sinceras e aproximação física. É um momento de fluidez onde os conflitos antigos perdem força.",
            "layer_3": "As defesas emocionais estão mais baixas, permitindo que a vulnerabilidade vire força de união. O outro se torna um espelho positivo da sua melhor versão.",
            "actions": ["Inicie aquela conversa importante", "Planeje um momento a sós", "Expresse o que sente"],
            "risks": ["Idealizar demais e esquecer da realidade prática", "Ficar na passividade esperando o outro agir"]
        }
    },
    "challenging": {
        "default": {
            "layer_1": "Relações e parcerias vão exigir mais maturidade agora.",
            "layer_2": "Diferenças de valores ou expectativas ficam evidentes. O momento pede menos cobrança e mais escuta para evitar rompimentos desnecessários.",
            "layer_3": "Este ciclo expõe onde você tem cedido demais ou onde falta limite. A tensão serve para recalibrar o equilíbrio entre 'eu' e 'nós'.",
            "actions": ["Escute antes de reagir", "Defina limites claros", "Dê espaço para o outro"],
            "risks": ["Explodir por acúmulo de silêncio", "Tentar controlar a reação do parceiro"]
        }
    },
    "mixed": {
        "default": {
            "layer_1": "Momento de redefinir as regras do jogo no afeto.",
            "layer_2": "Há uma mistura de atração e estranhamento. Algo novo está tentando entrar na dinâmica do relacionamento, exigindo adaptação de ambos.",
            "layer_3": "A instabilidade atual é um convite para sair da rotina automática. A incerteza não é um erro, mas uma fase de transição para um novo tipo de compromisso.",
            "actions": ["Observe os sinais antes de decidir", "Seja honesto sobre suas dúvidas", "Experimente novas formas de convivência"],
            "risks": ["Agir por impulso para aliviar a ansiedade", "Fazer promessas que não pode cumprir"]
        }
    }
}

CAREER_SCENARIOS = {
    "supportive": {
        "default": {
            "layer_1": "Sua competência será notada e recompensada.",
            "layer_2": "Portas se abrem para novos projetos ou reconhecimento de liderança. Sua visão estratégica está afiada e as decisões fluem com facilidade.",
            "layer_3": "O alinhamento entre sua vocação e sua ação prática atinge um pico. É a hora de ocupar o espaço que você conquistou com esforço.",
            "actions": ["Apresente suas ideias para superiores", "Assuma novas responsabilidades", "Atualize seu posicionamento profissional"],
            "risks": ["Arrogância por excesso de confiança", "Negligenciar detalhes técnicos por focar no bônus"]
        }
    },
    "challenging": {
        "default": {
            "layer_1": "Pressão e cobrança testam sua resiliência no trabalho.",
            "layer_2": "Prazos apertados ou figuras de autoridade rígidas podem gerar estresse. O foco deve ser na entrega técnica e na paciência estratégica.",
            "layer_3": "Você está sendo provado em sua capacidade de sustentar o que construiu. Não é um castigo, é um teste de estrutura para o seu próximo nível.",
            "actions": ["Organize suas prioridades rigorosamente", "Evite confrontos diretos com chefes", "Foque na solução, não na reclamação"],
            "risks": ["Absorver o estresse e levar para casa", "Desistir de um projeto por cansaço temporário"]
        }
    },
    "mixed": {
        "default": {
            "layer_1": "Mudanças na estrutura profissional exigem agilidade.",
            "layer_2": "Uma transição de cargo, equipe ou método de trabalho está em curso. O cenário é incerto, mas oferece brechas para quem sabe se adaptar.",
            "layer_3": "A desorganização externa reflete a necessidade de uma nova ordem interna. É o fim de um ciclo de atuação para o início de outro mais autêntico.",
            "actions": ["Esteja aberto a aprender novos processos", "Mantenha o networking ativo", "Documente seus resultados"],
            "risks": ["Ficar apegado a métodos antigos", "Paralisar diante da falta de clareza total"]
        }
    }
}

FINANCIAL_SCENARIOS = {
    "supportive": {
        "default": {
            "layer_1": "Dinheiro e segurança entram em uma fase favorável.",
            "layer_2": "Boas notícias sobre investimentos, aumentos ou negociações. O fluxo financeiro está mais livre, permitindo planos de médio prazo.",
            "layer_3": "Sua relação com o valor material está se tornando mais consciente. A abundância atual é fruto de escolhas sensatas feitas anteriormente.",
            "actions": ["Invista em algo sólido", "Organize sua reserva de emergência", "Negocie melhores taxas ou contratos"],
            "risks": ["Gastar por euforia passageira", "Emprestar dinheiro sem garantias reais"]
        }
    },
    "challenging": {
        "default": {
            "layer_1": "Atenção redobrada com gastos e recursos.",
            "layer_2": "Gastos inesperados ou atrasos em recebimentos exigem um pé no freio. É hora de cortar o supérfluo e focar na sobrevivência financeira básica.",
            "layer_3": "Este aperto força uma revisão de onde você está desperdiçando energia e dinheiro. A escassez temporária é uma professora de prioridades.",
            "actions": ["Corte assinaturas e gastos inúteis", "Renegocie dívidas imediatamente", "Evite compras por impulso"],
            "risks": ["Entrar em dívidas de juros altos", "Esconder a realidade financeira de quem divide as contas com você"]
        }
    },
    "mixed": {
        "default": {
            "layer_1": "Oportunidades financeiras vêm com letras miúdas.",
            "layer_2": "Dinheiro pode entrar, mas exigirá mais trabalho ou riscos calculados. Não aceite propostas sem analisar cada detalhe técnico.",
            "layer_3": "Sua ambição está alta, mas o terreno é instável. O sucesso depende da sua capacidade de equilibrar ousadia com prudência extrema.",
            "actions": ["Analise contratos com calma", "Busque uma segunda opinião técnica", "Diversifique pequenas fontes de renda"],
            "risks": ["Apostar tudo em uma 'promessa' milagrosa", "Ignorar alertas de risco óbvios"]
        }
    }
}

HEALTH_SCENARIOS = {
    "supportive": {
        "default": {
            "layer_1": "Vitalidade e disposição em alta.",
            "layer_2": "O corpo responde bem a novos hábitos e tratamentos. É o melhor momento para iniciar atividades físicas ou ajustar a dieta de forma prazerosa.",
            "layer_3": "Sua energia física está em harmonia com sua vontade mental. O corpo se torna um aliado eficiente para seus objetivos de vida.",
            "actions": ["Comece aquela nova rotina de exercícios", "Marque exames de rotina", "Melhore a qualidade do seu sono"],
            "risks": ["Exagerar no treino por se sentir invencível", "Negligenciar o descanso necessário"]
        }
    },
    "challenging": {
        "default": {
            "layer_1": "O corpo pede pausa e cuidados imediatos.",
            "layer_2": "Sinais de cansaço ou baixa imunidade não devem ser ignorados. Pequenos sintomas podem piorar se você continuar forçando o ritmo atual.",
            "layer_3": "Sua saúde está sinalizando um desequilíbrio emocional ou excesso de carga. Ouvir o corpo agora evita uma parada forçada no futuro.",
            "actions": ["Desacelere a agenda imediatamente", "Durma mais e coma melhor", "Busque ajuda profissional se a dor persistir"],
            "risks": ["Tentar resolver sintomas com automedicação", "Ignorar alertas óbvios do organismo"]
        }
    },
    "mixed": {
        "default": {
            "layer_1": "Sua rotina precisa de uma nova organização.",
            "layer_2": "Alternância entre picos de energia e esgotamento. O segredo está em encontrar um ritmo sustentável que não dependa de adrenalina.",
            "layer_3": "Você está redefinindo o que significa 'estar bem'. A saúde não é apenas ausência de doença, mas qualidade de presença no dia a dia.",
            "actions": ["Crie rituais de início e fim de dia", "Observe o que drena sua energia", "Mantenha a hidratação e pausas regulares"],
            "risks": ["Viver em um ciclo de cafeína e estresse", "Tentar mudar todos os hábitos de uma vez"]
        }
    }
}

GENERIC_SCENARIOS = {
    "supportive": {
        "default": {
            "layer_1": "Movimento positivo e portas abertas.",
            "layer_2": "As coisas tendem a fluir com menos esforço. Aproveite a clareza mental para resolver pendências e avançar em seus planos.",
            "layer_3": "A vida está dando sinal verde. É um período de colheita e facilidade que deve ser aproveitado com consciência.",
            "actions": ["Tome decisões que estava adiando", "Avance em seus projetos", "Comunique suas intenções"],
            "risks": ["Deixar a oportunidade passar por preguiça", "Ficar na zona de conforto"]
        }
    },
    "challenging": {
        "default": {
            "layer_1": "Fase de ajuste e enfrentamento de limites.",
            "layer_2": "Obstáculos e atrasos podem surgir para testar sua paciência. O foco deve ser na persistência e na correção de rotas erradas.",
            "layer_3": "A resistência externa é um convite para fortalecer sua determinação interna. O que não funciona agora precisa ser reformado ou descartado.",
            "actions": ["Encare os problemas de frente", "Seja resiliente e persistente", "Corrija falhas de planejamento"],
            "risks": ["Desistir diante do primeiro obstáculo", "Reagir com agressividade aos atrasos"]
        }
    },
    "mixed": {
        "default": {
            "layer_1": "Cenário de transição com sinais variados.",
            "layer_2": "Algumas coisas avançam enquanto outras travam. O momento pede observação atenta e flexibilidade para mudar conforme a necessidade.",
            "layer_3": "Você está no meio de uma mudança de ciclo. Nada está totalmente decidido, e seu comportamento atual influenciará o desfecho final.",
            "actions": ["Mantenha a flexibilidade", "Observe antes de agir", "Adapte-se às mudanças"],
            "risks": ["Paralisar por excesso de análise", "Tomar decisões definitivas em terreno instável"]
        }
    }
}

DOMAIN_SCENARIO_MAP = {
    "relacionamentos": RELATIONSHIP_SCENARIOS,
    "criatividade_afetos": RELATIONSHIP_SCENARIOS,
    "carreira_status": CAREER_SCENARIOS,
    "familia_lar": RELATIONSHIP_SCENARIOS, # For simplicity, using same bank
    "saude_rotina": HEALTH_SCENARIOS,
    "financeiro": FINANCIAL_SCENARIOS,
    "crises_recursos": FINANCIAL_SCENARIOS,
}

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def translate_event_to_reality(event: dict[str, Any], user_context: dict[str, Any] | None = None) -> dict[str, Any]:
    domain = str(event.get("category", ""))
    tone = _infer_tone_from_event(event)
    scenario_bank = DOMAIN_SCENARIO_MAP.get(domain, GENERIC_SCENARIOS)
    tone_bank = scenario_bank.get(tone, scenario_bank.get("mixed", GENERIC_SCENARIOS["mixed"]))

    entry = tone_bank.get("default")

    return {
        "layer_1": entry["layer_1"],
        "layer_2": entry["layer_2"],
        "layer_3": entry.get("layer_3"),
        "actions": entry["actions"],
        "risks": entry["risks"]
    }

def enrich_events_with_reality(events: list[dict[str, Any]], user_context: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    for event in events:
        event["reality_translation"] = translate_event_to_reality(event, user_context)
    return events

def _infer_tone_from_event(event: dict[str, Any]) -> str:
    ctx = event.get("context", {})
    sup = float(ctx.get("supportive_weight", 0))
    chal = float(ctx.get("challenging_weight", 0))
    if chal > (sup + 0.25): return "challenging"
    if sup > (chal + 0.25): return "supportive"
    return "mixed"
