from flask_login import UserMixin
from datetime import datetime as dt
from werkzeug.security import generate_password_hash, check_password_hash
from . import db  # Keep this line to import db after it is initialized in __init__.py

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(56), nullable=False, unique=True)
    name = db.Column(db.String(56), nullable=False, unique=False)
    email = db.Column(db.String(128), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=dt.utcnow)
    last_login = db.Column(db.DateTime, nullable=False, default=dt.utcnow)
    accepted = db.Column(db.Boolean, nullable=False, default=False)
    raports = db.Column(db.Boolean, nullable=False, default=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Settings(db.Model):
    __tablename__ = 'settings'  # Optional: Specify the table name
    id = db.Column(db.Integer, primary_key=True)
    strategy = db.Column(db.String(150), default="default_strategy")
    trading_enabled = db.Column(db.Boolean, default=False)


class TradeHistory(db.Model):
    __tablename__ = 'trade_history'  # Optional: Specify the table name
    id = db.Column(db.Integer, primary_key=True)
    trade_time = db.Column(db.DateTime, default=dt.utcnow)
    buy_or_sell = db.Column(db.String(10))
    amount = db.Column(db.Float)
    price = db.Column(db.Float)

    def __repr__(self):
        return f'<Trade {self.buy_or_sell} {self.amount} BTC at {self.price}>'