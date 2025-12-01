"""
Doctor Routes
Handles HTTP requests for doctor operations
"""
from flask import Blueprint, request, Response
from utils.jwt_auth import jwt_required
from utils.helpers import success_response, error_response
from services.doctor_service import DoctorService
from datetime import datetime
import logging
from tasks import send_prescription_email_task

doctor_bp = Blueprint('doctor', __name__)
logger = logging.getLogger(__name__)

# ================= Dashboard & Statistics =================

@doctor_bp.route('/dashboard', methods=['GET'])
@jwt_required('doctor')
def get_dashboard():
    """Get doctor dashboard data"""
    try:
        doctor = DoctorService.get_current_doctor()
        if not doctor:
            return error_response('Doctor profile not found', 404)
        
        dashboard_data = DoctorService.get_dashboard_stats(doctor.id)
        return success_response(dashboard_data)
    except Exception as e:
        logger.error(f"Error fetching dashboard: {str(e)}")
        return error_response('Failed to fetch dashboard', 500)

@doctor_bp.route('/analytics', methods=['GET'])
@jwt_required('doctor')
def get_analytics():
    """Get analytics data"""
    try:
        doctor = DoctorService.get_current_doctor()
        if not doctor:
            return error_response('Doctor profile not found', 404)
        
        analytics = DoctorService.get_analytics(doctor.id)
        return success_response(analytics)
    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        return error_response('Failed to fetch analytics', 500)

# ================= Appointment Management =================

@doctor_bp.route('/appointments', methods=['GET'])
@jwt_required('doctor')
def get_appointments():
    """Get all appointments for doctor"""
    try:
        doctor = DoctorService.get_current_doctor()
        if not doctor:
            return error_response('Doctor profile not found', 404)
        
        appointments = DoctorService.get_all_appointments(doctor.id)
        return success_response(appointments)
    except Exception as e:
        logger.error(f"Error fetching appointments: {str(e)}")
        return error_response('Failed to fetch appointments', 500)

@doctor_bp.route('/appointment/<int:id>/complete', methods=['POST'])
@jwt_required('doctor')
def complete_appointment(id):
    """Complete an appointment with treatment details"""
    try:
        doctor = DoctorService.get_current_doctor()
        if not doctor:
            return error_response('Doctor profile not found', 404)
        
        data = request.get_json()
        DoctorService.complete_appointment(id, doctor.id, data)
        return success_response(message='Appointment completed successfully')
    except PermissionError as e:
        return error_response(str(e), 403)
    except Exception as e:
        logger.error(f"Error completing appointment: {str(e)}")
        return error_response('Failed to complete appointment', 500)

@doctor_bp.route('/appointment/<int:id>/cancel', methods=['POST'])
@jwt_required('doctor')
def cancel_appointment(id):
    """Cancel an appointment"""
    try:
        doctor = DoctorService.get_current_doctor()
        if not doctor:
            return error_response('Doctor profile not found', 404)
        
        DoctorService.cancel_appointment(id, doctor.id)
        return success_response(message='Appointment cancelled successfully')
    except PermissionError as e:
        return error_response(str(e), 403)
    except Exception as e:
        logger.error(f"Error cancelling appointment: {str(e)}")
        return error_response('Failed to cancel appointment', 500)

@doctor_bp.route('/appointment/<int:id>/reschedule', methods=['POST'])
@jwt_required('doctor')
def reschedule_appointment(id):
    """Reschedule an appointment"""
    try:
        doctor = DoctorService.get_current_doctor()
        if not doctor:
            return error_response('Doctor profile not found', 404)
        
        data = request.get_json()
        new_date = datetime.strptime(data.get('date'), '%Y-%m-%d').date()
        new_time = datetime.strptime(data.get('time'), '%H:%M').time()
        
        DoctorService.reschedule_appointment(id, doctor.id, new_date, new_time)
        return success_response(message='Appointment rescheduled successfully')
    except PermissionError as e:
        return error_response(str(e), 403)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        logger.error(f"Error rescheduling appointment: {str(e)}")
        return error_response('Failed to reschedule appointment', 500)

# ================= Patient Management =================

@doctor_bp.route('/patients', methods=['GET'])
@jwt_required('doctor')
def get_patients():
    """Get all patients for this doctor"""
    try:
        doctor = DoctorService.get_current_doctor()
        if not doctor:
            return error_response('Doctor profile not found', 404)
        
        patients = DoctorService.get_patients(doctor.id)
        return success_response(patients)
    except Exception as e:
        logger.error(f"Error fetching patients: {str(e)}")
        return error_response('Failed to fetch patients', 500)

