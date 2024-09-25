from .. import db  # Keep this line to import db after it is initialized in __init__.py

class Settings(db.Model):
    __tablename__ = 'settings'  # Optional: Specify the table name
    id = db.Column(db.Integer, primary_key=True)
    strategy = db.Column(db.String(150), default="default_strategy")
    trading_enabled = db.Column(db.Boolean, default=False)