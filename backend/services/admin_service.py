"""
Admin Service Layer
Contains business logic for admin operations
"""
from extensions import db
from models import (
    DoctorDetails, PatientDetails, Appointment, Treatment, 
    ActivityLog, PatientActivityLog, user_datastore, User
)
from flask_security.utils import hash_password
from datetime import datetime
import logging
from utils.sanitizer import InputSanitizer
from utils.constants import DEFAULT_PAGE, DEFAULT_PER_PAGE, MAX_PER_PAGE


logger = logging.getLogger(__name__)

class AdminService:
    """Service class for admin operations"""
    
    @staticmethod
    def get_stats():
        """Get system statistics"""
        return {
            'doctors': DoctorDetails.query.count(),
            'patients': PatientDetails.query.count(),
            'appointments': Appointment.query.count()
        }
    
    @staticmethod
    def get_analytics():
        """Get analytics data"""
        from datetime import datetime, timedelta
        from sqlalchemy import func, case
        
        try:
            # Basic counts
            total_appointments = Appointment.query.count()
            completed = Appointment.query.filter_by(status='Completed').count()
            cancelled = Appointment.query.filter_by(status='Cancelled').count()
            booked = Appointment.query.filter_by(status='Booked').count()
            
            # Appointment trends (last 7 days)
            trends = []
            today = datetime.utcnow().date()
            for i in range(6, -1, -1):  # Last 7 days
                date = today - timedelta(days=i)
                count = Appointment.query.filter(
                    func.date(Appointment.date) == date
                ).count()
                trends.append({
                    'date': str(date),
                    'count': count
                })
            
            # Status distribution
            status_distribution = [
                {'status': 'Completed', 'count': completed},
                {'status': 'Booked', 'count': booked},
                {'status': 'Cancelled', 'count': cancelled}
            ]
            
            # Top performing doctors (by completed appointments)
            top_doctors_query = db.session.query(
                DoctorDetails.name,
                func.count(Appointment.id).label('appointment_count')
            ).join(Appointment, DoctorDetails.id == Appointment.doctor_id)\
             .filter(Appointment.status == 'Completed')\
             .group_by(DoctorDetails.id, DoctorDetails.name)\
             .order_by(func.count(Appointment.id).desc())\
             .limit(5)
            
            top_doctors = [{'name': row[0], 'count': row[1]} for row in top_doctors_query.all()]
            
            # Patient demographics (age groups)
            demographics_query = db.session.query(
                case(
                    (PatientDetails.age < 18, 'Under 18'),
                    (PatientDetails.age.between(18, 35), '18-35'),
                    (PatientDetails.age.between(36, 55), '36-55'),
                    (PatientDetails.age > 55, 'Over 55'),
                    else_='Unknown'
                ).label('age_group'),
                func.count(PatientDetails.id).label('count')
            ).group_by(
                case(
                    (PatientDetails.age < 18, 'Under 18'),
                    (PatientDetails.age.between(18, 35), '18-35'),
                    (PatientDetails.age.between(36, 55), '36-55'),
                    (PatientDetails.age > 55, 'Over 55'),
                    else_='Unknown'
                )
            ).all()
            
            demographics = [{'group': row[0], 'count': row[1]} for row in demographics_query]
            
            return {
                'total_appointments': total_appointments,
                'completed_appointments': completed,
                'cancelled_appointments': cancelled,
                'booked_appointments': booked,
                'total_doctors': DoctorDetails.query.count(),
                'total_patients': PatientDetails.query.count(),
                'trends': trends,
                'status_distribution': status_distribution,
                'top_doctors': top_doctors,
                'demographics': demographics
            }
        except Exception as e:
            logger.error(f"Error fetching analytics: {str(e)}")
            # Return basic data if advanced analytics fail
            return {
                'total_appointments': Appointment.query.count(),
                'completed_appointments': Appointment.query.filter_by(status='Completed').count(),
                'cancelled_appointments': Appointment.query.filter_by(status='Cancelled').count(),
                'booked_appointments': Appointment.query.filter_by(status='Booked').count(),
                'total_doctors': DoctorDetails.query.count(),
                'total_patients': PatientDetails.query.count(),
                'trends': [],
                'status_distribution': [],
                'top_doctors': [],
                'demographics': []
            }
    
    @staticmethod
    def get_all_doctors(page=DEFAULT_PAGE, per_page=DEFAULT_PER_PAGE):
        """Get all doctors with pagination"""
        query = DoctorDetails.query.join(DoctorDetails.user).options(
            db.joinedload(DoctorDetails.user)
        )
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        doctors = []
        for doctor in paginated.items:
            doctors.append({
                'id': doctor.id,
                'name': doctor.name,
                'email': doctor.user.email,
                'specialization': doctor.specialization,
                'experience': doctor.experience,
                'active': doctor.user.active,
                'flagged': doctor.flagged
            })
        
        return {
            'doctors': doctors,
            'total': paginated.total,
            'page': paginated.page,
            'pages': paginated.pages
        }
    
    @staticmethod
    def create_doctor(data):
        """Create a new doctor"""
        try:
            # Sanitize inputs
            sanitized_data = {
                'name': InputSanitizer.sanitize_string(data['name']),
                'email': InputSanitizer.sanitize_email(data['email']),
                'password': data['password'],  # Will be hashed
                'specialization': InputSanitizer.sanitize_string(data['specialization']),
                'experience': data.get('experience', 0)
            }
            
            # Validate experience
            if sanitized_data['experience'] < 0 or sanitized_data['experience'] > 70:
                raise ValueError('Experience must be between 0 and 70 years')
            
            # Check if email exists
            if user_datastore.find_user(email=sanitized_data['email']):
                raise ValueError('Email already exists')
            
            # Find or create doctor role
            doctor_role = user_datastore.find_role('doctor')
            if not doctor_role:
                doctor_role = user_datastore.create_role(name='doctor', description='Doctor')
                db.session.commit()
            
            # Create user
            user = user_datastore.create_user(
                email=sanitized_data['email'],
                password=hash_password(sanitized_data['password']),
                roles=[doctor_role],
                active=True
            )
            db.session.commit()
            
            # Create doctor details
            doctor = DoctorDetails(
                user_id=user.id,
                name=sanitized_data['name'],
                specialization=sanitized_data['specialization'],
                experience=sanitized_data['experience'],
            )
            db.session.add(doctor)
            db.session.commit()
            
            logger.info(f"Doctor created: {sanitized_data['email']}")
            return doctor
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating doctor: {str(e)}")
            raise
    
    @staticmethod
    def update_doctor(doctor_id, data):
        """Update doctor details"""
        doctor = DoctorDetails.query.get_or_404(doctor_id)
        
        # Store previous value for logging
        previous_values = {
            'name': doctor.name,
            'specialization': doctor.specialization,
            'experience': doctor.experience
        }

        # Sanitize inputs if provided
        if 'name' in data:
            doctor.name = InputSanitizer.sanitize_string(data['name'])
        if 'specialization' in data:
            doctor.specialization = InputSanitizer.sanitize_string(data['specialization'])
        if 'experience' in data:
            experience = data['experience']
            if experience < 0 or experience > 70:
                raise ValueError('Experience must be between 0 and 70 years')
            doctor.experience = experience
        
        db.session.commit()

        # Log update activity
        changes = []
        if 'name' in data and data['name'] != previous_values['name']:
            changes.append(f"Name: {previous_values['name']} -> {data['name']}")
        if 'specialization' in data and data['specialization'] != previous_values['specialization']:
            changes.append(f"Specialization: {previous_values['specialization']} -> {data['specialization']}")
        if 'experience' in data and data['experience'] != previous_values['experience']:
            changes.append(f"Experience: {previous_values['experience']} -> {data['experience']}")
        if changes:
            activity = ActivityLog(
                doctor_id=doctor_id,
                activity_type='updated',
                description=f'Doctor details updated: {", ".join(changes)}'
            )
            db.session.add(activity)
            db.session.commit()
        logger.info(f"Doctor updated: {doctor_id}")
        return doctor
    
    @staticmethod
    def delete_doctor(doctor_id):
        """Deactivate doctor account"""
        doctor = DoctorDetails.query.get_or_404(doctor_id)
        doctor.user.active = False
        db.session.commit()
        logger.info(f"Doctor deactivated: {doctor_id}")
    
    @staticmethod
    def toggle_doctor_flag(doctor_id):
        """Toggle doctor flagged status"""
        doctor = DoctorDetails.query.get_or_404(doctor_id)
        doctor.flagged = not doctor.flagged
        
        # Log activity
        activity = ActivityLog(
            doctor_id=doctor_id,
            activity_type='flag_toggled',
            description=f"Doctor {'flagged' if doctor.flagged else 'unflagged'} by admin"
        )
        db.session.add(activity)
        db.session.commit()
        
        logger.info(f"Doctor flag toggled: {doctor_id}, flagged={doctor.flagged}")
        return doctor.flagged
    
    @staticmethod
    def reactivate_doctor(doctor_id):
        """Reactivate doctor account"""
        try:
            doctor = DoctorDetails.query.get_or_404(doctor_id)
            doctor.user.active = True
            db.session.commit()
            logger.info(f"Doctor reactivated: {doctor_id}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error reactivating doctor: {str(e)}")
            raise

    @staticmethod
    def get_doctor_details(doctor_id):
        """Get detailed doctor information"""
        doctor = DoctorDetails.query.get_or_404(doctor_id)
        
        # Get appointments
        appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()
        upcoming = [a for a in appointments if a.status == 'Booked']
        completed = [a for a in appointments if a.status == 'Completed']
        
        # Format upcoming appointments
        upcoming_data = []
        for appt in upcoming[:5]:  # Limit to 5
            upcoming_data.append({
                'id': appt.id,
                'patient_name': appt.patient.name,
                'date': str(appt.date),
                'time': str(appt.time),
                'status': appt.status
            })
        
        # Get activity logs
        logs = ActivityLog.query.filter_by(doctor_id=doctor_id)\
            .order_by(ActivityLog.timestamp.desc()).limit(10).all()
        
        logs_data = [{
            'id': log.id,
            'activity_type': log.activity_type,
            'description': log.description,
            'timestamp': str(log.timestamp)
        } for log in logs]
        
        return {
            'doctor': {
                'id': doctor.id,
                'name': doctor.name,
                'email': doctor.user.email,
                'specialization': doctor.specialization,
                'experience': doctor.experience,
                'active': doctor.user.active,
                'flagged': doctor.flagged
            },
            'total_appointments': len(appointments),
            'completed_count': len(completed),
            'upcoming_count': len(upcoming),
            'upcoming_appointments': upcoming_data,
            'activity_logs': logs_data
        }
    
    @staticmethod
    def get_all_patients(page=DEFAULT_PAGE, per_page=DEFAULT_PER_PAGE):
        """Get all patients with pagination"""
        query = PatientDetails.query.join(PatientDetails.user).options(
            db.joinedload(PatientDetails.user)
        )
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        patients = []
        for patient in paginated.items:
            patients.append({
                'id': patient.id,
                'name': patient.name,
                'email': patient.user.email,
                'age': patient.age,
                'contact': patient.contact,
                'active': patient.user.active,
                'flagged': patient.flagged
            })
        
        return {
            'patients': patients,
            'total': paginated.total,
            'page': paginated.page,
            'pages': paginated.pages
        }
    
    @staticmethod
    def create_patient(data):
        """Create a new patient"""
        try:

            # Sanitize Data
            sanitized_data = {
                'name': InputSanitizer.sanitize_string(data['name']),
                'email': InputSanitizer.sanitize_email(data['email']),
                'password': data['password'],  
                'age': data['age'],
                'contact': InputSanitizer.sanitize_phone(data['contact'])
            }

            # Validate age
            if sanitized_data['age'] < 0 or sanitized_data['age'] > 150:
                raise ValueError('Age must be between 0 and 150')

            if user_datastore.find_user(email=sanitized_data['email']):
                raise ValueError('Email already exists')
            
            patient_role = user_datastore.find_role('patient')
            if not patient_role:
                patient_role = user_datastore.create_role(name='patient', description='Patient')
                db.session.commit()
            
            user = user_datastore.create_user(
                email=sanitized_data['email'],
                password=hash_password(sanitized_data['password']),
                roles=[patient_role],
                active=True
            )
            db.session.commit()
            
            patient = PatientDetails(
                user_id=user.id,
                name=sanitized_data['name'],
                age=sanitized_data['age'],
                contact=sanitized_data['contact']
            )
            db.session.add(patient)
            db.session.commit()
            
            logger.info(f"Patient created: {sanitized_data['email']}")
            return patient
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating patient: {str(e)}")
            raise
    
    @staticmethod
    def update_patient(patient_id, data):
        """Update patient details"""
        patient = PatientDetails.query.get_or_404(patient_id)

        # Store previous value for logging
        previous_values = {
            'name': patient.name,
            'age': patient.age,
            'contact': patient.contact,
            'medical_history': patient.medical_history
        }
        
        # Sanitize inputs if provided
        if 'name' in data:
            patient.name = InputSanitizer.sanitize_string(data['name'])
        if 'age' in data:
            age = data['age']
            if age < 0 or age > 150:
                raise ValueError('Age must be between 0 and 150')
            patient.age = age
        if 'contact' in data:
            patient.contact = InputSanitizer.sanitize_phone(data['contact'])
        if 'medical_history' in data:
            patient.medical_history = InputSanitizer.sanitize_html(data['medical_history'])
        
        db.session.commit()

        # Log the update activity
        changes = []
        if 'name' in data and data['name'] != previous_values['name']:
            changes.append(f"Name: {previous_values['name']} -> {data['name']}")
        if 'age' in data and data['age'] != previous_values['age']:
            changes.append(f"Age: {previous_values['age']} -> {data['age']}")
        if 'contact' in data and data['contact'] != previous_values['contact']:
            changes.append(f"Contact: {previous_values['contact']} -> {data['contact']}")
        if 'medical_history' in data and data['medical_history'] != previous_values['medical_history']:
            changes.append(f"Medical History: {previous_values['medical_history']} -> {data['medical_history']}")
        
        if changes:
            activity = PatientActivityLog(
                patient_id=patient_id,
                activity_type='updated',
                description=f'Patient details updated: {", ".join(changes)}',
            )
            db.session.add(activity)
            db.session.commit()
        logger.info(f"Patient updated: {patient_id}")
        return patient
    
    @staticmethod
    def delete_patient(patient_id):
        """Deactivate patient account"""
        patient = PatientDetails.query.get_or_404(patient_id)
        patient.user.active = False
        db.session.commit()
        logger.info(f"Patient deactivated: {patient_id}")
    
    @staticmethod
    def get_patient_details(patient_id):
        """Get detailed patient information"""
        patient = PatientDetails.query.get_or_404(patient_id)
        
        # Get all appointments
        appointments = Appointment.query.filter_by(patient_id=patient_id).all()
        
        appointments_data = []
        for appt in appointments:
            appt_data = {
                'id': appt.id,
                'doctor_name': appt.doctor.name,
                'doctor_id': appt.doctor_id,
                'date': str(appt.date),
                'time': str(appt.time),
                'status': appt.status
            }
            
            if appt.treatment:
                appt_data['diagnosis'] = appt.treatment.diagnosis
                appt_data['prescription'] = appt.treatment.prescription
                appt_data['notes'] = appt.treatment.notes
            
            appointments_data.append(appt_data)
        
        # Get activity logs
        logs = PatientActivityLog.query.filter_by(patient_id=patient_id)\
            .order_by(PatientActivityLog.timestamp.desc()).all()
        
        logs_data = [{
            'id': log.id,
            'activity_type': log.activity_type,
            'description': log.description,
            'timestamp': str(log.timestamp)
        } for log in logs]
        
        # Sort appointments by date (most recent first)
        appointments_data.sort(key=lambda x: x['date'], reverse=True)

        # Process appointments once and categorize to avoid multiple iterations
        completed_appointments = []
        upcoming_appointments = []
        completed_count = 0
        upcoming_count = 0

        for appt in appointments_data:
            if appt['status'] == 'Completed':
                completed_appointments.append(appt)
                completed_count += 1
            elif appt['status'] == 'Booked':
                upcoming_appointments.append(appt)
                upcoming_count += 1


        return {
            'patient': {
                'id': patient.id,
                'name': patient.name,
                'email': patient.user.email,
                'age': patient.age,
                'contact': patient.contact,
                'medical_history': patient.medical_history,
                'active': patient.user.active,
                'flagged': patient.flagged
            },
            'appointments': appointments_data,
            'completed_appointments': completed_appointments,
            'upcoming_appointments': upcoming_appointments,
            'total_appointments': len(appointments),
            'completed_count': completed_count,
            'upcoming_count': upcoming_count,
            'activity_logs': logs_data
        }
    
    @staticmethod
    def toggle_patient_flag(patient_id):
        """Toggle patient flagged status"""
        try:
            patient = PatientDetails.query.get_or_404(patient_id)
            patient.flagged = not patient.flagged

            # Log activities
            activity = PatientActivityLog(
                patient_id=patient_id,
                activity_type='flag_toggled',
                description=f"Patient {'flagged' if patient.flagged else 'unflagged'} by admin"
            )
            db.session.add(activity)
            db.session.commit()

            logger.info(f"Patient flag toggled: {patient_id}, flagged: {patient.flagged}")
            return patient.flagged
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error toggling patient flag: {str(e)}")
            raise

    @staticmethod
    def reactivate_patient(patient_id):
        try:
            patient = PatientDetails.query.get_or_404(patient_id)
            patient.user.active = True
            db.session.commit()
            logger.info(f"Patient reactivated: {patient_id}")

        except Exception as e:
            db.session.rollback()    
            logger.error(f"Error reactivating patient: {str(e)}")
            raise

    @staticmethod
    def get_all_appointments(page=DEFAULT_PAGE, per_page=DEFAULT_PER_PAGE):
        """Get all appointments with pagination"""
        query = Appointment.query.options(
            db.joinedload(Appointment.doctor),
            db.joinedload(Appointment.patient),
            db.joinedload(Appointment.treatment)
        ).order_by(Appointment.date.desc())
        
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        appointments = []
        for appt in paginated.items:
            data = {
                'id': appt.id,
                'doctor_name': appt.doctor.name,
                'patient_name': appt.patient.name,
                'date': str(appt.date),
                'time': str(appt.time),
                'status': appt.status,
                'diagnosis': None,
                'prescription': None,
                'notes': None
            }
            
            if appt.treatment:
                data['diagnosis'] = appt.treatment.diagnosis
                data['prescription'] = appt.treatment.prescription
                data['notes'] = appt.treatment.notes
            
            appointments.append(data)
        
        return {
            'appointments': appointments,
            'total': paginated.total,
            'page': paginated.page,
            'pages': paginated.pages
        }
    
    @staticmethod
    def delete_appointment(appointment_id):
        """Delete an appointment"""
        appointment = Appointment.query.get_or_404(appointment_id)
        db.session.delete(appointment)
        db.session.commit()
        logger.info(f"Appointment deleted: {appointment_id}")
    
    @staticmethod
    def search_users(query):
        """Search for doctors and patients"""
        doctors = DoctorDetails.query.join(DoctorDetails.user).filter(
            db.or_(
                DoctorDetails.name.ilike(f'%{query}%'),
                DoctorDetails.user.has(User.email.ilike(f'%{query}%'))
            )
        ).limit(10).all()
        
        patients = PatientDetails.query.join(PatientDetails.user).filter(
            db.or_(
                PatientDetails.name.ilike(f'%{query}%'),
                PatientDetails.user.has(User.email.ilike(f'%{query}%'))
            )
        ).limit(10).all()
        
        return {
            'doctors': [{
                'id': d.id,
                'name': d.name,
                'email': d.user.email,
                'specialization': d.specialization
            } for d in doctors],
            'patients': [{
                'id': p.id,
                'name': p.name,
                'email': p.user.email,
                'age': p.age
            } for p in patients]
        }
