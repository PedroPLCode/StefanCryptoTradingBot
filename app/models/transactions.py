from datetime import datetime as dt
from app import db

class Buy(db.Model):
    __tablename__ = 'buy' 
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, default=dt.utcnow)
    amount = db.Column(db.Float)
    price = db.Column(db.Float)

    def __repr__(self):
        return f'<Buy {self.time} {self.amount} {self.price}>'
    

class Sell(db.Model):
    __tablename__ = 'sell' 
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, default=dt.utcnow)
    amount = db.Column(db.Float)
    price = db.Column(db.Float)

    def __repr__(self):
        return f'<Sell {self.time} {self.amount} {self.price}>'