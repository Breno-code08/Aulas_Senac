import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root@127.0.0.1:3306/conectta?charset=utf8mb4',
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    WTF_CSRF_HEADERS = ['X-CSRF-Token']
    MAX_CONTENT_LENGTH = 20000
    DEMO_MODE = os.getenv('DEMO_MODE', 'true').lower() == 'true'
