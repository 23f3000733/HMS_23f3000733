"""
Response Helpers and Validators
"""
from flask import jsonify
from marshmallow import ValidationError

def success_response(data=None, message='Success', status_code=200):
    """
    Standard success response format.
    """
    response = {'success': True, 'message': message}
    if data is not None:
        response['data'] = data
    return jsonify(response), status_code

def error_response(message='An error occurred', status_code=400, errors=None):
    """
    Standard error response format.
    """
    response = {'success': False, 'message': message}
    if errors:
        response['errors'] = errors
    return jsonify(response), status_code

def paginate_query(query, page=1, per_page=10):
    """
    Paginate a SQLAlchemy query.
    
    Returns:
        dict with items, total, page, per_page, pages
    """
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        'items': paginated.items,
        'total': paginated.total,
        'page': paginated.page,
        'per_page': paginated.per_page,
        'pages': paginated.pages
    }
