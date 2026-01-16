"""
Admin Routes
Handles HTTP requests for admin operations
"""
from flask import Blueprint, request, Response
from utils.jwt_auth import jwt_required
from utils.helpers import success_response, error_response
from services.admin_service import AdminService
from schemas import (
    DoctorCreateSchema, DoctorUpdateSchema,
    PatientCreateSchema, PatientUpdateSchema,
    PaginationSchema
)
from marshmallow import ValidationError
import logging
from utils.rate_limiter import strict_rate_limit
from tasks import send_flag_notification, send_patient_flag_notification
import csv
import io
from models import DoctorDetails, PatientDetails, Appointment

admin_bp = Blueprint('admin', __name__)
logger = logging.getLogger(__name__)

# Initialize schemas
doctor_create_schema = DoctorCreateSchema()
doctor_update_schema = DoctorUpdateSchema()
patient_create_schema = PatientCreateSchema()
patient_update_schema = PatientUpdateSchema()
pagination_schema = PaginationSchema()

# ==================== Statistics & Analytics ====================

@admin_bp.route('/stats', methods=['GET'])
@jwt_required('admin')
def get_stats():
    """Get system statistics"""
    try:
        stats = AdminService.get_stats()
        return success_response(stats)
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        return error_response('Failed to fetch statistics', 500)

@admin_bp.route('/analytics', methods=['GET'])
@jwt_required('admin')
def get_analytics():
    """Get system analytics"""
    try:
        analytics = AdminService.get_analytics()
        return success_response(analytics)
    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        return error_response('Failed to fetch analytics', 500)

# ==================== Doctor Management ====================

@admin_bp.route('/doctors', methods=['GET', 'POST'])
@jwt_required('admin')
@strict_rate_limit
def manage_doctors():
    """List all doctors or create a new doctor"""
    if request.method == 'POST':
        try:
            data = doctor_create_schema.load(request.get_json())
            doctor = AdminService.create_doctor(data)
            return success_response(
                {'id': doctor.id, 'name': doctor.name},
                'Doctor created successfully',
                201
            )
        except ValidationError as err:
            return error_response('Validation failed', 400, err.messages)
        except ValueError as e:
            return error_response(str(e), 400)
        except Exception as e:
            logger.error(f"Error creating doctor: {str(e)}")
            return error_response('Failed to create doctor', 500)
    
    # GET request
    try:
        params = pagination_schema.load(request.args)
        result = AdminService.get_all_doctors(
            page=params['page'],
            per_page=params['per_page']
        )
        return success_response(result)
    except Exception as e:
        logger.error(f"Error fetching doctors: {str(e)}")
        return error_response('Failed to fetch doctors', 500)

