"""
Doctor Service Layer
Contains business logic for doctor operations
"""
from extensions import db
from models import (
    Appointment, Treatment, DoctorDetails, PatientDetails
)
from utils.jwt_auth import get_current_user_from_jwt
from datetime import date, timedelta
from sqlalchemy import func
import csv
import io
import logging

logger = logging.getLogger(__name__)

class DoctorService:
    """Service class for doctor operations"""
    
    @staticmethod
    def get_current_doctor():
        """Get the doctor details for the current logged-in user"""
        current_user = get_current_user_from_jwt()
        user_id = current_user.get('user_id')
        if not user_id:
            return None
        return DoctorDetails.query.filter_by(user_id=user_id).first()
    
    @staticmethod
    def get_dashboard_stats(doctor_id):
        """Get dashboard statistics for a doctor"""
        total_appointments = Appointment.query.filter_by(doctor_id=doctor_id).count()
        today_appointments = Appointment.query.filter_by(
            doctor_id=doctor_id,
            date=date.today()
        ).count()
        completed_appointments = Appointment.query.filter_by(
            doctor_id=doctor_id,
            status='Completed'
        ).count()
        
        total_patients = db.session.query(
            func.count(func.distinct(Appointment.patient_id))
        ).filter(Appointment.doctor_id == doctor_id).scalar()
        
        # Recent patients
        recent_patient_ids = db.session.query(Appointment.patient_id)\
            .filter(Appointment.doctor_id == doctor_id)\
            .distinct()\
            .order_by(Appointment.date.desc())\
            .limit(5)\
            .all()
        
        recent_patients = []
        for (patient_id,) in recent_patient_ids:
            patient = PatientDetails.query.get(patient_id)
            if patient:
                recent_patients.append({
                    'id': patient.id,
                    'name': patient.name,
                    'age': patient.age,
                    'contact': patient.contact
                })
        
        # Recent appointments
        recent_appointments = Appointment.query.filter_by(doctor_id=doctor_id)\
            .order_by(Appointment.date.desc(), Appointment.time.desc())\
            .limit(5)\
            .all()
        
        appointments_list = [{
            'id': a.id,
            'patient_name': a.patient.name,
            'patient_id': a.patient.id,
            'date': a.date.isoformat() if a.date else None,
            'time': str(a.time),
            'status': a.status
        } for a in recent_appointments]
        
        return {
            'statistics': {
                'total_appointments': total_appointments,
                'today_appointments': today_appointments,
                'total_patients': total_patients,
                'completed_appointments': completed_appointments
            },
            'recent_patients': recent_patients,
            'recent_appointments': appointments_list
        }
    
    @staticmethod
    def get_all_appointments(doctor_id):
        """Get all appointments for a doctor"""
        appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()
        
        return [{
            'id': a.id,
            'patient_name': a.patient.name,
            'patient_id': a.patient.id,
            'patient_age': a.patient.age,
            'patient_contact': a.patient.contact,
            'date': a.date.isoformat() if a.date else None,
            'time': str(a.time),
            'status': a.status
        } for a in appointments]
    
    @staticmethod
    def complete_appointment(appointment_id, doctor_id, data):
        """Complete an appointment with treatment details"""
        appointment = Appointment.query.get_or_404(appointment_id)
        
        if appointment.doctor_id != doctor_id:
            raise PermissionError("Unauthorized")
        
        appointment.status = 'Completed'
        
        treatment = Treatment(
            appointment_id=appointment.id,
            diagnosis=data.get('diagnosis'),
            prescription=data.get('prescription'),
            notes=data.get('notes')
        )
        
        db.session.add(treatment)
        db.session.commit()
        
        logger.info(f"Appointment {appointment_id} completed by doctor {doctor_id}")
        return appointment
    
    @staticmethod
    def cancel_appointment(appointment_id, doctor_id):
        """Cancel an appointment"""
        appointment = Appointment.query.get_or_404(appointment_id)
        
        if appointment.doctor_id != doctor_id:
            raise PermissionError("Unauthorized")
        
        appointment.status = 'Cancelled'
        db.session.commit()
        
        logger.info(f"Appointment {appointment_id} cancelled by doctor {doctor_id}")
    
    @staticmethod
    def reschedule_appointment(appointment_id, doctor_id, new_date, new_time):
        """Reschedule an appointment"""
        appointment = Appointment.query.get_or_404(appointment_id)
        
        if appointment.doctor_id != doctor_id:
            raise PermissionError("Unauthorized")
        
        appointment.date = new_date
        appointment.time = new_time
        db.session.commit()
        
        logger.info(f"Appointment {appointment_id} rescheduled by doctor {doctor_id}")
        return appointment
    
    @staticmethod
    def get_patients(doctor_id):
        """Get all patients who have appointments with this doctor"""
        patient_ids = db.session.query(Appointment.patient_id)\
            .filter(Appointment.doctor_id == doctor_id)\
            .distinct()\
            .all()
        
        patients = []
        for (patient_id,) in patient_ids:
            patient = PatientDetails.query.get(patient_id)
            if patient:
                appointment_count = Appointment.query.filter_by(
                    doctor_id=doctor_id,
                    patient_id=patient_id
                ).count()
                
                patients.append({
                    'id': patient.id,
                    'name': patient.name,
                    'age': patient.age,
                    'contact': patient.contact,
                    'email': patient.user.email if patient.user else None,
                    'appointment_count': appointment_count
                })
        
        return patients
    
    @staticmethod
    def get_patient_history(doctor_id, patient_id):
        """Get appointment history for a specific patient"""
        appointments = Appointment.query.filter_by(
            doctor_id=doctor_id,
            patient_id=patient_id
        ).order_by(Appointment.date.desc()).all()
        
        history = []
        for a in appointments:
            appt_data = {
                'id': a.id,
                'date': a.date.isoformat() if a.date else None,
                'time': str(a.time),
                'status': a.status,
                'diagnosis': None,
                'prescription': None,
                'notes': None
            }
            
            if a.treatment:
                appt_data['diagnosis'] = a.treatment.diagnosis
                appt_data['prescription'] = a.treatment.prescription
                appt_data['notes'] = a.treatment.notes
            
            history.append(appt_data)
        
        patient = PatientDetails.query.get(patient_id)
        return {
            'patient': {
                'id': patient.id,
                'name': patient.name,
                'age': patient.age,
                'contact': patient.contact,
                'medical_history': patient.medical_history
            },
            'appointments': history
        }
    
    @staticmethod
    def get_prescriptions(doctor_id):
        """Get all prescriptions issued by this doctor"""
        treatments = db.session.query(Treatment)\
            .join(Appointment)\
            .filter(Appointment.doctor_id == doctor_id)\
            .order_by(Treatment.id.desc())\
            .all()
        
        prescriptions = []
        for t in treatments:
            prescriptions.append({
                'id': t.id,
                'appointment_id': t.appointment_id,
                'patient_name': t.appointment.patient.name,
                'patient_id': t.appointment.patient_id,
                'date': t.appointment.date.isoformat() if t.appointment.date else None,
                'diagnosis': t.diagnosis,
                'prescription': t.prescription,
                'notes': t.notes,
                'email_sent': t.email_sent,
                'resend_count': t.resend_count
            })
        
        return prescriptions
    
    @staticmethod
    def get_prescription_by_id(prescription_id, doctor_id=None):
        """Get a specific prescription by ID, optionally verifying doctor ownership"""
        treatment = Treatment.query.get(prescription_id)
        
        if not treatment:
            return None
            
        # If doctor_id is provided, verify ownership
        if doctor_id and treatment.appointment.doctor_id != doctor_id:
            return None
            
        # Get patient details
        appointment = treatment.appointment
        patient = appointment.patient
        
        return {
            'id': treatment.id,
            'appointment_id': appointment.id,
            'patient_name': patient.name,
            'patient_email': patient.user.email if patient.user else None,
            'patient_id': patient.id,
            'date': appointment.date.isoformat() if appointment.date else None,
            'diagnosis': treatment.diagnosis,
            'prescription': treatment.prescription,
            'notes': treatment.notes
        }
    
    @staticmethod
    def export_data_csv(doctor_id, data_type):
        """Export doctor data as CSV"""
        logger.info(f"GENERATING CSV DATA - Doctor ID: {doctor_id}, Data type: {data_type}")
        
        output = io.StringIO()
        
        if data_type == 'appointments':
            logger.info("Generating appointments CSV...")
            appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()
            logger.info(f"Found {len(appointments)} appointments for doctor {doctor_id}")
            
            writer = csv.writer(output)
            writer.writerow(['ID', 'Patient', 'Date', 'Time', 'Status'])
            
            for i, a in enumerate(appointments):
                try:
                    row = [
                        a.id, 
                        a.patient.name if a.patient else 'Unknown', 
                        a.date.isoformat() if a.date else '',
                        str(a.time) if a.time else '',
                        a.status if a.status else ''
                    ]
                    writer.writerow(row)
                    if i < 5:  # Log first 5 rows for debugging
                        logger.debug(f"Row {i+1}: {row}")
                except Exception as e:
                    logger.error(f"Error processing appointment {a.id}: {str(e)}")
                    writer.writerow([a.id, 'Error', '', '', ''])
            
            logger.info(f"Appointments CSV generation completed. Rows: {len(appointments)}")
            
        elif data_type == 'prescriptions':
            logger.info("Generating prescriptions CSV...")
            treatments = db.session.query(Treatment)\
                .join(Appointment)\
                .filter(Appointment.doctor_id == doctor_id)\
                .all()
            logger.info(f"Found {len(treatments)} treatments for doctor {doctor_id}")
            
            writer = csv.writer(output)
            writer.writerow(['ID', 'Patient', 'Date', 'Diagnosis', 'Prescription'])
            
            for i, t in enumerate(treatments):
                try:
                    row = [
                        t.id, 
                        t.appointment.patient.name if t.appointment and t.appointment.patient else 'Unknown',
                        t.appointment.date.isoformat() if t.appointment and t.appointment.date else '',
                        t.diagnosis if t.diagnosis else '',
                        t.prescription if t.prescription else ''
                    ]
                    writer.writerow(row)
                    if i < 5:  # Log first 5 rows for debugging
                        logger.debug(f"Row {i+1}: {row}")
                except Exception as e:
                    logger.error(f"Error processing treatment {t.id}: {str(e)}")
                    writer.writerow([t.id, 'Error', '', '', ''])
            
            logger.info(f"Prescriptions CSV generation completed. Rows: {len(treatments)}")
            
        elif data_type == 'patients':
            logger.info("Generating patients CSV...")
            patients = DoctorService.get_patients(doctor_id)
            logger.info(f"Found {len(patients)} patients for doctor {doctor_id}")
            
            writer = csv.writer(output)
            writer.writerow(['ID', 'Name', 'Age', 'Contact', 'Appointments'])
            
            for i, p in enumerate(patients):
                try:
                    row = [
                        p['id'], 
                        p['name'] if p['name'] else 'Unknown',
                        p['age'] if p['age'] else '',
                        p['contact'] if p['contact'] else '',
                        p['appointment_count'] if 'appointment_count' in p else ''
                    ]
                    writer.writerow(row)
                    if i < 5:  # Log first 5 rows for debugging
                        logger.debug(f"Row {i+1}: {row}")
                except Exception as e:
                    logger.error(f"Error processing patient {p.get('id', 'Unknown')}: {str(e)}")
                    writer.writerow(['Error', '', '', '', ''])
            
            logger.info(f"Patients CSV generation completed. Rows: {len(patients)}")
            
        else:
            logger.error(f"Unsupported data type: {data_type}")
            raise ValueError(f"Unsupported data type: {data_type}")
        
        csv_content = output.getvalue()
        logger.info(f"Total CSV content size: {len(csv_content)} characters")
        return csv_content
    
    @staticmethod
    def get_profile(doctor_id):
        """Get doctor profile"""
        doctor = DoctorDetails.query.get_or_404(doctor_id)
        
        return {
            'id': doctor.id,
            'name': doctor.name,
            'email': doctor.user.email,
            'specialization': doctor.specialization,
            'experience': doctor.experience
        }
    
    @staticmethod
    def update_profile(doctor_id, data):
        """Update doctor profile"""
        doctor = DoctorDetails.query.get_or_404(doctor_id)
        
        doctor.name = data.get('name', doctor.name)
        doctor.specialization = data.get('specialization', doctor.specialization)
        doctor.experience = data.get('experience', doctor.experience)
        
        db.session.commit()
        logger.info(f"Profile updated for doctor {doctor_id}")
        return doctor
    
    @staticmethod
    def get_analytics(doctor_id):
        """Get analytics data for doctor"""
        appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()
        
        total = len(appointments)
        
        # Calculate status distribution
        status_counts = {}
        for a in appointments:
            status_counts[a.status] = status_counts.get(a.status, 0) + 1
            
        status_distribution = [
            {'status': status, 'count': count}
            for status, count in status_counts.items()
        ]
        
        # Unique patients
        unique_patients = db.session.query(func.count(func.distinct(Appointment.patient_id)))\
            .filter(Appointment.doctor_id == doctor_id).scalar()
            
        # Daily trends (last 7 days)
        daily_trends = []
        today = date.today()
        for i in range(7):
            day = today - timedelta(days=i)
            day_count = sum(1 for a in appointments if a.date == day)
            daily_trends.append({
                'date': day.isoformat(),
                'count': day_count
            })
        
        return {
            'total_appointments': total,
            'unique_patients': unique_patients,
            'status_distribution': status_distribution,
            'trends': list(reversed(daily_trends))
        }
