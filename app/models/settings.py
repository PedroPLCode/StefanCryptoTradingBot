from .. import db

class Settings(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(16), default="BTCUSDT")
    stop_loss_pct = db.Column(db.Float, default=0.02)
    trailing_stop_pct = db.Column(db.Float, default=0.01)
    take_profit_pct = db.Column(db.Float, default=0.03)
    lookback_days = db.Column(db.String(16), default="30 days")
    bot_running = db.Column(db.Boolean, default=False)