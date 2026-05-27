# CodigodoDestino

Backend e frontend para leitura de destino com astrologia, numerologia e narrativa em 12 secoes.

## Stack

- Backend: FastAPI, PostgreSQL/SQLite, Redis (opcional), pyswisseph, OpenRouter
- Frontend: Next.js 14 + Tailwind
- Deploy: Vercel (frontend) + Render/Docker (backend)

## Rodar tudo localmente

### 1. Infra (Postgres + Redis + API)

```bash
docker compose up -d postgres redis backend
```

Sem Docker, suba Postgres/Redis manualmente ou deixe o backend cair para SQLite automaticamente.

### 2. Backend sozinho

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn api.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
copy .env.example .env.local
npm run dev
```

Abra http://localhost:3000 — o frontend usa `/api/mapa` como proxy para `http://127.0.0.1:8000`.

## Deploy producao

### Frontend (Vercel)

Projeto: `codigododestino`  
URL: https://frontend-alpha-flame-16.vercel.app

Variaveis no Vercel:

| Variavel | Uso |
|----------|-----|
| `BACKEND_URL` | URL publica da API FastAPI (Render/Railway) |
| `NEXT_PUBLIC_MAIN_SITE_URL` | Site de origem (ex.: Celestia) |
| `NEXT_PUBLIC_MAIN_SITE_NAME` | Nome exibido na barra de retorno |
| `OPENROUTER_API_KEY` | Opcional no backend para narrativa LLM |

O frontend faz proxy server-side em `/api/mapa` e `/api/horaria`, entao CORS no browser deixa de ser problema.

### Backend (Render)

1. Conecte o repo no Render
2. Use o `render.yaml` na raiz
3. Configure `OPENROUTER_API_KEY` no painel
4. Copie a URL publica (ex.: `https://codigododestino-api.onrender.com`)
5. Cole em `BACKEND_URL` no Vercel e redeploy

Health check: `GET /health`

## Endpoint principal

`POST /mapa`

Resposta inclui `destiny_sections` (12 secoes), `predictive_insights`, `narrative`, `forecast_360`.

## Testes

```bash
cd backend
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m pytest tests -q
```
