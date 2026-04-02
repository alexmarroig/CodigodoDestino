# CodigodoDestino

## Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
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
