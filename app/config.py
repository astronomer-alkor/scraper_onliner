class Configuration:
    DEBUG = True
    BROKER_URL = 'mongodb://localhost:27017/database_name'
    CELERY_RESULT_BACKEND = 'mongodb://localhost:27017/database_name'
