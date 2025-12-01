from celery_app import celery

# Configure periodic tasks
celery.conf.beat_schedule = {
    'daily-reminders': {
        'task': 'tasks.reminder_tasks.daily_reminder',
        'schedule': 86400.0,  # Every 24 hours (in seconds)
    },
    'monthly-reports': {
        'task': 'tasks.report_tasks.monthly_activity_report',
        'schedule': 2592000.0,  # Every 30 days (in seconds)
    },
}

# Set the timezone
celery.conf.timezone = 'Asia/Kolkata'

if __name__ == '__main__':
    celery.start()