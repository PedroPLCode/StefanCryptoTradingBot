#tests ok
from flask_login import UserMixin
from datetime import datetime as dt
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db  # Keep this line to import db after it is initialized in __init__.py

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(56), nullable=False, unique=True)
    name = db.Column(db.String(56), nullable=False, unique=False)
    email = db.Column(db.String(128), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=dt.utcnow)
    last_login = db.Column(db.DateTime, nullable=False, default=dt.utcnow)
    control_panel_access = db.Column(db.Boolean, nullable=False, default=False)
    admin_panel_access = db.Column(db.Boolean, nullable=False, default=False)
    email_raports_receiver = db.Column(db.Boolean, nullable=False, default=False)
    login_errors = db.Column(db.Integer, nullable=False, unique=False, default=0)
    account_suspended = db.Column(db.Boolean, nullable=False, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        self.last_login = dt.utcnow()

    def increment_login_errors(self):
        if self.login_errors is None: 
            self.login_errors = 0
        self.login_errors += 1

    def reset_login_errors(self):
        self.login_errors = 0

    def __repr__(self):
        return f'<User {self.login}, Email: {self.email}, Admin: {self.admin_panel_access}>'