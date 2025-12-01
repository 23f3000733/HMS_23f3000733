import os
from pickle import TRUE

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-for-hms-v2'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///hms.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'random_salt_for_dev_only'
    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False

    # Celery (Redis backend, correct for Windows)
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/0'

    # Set to False to use actual Celery workers (recommended for production)
    # Set to True for testing without Redis/Celery worker (tasks run synchronously)
    CELERY_TASK_ALWAYS_EAGER = True

    WTF_CSRF_ENABLED = False

    # Uploads
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(os.getcwd(), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # Mail Settings for Gmail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'sangalkartik4@gmail.com'
    MAIL_PASSWORD = 'xwaxigsjxauqlcvd'
    MAIL_DEFAULT_SENDER = 'sangalkartik4@gmail.com'