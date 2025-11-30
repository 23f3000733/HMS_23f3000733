"""
JWT Token Management
"""
import jwt
from datetime import datetime, timedelta
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class JWTManager:
    """Manage JWT tokens for authentication"""
    
    @staticmethod
    def generate_token(user_id, email, role, expires_in_hours=24):
        """Generate a JWT token"""
        try:
            payload = {
                'user_id': user_id,
                'email': email,
                'role': role,
                'exp': datetime.utcnow() + timedelta(hours=expires_in_hours),
                'iat': datetime.utcnow()
            }
            
            token = jwt.encode(
                payload,
                current_app.config['SECRET_KEY'],
                algorithm='HS256'
            )
            
            return token
        except Exception as e:
            logger.error(f"Error generating token: {str(e)}")
            return None
    
    @staticmethod
    def verify_token(token):
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
    
    @staticmethod
    def generate_refresh_token(user_id, expires_in_days=7):
        """Generate a refresh token"""
        try:
            payload = {
                'user_id': user_id,
                'type': 'refresh',
                'exp': datetime.utcnow() + timedelta(days=expires_in_days),
                'iat': datetime.utcnow()
            }
            
            token = jwt.encode(
                payload,
                current_app.config['SECRET_KEY'],
                algorithm='HS256'
            )
            
            return token
        except Exception as e:
            logger.error(f"Error generating refresh token: {str(e)}")
            return None
    
    @staticmethod
    def verify_refresh_token(token):
        """Verify a refresh token"""
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            
            if payload.get('type') != 'refresh':
                return None
            
            return payload
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None
