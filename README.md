# CodigodoDestino

## Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment

```bash
export DATABASE_URL='postgresql+psycopg://postgres:postgres@localhost:5432/astrologia'
export REDIS_URL='redis://localhost:6379/0'
export OPENROUTER_API_KEY='your_key'
export OPENROUTER_MODEL='deepseek/deepseek-chat-v3.1'
export OPENROUTER_FALLBACK_MODEL='deepseek/deepseek-v3.2'
```

## Database Migration

```bash
cd backend
alembic upgrade head
```

## Run API

```bash
cd backend
uvicorn api.main:app --reload
```

## Run Tests

```bash
cd backend
pytest -q
```
