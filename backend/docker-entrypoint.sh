#!/bin/sh
set -e

echo "Waiting for the database to be ready..."
python - <<'PY'
import time
import sys
from sqlalchemy import create_engine
from app.core.config import settings

for attempt in range(60):
    try:
        engine = create_engine(settings.database_url)
        with engine.connect():
            pass
        print("Database is up.")
        break
    except Exception as exc:  # noqa: BLE001
        print(f"  ...not ready yet ({exc.__class__.__name__}); retrying")
        time.sleep(2)
else:
    sys.exit("Database did not become ready in time.")
PY

echo "Applying migrations..."
alembic upgrade head

echo "Seeding base countries..."
python -m scripts.seed_countries

echo "Importing products from CSV (idempotent)..."
python -m scripts.import_products data/items.csv

echo "Ensuring demo user exists..."
python -m scripts.create_user demo Demo@12345

echo "Ensuring admin user exists..."
python -m scripts.create_user admin Admin@12345 --admin

echo "Ensuring demo has country access..."
python -m scripts.seed_access

echo "Starting API on :8000"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
