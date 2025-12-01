from celery_app import celery
import csv
import io

@celery.task(name='tasks.export_tasks.export_patient_history', bind=True, max_retries=3)
def export_patient_history(self, patient_id):
    print(f"EXECUTING patient history export task for patient ID: {patient_id}")
    
    from models import Appointment, Treatment, db, ActivityLog

    try:
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
        
        # Send the email with attachment
        if appointments:
            patient = appointments[0].patient
            to = patient.user.email
            subject = "Your Patient History"
            body = f"""
Dear {patient.name},

Please find attached your patient history record.

Regards,
Hospital Management System
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
Dear Dr. {doctor.name},

Please find attached your {data_type} data export.

Regards,
Hospital Management System
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
Dear Admin,

Please find attached the {data_type} data export.

Regards,
Hospital Management System
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
