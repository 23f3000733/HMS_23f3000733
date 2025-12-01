from celery_app import celery
from flask_mail import Message
from extensions import mail
from flask import current_app

def send_email(to, subject, body, attachment=None, attachment_name=None, attachment_type=None):
    try:
        msg = Message(subject, recipients=[to])
        msg.body = body
        
        if attachment:
            msg.attach(attachment_name, attachment_type, attachment)
            
        with current_app.app_context():
            mail.send(msg)
            print(f"EMAIL SENT TO: {to}")
    except Exception as e:
        print(f"FAILED TO SEND EMAIL TO {to}: {str(e)}")


@celery.task(name='tasks.notification_tasks.send_flag_notification')
def send_flag_notification(doctor_email, doctor_name):
    subject = "Account Flagged - Dashboard Access Restricted"
    body = f"""
Dear Dr. {doctor_name},

Your account has been flagged by the administrator.
You no longer have access to the HMS dashboard until this is resolved.
Please contact the administrator for clarification.

Best regards,
Hospital Management System
"""
    send_email(doctor_email, subject, body)
    return f"Flag notification sent to {doctor_email}"


@celery.task(name='tasks.notification_tasks.send_patient_flag_notification')
def send_patient_flag_notification(patient_email, patient_name):
    subject = "Account Flagged - Important Notice"
    body = f"""
Dear {patient_name},

Your account has been flagged by the hospital administration.
Please contact the administration for further information.

Best regards,
Hospital Management System
"""
    send_email(patient_email, subject, body)
    return f"Flag notification sent to {patient_email}"


@celery.task(name='tasks.notification_tasks.send_prescription_email_task', ignore_result=False)
def send_prescription_email_task(
    patient_email, patient_name, doctor_name,
    diagnosis, prescription, notes, date,
    is_resend=False
):
    subject = f"Prescription from Dr. {doctor_name} - {date}"
    if is_resend:
        subject += " (Resent)"

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

    send_email(patient_email, subject, body)
    return f"Prescription email sent to {patient_email}"