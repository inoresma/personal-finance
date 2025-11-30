#!/bin/bash
set -e

echo "Esperando a que la base de datos esté lista..."
python -c "import time; time.sleep(2)"

echo "Ejecutando migraciones..."
python manage.py migrate --noinput

echo "Recopilando archivos estáticos (si es necesario)..."
python manage.py collectstatic --noinput || echo "Collectstatic ya ejecutado o falló"

echo "Iniciando servidor..."
exec gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 2 --threads 4 --timeout 120 config.wsgi:application

