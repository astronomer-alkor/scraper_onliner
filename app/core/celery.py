from celery import Celery
from app.application import APP


def make_celery():
    celery = Celery(APP.import_name,
                    backend=APP.config['CELERY_RESULT_BACKEND'],
                    broker=APP.config['CELERY_BROKER_URL'])
    celery.conf.update(APP.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with APP.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = make_celery()
