#!/usr/bin/env bash
# Container entrypoint for the Chambers of Men platform.
#
# Railway builds from the Dockerfile, so the Procfile is ignored. The project
# already runs a dedicated "worker" service whose start command is
# `python manage.py qcluster`, so this entrypoint does NOT start a worker by
# default - doing so would run a second cluster inside the web container.
#
# Set RUN_WORKER=1 only when running web+worker in a single container (local
# `docker run`, or a single-service deployment with no separate worker).
set -euo pipefail

PORT="${PORT:-8080}"

echo "==> Applying migrations"
python manage.py migrate --noinput

echo "==> Ensuring superuser"
python manage.py ensure_superuser

echo "==> Seeding agent configuration and email templates"
python manage.py seed_agents

echo "==> Registering scheduled tasks"
python manage.py setup_schedules

if [ "${RUN_WORKER:-0}" = "1" ]; then
    echo "==> Starting django-q worker"
    python manage.py qcluster &
    WORKER_PID=$!
    # If the worker dies, take the container down so Railway restarts it
    # rather than leaving a web process with no agents behind it.
    trap 'kill -TERM "$WORKER_PID" 2>/dev/null || true' EXIT INT TERM
fi

echo "==> Starting gunicorn on :${PORT}"
exec gunicorn chambers.wsgi:application \
    --bind "0.0.0.0:${PORT}" \
    --workers "${WEB_CONCURRENCY:-2}" \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
