from flask import Flask
from config import Config
from extensions import db, security, cors, celery
from models import user_datastore
from flask_migrate import Migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    cors.init_app(app)
    security.init_app(app, user_datastore)
    Migrate(app, db)
    
    # Initialize Celery
    app.config.update(CELERY_CONFIG={
        'broker_url': app.config['CELERY_BROKER_URL'],
        'result_backend': app.config['CELERY_RESULT_BACKEND'],
    })
    celery.conf.update(app.config)

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.doctor import doctor_bp
    from routes.patient import patient_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(doctor_bp, url_prefix='/doctor')
    app.register_blueprint(patient_bp, url_prefix='/patient')

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Always seed the database with sample data for development
        print("Seeding database...")
        admin_role = user_datastore.find_or_create_role(name='admin', description='Administrator')
        doctor_role = user_datastore.find_or_create_role(name='doctor', description='Doctor')
        patient_role = user_datastore.find_or_create_role(name='patient', description='Patient')
        
        # Create admin user if not exists
        if not user_datastore.find_user(email='admin@hms.com'):
            admin_user = user_datastore.create_user(
                email='admin@hms.com', 
                password='password', 
                roles=[admin_role],
                fs_uniquifier='admin_uniquifier'
            )
        
        # Create sample doctors if not exist
        if not user_datastore.find_user(email='john.doe@hms.com'):
            doctor1_user = user_datastore.create_user(
                email='john.doe@hms.com',
                password='password',
                roles=[doctor_role],
                fs_uniquifier='doctor1_uniquifier'
            )
        
        if not user_datastore.find_user(email='jane.smith@hms.com'):
            doctor2_user = user_datastore.create_user(
                email='jane.smith@hms.com',
                password='password',
                roles=[doctor_role],
                fs_uniquifier='doctor2_uniquifier'
            )
        
        # Create sample patient if not exists
        if not user_datastore.find_user(email='patient1@example.com'):
            patient1_user = user_datastore.create_user(
                email='patient1@example.com',
                password='password',
                roles=[patient_role],
                fs_uniquifier='patient1_uniquifier'
            )
        
        db.session.commit()
        
        # Create doctor details if not exist
        from models import DoctorDetails, PatientDetails
        
        doctor1 = user_datastore.find_user(email='john.doe@hms.com')
        doctor2 = user_datastore.find_user(email='jane.smith@hms.com')
        patient1 = user_datastore.find_user(email='patient1@example.com')
        
        if doctor1 and not DoctorDetails.query.filter_by(user_id=doctor1.id).first():
            doctor1_details = DoctorDetails(
                user_id=doctor1.id,
                name='John Doe',
                specialization='Cardiology',
                experience=10
            )
            db.session.add(doctor1_details)
        
        if doctor2 and not DoctorDetails.query.filter_by(user_id=doctor2.id).first():
            doctor2_details = DoctorDetails(
                user_id=doctor2.id,
                name='Jane Smith',
                specialization='Dentist',
                experience=8
            )
            db.session.add(doctor2_details)
        
        if patient1 and not PatientDetails.query.filter_by(user_id=patient1.id).first():
            patient1_details = PatientDetails(
                user_id=patient1.id,
                name='Sample Patient',
                age=30,
                contact='123-456-7890'
            )
            db.session.add(patient1_details)
        
        db.session.commit()
        print("Database seeded with sample data.")

    app.run(debug=True)
