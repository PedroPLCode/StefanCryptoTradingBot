import os 
from flask.cli import load_dotenv

load_dotenv()  

class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///stefan.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ['APP_SECRET_KEY']
    WTF_CSRF_SECRET_KEY = os.environ['CSRF_SECRET_KEY']
    SESSION_COOKIE_SECURE = False # ssl https dodac
    WTF_CSRF_SSL_STRICT = False # ssl https dodac
    WTF_CSRF_ENABLED = False # ssl https dodac
    PERMANENT_SESSION_LIFETIME = 300
    SESSION_PERMANENT = False
    
    GMAIL_APP_PASSWORD = os.environ['GMAIL_APP_PASSWORD']
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ['GMAIL_USERNAME']
    MAIL_PASSWORD = os.environ['GMAIL_APP_PASSWORD']
    MAIL_DEFAULT_SENDER = os.environ['GMAIL_USERNAME']
    
    RECAPTCHA_PUBLIC_KEY = os.environ['RECAPTCHA_PUBLIC_KEY']
    RECAPTCHA_PRIVATE_KEY = os.environ['RECAPTCHA_PRIVATE_KEY']
    
    
class TestingConfig:
    TESTING = True
    RECAPTCHA_TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SERVER_NAME = 'localhost:5000'
    SECRET_KEY = 'test-secret-key'