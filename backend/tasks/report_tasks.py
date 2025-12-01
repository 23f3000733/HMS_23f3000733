from celery_app import celery
from datetime import datetime, timedelta

@celery.task(name='tasks.report_tasks.monthly_activity_report', bind=True, max_retries=3)
def monthly_activity_report(self):
    from models import DoctorDetails, Appointment, db, ActivityLog

    try:
        today = datetime.now()
        last_month_start = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        last_month_end = today.replace(day=1) - timedelta(days=1)

        doctors = DoctorDetails.query.all()
        total_sent = 0

        for doctor in doctors:
            try:
                appointments = Appointment.query.filter(
                    Appointment.doctor_id == doctor.id,
                    Appointment.date >= last_month_start.date(),
                    Appointment.date <= last_month_end.date()
                ).all()

                completed = len([a for a in appointments if a.status == 'Completed'])
                total = len(appointments)

                # Send report
                to = doctor.user.email
                subject = "Monthly Activity Report"
                body = f"""
Dear Dr. {doctor.name},

Here is your monthly activity summary:

Total Appointments: {total}
Completed: {completed}

Regards,
Hospital Management System
"""
                # Use the new send_email function from notification_tasks
                from tasks.notification_tasks import send_email
                send_email(to, subject, body)
                
                total_sent += 1

                # Log report generation
                log = ActivityLog(
                    doctor_id=doctor.id,
                    activity_type='monthly_report',
                    description=f"Report: {total} total, {completed} completed"
                )
                db.session.add(log)
                db.session.commit()
                
            except Exception as e:
                db.session.rollback()
                print(f"FAILED TO SEND REPORT TO DR. {doctor.name}: {str(e)}")

        return f"Sent monthly reports to {total_sent} doctors"
    except Exception as exc:
        # Retry with exponential backoff: 60s, 120s, 240s
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))