@admin_bp.route('/doctors/<int:doctor_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required('admin')
def doctor_detail(doctor_id):
    """Get, update, or delete a doctor"""
    if request.method == 'DELETE':
        try:
            AdminService.delete_doctor(doctor_id)
            return success_response(message='Doctor deactivated successfully')
        except Exception as e:
            logger.error(f"Error deleting doctor: {str(e)}")
            return error_response('Failed to delete doctor', 500)
    
    if request.method == 'PUT':
        try:
            data = doctor_update_schema.load(request.get_json())
            doctor = AdminService.update_doctor(doctor_id, data)
            return success_response(
                {'id': doctor.id, 'name': doctor.name},
                'Doctor updated successfully'
            )
        except ValidationError as err:
            return error_response('Validation failed', 400, err.messages)
        except Exception as e:
            logger.error(f"Error updating doctor: {str(e)}")
            return error_response('Failed to update doctor', 500)

@admin_bp.route('/doctors/<int:doctor_id>/details', methods=['GET'])
@jwt_required('admin')
def get_doctor_details(doctor_id):
    """Get detailed doctor information"""
    try:
        details = AdminService.get_doctor_details(doctor_id)
        return success_response(details)
    except Exception as e:
        logger.error(f"Error fetching doctor details: {str(e)}")
        return error_response('Failed to fetch doctor details', 500)

@admin_bp.route('/doctors/<int:doctor_id>/flag', methods=['POST'])
@jwt_required('admin')
@strict_rate_limit
def toggle_doctor_flag(doctor_id):
    """Toggle doctor flagged status"""
    try:
        logger.info(f"Toggling flag for doctor ID: {doctor_id}")
        flagged = AdminService.toggle_doctor_flag(doctor_id)
        logger.info(f"Doctor flagged status: {flagged}")
        
        task = None
        if flagged:
            # Get doctor details to send notification
            doctor_details = AdminService.get_doctor_details(doctor_id)
            doctor = doctor_details['doctor']  # Extract doctor from nested structure
            logger.info(f"Sending flag notification to doctor: {doctor['name']} ({doctor['email']})")
            task = send_flag_notification.delay(doctor['email'], doctor['name'])
            logger.info(f"Flag notification task created with ID: {task.id}")

        return success_response(
            {'flagged': flagged, 'task_id': task.id if flagged else None},
            f"Doctor {'flagged' if flagged else 'unflagged'} successfully"
        )
    except Exception as e:
        logger.error(f"Error toggling doctor flag: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        logger.error(f"Error toggling doctor flag: {str(e)}")
        return error_response('Failed to toggle flag', 500)


@admin_bp.route('/doctors/<int:doctor_id>/reactivate', methods=['POST'])
@jwt_required('admin')
@strict_rate_limit
def reactivate_doctor(doctor_id):
    try:
        AdminService.reactivate_doctor(doctor_id)
        return success_response(message='Doctor reactivated successfully')
    except Exception as e:
        logger.error(f'Error reactivating doctor: {str(e)}')
        return error_response('Failed to reactivate doctor', 500)

# ==================== Patient Management ====================

@admin_bp.route('/patients', methods=['GET', 'POST'])
@jwt_required('admin')
@strict_rate_limit
def manage_patients():
    """List all patients or create a new patient"""
    if request.method == 'POST':
        try:
            data = patient_create_schema.load(request.get_json())
            patient = AdminService.create_patient(data)
            return success_response(
                {'id': patient.id, 'name': patient.name},
                'Patient created successfully',
                201
            )
        except ValidationError as err:
            return error_response('Validation failed', 400, err.messages)
        except ValueError as e:
            return error_response(str(e), 400)
        except Exception as e:
            logger.error(f"Error creating patient: {str(e)}")
            return error_response('Failed to create patient', 500)
    
    # GET request
    try:
        params = pagination_schema.load(request.args)
        result = AdminService.get_all_patients(
            page=params['page'],
            per_page=params['per_page']
        )
        return success_response(result)
    except Exception as e:
        logger.error(f"Error fetching patients: {str(e)}")
        return error_response('Failed to fetch patients', 500)

@admin_bp.route('/patients/<int:patient_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required('admin')
def patient_detail(patient_id):
    """Get, update, or delete a patient"""
    if request.method == 'DELETE':
        try:
            AdminService.delete_patient(patient_id)
            return success_response(message='Patient deactivated successfully')
        except Exception as e:
            logger.error(f"Error deleting patient: {str(e)}")
            return error_response('Failed to delete patient', 500)
    
    if request.method == 'PUT':
        try:
            data = patient_update_schema.load(request.get_json())
            patient = AdminService.update_patient(patient_id, data)
            return success_response(
                {'id': patient.id, 'name': patient.name},
                'Patient updated successfully'
            )
        except ValidationError as err:
            return error_response('Validation failed', 400, err.messages)
        except Exception as e:
            logger.error(f"Error updating patient: {str(e)}")
            return error_response('Failed to update patient', 500)

@admin_bp.route('/patients/<int:patient_id>/details', methods=['GET'])
@jwt_required('admin')
def get_patient_details(patient_id):
    """Get detailed patient information"""
    try:
        details = AdminService.get_patient_details(patient_id)
        return success_response(details)
    except Exception as e:
        logger.error(f"Error fetching patient details: {str(e)}")
        return error_response('Failed to fetch patient details', 500)

@admin_bp.route('/patients/<int:patient_id>/flag', methods=['POST'])
@jwt_required('admin')
@strict_rate_limit
def toggle_patient_flag(patient_id):
    """Toggle patient flagged status"""
    try:
        logger.info(f"Toggling flag for patient ID: {patient_id}")
        flagged = AdminService.toggle_patient_flag(patient_id)
        logger.info(f"Patient flagged status: {flagged}")
        
        task = None
        if flagged:
            # Get patient details to send notification
            patient_details = AdminService.get_patient_details(patient_id)
            patient = patient_details['patient']  # Extract patient from nested structure
            logger.info(f"Sending flag notification to patient: {patient['name']} ({patient['email']})")
            task = send_patient_flag_notification.delay(patient['email'], patient['name'])
            logger.info(f"Flag notification task created with ID: {task.id}")
            
        return success_response(
            {'flagged': flagged, 'task_id': task.id if flagged else None},
            f"Patient {'flagged' if flagged else 'unflagged'} successfully"
        )
    except Exception as e:
        logger.error(f"Error toggling patient flag: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        logger.error(f"Error toggling patient flag: {str(e)}")
        return error_response('Failed to toggle flag', 500)

@admin_bp.route('/patients/<int:patient_id>/reactivate', methods=['POST'])
@jwt_required('admin')
@strict_rate_limit
def reactivate_patient(patient_id):
    try:
        AdminService.reactivate_patient(patient_id)
        return success_response(message="Patient reactivated successfully")
    except Exception as e:
        logger.error(f'Error reactivating patient: {str(e)}')
        return error_response('Failed to reactivate patient', 500)

        
# ==================== Appointment Management ====================

@admin_bp.route('/appointments', methods=['GET'])
@jwt_required('admin')
def get_appointments():
    """Get all appointments with pagination"""
    try:
        params = pagination_schema.load(request.args)
        result = AdminService.get_all_appointments(
            page=params['page'],
            per_page=params['per_page']
        )
        return success_response(result)
    except Exception as e:
        logger.error(f"Error fetching appointments: {str(e)}")
        return error_response('Failed to fetch appointments', 500)

@admin_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
@jwt_required('admin')
def delete_appointment(appointment_id):
    """Delete an appointment"""
    try:
        AdminService.delete_appointment(appointment_id)
        return success_response(message='Appointment deleted successfully')
    except Exception as e:
        logger.error(f"Error deleting appointment: {str(e)}")
        return error_response('Failed to delete appointment', 500)

# ==================== Search ====================

@admin_bp.route('/search', methods=['GET'])
@jwt_required('admin')
def search():
    """Search for doctors and patients"""
    try:
        query = request.args.get('q', '')
        if not query or len(query) < 2:
            return error_response('Search query must be at least 2 characters', 400)
        
        results = AdminService.search_users(query)
        return success_response(results)
    except Exception as e:
        logger.error(f"Error searching: {str(e)}")
        return error_response('Search failed', 500)

# ==================== Data Export ====================

@admin_bp.route('/doctors/export/csv', methods=['GET'])
@jwt_required('admin')
def export_doctors_csv():
    """Export all doctors as CSV"""
    try:
        # Generate CSV data for all doctors
        output = io.StringIO()
        writer = csv.writer(output)
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
        
        csv_content = output.getvalue()
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=doctors.csv'}
        )
    except Exception as e:
        logger.error(f"Error exporting doctors: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response('Failed to export doctors', 500)

@admin_bp.route('/doctors/export/email', methods=['POST'])
@jwt_required('admin')
def export_doctors_csv_email():
    """Export all doctors as CSV and send via email"""
    try:
        logger.info("Initiating doctors export for admin")
        from models import User
        admin_user_id = request.current_user_id
        logger.debug(f"Admin user ID from JWT: {admin_user_id}")
        admin_user = User.query.get(admin_user_id)
        if not admin_user:
            logger.error("Admin user not found")
            return error_response('Admin profile not found', 404)
        
        logger.info(f"Admin user found: {admin_user.email}")
        # Trigger background task to generate and send CSV
        from tasks.export_tasks import export_admin_data
        task = export_admin_data.delay(admin_user.id, 'doctors')
        logger.info(f"Export task created with ID: {task.id}")
        
        return success_response({'task_id': task.id}, 'Doctors export initiated. You will receive an email when ready.')
    except Exception as e:
        logger.error(f"Error initiating doctors export: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        logger.error(f"Error initiating doctors export: {str(e)}")
        return error_response('Failed to initiate doctors export', 500)

@admin_bp.route('/patients/export/csv', methods=['GET'])
@jwt_required('admin')
def export_patients_csv():
    """Export all patients as CSV"""
    try:
        # Generate CSV data for all patients
        output = io.StringIO()
        writer = csv.writer(output)
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
        
        csv_content = output.getvalue()
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=patients.csv'}
        )
    except Exception as e:
        logger.error(f"Error exporting patients: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response('Failed to export patients', 500)

@admin_bp.route('/patients/export/email', methods=['POST'])
@jwt_required('admin')
def export_patients_csv_email():
    """Export all patients as CSV and send via email"""
    try:
        logger.info("Initiating patients export for admin")
        from models import User
        admin_user_id = request.current_user_id
        logger.debug(f"Admin user ID from JWT: {admin_user_id}")
        admin_user = User.query.get(admin_user_id)
        if not admin_user:
            logger.error("Admin user not found")
            return error_response('Admin profile not found', 404)
        
        logger.info(f"Admin user found: {admin_user.email}")
        # Trigger background task to generate and send CSV
        from tasks.export_tasks import export_admin_data
        task = export_admin_data.delay(admin_user.id, 'patients')
        logger.info(f"Export task created with ID: {task.id}")
        
        return success_response({'task_id': task.id}, 'Patients export initiated. You will receive an email when ready.')
    except Exception as e:
        logger.error(f"Error initiating patients export: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        logger.error(f"Error initiating patients export: {str(e)}")
        return error_response('Failed to initiate patients export', 500)

@admin_bp.route('/appointments/export/csv', methods=['GET'])
@jwt_required('admin')
def export_appointments_csv():
    """Export all appointments as CSV"""
    try:
        # Generate CSV data for all appointments
        output = io.StringIO()
        writer = csv.writer(output)
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
        
        csv_content = output.getvalue()
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=appointments.csv'}
        )
    except Exception as e:
        logger.error(f"Error exporting appointments: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response('Failed to export appointments', 500)

@admin_bp.route('/appointments/export/email', methods=['POST'])
@jwt_required('admin')
def export_appointments_csv_email():
    """Export all appointments as CSV and send via email"""
    try:
        logger.info("Initiating appointments export for admin")
        from models import User
        admin_user_id = request.current_user_id
        logger.debug(f"Admin user ID from JWT: {admin_user_id}")
        admin_user = User.query.get(admin_user_id)
        if not admin_user:
            logger.error("Admin user not found")
            return error_response('Admin profile not found', 404)
        
        logger.info(f"Admin user found: {admin_user.email}")
        # Trigger background task to generate and send CSV
        from tasks.export_tasks import export_admin_data
        task = export_admin_data.delay(admin_user.id, 'appointments')
        logger.info(f"Export task created with ID: {task.id}")
        
        return success_response({'task_id': task.id}, 'Appointments export initiated. You will receive an email when ready.')
    except Exception as e:
        logger.error(f"Error initiating appointments export: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        logger.error(f"Error initiating appointments export: {str(e)}")
        return error_response('Failed to initiate appointments export', 500)
