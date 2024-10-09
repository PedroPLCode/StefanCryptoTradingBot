from .. import db

class Settings(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(16), default="BTCUSDC")
    trailing_stop_pct = db.Column(db.Float, default=0.01)
    interval = db.Column(db.String(16), default="1m")
    lookback_days = db.Column(db.String(16), default="30 days")
    bot_running = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return (
            f'<Settings:\n'
            f'symbol: {self.symbol}\n'
            f'trailing_stop_pct: {self.trailing_stop_pct}>'
            f'interval: {self.interval}\n'
            f'lookback_days: {self.lookback_days}\n'
            f'bot_running: {self.bot_running}>'
        )