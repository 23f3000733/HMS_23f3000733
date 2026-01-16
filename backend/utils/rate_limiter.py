"""
Rate Limiting Implementation
"""
from flask import request, jsonify
from functools import wraps
import time
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = defaultdict(list)
    
    def is_allowed(self, key, max_requests, window_seconds):
        """Check if request is allowed based on rate limit"""
        now = time.time()
        window_start = now - window_seconds
        
        # Clean old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > window_start
        ]
        
        # Check if limit exceeded
        if len(self.requests[key]) >= max_requests:
            return False
        
        # Add current request
        self.requests[key].append(now)
        return True
    
    def get_remaining(self, key, max_requests, window_seconds):
        """Get remaining requests in current window"""
        now = time.time()
        window_start = now - window_seconds
        
        current_requests = [
            req_time for req_time in self.requests.get(key, [])
            if req_time > window_start
        ]
        
        return max(0, max_requests - len(current_requests))

# Global rate limiter instance
rate_limiter = RateLimiter()

def limit_requests(max_requests=100, window_seconds=60, key_func=None):
    """
    Rate limiting decorator
    
    Args:
        max_requests: Maximum requests allowed in window
        window_seconds: Time window in seconds
        key_func: Function to generate rate limit key (default: IP address)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get rate limit key
            if key_func:
                key = key_func()
            else:
                key = request.remote_addr
            
            # Check if allowed
            if not rate_limiter.is_allowed(key, max_requests, window_seconds):
                remaining = rate_limiter.get_remaining(key, max_requests, window_seconds)
                logger.warning(f"Rate limit exceeded for {key}")
                return jsonify({
                    'success': False,
                    'message': 'Rate limit exceeded. Please try again later.',
                    'retry_after': window_seconds
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Predefined rate limiters
def auth_rate_limit(f):
    """Rate limit for authentication endpoints (5 requests per minute)"""
    return limit_requests(max_requests=5, window_seconds=60)(f)

def strict_rate_limit(f):
    """Strict rate limit for sensitive operations (10 requests per minute)"""
    return limit_requests(max_requests=10, window_seconds=60)(f)
