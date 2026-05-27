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

if [ -n "${ALLOWED_ORIGINS:-}" ]; then
  export ALLOWED_ORIGINS="$(python - <<'PY'
import json
import os

raw = os.environ.get("ALLOWED_ORIGINS", "").strip()
if not raw:
    print("")
elif raw.startswith("["):
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            print(json.dumps(parsed))
        else:
            print("")
    except json.JSONDecodeError:
        print("")
else:
    origins = [item.strip() for item in raw.split(",") if item.strip()]
    print(json.dumps(origins) if origins else "")
PY
)"
  if [ -z "${ALLOWED_ORIGINS}" ]; then
    unset ALLOWED_ORIGINS
  fi
fi

echo "Running Alembic migrations..."
python -c "from alembic.config import main; main(argv=['upgrade', 'head'])"

echo "Seeding editorial data..."
python scripts/seed/full_seed.py

echo "Starting Astro Platform API..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
