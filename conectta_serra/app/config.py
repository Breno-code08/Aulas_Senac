import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///conectta.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    WTF_CSRF_HEADERS = ['X-CSRF-Token']
    MAX_CONTENT_LENGTH = 20000
    DEMO_MODE = os.getenv('DEMO_MODE', 'true').lower() == 'true'
