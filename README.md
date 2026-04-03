# CodigodoDestino

Backend e frontend para um SaaS de previsoes com astrologia, numerologia e narrativa assistida por IA.

## Stack

- Backend: FastAPI, PostgreSQL, Redis, SQLAlchemy, Alembic
- Engine: pyswisseph, numerologia, regras de eventos, OpenRouter
- Frontend: Next.js + Tailwind

## Subindo a infraestrutura local

Na raiz do projeto:

```bash
docker compose up -d postgres redis
```

## Setup do backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn api.main:app --reload
```

## Endpoint principal

`POST /mapa`

Payload minimo:

```json
{
  "date": "1995-03-10",
  "time": "14:30",
  "lat": -23.55,
  "lon": -46.63,
  "timezone": "America/Sao_Paulo"
}
```

## Testes

```bash
cd backend
pytest -q
```
