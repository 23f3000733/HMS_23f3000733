"""
Patient Service Layer
Contains business logic for patient operations
"""
from extensions import db
from models import (
    Appointment, DoctorDetails, PatientDetails, PatientDocument,
    PatientActivityLog
)
from utils.jwt_auth import get_current_user_from_jwt
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import logging

logger = logging.getLogger(__name__)

class PatientService:
    """Service class for patient operations"""
    
    @staticmethod
    def get_current_patient():
        """Get the patient details for the current logged-in user"""
        current_user = get_current_user_from_jwt()
        user_id = current_user.get('user_id')
        if not user_id:
            return None
        return PatientDetails.query.filter_by(user_id=user_id).first()
    
    @staticmethod
    def search_doctors(specialization=None):
        """Search for doctors by specialization"""
        query = DoctorDetails.query
        if specialization:
            query = query.filter(
                DoctorDetails.specialization.ilike(f'%{specialization}%')
            )
        
        doctors = query.all()
        return [{
            'id': d.id,
            'name': d.name,
            'specialization': d.specialization,
            'experience': d.experience
        } for d in doctors]
    
    @staticmethod
    def book_appointment(patient_id, doctor_id, appointment_date, appointment_time):
        """Book an appointment for a patient"""
        # Check for existing appointment
        existing = Appointment.query.filter_by(
            doctor_id=doctor_id,
            date=appointment_date,
            time=appointment_time
        ).filter(Appointment.status != 'Cancelled').first()
        
        if existing:
            raise ValueError('Doctor is not available at this time')
        
        appointment = Appointment(
            doctor_id=doctor_id,
            patient_id=patient_id,
            date=appointment_date,
            time=appointment_time,
            status='Booked'
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        # Send email notifications
        try:
            from tasks import send_appointment_confirmation, send_appointment_notification
            
            # Get patient and doctor details
            patient = PatientDetails.query.get(patient_id)
            doctor = DoctorDetails.query.get(doctor_id)
            
            if patient and doctor:
                # Send confirmation to patient
                send_appointment_confirmation.delay(
                    patient.user.email,
                    patient.name,
                    doctor.name,
                    str(appointment_date),
                    str(appointment_time)
                )
                
                # Send notification to doctor
                send_appointment_notification.delay(
                    doctor.user.email,
                    doctor.name,
                    patient.name,
                    str(appointment_date),
                    str(appointment_time)
                )
        except Exception as e:
            # Log the error but don't fail the booking
            logger.error(f"Failed to send appointment notification emails: {str(e)}")
        
        # Log the activity
        PatientService.create_activity_log(
            patient_id,
            'appointment_booked',
            f'Appointment booked with Dr. {appointment.doctor.name} on {appointment_date}'
        )
        
        logger.info(f"Appointment booked for patient {patient_id} with doctor {doctor_id}")
        return appointment
    
    @staticmethod
    def cancel_appointment(appointment_id, patient_id):
        """Cancel an appointment"""
        appointment = Appointment.query.get_or_404(appointment_id)
        
        if appointment.patient_id != patient_id:
            raise PermissionError("Unauthorized")
        
        appointment.status = 'Cancelled'
        db.session.commit()
        
        # Log the activity
        PatientService.create_activity_log(
            patient_id,
            'appointment_cancelled',
            f'Appointment with Dr. {appointment.doctor.name} cancelled'
        )
        
        logger.info(f"Appointment {appointment_id} cancelled by patient {patient_id}")
    
    @staticmethod
    def reschedule_appointment(appointment_id, patient_id, new_date, new_time):
        """Reschedule an appointment"""
        appointment = Appointment.query.get_or_404(appointment_id)
        
        if appointment.patient_id != patient_id:
            raise PermissionError("Unauthorized")
        
        # Check if new slot is available
        existing = Appointment.query.filter_by(
            doctor_id=appointment.doctor_id,
            date=new_date,
            time=new_time
        ).filter(
            Appointment.status != 'Cancelled',
            Appointment.id != appointment_id
        ).first()
        
        if existing:
            raise ValueError('This time slot is not available')
        
        old_date = appointment.date
        old_time = appointment.time
        appointment.date = new_date
        appointment.time = new_time
        db.session.commit()
        
        # Log the activity
        PatientService.create_activity_log(
            patient_id,
            'appointment_rescheduled',
            f'Appointment with Dr. {appointment.doctor.name} rescheduled from {old_date} to {new_date}'
        )
        
        logger.info(f"Appointment {appointment_id} rescheduled by patient {patient_id}")
        return appointment
    
    @staticmethod
    def get_history(patient_id):
        """Get appointment history for a patient"""
        appointments = Appointment.query.filter_by(patient_id=patient_id).all()
        
        return [{
            'id': a.id,
            'doctor_name': a.doctor.name,
            'date': str(a.date),
            'time': str(a.time),
            'status': a.status,
            'diagnosis': a.treatment.diagnosis if a.treatment else None,
            'prescription': a.treatment.prescription if a.treatment else None
        } for a in appointments]
    
    @staticmethod
    def get_profile(patient_id):
        """Get patient profile"""
        patient = PatientDetails.query.get_or_404(patient_id)
        
        return {
            'id': patient.id,
            'name': patient.name,
            'email': patient.user.email,
            'age': patient.age,
            'contact': patient.contact,
            'medical_history': patient.medical_history
        }
    
    @staticmethod
    def update_profile(patient_id, data):
        """Update patient profile"""
        patient = PatientDetails.query.get_or_404(patient_id)
        
        patient.name = data.get('name', patient.name)
        patient.age = data.get('age', patient.age)
        patient.contact = data.get('contact', patient.contact)
        patient.medical_history = data.get('medical_history', patient.medical_history)
        
        db.session.commit()
        logger.info(f"Profile updated for patient {patient_id}")
        return patient
    
    @staticmethod
    def get_dashboard_stats(patient_id):
        """Get dashboard statistics for a patient"""
        appointments = Appointment.query.filter_by(patient_id=patient_id).all()
        
        upcoming = [a for a in appointments if a.status == 'Booked']
        completed = [a for a in appointments if a.status == 'Completed']
        
        # Get the next upcoming appointment (closest future date)
        upcoming_appointment = None
        if upcoming:
            # Sort by date and time to get the earliest
            upcoming_sorted = sorted(upcoming, key=lambda x: (x.date, x.time))
            next_appointment = upcoming_sorted[0]
            upcoming_appointment = {
                'id': next_appointment.id,
                'doctor_name': next_appointment.doctor.name,
                'specialization': next_appointment.doctor.specialization,
                'date': str(next_appointment.date),
                'time': str(next_appointment.time),
                'status': next_appointment.status
            }
        
        return {
            'total_appointments': len(appointments),
            'upcoming_appointments': len(upcoming),
            'completed_appointments': len(completed),
            'upcoming_appointment': upcoming_appointment,
            'recent_activity': PatientService._get_recent_activity(patient_id)
        }
    
    @staticmethod
    def _get_recent_activity(patient_id):
        """Get recent activity for a patient"""
        # Get actual patient activity logs instead of appointment data
        activity_logs = PatientActivityLog.query.filter_by(patient_id=patient_id)\
            .order_by(PatientActivityLog.timestamp.desc())\
            .limit(5)\
            .all()
        
        return [{
            'id': log.id,
            'description': log.description,
            'timestamp': log.timestamp.isoformat() if log.timestamp else None
        } for log in activity_logs]
    
    @staticmethod
    def get_analytics(patient_id):
        """Get analytics data for patient"""
        appointments = Appointment.query.filter_by(patient_id=patient_id).all()
        
        # Calculate visit frequency
        doctor_visits = {}
        for a in appointments:
            doctor_name = a.doctor.name
            doctor_visits[doctor_name] = doctor_visits.get(doctor_name, 0) + 1
        
        top_doctors = sorted(
            doctor_visits.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Visit history by month
        monthly_visits = {}
        for a in appointments:
            month_key = a.date.strftime('%Y-%m')
            monthly_visits[month_key] = monthly_visits.get(month_key, 0) + 1
        
        visit_history = [
            {'month': k, 'visits': v} 
            for k, v in sorted(monthly_visits.items())
        ]
        
        return {
            'total_visits': len(appointments),
            'top_doctors': [{'name': d[0], 'visits': d[1]} for d in top_doctors],
            'visit_history': visit_history
        }
    
    @staticmethod
    def upload_document(patient_id, file, upload_folder):
        """Upload a document for a patient"""
        if not file:
            raise ValueError('No file provided')
        
        filename = secure_filename(file.filename)
        if not filename:
            raise ValueError('Invalid filename')
        
        # Create unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{patient_id}_{timestamp}_{filename}"
        
        # Ensure upload directory exists
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # Save document record
        doc = PatientDocument(
            patient_id=patient_id,
            filename=unique_filename,
            original_filename=filename,
            file_type=file.content_type
        )
        db.session.add(doc)
        db.session.commit()
        
        logger.info(f"Document uploaded for patient {patient_id}")
        return doc
    
    @staticmethod
    def get_documents(patient_id):
        """Get all documents for a patient"""
        documents = PatientDocument.query.filter_by(patient_id=patient_id).all()
        
        return [{
            'id': d.id,
            'filename': d.original_filename,
            'file_type': d.file_type,
            'uploaded_at': str(d.uploaded_at)
        } for d in documents]
    
    @staticmethod
    def get_document(document_id, patient_id):
        """Get a specific document"""
        doc = PatientDocument.query.get_or_404(document_id)
        
        if doc.patient_id != patient_id:
            raise PermissionError("Unauthorized")
        
        return doc
    
    @staticmethod
    def create_activity_log(patient_id, activity_type, description):
        """Create an activity log entry"""
        log = PatientActivityLog(
            patient_id=patient_id,
            activity_type=activity_type,
            description=description
        )
        db.session.add(log)
        db.session.commit()
        
        logger.info(f"Activity logged for patient {patient_id}: {activity_type}")
        return log