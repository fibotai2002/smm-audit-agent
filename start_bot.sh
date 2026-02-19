#!/bin/bash
echo "🚀 SMM Audit Agentni ishga tushirish..."

# Dependencies are already installed in Dockerfile
set -e

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Bot..."
echo "Starting Gunicorn..."
# Default to port 8080 if not set
PORT=${PORT:-8080}
echo "Starting Gunicorn on port $PORT..."
gunicorn smm_audit.wsgi:application --bind 0.0.0.0:$PORT --timeout 120 --workers 2
