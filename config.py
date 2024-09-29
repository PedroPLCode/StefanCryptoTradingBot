import os 
from flask.cli import load_dotenv

load_dotenv()  

class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///stefan.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your-secret-key'
    PERMANENT_SESSION_LIFETIME = 300  # 300 sekund = 5 minut
    SESSION_PERMANENT = False
    
    #GOOGLE_CLIENT_ID = os.environ['GOOGLE_CLIENT_ID']
    #GOOGLE_SECRET_KEY = os.environ['GOOGLE_SECRET_KEY']
    GMAIL_APP_PASSWORD = os.environ['GMAIL_APP_PASSWORD']
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ['GMAIL_USERNAME']
    MAIL_PASSWORD = os.environ['GMAIL_APP_PASSWORD']
    MAIL_DEFAULT_SENDER = os.environ['GMAIL_USERNAME']
    
    BINANCE_API_KEY = 'secret' #os.environ['BINANCE_API_KEY']
    BINANCE_API_SECRET = 'secret' #os.environ['BINANCE_API_SECRET']
    BINANCE_API_URL = 'https://testnet.binance.vision/api'  # Binance sandbox API
    
class TestingConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Baza danych in-memory dla testów
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SERVER_NAME = 'localhost:5000'
    SECRET_KEY = 'test-secret-key'