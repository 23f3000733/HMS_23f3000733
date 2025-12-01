from celery_app import celery
import csv
import io

@celery.task(name='tasks.export_tasks.export_patient_history')
def export_patient_history(patient_id):
    from models import Appointment, Treatment, db, ActivityLog

    appointments = Appointment.query.filter_by(
        patient_id=patient_id,
        status='Completed'
    ).all()

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

    return f"Exported history for patient {patient_id}"