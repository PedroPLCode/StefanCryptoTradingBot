import os
from flask.cli import load_dotenv

load_dotenv()


class DevelopmentConfig:
    """
    Configuration class for the development environment.

    This class contains settings for the Flask application that are specific to the
    development environment, such as database URI, secret keys, session settings,
    email configuration, and CAPTCHA settings.

    Attributes:
        SQLALCHEMY_DATABASE_URI (str): URI for connecting to the database.
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Disable modification tracking.
        SQLALCHEMY_ENGINE_OPTIONS (dict): Database engine options, including timeout settings.
        SECRET_KEY (str): Secret key for signing cookies and other sensitive data.
        WTF_CSRF_SECRET_KEY (str): Secret key for CSRF protection.
        SESSION_COOKIE_SECURE (bool): Whether to use HTTPS (SSL) for session cookies.
        WTF_CSRF_SSL_STRICT (bool): Whether to enforce CSRF protection with SSL.
        WTF_CSRF_ENABLED (bool): Enable/disable CSRF protection.
        PERMANENT_SESSION_LIFETIME (int): Lifetime of permanent sessions in seconds.
        SESSION_PERMANENT (bool): Whether sessions are permanent.
        GMAIL_APP_PASSWORD (str): Password for Gmail app-specific login.
        MAIL_SERVER (str): SMTP server for sending email.
        MAIL_PORT (int): SMTP port for email service.
        MAIL_USE_TLS (bool): Whether to use TLS for email.
        MAIL_USE_SSL (bool): Whether to use SSL for email.
        MAIL_USERNAME (str): Username for Gmail login.
        MAIL_PASSWORD (str): Password for Gmail login.
        MAIL_DEFAULT_SENDER (str): Default sender for emails.
        RECAPTCHA_PUBLIC_KEY (str): Public key for Google reCAPTCHA.
        RECAPTCHA_PRIVATE_KEY (str): Private key for Google reCAPTCHA.
    """

    SQLALCHEMY_DATABASE_URI = "sqlite:///stefan.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"connect_args": {"timeout": 30}}
    SECRET_KEY = os.environ["APP_SECRET_KEY"]
    WTF_CSRF_SECRET_KEY = os.environ["CSRF_SECRET_KEY"]
    SESSION_COOKIE_SECURE = True  # False if https ssl disabled
    WTF_CSRF_SSL_STRICT = True  # False if https ssl disabled
    WTF_CSRF_ENABLED = True  # False if https ssl disabled
    PERMANENT_SESSION_LIFETIME = 300
    SESSION_PERMANENT = False

    GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ["GMAIL_USERNAME"]
    MAIL_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
    MAIL_DEFAULT_SENDER = os.environ["GMAIL_USERNAME"]

    RECAPTCHA_PUBLIC_KEY = os.environ["RECAPTCHA_PUBLIC_KEY"]
    RECAPTCHA_PRIVATE_KEY = os.environ["RECAPTCHA_PRIVATE_KEY"]


class TestingConfig:
    """
    Configuration class for the testing environment.

    This class contains settings for the Flask application that are specific to the
    testing environment. It includes configuration for in-memory SQLite database,
    testing-specific settings, and server configurations.

    Attributes:
        TESTING (bool): Whether the application is in testing mode.
        RECAPTCHA_TESTING (bool): Enable/disable reCAPTCHA testing mode.
        SQLALCHEMY_DATABASE_URI (str): URI for connecting to an in-memory database during tests.
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Disable modification tracking during tests.
        SERVER_NAME (str): Name of the server for testing purposes.
        SECRET_KEY (str): Secret key for signing cookies and other sensitive data during tests.
    """

    TESTING = True
    RECAPTCHA_TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SERVER_NAME = "localhost:5000"
    SECRET_KEY = "test-secret-key"
