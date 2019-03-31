class Configuration:
    DEBUG = True
    CELERY_BROKER_URL = 'mongodb://localhost:27017/main_database'
    CELERY_RESULT_BACKEND = 'mongodb://localhost:27017/main_database'
