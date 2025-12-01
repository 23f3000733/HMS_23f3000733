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
        # For HTML emails, use html instead of body
        msg.html = body
        
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
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Account Flagged</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #2c3e50; margin-bottom: 10px;">Account Flagged</h1>
            <div style="width: 50px; height: 3px; background-color: #e74c3c; margin: 0 auto;"></div>
        </div>
        
        <div style="background-color: #ffffff; padding: 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <p style="font-size: 18px; margin-bottom: 20px;">Dear <strong>Dr. {doctor_name}</strong>,</p>
            
            <div style="background-color: #fadbd8; padding: 20px; border-radius: 8px; margin-bottom: 25px; border-left: 4px solid #e74c3c;">
                <h2 style="color: #c0392b; margin-top: 0;">Important Notice</h2>
                <p style="margin-bottom: 0;">Your account has been flagged by the administrator.</p>
                <p style="margin-top: 10px; margin-bottom: 0;">You no longer have access to the HMS dashboard until this is resolved.</p>
            </div>
            
            <p style="margin-bottom: 25px;">Please contact the administrator for clarification and to resolve this issue.</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <div style="display: inline-block; background-color: #e74c3c; color: white; padding: 12px 25px; border-radius: 5px; text-decoration: none; font-weight: bold;">
                    Hospital Management System
                </div>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 20px; color: #7f8c8d; font-size: 14px;">
            <p style="margin-bottom: 5px;">© 2025 Hospital Management System. All rights reserved.</p>
            <p>This is an automated message. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
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
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Account Flagged</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #2c3e50; margin-bottom: 10px;">Account Flagged</h1>
            <div style="width: 50px; height: 3px; background-color: #e74c3c; margin: 0 auto;"></div>
        </div>
        
        <div style="background-color: #ffffff; padding: 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <p style="font-size: 18px; margin-bottom: 20px;">Dear <strong>{patient_name}</strong>,</p>
            
            <div style="background-color: #fadbd8; padding: 20px; border-radius: 8px; margin-bottom: 25px; border-left: 4px solid #e74c3c;">
                <h2 style="color: #c0392b; margin-top: 0;">Important Notice</h2>
                <p style="margin-bottom: 0;">Your account has been flagged by the hospital administration.</p>
            </div>
            
            <p style="margin-bottom: 25px;">Please contact the administration for further information.</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <div style="display: inline-block; background-color: #e74c3c; color: white; padding: 12px 25px; border-radius: 5px; text-decoration: none; font-weight: bold;">
                    Hospital Management System
                </div>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 20px; color: #7f8c8d; font-size: 14px;">
            <p style="margin-bottom: 5px;">© 2025 Hospital Management System. All rights reserved.</p>
            <p>This is an automated message. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
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
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prescription from Dr. {doctor_name}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #2c3e50; margin-bottom: 10px;">Medical Prescription</h1>
            <div style="width: 50px; height: 3px; background-color: #9b59b6; margin: 0 auto;"></div>
        </div>
        
        <div style="background-color: #ffffff; padding: 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <p style="font-size: 18px; margin-bottom: 20px;">Dear <strong>{patient_name}</strong>,</p>
            
            <p style="margin-bottom: 25px;">Here are your prescription details from Dr. {doctor_name}:</p>
            
            <div style="background-color: #f5e8fc; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                <h2 style="color: #8e44ad; margin-top: 0; border-bottom: 2px solid #9b59b6; padding-bottom: 10px;">Prescription Details</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold; width: 30%;">Date:</td>
                        <td style="padding: 8px 0;">{date}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold;">Doctor:</td>
                        <td style="padding: 8px 0;">Dr. {doctor_name}</td>
                    </tr>
                </table>
            </div>
            
            <div style="background-color: #e8f4fc; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                <h3 style="color: #2980b9; margin-top: 0; border-bottom: 1px solid #3498db; padding-bottom: 10px;">DIAGNOSIS</h3>
                <p style="margin: 10px 0; white-space: pre-wrap;">{diagnosis}</p>
            </div>
            
            <div style="background-color: #e8fcf4; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                <h3 style="color: #27ae60; margin-top: 0; border-bottom: 1px solid #2ecc71; padding-bottom: 10px;">PRESCRIPTION</h3>
                <p style="margin: 10px 0; white-space: pre-wrap; font-family: monospace; background-color: #f8f9fa; padding: 15px; border-radius: 5px;">{prescription}</p>
            </div>
            
            {f'''
            <div style="background-color: #fff8e1; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                <h3 style="color: #d35400; margin-top: 0; border-bottom: 1px solid #f39c12; padding-bottom: 10px;">NOTES</h3>
                <p style="margin: 10px 0; white-space: pre-wrap;">{notes}</p>
            </div>
            ''' if notes else ''}
            
            <div style="background-color: #fef9e7; padding: 20px; border-radius: 8px; margin-bottom: 25px; border-left: 4px solid #f1c40f;">
                <h3 style="color: #d35400; margin-top: 0;">Important Instructions</h3>
                <ul style="padding-left: 20px; margin-bottom: 0;">
                    <li style="margin-bottom: 10px;">Follow the directions given exactly as prescribed</li>
                    <li style="margin-bottom: 10px;">Contact your doctor if you experience any adverse reactions</li>
                    <li style="margin-bottom: 10px;">Keep this prescription for your records</li>
                    <li style="margin-bottom: 10px;">Bring this prescription when visiting the pharmacy</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <div style="display: inline-block; background-color: #9b59b6; color: white; padding: 12px 25px; border-radius: 5px; text-decoration: none; font-weight: bold;">
                    Hospital Management System
                </div>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 20px; color: #7f8c8d; font-size: 14px;">
            <p style="margin-bottom: 5px;">© 2025 Hospital Management System. All rights reserved.</p>
            <p>This is an automated message. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
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
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Appointment Confirmation</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #2c3e50; margin-bottom: 10px;">Appointment Confirmed</h1>
            <div style="width: 50px; height: 3px; background-color: #3498db; margin: 0 auto;"></div>
        </div>
        
        <div style="background-color: #ffffff; padding: 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <p style="font-size: 18px; margin-bottom: 20px;">Dear <strong>{patient_name}</strong>,</p>
            
            <p style="margin-bottom: 25px;">Your appointment has been successfully booked. Here are the details:</p>
            
            <div style="background-color: #e8f4fc; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                <h2 style="color: #2980b9; margin-top: 0; border-bottom: 2px solid #3498db; padding-bottom: 10px;">Appointment Details</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold; width: 40%;">Doctor:</td>
                        <td style="padding: 8px 0;">Dr. {doctor_name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold;">Date:</td>
                        <td style="padding: 8px 0;">{appointment_date}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold;">Time:</td>
                        <td style="padding: 8px 0;">{appointment_time}</td>
                    </tr>
                </table>
            </div>
            
            <div style="background-color: #fff8e1; padding: 20px; border-radius: 8px; margin-bottom: 25px; border-left: 4px solid #f39c12;">
                <h3 style="color: #d35400; margin-top: 0;">Important Information</h3>
                <ul style="padding-left: 20px; margin-bottom: 0;">
                    <li style="margin-bottom: 10px;">Please arrive 15 minutes before your scheduled appointment</li>
                    <li style="margin-bottom: 10px;">Bring your ID and any relevant medical documents</li>
                    <li style="margin-bottom: 10px;">In case of emergency, contact us at least 2 hours in advance</li>
                </ul>
            </div>
            
            <p style="margin-bottom: 25px;">If you need to reschedule or cancel your appointment, please contact us at least 24 hours in advance.</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <div style="display: inline-block; background-color: #3498db; color: white; padding: 12px 25px; border-radius: 5px; text-decoration: none; font-weight: bold;">
                    Hospital Management System
                </div>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 20px; color: #7f8c8d; font-size: 14px;">
            <p style="margin-bottom: 5px;">© 2025 Hospital Management System. All rights reserved.</p>
            <p>This is an automated message. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
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
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>New Appointment Notification</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #2c3e50; margin-bottom: 10px;">New Appointment</h1>
            <div style="width: 50px; height: 3px; background-color: #27ae60; margin: 0 auto;"></div>
        </div>
        
        <div style="background-color: #ffffff; padding: 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <p style="font-size: 18px; margin-bottom: 20px;">Dear <strong>Dr. {doctor_name}</strong>,</p>
            
            <p style="margin-bottom: 25px;">You have a new appointment booking. Here are the details:</p>
            
            <div style="background-color: #e8f8f5; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                <h2 style="color: #27ae60; margin-top: 0; border-bottom: 2px solid #2ecc71; padding-bottom: 10px;">Appointment Details</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold; width: 40%;">Patient:</td>
                        <td style="padding: 8px 0;">{patient_name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold;">Date:</td>
                        <td style="padding: 8px 0;">{appointment_date}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold;">Time:</td>
                        <td style="padding: 8px 0;">{appointment_time}</td>
                    </tr>
                </table>
            </div>
            
            <div style="background-color: #fef9e7; padding: 20px; border-radius: 8px; margin-bottom: 25px; border-left: 4px solid #f1c40f;">
                <h3 style="color: #d35400; margin-top: 0;">Schedule Reminder</h3>
                <p>Please review your schedule and prepare for the appointment.</p>
            </div>
            
            <p style="margin-bottom: 25px;">If you need to make any changes to this appointment, please update the system accordingly.</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <div style="display: inline-block; background-color: #27ae60; color: white; padding: 12px 25px; border-radius: 5px; text-decoration: none; font-weight: bold;">
                    Hospital Management System
                </div>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 20px; color: #7f8c8d; font-size: 14px;">
            <p style="margin-bottom: 5px;">© 2025 Hospital Management System. All rights reserved.</p>
            <p>This is an automated message. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
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
