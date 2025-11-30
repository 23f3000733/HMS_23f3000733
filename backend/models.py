from extensions import db
from flask_security import UserMixin, RoleMixin, SQLAlchemyUserDatastore
from datetime import datetime
import enum

class AppointmentStatus(enum.Enum):
    BOOKED = 'Booked'
    COMPLETED = 'Completed'
    CANCELLED = 'Cancelled'

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id'), index=True),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'), index=True)
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, index=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, index=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    
    # Relationships
    doctor_details = db.relationship('DoctorDetails', backref='user', uselist=False, cascade="all, delete-orphan")
    patient_details = db.relationship('PatientDetails', backref='user', uselist=False, cascade="all, delete-orphan")

class DoctorDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, index=True)
    name = db.Column(db.String(100), index=True)
    specialization = db.Column(db.String(100), index=True)
    experience = db.Column(db.Integer)
    flagged = db.Column(db.Boolean, default=False)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)
    activity_logs = db.relationship('ActivityLog', backref='doctor', lazy=True)

class PatientDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, index=True)
    name = db.Column(db.String(100), index=True)
    age = db.Column(db.Integer)
    contact = db.Column(db.String(20))
    medical_history = db.Column(db.Text)
    flagged = db.Column(db.Boolean, default=False)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='patient', lazy=True)
    activity_logs = db.relationship('PatientActivityLog', backref='patient', lazy=True)
    documents = db.relationship('PatientDocument', backref='patient', lazy=True)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor_details.id'), index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient_details.id'), index=True)
    date = db.Column(db.Date, index=True)
    time = db.Column(db.Time)
    status = db.Column(db.String(20), default=AppointmentStatus.BOOKED.value, index=True)
    
    # Relationship to Treatment (One-to-One)
    treatment = db.relationship('Treatment', backref=db.backref('appointment', uselist=False), uselist=False, cascade="all, delete-orphan")

class Treatment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), unique=True, index=True)
    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)
    email_sent = db.Column(db.Boolean, default=False)
    email_sent_at = db.Column(db.DateTime, nullable=True)
    resend_count = db.Column(db.Integer, default=0)

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor_details.id'), index=True)
    activity_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

class PatientActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient_details.id'), index=True)
    activity_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

class PatientDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient_details.id'), index=True)
    filename = db.Column(db.String(255))
    original_filename = db.Column(db.String(255))
    file_type = db.Column(db.String(50))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

user_datastore = SQLAlchemyUserDatastore(db, User, Role)