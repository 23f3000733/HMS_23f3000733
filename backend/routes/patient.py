"""
Patient Routes
Handles HTTP requests for patient operations
"""
from flask import Blueprint, request, send_from_directory, current_app
from utils.jwt_auth import jwt_required
from utils.helpers import success_response, error_response
from services.patient_service import PatientService
from datetime import datetime
import logging
from tasks.__init__ import export_patient_history

patient_bp = Blueprint('patient', __name__)
logger = logging.getLogger(__name__)

# ================= Doctor Search =================

@patient_bp.route('/doctors', methods=['GET'])
@jwt_required('patient')
def search_doctors():
    """Search for doctors by specialization"""
    try:
        specialization = request.args.get('specialization')
        logger.info(f"Search doctors endpoint called with specialization: '{specialization}'")
        doctors = PatientService.search_doctors(specialization)
        logger.info(f"Returning {len(doctors)} doctors")
        return success_response(doctors)
    except Exception as e:
        logger.error(f"Error searching doctors: {str(e)}")
        return error_response('Failed to search doctors', 500)

# ================= Appointment Management =================

@patient_bp.route('/book', methods=['POST'])
@jwt_required('patient')
def book_appointment():
    """Book a new appointment"""
    try:
        patient = PatientService.get_current_patient()
        if not patient:
            return error_response('Patient profile not found', 404)
        
        data = request.get_json()
        appointment_date = datetime.strptime(data.get('date'), '%Y-%m-%d').date()
        appointment_time = datetime.strptime(data.get('time'), '%H:%M').time()
        
        appointment = PatientService.book_appointment(
            patient.id,
            data.get('doctor_id'),
            appointment_date,
            appointment_time
        )
        
        return success_response(
            {'id': appointment.id},
            'Appointment booked successfully',
            201
        )
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        logger.error(f"Error booking appointment: {str(e)}")
        return error_response('Failed to book appointment', 500)

@patient_bp.route('/appointments/<int:id>/cancel', methods=['POST'])
@jwt_required('patient')
def cancel_appointment(id):
    """Cancel an appointment"""
    try:
        patient = PatientService.get_current_patient()
        if not patient:
            return error_response('Patient profile not found', 404)
        
        PatientService.cancel_appointment(id, patient.id)
        return success_response(message='Appointment cancelled successfully')
    except PermissionError as e:
        return error_response(str(e), 403)
    except Exception as e:
        logger.error(f"Error cancelling appointment: {str(e)}")
        return error_response('Failed to cancel appointment', 500)

@patient_bp.route('/appointments/<int:id>/reschedule', methods=['POST'])
@jwt_required('patient')
def reschedule_appointment(id):
    """Reschedule an appointment"""
    try:
        patient = PatientService.get_current_patient()
        if not patient:
            return error_response('Patient profile not found', 404)
        
        data = request.get_json()
        new_date = datetime.strptime(data.get('date'), '%Y-%m-%d').date()
        new_time = datetime.strptime(data.get('time'), '%H:%M').time()
        
        PatientService.reschedule_appointment(id, patient.id, new_date, new_time)
        return success_response(message='Appointment rescheduled successfully')
    except ValueError as e:
        return error_response(str(e), 400)
    except PermissionError as e:
        return error_response(str(e), 403)
    except Exception as e:
        logger.error(f"Error rescheduling appointment: {str(e)}")
        return error_response('Failed to reschedule appointment', 500)

@patient_bp.route('/history', methods=['GET'])
@jwt_required('patient')
def get_history():
    """Get appointment history"""
    try:
        patient = PatientService.get_current_patient()
        if not patient:
            return success_response([])
        
        history = PatientService.get_history(patient.id)
        return success_response(history)
    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}")
        return error_response('Failed to fetch history', 500)

# ================= Profile Management =================

@patient_bp.route('/profile', methods=['GET', 'PUT'])
@jwt_required('patient')
def manage_profile():
    """Get or update patient profile"""
    try:
        patient = PatientService.get_current_patient()
        if not patient:
            return error_response('Patient profile not found', 404)
        
        if request.method == 'PUT':
            data = request.get_json()
            PatientService.update_profile(patient.id, data)
            return success_response(message='Profile updated successfully')
        
        profile = PatientService.get_profile(patient.id)
        return success_response(profile)
    except Exception as e:
        logger.error(f"Error managing profile: {str(e)}")
        return error_response('Failed to manage profile', 500)

# ================= Dashboard & Analytics =================

@patient_bp.route('/dashboard', methods=['GET'])
@jwt_required('patient')
def get_dashboard():
    """Get patient dashboard data"""
    try:
        patient = PatientService.get_current_patient()
        if not patient:
            return error_response('Patient profile not found', 404)
        
        dashboard = PatientService.get_dashboard_stats(patient.id)
        return success_response(dashboard)
    except Exception as e:
        logger.error(f"Error fetching dashboard: {str(e)}")
        return error_response('Failed to fetch dashboard', 500)

@patient_bp.route('/analytics', methods=['GET'])
@jwt_required('patient')
def get_analytics():
    """Get patient analytics"""
    try:
        patient = PatientService.get_current_patient()
        if not patient:
            return error_response('Patient profile not found', 404)
        
        analytics = PatientService.get_analytics(patient.id)
        return success_response(analytics)
    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        return error_response('Failed to fetch analytics', 500)

# ================= Document Management =================

@patient_bp.route('/documents', methods=['GET', 'POST'])
@jwt_required('patient')
def manage_documents():
    """Get all documents or upload a new one"""
    try:
        patient = PatientService.get_current_patient()
        if not patient:
            return error_response('Patient profile not found', 404)
        
        if request.method == 'POST':
            if 'file' not in request.files:
                return error_response('No file provided', 400)
            
            file = request.files['file']
            if file.filename == '':
                return error_response('No file selected', 400)
            
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
            doc = PatientService.upload_document(patient.id, file, upload_folder)
            
            return success_response(
                {'id': doc.id, 'filename': doc.original_filename},
                'Document uploaded successfully',
                201
            )
        
        documents = PatientService.get_documents(patient.id)
        return success_response(documents)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        logger.error(f"Error managing documents: {str(e)}")
        return error_response('Failed to manage documents', 500)

@patient_bp.route('/documents/<int:id>/download', methods=['GET'])
@jwt_required('patient')
def download_document(id):
    """Download a document"""
    try:
        patient = PatientService.get_current_patient()
        if not patient:
            return error_response('Patient profile not found', 404)
        
        doc = PatientService.get_document(id, patient.id)
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
        
        return send_from_directory(
            upload_folder,
            doc.filename,
            as_attachment=True,
            download_name=doc.original_filename
        )
    except PermissionError as e:
        return error_response(str(e), 403)
    except Exception as e:
        logger.error(f"Error downloading document: {str(e)}")
        return error_response('Failed to download document', 500)

# ================= Data Export =================

@patient_bp.route('/export', methods=['POST'])
@jwt_required('patient')
def export_history():
    """Export patient history (triggers Celery task)"""
    try:
        patient = PatientService.get_current_patient()
        if not patient:
            return error_response('Patient profile not found', 404)
        
        # Log the export activity
        PatientService.create_activity_log(
            patient.id,
            'history_export',
            'Patient exported medical history'
        )
        
        export_patient_history.delay(patient.id)

        return success_response(message='Export initiated. You will receive an email when ready.')
    except Exception as e:
        logger.error(f"Error exporting history: {str(e)}")
        return error_response('Failed to export history', 500)
