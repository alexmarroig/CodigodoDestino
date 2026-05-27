# Constituição do motor preditivo — Codigo do Destino

Base permanente para **todos** os domínios (relações, saúde, carreira, dinheiro, família, mudanças).

## Fórmula de confiança

```
Confiança máxima permitida ≈
  Promessa natal
× Dignidades (essencial + acidental)
× Cluster temático (técnicas + alvos distintos)
× Era + gatilho temporal
× Contexto do utilizador
× Natureza do aspecto (duro vs mole)
```

## Os 6 pilares

### 1. Promessa natal

Nenhum trânsito entrega o que o mapa natal não promete. Trânsitos de apoio a planetas em exílio/queda → conforto ilusório, não ganho estrutural.

**Módulo:** `backend/engine/essential_dignity.py`

### 2. Dignidades (Lilly)

Domicílio/exaltação reforçam manifestação; exílio/queda limitam. Casas angulares (1, 4, 7, 10) tornam eventos mais visíveis.

### 3. Causa — Ação — Efeito (Brady)

- **Causa:** casa do planeta em trânsito
- **Ação:** natureza do aspecto
- **Efeito:** casa do planeta natal atingido

**Módulo:** `backend/engine/signal_enrichment.py`

### 4. Hit cluster temático

Contar técnicas **e** convergência em alvos distintos (par de planetas, casas, regras). Três técnicas no mesmo par Saturno–Vênus ≠ três testemunhas independentes.

**Módulo:** `backend/engine/cluster_convergence.py`

### 5. Era + gatilho

Planetas lentos abrem janela; Sol/Lua/Mercúrio/Marte no grau exato disparam pico datável.

**Módulo:** `backend/engine/transit_triggers.py`

### 6. Contexto + aspectos

- Utilizador casado/solteiro altera narrativa da Casa 7
- Trígonos/sextis → oportunidade; quadratura/oposição (+ conjunção tensa) → impacto
- Ruptura/crise exige aspecto **duro de planeta lento** para linguagem forte

## Certeza na UI

`resolve_certainty()` em `certainty.py` combina contagem efetiva, aspectos tensos reais e convergência temática. `astro_provenance` expõe drivers, exclusões e limites no acordeão «Como o mapa chegou aqui».

## Testes de referência

- `backend/tests/test_cluster_convergence.py`
- `backend/tests/test_resolve_certainty.py`
- `backend/tests/test_astro_provenance.py`
- `backend/tests/test_acceptance_married_2026.py`
