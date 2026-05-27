# Deploy no Render — Codigo do Destino + Astrologydatabase

Este guia sobe **dois backends** e liga o frontend no Vercel.

## Arquitetura

```text
Vercel (frontend)
  └─ /api/mapa  ──►  codigododestino-api (Render)
                         └─ ASTROLOGY_DATABASE_URL ──►  astrologydatabase-api (Render)
                                                              └─ Postgres (Render)
```

## Passo 1 — Blueprint no Render

1. Acesse [render.com](https://render.com) e faça login com GitHub.
2. **New → Blueprint**.
3. Conecte o repo `alexmarroig/CodigodoDestino`.
4. O Render vai ler o `render.yaml` na raiz e criar:
   - `astrologydatabase-db` (Postgres)
   - `astrologydatabase-api` (editorial + priorização)
   - `codigododestino-api` (motor de destino)

5. Quando pedir variáveis secretas, informe:
   - `OPENROUTER_API_KEY` (opcional — narrativa LLM)

6. Aguarde os dois serviços ficarem **Live**.

## Passo 2 — Copiar URLs

No painel Render:

| Serviço | URL exemplo |
|---------|-------------|
| `codigododestino-api` | `https://codigododestino-api.onrender.com` |
| `astrologydatabase-api` | `https://astrologydatabase-api.onrender.com` |

Teste:

```bash
curl https://astrologydatabase-api.onrender.com/health
curl https://codigododestino-api.onrender.com/health
```

O `codigododestino-api` já recebe `ASTROLOGY_DATABASE_URL` automaticamente via Blueprint.

## Passo 3 — Vercel (frontend)

Projeto: **codigododestino**

Settings → Environment Variables → Production:

| Variável | Valor |
|----------|--------|
| `BACKEND_URL` | `https://codigododestino-api.onrender.com` |
| `NEXT_PUBLIC_MAIN_SITE_URL` | `https://sitecelestia.vercel.app` |
| `NEXT_PUBLIC_MAIN_SITE_NAME` | `Celestia` |

Depois: **Deployments → Redeploy**.

## Passo 4 — Testar leitura

1. Abra https://frontend-alpha-flame-16.vercel.app
2. Preencha o questionário
3. Gere a leitura — deve retornar **12 seções**
4. Se Astrologydatabase estiver ok, seções como **Ferida** e **Personalidade** usam texto editorial com tom mais fatalista (`poorly_expressed` / `challenges`)

## Rodar tudo localmente

```bash
# Terminal 1 — Postgres/Redis/API Codigo do Destino
docker compose up -d postgres redis backend

# Terminal 2 — Astrologydatabase (clone separado)
git clone https://github.com/alexmarroig/Astrologydatabase.git
cd Astrologydatabase
pip install -r requirements.txt
copy .env.example .env
# ajuste DATABASE_URL para postgres local
python -c "from alembic.config import main; main(argv=['upgrade', 'head'])"
python scripts/seed/full_seed.py
uvicorn app.main:app --port 8010

# Terminal 3 — backend com integração
cd ../CodigodoDestino/backend
set ASTROLOGY_DATABASE_URL=http://127.0.0.1:8010
uvicorn api.main:app --port 8000

# Terminal 4 — frontend
cd ../frontend
npm run dev
```

## Escola editorial (tom fatalista)

Variável `ASTROLOGY_SCHOOL_CODE` no Render:

| Valor | Conteúdo |
|-------|----------|
| `luz_e_sombra` | Claudia Lisboa — mais sombra/risco (padrão) |
| `hellenistic` | Dataset helenístico com `risk_expression` |

O filtro fatalista prioriza campos `poorly_expressed` e `challenges`, temas `shadow` / `transformation`, e sobe a certeza conforme o `total_score` da priorização.

## Problemas comuns

| Sintoma | Causa | Solução |
|---------|-------|---------|
| 502 no Vercel | `BACKEND_URL` vazio ou backend dormindo | Configure env + acorde o serviço Render (free tier) |
| Seções genéricas | Astrologydatabase sem seed | Veja logs do `astrologydatabase-api` — `full_seed.py` deve rodar no start |
| CORS | Chamada direta ao backend | Use o proxy `/api/mapa` do Next.js (já configurado) |
| Cold start lento | Plano free Render | Primeira requisição pode levar ~30–60s |
