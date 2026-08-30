#!/bin/sh
# Fly.io Docker entrypoint script
# Elvégzi az adatbázis inicializálást, majd elindítja a Gunicorn szervert

set -e

echo "[GyepMester] Adatbázis inicializálása..."
python -c "
from app import app
from models import db
from seed_data import seed_products
import os

with app.app_context():
    db.create_all()
    seed_products(app)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

print('[GyepMester] Adatbazis kesz.')
"

echo "[GyepMester] Gunicorn szerver inditasa..."
exec gunicorn \
  --bind "0.0.0.0:${PORT:-8080}" \
  --workers 2 \
  --timeout 60 \
  --access-logfile - \
  --error-logfile - \
  app:app
