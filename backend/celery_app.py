from celery import Celery

# Create celery instance without Flask app context
celery = Celery()

# Configure celery
celery.conf.update(
    timezone="Asia/Kolkata",
    enable_utc=False,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0'
)

def make_celery(flask_app):
    celery.conf.update(
        broker_url=flask_app.config['CELERY_BROKER_URL'],
        result_backend=flask_app.config['CELERY_RESULT_BACKEND']
    )

    class ContextTask(celery.Task):
        abstract = True
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return super().__call__(*args, **kwargs)

    celery.Task = ContextTask
    return celery