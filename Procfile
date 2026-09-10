# Railway builds from the Dockerfile, so this Procfile is not used by the
# current deployment - docker-entrypoint.sh is the real startup path. It is
# kept for local `honcho`/`foreman` use and for a future split into separate
# web and worker services.
web: python manage.py migrate --noinput && gunicorn chambers.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
worker: python manage.py qcluster
