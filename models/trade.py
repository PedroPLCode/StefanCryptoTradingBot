from app import db
import datetime as dt

class TradeHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, nullable=False, default=dt.utcnow)
    detail = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    success = db.Column(db.Boolean, nullable=False, default=False)