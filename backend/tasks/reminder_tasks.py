from celery_app import celery
from datetime import datetime

@celery.task
def daily_reminder():
    from models import Appointment, db, ActivityLog

    today = datetime.now().date()
    appointments = Appointment.query.filter_by(date=today).all()

    count = 0
    for appt in appointments:
        if appt.status == 'Booked':
            # Send reminder
            to = appt.patient.user.email
            subject = "Appointment Reminder"
            body = f"You have an appointment today at {appt.time} with Dr. {appt.doctor.name}"
            print(f"EMAIL TO: {to}\n{body}")
            count += 1

            # Log activity
            log = ActivityLog(
                doctor_id=appt.doctor_id,
                activity_type='reminder_sent',
                description=f"Reminder sent to patient {appt.patient.name}"
            )
            db.session.add(log)

    db.session.commit()
    return f"Sent {count} reminders"
