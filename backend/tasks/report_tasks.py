from celery_app import celery
from datetime import datetime, timedelta

@celery.task
def monthly_activity_report():
    from models import DoctorDetails, Appointment, db, ActivityLog

    today = datetime.now()
    last_month_start = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_month_end = today.replace(day=1) - timedelta(days=1)

    doctors = DoctorDetails.query.all()
    total_sent = 0

    for doctor in doctors:
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
        print(f"SENDING EMAIL TO: {to}\n{body}")
        total_sent += 1

        # Log report generation
        log = ActivityLog(
            doctor_id=doctor.id,
            activity_type='monthly_report',
            description=f"Report: {total} total, {completed} completed"
        )
        db.session.add(log)

    db.session.commit()
    return f"Sent monthly reports to {total_sent} doctors"
