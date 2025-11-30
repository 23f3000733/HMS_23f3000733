from celery import shared_task
from datetime import datetime, timedelta
import csv
import io

# Mock email sending
def send_email(to, subject, body):
    print(f"SENDING EMAIL TO: {to}")
    print(f"SUBJECT: {subject}")
    print(f"BODY: {body}")

@shared_task
def send_flag_notification(doctor_email, doctor_name):
    """Send email notification when doctor is flagged"""
    subject = "Account Flagged - Dashboard Access Restricted"
    body = f"""
Dear Dr. {doctor_name},

Your account has been flagged by the administrator.

You no longer have access to the HMS dashboard until this issue is resolved.
Please contact the administrator for more information.

Best regards,
Hospital Management System
    """
    send_email(doctor_email, subject, body)
    return f"Flag notification sent to {doctor_email}"

@shared_task
def send_patient_flag_notification(patient_email, patient_name):
    """Send email notification when patient is flagged"""
    subject = "Account Flagged - Important Notice"
    body = f"""
Dear {patient_name},

Your account has been flagged by the administrator.

Please contact the hospital administration for more information regarding your account status.

Best regards,
Hospital Management System
    """
    send_email(patient_email, subject, body)
    return f"Flag notification sent to {patient_email}"


@shared_task
def daily_reminder():
    from models import Appointment, db, ActivityLog
    # Check appointments for today
    today = datetime.now().date()
    appointments = Appointment.query.filter_by(date=today).all()
    
    count = 0
    for appt in appointments:
        if appt.status == 'Booked':
            # Send reminder to patient
            send_email(
                appt.patient.user.email,
                "Appointment Reminder",
                f"You have an appointment today at {appt.time} with Dr. {appt.doctor.name}"
            )
            count += 1
            
            # Log activity for doctor
            log = ActivityLog(
                doctor_id=appt.doctor_id,
                activity_type='reminder_sent',
                description=f"Reminder sent for appointment with {appt.patient.name}"
            )
            db.session.add(log)
    
    db.session.commit()
    return f"Sent {count} reminders"

@shared_task
def monthly_activity_report():
    from models import DoctorDetails, Appointment, db, ActivityLog
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    
    # Get last month's date range
    today = datetime.now()
    last_month_start = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_month_end = today.replace(day=1) - timedelta(days=1)
    
    doctors = DoctorDetails.query.all()
    
    for doctor in doctors:
        # Count appointments for this doctor in last month
        appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.date >= last_month_start.date(),
            Appointment.date <= last_month_end.date()
        ).all()
        
        completed = len([a for a in appointments if a.status == 'Completed'])
        total = len(appointments)
        
        # Send report
        send_email(
            doctor.user.email,
            "Monthly Activity Report",
            f"Dear Dr. {doctor.name},\n\nYour activity for last month:\nTotal Appointments: {total}\nCompleted: {completed}\n\nThank you!"
        )
        
        # Log activity
        log = ActivityLog(
            doctor_id=doctor.id,
            activity_type='monthly_report',
            description=f"Monthly report generated: {total} appointments, {completed} completed"
        )
        db.session.add(log)
    
    db.session.commit()
    return f"Sent reports to {len(doctors)} doctors"

@shared_task
def export_patient_history(patient_id):
    from models import Appointment, Treatment, db, ActivityLog
    
    appointments = Appointment.query.filter_by(patient_id=patient_id, status='Completed').all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Doctor', 'Diagnosis', 'Prescription', 'Notes'])
    
    for appt in appointments:
        treatment = Treatment.query.filter_by(appointment_id=appt.id).first()
        if treatment:
            writer.writerow([
                appt.date,
                appt.doctor.name,
                treatment.diagnosis,
                treatment.prescription,
                treatment.notes or ''
            ])
            
            # Log activity for doctor
            log = ActivityLog(
                doctor_id=appt.doctor_id,
                activity_type='history_export',
                description=f"Patient history exported for {appt.patient.name}"
            )
            db.session.add(log)
    
    db.session.commit()
    
    # In production, save CSV and send email with attachment
    csv_content = output.getvalue()
    patient = appointments[0].patient if appointments else None
    if patient:
        send_email(
            patient.user.email,
            "Your Medical History",
            f"Dear {patient.name},\n\nYour medical history export is attached.\n\nBest regards,\nHMS"
        )
    
    return f"Exported history for patient {patient_id}"

@shared_task(ignore_result=False)
def send_prescription_email_task(patient_email, patient_name, doctor_name, diagnosis, prescription, notes, date, is_resend=False):
    """Send prescription details to patient via email"""
    subject = f"Prescription from Dr. {doctor_name} - {date}"
    if is_resend:
        subject += " (Resent)"
        
    body = f"""
Dear {patient_name},

Please find your prescription details below:

Date: {date}
Doctor: Dr. {doctor_name}

DIAGNOSIS:
{diagnosis}

PRESCRIPTION:
{prescription}

{f'ADDITIONAL NOTES:\n{notes}\n' if notes else ''}
Please follow the prescription as directed. If you have any questions or concerns, please contact your doctor.

Best regards,
Hospital Management System
    """
    send_email(patient_email, subject, body)
    return f"Prescription email sent to {patient_email}"
