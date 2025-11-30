"""
Doctor Service Layer
Contains business logic for doctor operations
"""
from extensions import db
from models import (
    Appointment, Treatment, DoctorDetails, PatientDetails
)
from utils.jwt_auth import get_current_user_from_jwt
from datetime import date, datetime, timedelta
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
    def export_data_csv(doctor_id, data_type):
        """Export doctor data as CSV"""
        output = io.StringIO()
        
        if data_type == 'appointments':
            appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()
            writer = csv.writer(output)
            writer.writerow(['ID', 'Patient', 'Date', 'Time', 'Status'])
            for a in appointments:
                writer.writerow([
                    a.id, a.patient.name, 
                    a.date.isoformat() if a.date else '',
                    str(a.time), a.status
                ])
        
        elif data_type == 'prescriptions':
            treatments = db.session.query(Treatment)\
                .join(Appointment)\
                .filter(Appointment.doctor_id == doctor_id)\
                .all()
            writer = csv.writer(output)
            writer.writerow(['ID', 'Patient', 'Date', 'Diagnosis', 'Prescription'])
            for t in treatments:
                writer.writerow([
                    t.id, t.appointment.patient.name, 
                    t.appointment.date.isoformat() if t.appointment.date else '',
                    t.diagnosis, t.prescription
                ])
        
        elif data_type == 'patients':
            patients = DoctorService.get_patients(doctor_id)
            writer = csv.writer(output)
            writer.writerow(['ID', 'Name', 'Age', 'Contact', 'Appointments'])
            for p in patients:
                writer.writerow([
                    p['id'], p['name'], p['age'], p['contact'], 
                    p['appointment_count']
                ])
        
        return output.getvalue()
    
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
    def export_data_csv(doctor_id, data_type):
        """Export doctor data as CSV"""
        output = io.StringIO()
        
        if data_type == 'appointments':
            appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()
            writer = csv.writer(output)
            writer.writerow(['ID', 'Patient', 'Date', 'Time', 'Status'])
            for a in appointments:
                writer.writerow([
                    a.id, a.patient.name, 
                    a.date.isoformat() if a.date else '',
                    str(a.time), a.status
                ])
        
        elif data_type == 'prescriptions':
            treatments = db.session.query(Treatment)\
                .join(Appointment)\
                .filter(Appointment.doctor_id == doctor_id)\
                .all()
            writer = csv.writer(output)
            writer.writerow(['ID', 'Patient', 'Date', 'Diagnosis', 'Prescription'])
            for t in treatments:
                writer.writerow([
                    t.id, t.appointment.patient.name, 
                    t.appointment.date.isoformat() if t.appointment.date else '',
                    t.diagnosis, t.prescription
                ])
        
        elif data_type == 'patients':
            patients = DoctorService.get_patients(doctor_id)
            writer = csv.writer(output)
            writer.writerow(['ID', 'Name', 'Age', 'Contact', 'Appointments'])
            for p in patients:
                writer.writerow([
                    p['id'], p['name'], p['age'], p['contact'], 
                    p['appointment_count']
                ])
        
        return output.getvalue()
    
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
