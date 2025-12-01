import os
import sys
import traceback
from flask import Flask
from config import Config
from extensions import db, mail
from models import user_datastore, Treatment, Appointment, DoctorDetails, PatientDetails
from tasks.notification_tasks import send_prescription_email_task

def test_prescription_email():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    mail.init_app(app)
    
    with app.app_context():
        try:
            # Test the prescription email task directly
            result = send_prescription_email_task(
                patient_email="sangalkartik4@gmail.com",
                patient_name="Test Patient",
                doctor_name="Test Doctor",
                diagnosis="Test Diagnosis",
                prescription="Test Prescription",
                notes="Test Notes",
                date="2023-01-01",
                is_resend=False,
                treatment_id=None
            )
            print(f"Prescription email task result: {result}")
        except Exception as e:
            print(f"Failed to send prescription email: {str(e)}")
            traceback.print_exc()

if __name__ == "__main__":
    test_prescription_email()