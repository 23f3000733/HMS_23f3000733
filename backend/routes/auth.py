"""
Authentication Routes with JWT
"""
from flask import Blueprint, request
from flask_security import login_user, logout_user
from flask_security.utils import verify_password, hash_password
from extensions import db
from models import user_datastore, PatientDetails
from utils.helpers import success_response, error_response
from utils.jwt_manager import JWTManager
from utils.rate_limiter import auth_rate_limit
from utils.sanitizer import InputSanitizer
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/login', methods=['POST'])
@auth_rate_limit
def login():
    """
    User login endpoint with JWT.
    Returns JWT access token and refresh token.
    """
    try:
        data = request.get_json()
        if not data:
            return error_response('No data provided', 400)
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return error_response('Email and password are required', 400)
        
        # Sanitize email
        try:
            email = InputSanitizer.sanitize_email(email)
        except ValueError as e:
            return error_response(str(e), 400)
        
        user = user_datastore.find_user(email=email)
        
        if not user:
            return error_response('Invalid credentials', 401)
        
        if not verify_password(password, user.password):
            return error_response('Invalid credentials', 401)
        
        if not user.active:
            return error_response('Account is inactive', 403)
        
        login_user(user)
        
        # Generate JWT tokens
        role = user.roles[0].name if user.roles else None
        access_token = JWTManager.generate_token(user.id, user.email, role)
        refresh_token = JWTManager.generate_refresh_token(user.id)
        
        if not access_token:
            return error_response('Failed to generate token', 500)
        
        return success_response({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 86400,  # 24 hours in seconds
            'role': role,
            'user_id': user.id,
            'email': user.email
        }, 'Login successful')
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return error_response('Login failed', 500)

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """Refresh access token using refresh token"""
    try:
        data = request.get_json()
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            return error_response('Refresh token required', 400)
        
        payload = JWTManager.verify_refresh_token(refresh_token)
        if not payload:
            return error_response('Invalid or expired refresh token', 401)
        
        user_id = payload.get('user_id')
        user = user_datastore.find_user(id=user_id)
        
        if not user or not user.active:
            return error_response('User not found or inactive', 401)
        
        # Generate new access token
        role = user.roles[0].name if user.roles else None
        access_token = JWTManager.generate_token(user.id, user.email, role)
        
        return success_response({
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': 86400
        }, 'Token refreshed')
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return error_response('Token refresh failed', 500)

@auth_bp.route('/register', methods=['POST'])
@auth_rate_limit
def register():
    """
    Patient registration endpoint with enhanced security.
    Creates a new patient user account.
    """
    try:
        data = request.get_json()
        if not data:
            return error_response('No data provided', 400)
        
        # Validate required fields
        required_fields = ['email', 'password', 'name', 'age', 'contact']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return error_response(
                f"Missing required fields: {', '.join(missing_fields)}", 
                400
            )
        
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        age = data.get('age')
        contact = data.get('contact')
        
        # Sanitize inputs
        try:
            email = InputSanitizer.sanitize_email(email)
            name = InputSanitizer.sanitize_string(name, max_length=100)
            contact = InputSanitizer.sanitize_phone(contact)
        except ValueError as e:
            return error_response(str(e), 400)
        
        # Truncate password to 72 bytes to avoid bcrypt limitations
        if password and len(password) > 72:
            password = password[:72]
            
        # Validate password strength
        try:
            InputSanitizer.validate_password_strength(password)
        except ValueError as e:
            return error_response(str(e), 400)
        
        # Check if user already exists
        if user_datastore.find_user(email=email):
            return error_response('User with this email already exists', 409)
        
        # Validate age
        try:
            age = int(age)
            if age < 0 or age > 150:
                return error_response('Invalid age', 400)
        except ValueError:
            return error_response('Age must be a number', 400)
        
        # Find or create patient role
        patient_role = user_datastore.find_role('patient')
        if not patient_role:
            patient_role = user_datastore.create_role(name='patient', description='Patient')
            db.session.commit()
        
        # Create user
        user = user_datastore.create_user(
            email=email,
            password=hash_password(password),
            roles=[patient_role],
            active=True
        )
        db.session.commit()
        
        # Create patient details
        patient_details = PatientDetails(
            user_id=user.id,
            name=name,
            age=age,
            contact=contact
        )
        db.session.add(patient_details)
        db.session.commit()
        
        logger.info(f"New patient registered: {email}")
        
        # Generate JWT tokens for immediate login
        access_token = JWTManager.generate_token(user.id, user.email, 'patient')
        refresh_token = JWTManager.generate_refresh_token(user.id)
        
        return success_response({
            'user_id': user.id,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer'
        }, 'Registration successful', 201)
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        db.session.rollback()
        return error_response('Registration failed', 500)

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    User logout endpoint.
    Note: With JWT, logout is handled client-side by removing the token.
    """
    logout_user()
    return success_response(message='Logged out successfully')
