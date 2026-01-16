"""
Input Sanitization and Validation Utilities
"""
import os
import re
import html
import bleach
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

class InputSanitizer:
    """Sanitize and validate user inputs"""
    
    @staticmethod
    def sanitize_html(text):
        """Remove potentially dangerous HTML/JavaScript"""
        if not text:
            return text
        
        # Allow only safe HTML tags
        allowed_tags = ['p', 'br', 'strong', 'em', 'u']
        allowed_attributes = {}
        
        cleaned = bleach.clean(
            text,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
        
        return cleaned
    
    @staticmethod
    def sanitize_string(text, max_length=None):
        """Sanitize a general string input"""
        if not text:
            return text
        
        # HTML escape
        sanitized = html.escape(str(text))
        
        # Trim if max length specified
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized.strip()
    
    @staticmethod
    def sanitize_email(email):
        """Validate and sanitize email address"""
        if not email:
            return None
        
        email = email.strip().lower()
        
        # Basic email regex
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise ValueError('Invalid email format')
        
        return email
    
    @staticmethod
    def sanitize_phone(phone):
        """Sanitize phone number"""
        if not phone:
            return None
        
        # Remove all non-digit characters
        phone = re.sub(r'\D', '', str(phone))
        
        # Basic validation (10-15 digits)
        if not 10 <= len(phone) <= 15:
            raise ValueError('Invalid phone number')
        
        return phone
    
    @staticmethod
    def sanitize_url(url):
        """Validate and sanitize URL"""
        if not url:
            return None
        
        try:
            parsed = urlparse(url)
            if not parsed.scheme in ['http', 'https']:
                raise ValueError('Invalid URL scheme')
            if not parsed.netloc:
                raise ValueError('Invalid URL')
            return url
        except Exception as e:
            raise ValueError(f'Invalid URL: {str(e)}')
    
    @staticmethod
    def sanitize_filename(filename):
        """Sanitize filename to prevent directory traversal"""
        if not filename:
            return None
        
        # Remove path separators and dangerous characters
        filename = os.path.basename(filename)
        filename = re.sub(r'[^\w\s.-]', '', filename)
        
        return filename
    
    @staticmethod
    def validate_password_strength(password):
        """Validate password strength"""
        if not password:
            raise ValueError('Password is required')
        
        if len(password) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', password):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', password):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'[0-9]', password):
            raise ValueError('Password must contain at least one number')
        
        return True
    
    @staticmethod
    def sanitize_sql_input(text):
        """Basic SQL injection prevention"""
        if not text:
            return text
        
        # Remove common SQL injection patterns
        dangerous_patterns = [
            r"(\s|^)(OR|AND)(\s|$)",
            r"--",
            r"/\*",
            r"\*/",
            r"xp_",
            r"sp_",
            r"exec(\s|\()",
            r"execute(\s|\()",
            r"insert(\s|\()",
            r"select(\s|\()",
            r"update(\s|\()",
            r"delete(\s|\()",
            r"drop(\s|\()",
            r"create(\s|\()",
            r"alter(\s|\()",
            r"union(\s|\()"
        ]
        
        sanitized = str(text)
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        return sanitized

# Export for easy importing
__all__ = ['InputSanitizer']
