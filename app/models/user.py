from flask_login import UserMixin
from datetime import datetime as dt
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db

class User(UserMixin, db.Model):
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
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        self.last_login = dt.now()

    def increment_login_errors(self):
        if self.login_errors is None: 
            self.login_errors = 0
        self.login_errors += 1

    def reset_login_errors(self):
        self.login_errors = 0

    def __repr__(self):
        return (
            f'<User:\n'
            f'id: {self.id}\n'
            f'login: {self.login}\n'
            f'name: {self.name}>'
            f'email: {self.email}\n'
            f'creation_date: {self.creation_date}\n'
            f'last_login: {self.last_login}\n'
            f'control_panel_access: {self.control_panel_access}\n'
            f'admin_panel_access: {self.admin_panel_access}\n'
            f'email_raports_receiver: {self.email_raports_receiver}\n'
            f'login_errors: {self.login_errors}\n'
            f'account_suspended: {self.account_suspended}>'
        )