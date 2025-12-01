from celery import Celery
from app import create_app

def make_celery():
    flask_app = create_app()
    
    celery = Celery(
        flask_app.import_name,
        broker=flask_app.config['CELERY_BROKER_URL'],
        backend=flask_app.config['CELERY_RESULT_BACKEND']
    )

    celery.conf.update(
        timezone="Asia/Kolkata",
        enable_utc=False,
        task_serializer='json',
        result_serializer='json',
        accept_content=['json']
    )

    class ContextTask(celery.Task):
        abstract = True
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return super().__call__(*args, **kwargs)

    celery.Task = ContextTask
    return celery

celery = make_celery()
