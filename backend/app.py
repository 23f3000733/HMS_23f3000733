from flask import Flask
from config import Config
from extensions import db, security, cors, mail
from models import user_datastore
from flask_migrate import Migrate



def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    security.init_app(app, user_datastore)
    cors.init_app(app)
    mail.init_app(app)
    Migrate(app, db)
    
    # Celery initialized in celery_worker.py for worker process
    # app.celery = make_celery(app)

    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.doctor import doctor_bp
    from routes.patient import patient_bp
    from routes.task_status import task_status_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(doctor_bp, url_prefix='/doctor')
    app.register_blueprint(patient_bp, url_prefix='/patient')
    app.register_blueprint(task_status_bp, url_prefix='/task')

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created.")
    
    app.run(debug=True)