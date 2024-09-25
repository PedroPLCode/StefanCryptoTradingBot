from datetime import datetime as dt
from app import db  # Keep this line to import db after it is initialized in __init__.py

class Trades(db.Model):
    __tablename__ = 'trades' 
    id = db.Column(db.Integer, primary_key=True)
    trade_time = db.Column(db.DateTime, default=dt.utcnow)
    buy_or_sell = db.Column(db.String(10))
    amount = db.Column(db.Float)
    price = db.Column(db.Float)

    def __repr__(self):
        return f'<Trade {self.buy_or_sell} {self.amount} BTC at {self.price}>'