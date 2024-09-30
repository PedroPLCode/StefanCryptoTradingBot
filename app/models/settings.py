from .. import db

class Settings(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    strategy = db.Column(db.String(150), default="default_strategy")
    trading_enabled = db.Column(db.Boolean, default=False)