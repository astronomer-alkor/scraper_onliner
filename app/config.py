class Configuration:
    DEBUG = True
    CELERY_BROKER_URL = 'amqp://admin:admin@localhost:5672/'
    CELERY_RESULT_BACKEND = 'amqp://admin:admin@localhost:5672/'
