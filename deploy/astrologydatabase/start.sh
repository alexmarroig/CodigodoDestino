#!/bin/sh
set -eu

if [ -n "${DATABASE_URL:-}" ]; then
  export DATABASE_ASYNC_URL="$(python - <<'PY'
import os
url = os.environ["DATABASE_URL"]
if url.startswith("postgresql://"):
    print("postgresql+asyncpg://" + url[len("postgresql://"):])
elif url.startswith("postgres://"):
    print("postgresql+asyncpg://" + url[len("postgres://"):])
else:
    print(url)
PY
)"
fi

echo "Running Alembic migrations..."
python -c "from alembic.config import main; main(argv=['upgrade', 'head'])"

echo "Seeding editorial data..."
python scripts/seed/full_seed.py

echo "Starting Astro Platform API..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
