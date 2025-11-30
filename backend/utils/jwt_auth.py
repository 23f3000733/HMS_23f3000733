"""
Enhanced Authentication and Authorization with JWT
"""
from functools import wraps
from flask import request, jsonify
from utils.jwt_manager import JWTManager
import logging

logger = logging.getLogger(__name__)

def jwt_required(*roles):
    """
    JWT-based authentication decorator
    Usage: @jwt_required('admin', 'doctor')
    """
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None
            
            # Get token from header
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                try:
                    token = auth_header.split(" ")[1]  # Bearer <token>
                except IndexError:
                    return jsonify({
                        'success': False,
                        'message': 'Invalid token format'
                    }), 401
            
            if not token:
                return jsonify({
                    'success': False,
                    'message': 'Authentication token required'
                }), 401
            
            # Verify token
            payload = JWTManager.verify_token(token)
            if not payload:
                return jsonify({
                    'success': False,
                    'message': 'Invalid or expired token'
                }), 401
            
            # Check roles
            user_role = payload.get('role')
            if roles and user_role not in roles:
                return jsonify({
                    'success': False,
                    'message': 'Insufficient permissions'
                }), 403
            
            # Attach user info to request
            request.current_user_id = payload.get('user_id')
            request.current_user_email = payload.get('email')
            request.current_user_role = user_role
            
            return f(*args, **kwargs)
        return decorated_function
    return wrapper

def get_current_user_from_jwt():
    """Get current user info from JWT token in request"""
    return {
        'user_id': getattr(request, 'current_user_id', None),
        'email': getattr(request, 'current_user_email', None),
        'role': getattr(request, 'current_user_role', None)
    }
