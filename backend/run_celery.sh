#!/bin/bash

# Script to run Celery worker and beat scheduler

echo "Starting Celery worker..."
celery -A celery_app worker --loglevel=info &

echo "Starting Celery beat scheduler..."
celery -A celery_beat beat --loglevel=info &

echo "Celery worker and beat scheduler started."
echo "Press Ctrl+C to stop."

# Wait for background processes
wait