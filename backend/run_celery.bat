@echo off
echo Starting Celery worker...
start "Celery Worker" cmd /k "celery -A celery_app worker --loglevel=info"

echo Starting Celery beat scheduler...
start "Celery Beat" cmd /k "celery -A celery_beat beat --loglevel=info"

echo Celery worker and beat scheduler started in separate windows.
echo Close the windows to stop the processes.
pause