from celery_app import celery
import csv
import io
from datetime import datetime

@celery.task(name='tasks.export_tasks.export_patient_history', bind=True, max_retries=3)
def export_patient_history(self, patient_id):
    print(f"EXECUTING patient history export task for patient ID: {patient_id}")
    
    from models import Appointment, Treatment, db, ActivityLog, PatientDetails

    try:
        # Get patient details first
        patient = PatientDetails.query.get(patient_id)
        if not patient:
            raise Exception(f"Patient with ID {patient_id} not found")
            
        appointments = Appointment.query.filter_by(
            patient_id=patient_id,
            status='Completed'
        ).all()
        print(f"Found {len(appointments)} completed appointments for export")

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

                # Log the export
                log = ActivityLog(
                    doctor_id=appt.doctor_id,
                    activity_type='history_export',
                    description=f"Exported history for {appt.patient.name}"
                )
                db.session.add(log)

        db.session.commit()

        csv_content = output.getvalue()
        print(f"Generated CSV content with {len(csv_content)} characters")
        
        # Always send the email, even if there are no appointments
        to = patient.user.email
        subject = "Your Patient History"
        body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Patient History Export</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #2c3e50; margin-bottom: 10px;">Patient History Export</h1>
            <div style="width: 50px; height: 3px; background-color: #34495e; margin: 0 auto;"></div>
        </div>
        
        <div style="background-color: #ffffff; padding: 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <p style="font-size: 18px; margin-bottom: 20px;">Dear <strong>{patient.name}</strong>,</p>
            
            <p style="margin-bottom: 25px;">Please find attached your patient history record.</p>
            
            <div style="background-color: #e8f4fc; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                <h2 style="color: #2980b9; margin-top: 0; border-bottom: 2px solid #3498db; padding-bottom: 10px;">Export Details</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold; width: 40%;">Records Exported:</td>
                        <td style="padding: 8px 0;">{len(appointments)} completed appointments</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold;">Export Date:</td>
                        <td style="padding: 8px 0;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold;">File Format:</td>
                        <td style="padding: 8px 0;">CSV (Comma-Separated Values)</td>
                    </tr>
                </table>
            </div>
            
            <p style="margin-bottom: 25px;">You can open this file with any spreadsheet application like Microsoft Excel or Google Sheets.</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <div style="display: inline-block; background-color: #34495e; color: white; padding: 12px 25px; border-radius: 5px; text-decoration: none; font-weight: bold;">
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
        from tasks.notification_tasks import send_email
        print(f"Sending export email to: {to}")
        send_email(
            to, 
            subject, 
            body, 
            attachment=csv_content, 
            attachment_name="patient_history.csv", 
            attachment_type="text/csv"
        )
        
        print(f"SENDING EMAIL TO: {to}")
        print("Patient history CSV generated and sent.")
        
        result_msg = f"Exported history for patient {patient_id}"
        print(f"TASK RESULT: {result_msg}")
        return result_msg
    except Exception as exc:
        print(f"FAILED TO EXPORT PATIENT HISTORY FOR PATIENT {patient_id}: {str(exc)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        # Retry with exponential backoff: 60s, 120s, 240s
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

@celery.task(name='tasks.export_tasks.export_doctor_data', bind=True, max_retries=3)
def export_doctor_data(self, doctor_id, data_type):
    print(f"EXECUTING doctor data export task for doctor ID: {doctor_id}, data type: {data_type}")
    
    from models import DoctorDetails, db
    from services.doctor_service import DoctorService

    try:
        doctor = DoctorDetails.query.get(doctor_id)
        if not doctor:
            raise Exception(f"Doctor with ID {doctor_id} not found")

        # Generate CSV data
        csv_content = DoctorService.export_data_csv(doctor_id, data_type)
        print(f"Generated CSV content with {len(csv_content)} characters")

        # Determine email subject and attachment name based on data type
        if data_type == 'prescriptions':
            subject = "Your Prescriptions Data"
            attachment_name = "prescriptions.csv"
        elif data_type == 'appointments':
            subject = "Your Appointments Data"
            attachment_name = "appointments.csv"
        elif data_type == 'patients':
            subject = "Your Patients Data"
            attachment_name = "patients.csv"
        else:
            subject = f"Your {data_type} Data"
            attachment_name = f"{data_type}.csv"

        # Send the email with attachment
        to = doctor.user.email
        body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #2c3e50; margin-bottom: 10px;">{subject}</h1>
            <div style="width: 50px; height: 3px; background-color: #34495e; margin: 0 auto;"></div>
        </div>
        
        <div style="background-color: #ffffff; padding: 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <p style="font-size: 18px; margin-bottom: 20px;">Dear <strong>Dr. {doctor.name}</strong>,</p>
            
            <p style="margin-bottom: 25px;">Please find attached your {data_type} data export.</p>
            
            <div style="background-color: #e8f4fc; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                <h2 style="color: #2980b9; margin-top: 0; border-bottom: 2px solid #3498db; padding-bottom: 10px;">Export Details</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold; width: 40%;">Data Type:</td>
                        <td style="padding: 8px 0;">{data_type.capitalize()}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold;">Export Date:</td>
                        <td style="padding: 8px 0;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold;">File Format:</td>
                        <td style="padding: 8px 0;">CSV (Comma-Separated Values)</td>
                    </tr>
                </table>
            </div>
            
            <p style="margin-bottom: 25px;">You can open this file with any spreadsheet application like Microsoft Excel or Google Sheets.</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <div style="display: inline-block; background-color: #34495e; color: white; padding: 12px 25px; border-radius: 5px; text-decoration: none; font-weight: bold;">
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
        from tasks.notification_tasks import send_email
        print(f"Sending export email to: {to}")
        send_email(
            to, 
            subject, 
            body, 
            attachment=csv_content, 
            attachment_name=attachment_name, 
            attachment_type="text/csv"
        )
        
        print(f"SENDING EMAIL TO: {to}")
        print(f"Doctor {data_type} CSV generated and sent.")
        
        result_msg = f"Exported {data_type} for doctor {doctor_id}"
        print(f"TASK RESULT: {result_msg}")
        return result_msg
    except Exception as exc:
        print(f"FAILED TO EXPORT DOCTOR DATA FOR DOCTOR {doctor_id}, TYPE {data_type}: {str(exc)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        # Retry with exponential backoff: 60s, 120s, 240s
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

@celery.task(name='tasks.export_tasks.export_admin_data', bind=True, max_retries=3)
def export_admin_data(self, admin_id, data_type):
    print(f"EXECUTING admin data export task for admin ID: {admin_id}, data type: {data_type}")
    
    from models import User, DoctorDetails, PatientDetails, Appointment, db

    try:
        admin_user = User.query.get(admin_id)
        if not admin_user:
            raise Exception(f"Admin with ID {admin_id} not found")

        # Generate CSV data based on data type
        output = io.StringIO()
        writer = csv.writer(output)
        
        if data_type == 'doctors':
            writer.writerow(['ID', 'Name', 'Email', 'Specialization', 'Experience', 'Active', 'Flagged'])
            doctors = DoctorDetails.query.join(DoctorDetails.user).all()
            for doctor in doctors:
                writer.writerow([
                    doctor.id,
                    doctor.name,
                    doctor.user.email if doctor.user else 'N/A',
                    doctor.specialization,
                    doctor.experience,
                    doctor.user.active if doctor.user else 'N/A',
                    doctor.flagged
                ])
            subject = "Doctors Data Export"
            attachment_name = "doctors.csv"
        elif data_type == 'patients':
            writer.writerow(['ID', 'Name', 'Email', 'Age', 'Contact', 'Active', 'Flagged'])
            patients = PatientDetails.query.join(PatientDetails.user).all()
            for patient in patients:
                writer.writerow([
                    patient.id,
                    patient.name,
                    patient.user.email if patient.user else 'N/A',
                    patient.age,
                    patient.contact,
                    patient.user.active if patient.user else 'N/A',
                    patient.flagged
                ])
            subject = "Patients Data Export"
            attachment_name = "patients.csv"
        elif data_type == 'appointments':
            writer.writerow(['ID', 'Doctor', 'Patient', 'Date', 'Time', 'Status'])
            appointments = Appointment.query.join(Appointment.doctor).join(Appointment.patient).all()
            for appt in appointments:
                writer.writerow([
                    appt.id,
                    appt.doctor.name if appt.doctor else 'N/A',
                    appt.patient.name if appt.patient else 'N/A',
                    appt.date.isoformat() if appt.date else '',
                    str(appt.time),
                    appt.status
                ])
            subject = "Appointments Data Export"
            attachment_name = "appointments.csv"
        else:
            raise Exception(f"Unsupported data type: {data_type}")

        csv_content = output.getvalue()
        print(f"Generated CSV content with {len(csv_content)} characters")

        # Send the email with attachment
        to = admin_user.email
        body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #2c3e50; margin-bottom: 10px;">{subject}</h1>
            <div style="width: 50px; height: 3px; background-color: #34495e; margin: 0 auto;"></div>
        </div>
        
        <div style="background-color: #ffffff; padding: 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <p style="font-size: 18px; margin-bottom: 20px;">Dear <strong>Admin</strong>,</p>
            
            <p style="margin-bottom: 25px;">Please find attached the {data_type} data export.</p>
            
            <div style="background-color: #e8f4fc; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                <h2 style="color: #2980b9; margin-top: 0; border-bottom: 2px solid #3498db; padding-bottom: 10px;">Export Details</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold; width: 40%;">Data Type:</td>
                        <td style="padding: 8px 0;">{data_type.capitalize()}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold;">Export Date:</td>
                        <td style="padding: 8px 0;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; font-weight: bold;">File Format:</td>
                        <td style="padding: 8px 0;">CSV (Comma-Separated Values)</td>
                    </tr>
                </table>
            </div>
            
            <p style="margin-bottom: 25px;">You can open this file with any spreadsheet application like Microsoft Excel or Google Sheets.</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <div style="display: inline-block; background-color: #34495e; color: white; padding: 12px 25px; border-radius: 5px; text-decoration: none; font-weight: bold;">
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
        from tasks.notification_tasks import send_email
        print(f"Sending export email to: {to}")
        send_email(
            to, 
            subject, 
            body, 
            attachment=csv_content, 
            attachment_name=attachment_name, 
            attachment_type="text/csv"
        )
        
        print(f"SENDING EMAIL TO: {to}")
        print(f"Admin {data_type} CSV generated and sent.")
        
        result_msg = f"Exported {data_type} for admin {admin_id}"
        print(f"TASK RESULT: {result_msg}")
        return result_msg
    except Exception as exc:
        print(f"FAILED TO EXPORT ADMIN DATA FOR ADMIN {admin_id}, TYPE {data_type}: {str(exc)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        # Retry with exponential backoff: 60s, 120s, 240s
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
