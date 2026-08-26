#!/usr/bin/env bash
# Container entrypoint for the Chambers of Men platform.
#
# Railway builds from the Dockerfile, which means the Procfile is ignored and
# its "worker: python manage.py qcluster" line never runs. Without a worker no
# scheduled agent fires, so the onboarding, pipeline and event agents were
# silently dormant. The worker is started here alongside gunicorn.
#
# Set RUN_WORKER=0 to run web-only (e.g. if the worker is split into its own
# Railway service later).
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

if [ "${RUN_WORKER:-1}" = "1" ]; then
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
