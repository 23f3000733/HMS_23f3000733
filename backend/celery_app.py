import os
from celery import Celery
from celery.schedules import crontab

# Celery (Redis backend, correct for Windows)
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/0'

# Define the single Celery app instance
celery = Celery(
    'hms',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=[
        'tasks.notification_tasks',
        'tasks.export_tasks',
        'tasks.reminder_tasks',
        'tasks.report_tasks'
    ]
)

# Configure Celery
celery.conf.update(
    timezone='Asia/Kolkata',
    enable_utc=False,
    task_always_eager=False,  # Use Redis
)

# Define Beat Schedule
celery.conf.beat_schedule = {
    'daily-reminders': {
        'task': 'tasks.reminder_tasks.daily_reminder',
        'schedule': crontab(hour=8, minute=0),
    },
    'monthly-reports': {
        'task': 'tasks.report_tasks.monthly_activity_report',
        'schedule': crontab(day_of_month=1, hour=9, minute=0),
    },
}