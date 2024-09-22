from . import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)

    # Metoda do ustawiania hasła
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Metoda do sprawdzania hasła
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    strategy = db.Column(db.String(150), default="default_strategy")
    trading_enabled = db.Column(db.Boolean, default=False)

class TradeHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trade_time = db.Column(db.DateTime, default=datetime.utcnow)
    buy_or_sell = db.Column(db.String(10))
    amount = db.Column(db.Float)
    price = db.Column(db.Float)

    def __repr__(self):
        return f'<Trade {self.buy_or_sell} {self.amount} BTC at {self.price}>'