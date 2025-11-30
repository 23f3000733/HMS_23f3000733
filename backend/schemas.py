"""
Validation Schemas using Marshmallow
"""
from marshmallow import Schema, fields, validates, ValidationError, validate
import re
from utils.constants import DEFAULT_PAGE, DEFAULT_PER_PAGE, MAX_PER_PAGE

def validate_password_strength(password):
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long')
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter')
    
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain at least one lowercase letter')
    if not re.search(r'[0-9]', password):
        raise ValidationError('Password must contain at least one number')
    if not re.search(r'[@!#$%^&*(){}[\]:<>,._=-]', password):
        raise ValidationError('Password must contain at least one special character')

class DoctorCreateSchema(Schema):
    """Schema for creating a doctor"""
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate_password_strength)
    specialization = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    experience = fields.Int(validate=validate.Range(min=0, max=70))

    @validates('specialization')
    def validate_specialization(self, value):
        if not value or not value.strip():
            raise ValidationError('Specialization is required')

    @validates('experience')
    def validate_experience(self, value):
        if value is not None and (value < 0 or value > 70):
            raise ValidationError('Experience is must be between 0 to 70 years')

class DoctorUpdateSchema(Schema):
    """Schema for updating a doctor"""
    name = fields.Str(validate=validate.Length(min=2, max=100))
    specialization = fields.Str(validate=validate.Length(min=2, max=100))
    experience = fields.Int(validate=validate.Range(min=0, max=70))

    @validates('specialization')
    def validate_specialization(self, value):
        if not value or not value.strip():
            raise ValidationError('Specialization is required')

    @validates('experience')
    def validate_experience(self, value):
        if value is not None and (value < 0 or value > 70):
            raise ValidationError('Experience is must be between 0 to 70 years')

class PatientCreateSchema(Schema):
    """Schema for creating a patient"""
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate_password_strength)
    age = fields.Int(required=True, validate=validate.Range(min=0, max=150))
    contact = fields.Str(required=True, validate=validate.Length(min=10, max=20))

class PatientUpdateSchema(Schema):
    """Schema for updating a patient"""
    name = fields.Str(validate=validate.Length(min=2, max=100))
    age = fields.Int(validate=validate.Range(min=0, max=150))
    contact = fields.Str(validate=validate.Length(min=10, max=20))
    medical_history = fields.Str()

class AppointmentCreateSchema(Schema):
    """Schema for creating an appointment"""
    doctor_id = fields.Int(required=True)
    patient_id = fields.Int(required=True)
    date = fields.Date(required=True)
    time = fields.Time(required=True)

class TreatmentSchema(Schema):
    """Schema for treatment details"""
    diagnosis = fields.Str(required=True)
    prescription = fields.Str(required=True)
    notes = fields.Str()

class PaginationSchema(Schema):
    """Schema for pagination parameters"""
    page = fields.Int(validate=validate.Range(min=1), missing=DEFAULT_PAGE)
    per_page = fields.Int(validate=validate.Range(min=1, max=MAX_PER_PAGE), missing=DEFAULT_PER_PAGE)
