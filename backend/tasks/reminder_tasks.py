from celery_app import celery
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@celery.task(name='tasks.reminder_tasks.daily_reminder', bind=True)
def daily_reminder(self):
    """
    Scheduler Task: Queries appointments and dispatches individual reminder tasks.
    No side effects, no emails, no heavy lifting.
    """
    from models import Appointment
    
    try:
        today = datetime.now().date()
        # Query only IDs to minimize memory usage preferred, but fetching objects is fine for now
        appointments = Appointment.query.filter_by(date=today, status='Booked').all()
        
        count = 0
        for appt in appointments:
            # Fan-out: Dispatch one task per appointment
            send_single_reminder.delay(appt.id)
            count += 1
            
        logger.info(f"Fan-out complete: Dispatched {count} reminder tasks")
        return f"Dispatched {count} reminders"
    except Exception as exc:
        logger.error(f"Daily reminder scheduler failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


@celery.task(name='tasks.reminder_tasks.send_single_reminder', bind=True, max_retries=3)
def send_single_reminder(self, appointment_id):
    """
    Worker Task: Handles a single appointment reminder.
    - Self-contained: Queries its own data
    - Isolated failure: If this fails, only this user is affected
    - Per-recipient retry logic
    """
    from models import Appointment, db, ActivityLog
    from tasks.notification_tasks import send_email

    try:
        # Re-query inside the worker task to ensure data freshness and isolation
        appt = Appointment.query.get(appointment_id)
        if not appt:
            logger.warning(f"Appointment {appointment_id} not found, skipping reminder")
            return "Skipped (not found)"
            
        if appt.status != 'Booked':
            logger.info(f"Appointment {appointment_id} status is {appt.status}, skipping reminder")
            return f"Skipped ({appt.status})"

        # Prepare email
        to = appt.patient.user.email
        subject = "Appointment Reminder"
        body = f"You have an appointment today at {appt.time} with Dr. {appt.doctor.name}"
        
        # Sync I/O (Email sending) happening in isolated task
        logger.info(f"Sending reminder to {to} for appointment {appointment_id}")
        send_email(to, subject, body)
        
        # Activity Logging
        log = ActivityLog(
            doctor_id=appt.doctor_id,
            activity_type='reminder_sent',
            description=f"Reminder sent to patient {appt.patient.name}"
        )
        db.session.add(log)
        db.session.commit()
        
        return f"Sent reminder for Appt {appointment_id}"

    except Exception as exc:
        db.session.rollback()
        logger.error(f"Failed to send reminder for appointment {appointment_id}: {str(exc)}")
        # Per-recipient retry
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))