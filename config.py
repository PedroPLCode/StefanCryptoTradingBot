class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///stefan.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your-secret-key'
    PERMANENT_SESSION_LIFETIME = 300  # 300 sekund = 5 minut
    MAIL_SERVER = 'smtp.yourmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your-email'
    MAIL_PASSWORD = 'your-password'
    BINANCE_API_KEY = 'your-binance-api-key'
    BINANCE_API_SECRET = 'your-binance-api-secret'
    BINANCE_API_URL = 'https://testnet.binance.vision/api'  # Binance sandbox API