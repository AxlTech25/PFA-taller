#!/bin/sh
set -e
python -c "from app.seed import wait_for_db; wait_for_db()"

# Railway usa la misma imagen para la API y el worker; PROCESO elige cuál arranca.
if [ "${PROCESO:-api}" = "worker" ]; then
  exec python -m app.worker
fi

alembic upgrade head
python -m app.seed
exec uvicorn app.main:app --host "${HOST:-0.0.0.0}" --port "${PORT:-8000}"
