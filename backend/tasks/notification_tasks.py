from celery_app import celery
from flask_mail import Message
from extensions import mail
from flask import current_app
from datetime import datetime
import traceback

def send_email(to, subject, body, attachment=None, attachment_name=None, attachment_type=None):
    try:
        print(f"Attempting to send email to: {to}")
        print(f"Subject: {subject}")
        print(f"Mail server: {current_app.config.get('MAIL_SERVER')}")
        print(f"Mail port: {current_app.config.get('MAIL_PORT')}")
        print(f"Mail username: {current_app.config.get('MAIL_USERNAME')}")
        
        msg = Message(subject, recipients=[to])
        msg.body = body
        
        if attachment:
            msg.attach(attachment_name, attachment_type, attachment)
            
        # Make sure we have an app context
        if not current_app:
            from app import app
            with app.app_context():
                mail.send(msg)
        else:
            with current_app.app_context():
                mail.send(msg)
        print(f"EMAIL SENT SUCCESSFULLY TO: {to}")
    except Exception as e:
        print(f"FAILED TO SEND EMAIL TO {to}")
        print(f"Error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise  # Re-raise for task retry


@celery.task(name='tasks.notification_tasks.send_flag_notification', bind=True, max_retries=3)
def send_flag_notification(self, doctor_email, doctor_name):
    print(f"EXECUTING doctor flag notification task:")
    print(f"  Doctor email: {doctor_email}")
    print(f"  Doctor name: {doctor_name}")
    
    subject = "Account Flagged - Dashboard Access Restricted"
    body = f"""
Dear Dr. {doctor_name},

Your account has been flagged by the administrator.
You no longer have access to the HMS dashboard until this is resolved.
Please contact the administrator for clarification.

Best regards,
Hospital Management System
"""
    try:
        send_email(doctor_email, subject, body)
        result_msg = f"Flag notification sent to {doctor_email}"
        print(f"TASK RESULT: {result_msg}")
        return result_msg
    except Exception as exc:
        print(f"FAILED TO SEND FLAG NOTIFICATION TO {doctor_email}: {str(exc)}")
        # Retry with exponential backoff: 60s, 120s, 240s
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery.task(name='tasks.notification_tasks.send_patient_flag_notification', bind=True, max_retries=3)
def send_patient_flag_notification(self, patient_email, patient_name):
    print(f"EXECUTING patient flag notification task:")
    print(f"  Patient email: {patient_email}")
    print(f"  Patient name: {patient_name}")
    
    subject = "Account Flagged - Important Notice"
    body = f"""
Dear {patient_name},

Your account has been flagged by the hospital administration.
Please contact the administration for further information.

Best regards,
Hospital Management System
"""
    try:
        send_email(patient_email, subject, body)
        result_msg = f"Flag notification sent to {patient_email}"
        print(f"TASK RESULT: {result_msg}")
        return result_msg
    except Exception as exc:
        print(f"FAILED TO SEND PATIENT FLAG NOTIFICATION TO {patient_email}: {str(exc)}")
        # Retry with exponential backoff: 60s, 120s, 240s
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery.task(name='tasks.notification_tasks.send_prescription_email_task', bind=True, max_retries=3, ignore_result=False)
def send_prescription_email_task(
    self, patient_email, patient_name, doctor_name,
    diagnosis, prescription, notes, date,
    is_resend=False, treatment_id=None
):
    print(f"EXECUTING prescription email task:")
    print(f"  Patient email: {patient_email}")
    print(f"  Patient name: {patient_name}")
    print(f"  Doctor name: {doctor_name}")
    print(f"  Date: {date}")
    print(f"  Is resend: {is_resend}")
    print(f"  Treatment ID: {treatment_id}")
    
    subject = f"Prescription from Dr. {doctor_name} - {date}"
    if is_resend:
        subject += " (Resent)"
    
    print(f"Preparing to send prescription email:")
    print(f"  Subject: {subject}")

    body = f"""
Dear {patient_name},

Here are your prescription details:

Date: {date}
Doctor: Dr. {doctor_name}

DIAGNOSIS:
{diagnosis}

PRESCRIPTION:
{prescription}

{f'NOTES:\n{notes}\n' if notes else ''}
Please follow the directions given. Contact your doctor for concerns.

Regards,
Hospital Management System
"""

    try:
        send_email(patient_email, subject, body)
        
        # Update treatment record if treatment_id is provided
        if treatment_id:
            from models import Treatment, db
            treatment = Treatment.query.get(treatment_id)
            if treatment:
                treatment.email_sent = True
                treatment.email_sent_at = datetime.utcnow()
                if is_resend:
                    treatment.resend_count += 1
                db.session.commit()
        
        result_msg = f"Prescription email sent to {patient_email}"
        print(f"TASK RESULT: {result_msg}")
        return result_msg
    except Exception as exc:
        # Log the error for debugging
        print(f"FAILED TO SEND PRESCRIPTION EMAIL TO {patient_email}: {str(exc)}")
        
        # Update treatment record with failure status if treatment_id is provided
        if treatment_id:
            from models import Treatment, db
            treatment = Treatment.query.get(treatment_id)
            if treatment:
                # We don't change email_sent to False here as it might have been sent successfully before
                # Just log that we had an error in this attempt
                pass
                # Note: In a more sophisticated system, we might want to track failed attempts separately
        
        # Retry with exponential backoff: 60s, 120s, 240s
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery.task(name='tasks.notification_tasks.send_appointment_confirmation', bind=True, max_retries=3)
def send_appointment_confirmation(self, patient_email, patient_name, doctor_name, appointment_date, appointment_time):
    """Send appointment confirmation email to patient"""
    print(f"EXECUTING appointment confirmation task:")
    print(f"  Patient email: {patient_email}")
    print(f"  Patient name: {patient_name}")
    print(f"  Doctor name: {doctor_name}")
    print(f"  Date: {appointment_date}")
    print(f"  Time: {appointment_time}")
    
    subject = f"Appointment Confirmation with Dr. {doctor_name}"
    
    print(f"Preparing to send appointment confirmation email:")
    print(f"  Subject: {subject}")

    body = f"""
Dear {patient_name},

Your appointment with Dr. {doctor_name} has been successfully booked.

Date: {appointment_date}
Time: {appointment_time}

Please arrive 15 minutes early for your appointment.

Regards,
Hospital Management System
"""

    try:
        send_email(patient_email, subject, body)
        
        result_msg = f"Appointment confirmation sent to {patient_email}"
        print(f"TASK RESULT: {result_msg}")
        return result_msg
    except Exception as exc:
        # Log the error for debugging
        print(f"FAILED TO SEND APPOINTMENT CONFIRMATION TO {patient_email}: {str(exc)}")
        
        # Retry with exponential backoff: 60s, 120s, 240s
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

@celery.task(name='tasks.notification_tasks.send_appointment_notification', bind=True, max_retries=3)
def send_appointment_notification(self, doctor_email, doctor_name, patient_name, appointment_date, appointment_time):
    """Send appointment notification email to doctor"""
    print(f"EXECUTING appointment notification task:")
    print(f"  Doctor email: {doctor_email}")
    print(f"  Doctor name: {doctor_name}")
    print(f"  Patient name: {patient_name}")
    print(f"  Date: {appointment_date}")
    print(f"  Time: {appointment_time}")
    
    subject = f"New Appointment Booking - {patient_name}"
    
    print(f"Preparing to send appointment notification email:")
    print(f"  Subject: {subject}")

    body = f"""
Dear Dr. {doctor_name},

You have a new appointment booking.

Patient: {patient_name}
Date: {appointment_date}
Time: {appointment_time}

Please review your schedule.

Regards,
Hospital Management System
"""

    try:
        send_email(doctor_email, subject, body)
        
        result_msg = f"Appointment notification sent to {doctor_email}"
        print(f"TASK RESULT: {result_msg}")
        return result_msg
    except Exception as exc:
        # Log the error for debugging
        print(f"FAILED TO SEND APPOINTMENT NOTIFICATION TO {doctor_email}: {str(exc)}")
        
        # Retry with exponential backoff: 60s, 120s, 240s
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
