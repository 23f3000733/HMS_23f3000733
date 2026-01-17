@echo off
echo Starting Celery worker...
start "Celery Worker" cmd /k "python -m celery -A celery_worker worker --loglevel=info --pool=solo"

echo Starting Celery beat scheduler...
start "Celery Beat" cmd /k "python -m celery -A celery_worker beat --loglevel=info"

echo Celery worker and beat scheduler started in separate windows.
echo Close the windows to stop the processes.
pause
