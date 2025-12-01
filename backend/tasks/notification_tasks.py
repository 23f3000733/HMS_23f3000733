from celery_app import celery

def send_email(to, subject, body):
    print(f"SENDING EMAIL TO: {to}")
    print(f"SUBJECT: {subject}")
    print(f"BODY:\n{body}")


@celery.task
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


@celery.task
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


@celery.task(ignore_result=False)
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
