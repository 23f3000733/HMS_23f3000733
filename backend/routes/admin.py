"""
Admin Routes
Handles HTTP requests for admin operations
"""
from flask import Blueprint, request
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
        flagged = AdminService.toggle_doctor_flag(doctor_id)
        return success_response(
            {'flagged': flagged},
            f"Doctor {'flagged' if flagged else 'unflagged'} successfully"
        )
    except Exception as e:
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
        flagged = AdminService.toggle_patient_flag(patient_id)
        
        return success_response(
            {'flagged': flagged},
            f"Patient {'flagged' if flagged else 'unflagged'} successfully"
        )
    except Exception as e:
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