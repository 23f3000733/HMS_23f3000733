from app import create_app
from celery_app import celery

# Create the Flask application
flask_app = create_app()

# Subclass Celery Task to wrap execution in Flask app context
class ContextTask(celery.Task):
    abstract = True
    def __call__(self, *args, **kwargs):
        with flask_app.app_context():
            return super().__call__(*args, **kwargs)

# Apply the patched Task class to the celery instance
celery.Task = ContextTask
