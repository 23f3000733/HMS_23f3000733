from celery_app import celery
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@celery.task(name='tasks.report_tasks.monthly_activity_report', bind=True)
def monthly_activity_report(self):
    """
    Scheduler Task: Queries active doctors and dispatches individual report tasks.
    """
    from models import DoctorDetails
    
    try:
        doctors = DoctorDetails.query.all()
        count = 0
        
        for doctor in doctors:
            # Fan-out: Dispatch one task per doctor
            generate_single_doctor_report.delay(doctor.id)
            count += 1
            
        logger.info(f"Fan-out complete: Dispatched {count} report tasks")
        return f"Dispatched {count} report generation tasks"
    except Exception as exc:
        logger.error(f"Monthly report scheduler failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


@celery.task(name='tasks.report_tasks.generate_single_doctor_report', bind=True, max_retries=3)
def generate_single_doctor_report(self, doctor_id):
    """
    Worker Task: Generates and sends a report for a single doctor.
    - Isolated failure domain
    - Per-doctor retry
    """
    from models import DoctorDetails, Appointment, db, ActivityLog
    from tasks.notification_tasks import send_email

    try:
        doctor = DoctorDetails.query.get(doctor_id)
        if not doctor:
            logger.warning(f"Doctor {doctor_id} not found, skipping report")
            return "Skipped (not found)"

        # Calculate dates
        today = datetime.now()
        last_month_start = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        last_month_end = today.replace(day=1) - timedelta(days=1)

        # Query Appointments
        appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.date >= last_month_start.date(),
            Appointment.date <= last_month_end.date()
        ).all()

        completed = len([a for a in appointments if a.status == 'Completed'])
        total = len(appointments)

        # Prepare email
        to = doctor.user.email
        subject = "Monthly Activity Report"
        body = f"""
Dear Dr. {doctor.name},

Here is your monthly activity summary for period {last_month_start.strftime('%B %Y')}:

Total Appointments: {total}
Completed: {completed}

Regards,
Hospital Management System
"""
        
        logger.info(f"Sending monthly report to Dr. {doctor.name}")
        send_email(to, subject, body)
        
        # Log activity
        log = ActivityLog(
            doctor_id=doctor.id,
            activity_type='monthly_report',
            description=f"Report: {total} total, {completed} completed"
        )
        db.session.add(log)
        db.session.commit()
        
        return f"Sent report to Dr. {doctor.name}"

    except Exception as exc:
        db.session.rollback()
        logger.error(f"Failed to generate report for doctor {doctor_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))