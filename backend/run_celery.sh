#!/bin/bash

echo "Starting Celery worker..."
celery -A celery_worker worker --loglevel=info &

echo "Starting Celery beat scheduler..."
celery -A celery_worker beat --loglevel=info &

echo "Celery worker and beat scheduler started."
echo "Press Ctrl+C to stop."

wait
