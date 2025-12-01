from celery_app import celery
import csv
import io

@celery.task
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

    # "Send" the email
    if appointments:
        patient = appointments[0].patient
        print(f"SENDING EMAIL TO: {patient.user.email}")
        print("Patient history CSV generated.")

    return f"Exported history for patient {patient_id}"
