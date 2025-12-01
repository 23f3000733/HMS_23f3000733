# HMS Backend - Celery Setup

## Running Celery Workers

To start the Celery worker:

```bash
celery -A celery_app worker --loglevel=info
```

## Running Celery Beat Scheduler

To start the Celery beat scheduler for periodic tasks:

```bash
celery -A celery_beat beat --loglevel=info
```

## Running Both Worker and Beat

You can also run both the worker and beat scheduler in separate terminals, or use:

```bash
celery -A celery_app worker --loglevel=info --beat
```

This will start both the worker and the beat scheduler in a single process.

## Periodic Tasks

The following periodic tasks are configured:

1. **Daily Reminders** - Runs every 24 hours to send appointment reminders
2. **Monthly Reports** - Runs every 30 days to generate activity reports for doctors

## Task Names

- `tasks.export_tasks.export_patient_history` - Export patient history to CSV
- `tasks.notification_tasks.send_flag_notification` - Send flag notification to doctors
- `tasks.notification_tasks.send_patient_flag_notification` - Send flag notification to patients
- `tasks.notification_tasks.send_prescription_email_task` - Send prescription emails
- `tasks.reminder_tasks.daily_reminder` - Send daily appointment reminders
- `tasks.report_tasks.monthly_activity_report` - Generate monthly activity reports