@doctor_bp.route('/patient/<int:id>/history', methods=['GET'])
@jwt_required('doctor')
def get_patient_history(id):
    """Get appointment history for a specific patient"""
    try:
        doctor = DoctorService.get_current_doctor()
        if not doctor:
            return error_response('Doctor profile not found', 404)
        
        history = DoctorService.get_patient_history(doctor.id, id)
        return success_response(history)
    except Exception as e:
        logger.error(f"Error fetching patient history: {str(e)}")
        return error_response('Failed to fetch patient history', 500)

# ================= Prescription Management =================

@doctor_bp.route('/prescriptions', methods=['GET'])
@jwt_required('doctor')
def get_prescriptions():
    """Get all prescriptions issued by this doctor"""
    try:
        doctor = DoctorService.get_current_doctor()
        if not doctor:
            return error_response('Doctor profile not found', 404)
        
        prescriptions = DoctorService.get_prescriptions(doctor.id)
        return success_response(prescriptions)
    except Exception as e:
        logger.error(f"Error fetching prescriptions: {str(e)}")
        return error_response('Failed to fetch prescriptions', 500)

@doctor_bp.route('/prescription/<int:id>/send-email', methods=['POST'])
@jwt_required('doctor')
def send_prescription_email(id):
    """Send prescription via email"""
    try:
        doctor = DoctorService.get_current_doctor()
        prescription = DoctorService.get_prescription_by_id(id, doctor.id)
        
        print(f"Sending prescription email for prescription ID: {id}")
        print(f"Doctor: {doctor.name}")
        print(f"Prescription details: {prescription}")
        
        if not prescription:
            print("Prescription not found or unauthorized")
            return error_response('Prescription not found or unauthorized', 404)
        
        task = send_prescription_email_task.delay(
            prescription['patient_email'], prescription['patient_name'], doctor.name,
            prescription['diagnosis'], prescription['prescription'], prescription['notes'], prescription['date'],
            treatment_id=prescription['id']
        )
        
        print(f"Task created with ID: {task.id}")

        return success_response({'task_id': task.id}, 'Prescription email is being sent')
    except Exception as e:
        print(f"Error sending prescription email: {str(e)}")
        import traceback
        traceback.print_exc()
        logger.error(f"Error sending prescription email: {str(e)}")
        return error_response('Failed to send email', 500)

@doctor_bp.route('/prescriptions/bulk-email', methods=['POST'])
@jwt_required('doctor')
def send_bulk_prescription_emails():
    try:
        doctor = DoctorService.get_current_doctor()
        data = request.get_json()
        prescription_ids = data.get('prescription_ids', [])

        for pid in prescription_ids:
            p = DoctorService.get_prescription_by_id(pid, doctor.id)
            if p:
                send_prescription_email_task.delay(
                    p['patient_email'],
                    p['patient_name'],
                    doctor.name,
                    p['diagnosis'],
                    p['prescription'],
                    p['notes'],
                    p['date'],
                    True,
                    treatment_id=p['id']
                )
        return success_response(message=f'{len(prescription_ids)} emails queued')
    except Exception as e:
        logger.error(f"Error sending bulk emails: {str(e)}")
        return error_response('Failed to send emails', 500)

# ================= Data Export =================

@doctor_bp.route('/prescriptions/export/csv', methods=['GET'])
@jwt_required('doctor')
def export_prescriptions_csv():
    """Export prescriptions as CSV"""
    try:
        print("Initiating prescriptions CSV export for doctor")
        doctor = DoctorService.get_current_doctor()
        print(f"Doctor object: {doctor}")
        if not doctor:
            print("Doctor profile not found")
            return error_response('Doctor profile not found', 404)
        
        print(f"Doctor found: {doctor.name} (ID: {doctor.id})")
        csv_data = DoctorService.export_data_csv(doctor.id, 'prescriptions')
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=prescriptions.csv'}
        )
    except Exception as e:
        print(f"Error exporting prescriptions: {str(e)}")
        import traceback
        traceback.print_exc()
        logger.error(f"Error exporting prescriptions: {str(e)}")
        return error_response('Failed to export prescriptions', 500)

@doctor_bp.route('/prescriptions/export/email', methods=['POST'])
@jwt_required('doctor')
def export_prescriptions_csv_email():
    """Export prescriptions as CSV and send via email"""
    try:
        print("Initiating prescriptions export for doctor")
        doctor = DoctorService.get_current_doctor()
        print(f"Doctor object: {doctor}")
        if not doctor:
            print("Doctor profile not found")
            return error_response('Doctor profile not found', 404)
        
        print(f"Doctor found: {doctor.name} (ID: {doctor.id})")
        # Trigger background task to generate and send CSV
        from tasks.export_tasks import export_doctor_data
        task = export_doctor_data.delay(doctor.id, 'prescriptions')
        print(f"Export task created with ID: {task.id}")
        
        return success_response({'task_id': task.id}, 'Prescriptions export initiated. You will receive an email when ready.')
    except Exception as e:
        print(f"Error initiating prescriptions export: {str(e)}")
        import traceback
        traceback.print_exc()
        logger.error(f"Error initiating prescriptions export: {str(e)}")
        return error_response('Failed to initiate prescriptions export', 500)

