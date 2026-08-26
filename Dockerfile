FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x /app/docker-entrypoint.sh

# collectstatic runs at build time and must not be allowed to fail silently:
# ManifestStaticFilesStorage will raise at request time for any missing asset.
# A build-only SECRET_KEY is used because settings requires one to import.
RUN SECRET_KEY=build-only-not-used DEBUG=False python manage.py collectstatic --noinput

EXPOSE ${PORT:-8080}

ENTRYPOINT ["/app/docker-entrypoint.sh"]
