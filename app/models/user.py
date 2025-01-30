from flask_login import UserMixin
from datetime import datetime as dt
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db

class User(UserMixin, db.Model):
    """
    Represents a user in the application.

    Attributes:
        id (int): The unique identifier for the user.
        login (str): The username, must be unique.
        name (str): The full name of the user.
        email (str): The email address, must be unique.
        comment (str, optional): A user-defined comment.
        password_hash (str): The hashed password for authentication.
        creation_date (datetime): The timestamp of account creation.
        last_login (datetime): The timestamp of the last login.
        control_panel_access (bool): Whether the user has access to the control panel.
        admin_panel_access (bool): Whether the user has admin privileges.
        email_raports_receiver (bool): Whether the user receives email reports.
        email_trades_receiver (bool): Whether the user receives trade-related emails.
        login_errors (int): The number of failed login attempts.
        account_suspended (bool): Whether the account is suspended.

    Methods:
        set_password(password): Hashes and sets the user's password.
        check_password(password): Checks if the provided password matches the stored hash.
        update_last_login(): Updates the last login timestamp.
        increment_login_errors(): Increments the login error counter.
        reset_login_errors(): Resets the login error counter to zero.
        __repr__(): Returns a string representation of the user object.
    """
    
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(56), nullable=False, unique=True)
    name = db.Column(db.String(56), nullable=False, unique=False)
    email = db.Column(db.String(128), nullable=False, unique=True)
    comment = db.Column(db.String(1024), nullable=True, unique=False)
    password_hash = db.Column(db.String(128), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=dt.now)
    last_login = db.Column(db.DateTime, nullable=False, default=dt.now)
    
    control_panel_access = db.Column(db.Boolean, nullable=False, default=False)
    admin_panel_access = db.Column(db.Boolean, nullable=False, default=False)
    email_raports_receiver = db.Column(db.Boolean, nullable=False, default=False)
    email_trades_receiver = db.Column(db.Boolean, nullable=False, default=False)
    
    login_errors = db.Column(db.Integer, nullable=False, unique=False, default=0)
    account_suspended = db.Column(db.Boolean, nullable=False, default=False)


    def set_password(self, password):
        """
        Hashes and sets the user's password.

        Args:
            password (str): The plain-text password to be hashed.
        """
        self.password_hash = generate_password_hash(password)


    def check_password(self, password):
        """
        Checks if the provided password matches the stored hash.

        Args:
            password (str): The plain-text password to be verified.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return check_password_hash(self.password_hash, password)
    
    
    def update_last_login(self):
        """Updates the last login timestamp to the current time."""
        self.last_login = dt.now()


    def increment_login_errors(self):
        """Increments the login error counter."""
        if self.login_errors is None: 
            self.login_errors = 0
        self.login_errors += 1


    def reset_login_errors(self):
        """Resets the login error counter to zero."""
        self.login_errors = 0


    def __repr__(self):
        """Returns a string representation of the user object."""
        return (
            f'<User:\n'
            f'id: {self.id}\n'
            f'login: {self.login}\n'
            f'name: {self.name}\n'
            f'email: {self.email}\n'
            f'creation_date: {self.creation_date}\n'
            f'last_login: {self.last_login}\n'
            f'control_panel_access: {self.control_panel_access}\n'
            f'admin_panel_access: {self.admin_panel_access}\n'
            f'email_raports_receiver: {self.email_raports_receiver}\n'
            f'email_trades_receiver: {self.email_trades_receiver}\n'
            f'login_errors: {self.login_errors}\n'
            f'account_suspended: {self.account_suspended}>'
        )