@doctor_bp.route('/appointments/export/csv', methods=['GET'])
@jwt_required('doctor')
def export_appointments_csv():
    """Export appointments as CSV"""
    try:
        print("Initiating appointments CSV export for doctor")
        doctor = DoctorService.get_current_doctor()
        print(f"Doctor object: {doctor}")
        if not doctor:
            print("Doctor profile not found")
            return error_response('Doctor profile not found', 404)
        
        print(f"Doctor found: {doctor.name} (ID: {doctor.id})")
        csv_data = DoctorService.export_data_csv(doctor.id, 'appointments')
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=appointments.csv'}
        )
    except Exception as e:
        print(f"Error exporting appointments: {str(e)}")
        import traceback
        traceback.print_exc()
        logger.error(f"Error exporting appointments: {str(e)}")
        return error_response('Failed to export appointments', 500)

@doctor_bp.route('/appointments/export/email', methods=['POST'])
@jwt_required('doctor')
def export_appointments_csv_email():
    """Export appointments as CSV and send via email"""
    try:
        print("Initiating appointments export for doctor")
        doctor = DoctorService.get_current_doctor()
        print(f"Doctor object: {doctor}")
        if not doctor:
            print("Doctor profile not found")
            return error_response('Doctor profile not found', 404)
        
        print(f"Doctor found: {doctor.name} (ID: {doctor.id})")
        # Trigger background task to generate and send CSV
        from tasks.export_tasks import export_doctor_data
        task = export_doctor_data.delay(doctor.id, 'appointments')
        print(f"Export task created with ID: {task.id}")
        
        return success_response({'task_id': task.id}, 'Appointments export initiated. You will receive an email when ready.')
    except Exception as e:
        print(f"Error initiating appointments export: {str(e)}")
        import traceback
        traceback.print_exc()
        logger.error(f"Error initiating appointments export: {str(e)}")
        return error_response('Failed to initiate appointments export', 500)

@doctor_bp.route('/patients/export/csv', methods=['GET'])
@jwt_required('doctor')
def export_patients_csv():
    """Export patients as CSV"""
    try:
        print("Initiating patients CSV export for doctor")
        doctor = DoctorService.get_current_doctor()
        print(f"Doctor object: {doctor}")
        if not doctor:
            print("Doctor profile not found")
            return error_response('Doctor profile not found', 404)
        
        print(f"Doctor found: {doctor.name} (ID: {doctor.id})")
        csv_data = DoctorService.export_data_csv(doctor.id, 'patients')
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=patients.csv'}
        )
    except Exception as e:
        print(f"Error exporting patients: {str(e)}")
        import traceback
        traceback.print_exc()
        logger.error(f"Error exporting patients: {str(e)}")
        return error_response('Failed to export patients', 500)

@doctor_bp.route('/patients/export/email', methods=['POST'])
@jwt_required('doctor')
def export_patients_csv_email():
    """Export patients as CSV and send via email"""
    try:
        print("Initiating patients export for doctor")
        doctor = DoctorService.get_current_doctor()
        print(f"Doctor object: {doctor}")
        if not doctor:
            print("Doctor profile not found")
            return error_response('Doctor profile not found', 404)
        
        print(f"Doctor found: {doctor.name} (ID: {doctor.id})")
        # Trigger background task to generate and send CSV
        from tasks.export_tasks import export_doctor_data
        task = export_doctor_data.delay(doctor.id, 'patients')
        print(f"Export task created with ID: {task.id}")
        
        return success_response({'task_id': task.id}, 'Patients export initiated. You will receive an email when ready.')
    except Exception as e:
        print(f"Error initiating patients export: {str(e)}")
        import traceback
        traceback.print_exc()
        logger.error(f"Error initiating patients export: {str(e)}")
        return error_response('Failed to initiate patients export', 500)

# ================= Profile Management =================

@doctor_bp.route('/profile', methods=['GET', 'PUT'])
@jwt_required('doctor')
def manage_profile():
    """Get or update doctor profile"""
    try:
        doctor = DoctorService.get_current_doctor()
        if not doctor:
            return error_response('Doctor profile not found', 404)
        
        if request.method == 'PUT':
            data = request.get_json()
            DoctorService.update_profile(doctor.id, data)
            return success_response(message='Profile updated successfully')
        
        profile = DoctorService.get_profile(doctor.id)
        return success_response(profile)
    except Exception as e:
        logger.error(f"Error managing profile: {str(e)}")
        return error_response('Failed to manage profile', 500)