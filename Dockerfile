# Fly.io Docker image a GyepMester Flask alkalmazáshoz

# Python 3.12 slim alap image
FROM python:3.12-slim

# Munkakönyvtár beállítása
WORKDIR /app

# Rendszer-függőségek (Pillow WebP támogatáshoz és psycopg2-hoz)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libwebp-dev \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python függőségek telepítése (cache réteg)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Gunicorn telepítése (prod WSGI szerver)
RUN pip install --no-cache-dir gunicorn==23.0.0

# Alkalmazás másolása
COPY . .

# Uploads mappa létrehozása (volume mount pont)
RUN mkdir -p /app/static/uploads

# Entrypoint futtatható
RUN chmod +x entrypoint.sh

# Nem root felhasználó a biztonság érdekében
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Port, amelyen a Gunicorn hallgat
EXPOSE 8080

# Entrypoint: DB init + Gunicorn indítás
CMD ["sh", "entrypoint.sh"]
