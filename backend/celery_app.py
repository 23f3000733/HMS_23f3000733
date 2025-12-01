from celery import Celery
from celery.schedules import crontab

# Create celery instance without Flask app context
celery = Celery()

# Configure celery
celery.conf.update(
    timezone="Asia/Kolkata",
    enable_utc=False,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0',
    # Add eager mode configuration directly here as well
    task_always_eager=True,
    task_eager_propagates=True
)

# Configure Celery Beat for scheduled tasks
celery.conf.beat_schedule = {
    'daily-appointment-reminders': {
        'task': 'tasks.reminder_tasks.daily_reminder',
        'schedule': crontab(hour=8, minute=0),  # 8:00 AM daily
    },
    'monthly-doctor-reports': {
        'task': 'tasks.report_tasks.monthly_activity_report',
        'schedule': crontab(day_of_month=1, hour=9, minute=0),  # 1st of month, 9 AM
    },
}

def make_celery(flask_app):
    celery.conf.update(
        broker_url=flask_app.config['CELERY_BROKER_URL'],
        result_backend=flask_app.config['CELERY_RESULT_BACKEND'],
        task_always_eager=flask_app.config['CELERY_TASK_ALWAYS_EAGER'],
        task_eager_propagates=True
    )

    class ContextTask(celery.Task):
        abstract = True
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return super().__call__(*args, **kwargs)

    celery.Task = ContextTask
    return celery