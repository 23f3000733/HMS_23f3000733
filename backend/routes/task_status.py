"""
Task Status Routes
Handles checking Celery task status
"""
from flask import Blueprint
from utils.jwt_auth import jwt_required
from utils.helpers import success_response, error_response
from celery_app import celery
from celery.result import AsyncResult
import logging

task_status_bp = Blueprint('task_status', __name__)
logger = logging.getLogger(__name__)

@task_status_bp.route('/status/<task_id>', methods=['GET'])
@jwt_required()  # Any authenticated user can check task status
def get_task_status(task_id):
    """Get status of a Celery task by task ID"""
    try:
        print(f"Checking status for task ID: {task_id}")
        task_result = AsyncResult(task_id, app=celery)
        print(f"Task state: {task_result.state}")
        
        response_data = {
            'task_id': task_id,
            'status': task_result.state,
            'result': None,
            'error': None
        }
        
        if task_result.state == 'PENDING':
            response_data['result'] = 'Task is waiting to be executed'
        elif task_result.state == 'STARTED':
            response_data['result'] = 'Task is currently running'
        elif task_result.state == 'SUCCESS':
            response_data['result'] = task_result.result
        elif task_result.state == 'FAILURE':
            response_data['error'] = str(task_result.info)
        elif task_result.state == 'RETRY':
            response_data['result'] = 'Task is being retried'
            response_data['error'] = str(task_result.info) if task_result.info else None
        
        print(f"Task status response: {response_data}")
        return success_response(response_data)
    except Exception as e:
        logger.error(f"Error fetching task status: {str(e)}")
        print(f"Error fetching task status: {str(e)}")
        return error_response('Failed to get task status', 500)