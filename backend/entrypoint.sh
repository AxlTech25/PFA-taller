#!/bin/sh
set -e
python -c "from app.seed import wait_for_db; wait_for_db()"
alembic upgrade head
python -m app.seed
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
