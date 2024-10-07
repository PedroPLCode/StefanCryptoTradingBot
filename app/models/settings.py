#tests 100% ok
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
    
    def __repr__(self):
        return (
            f'<Settings:\n'
            f'symbol: {self.symbol}\n'
            f'bot_running: {self.bot_running}\n'
            f'lookback_days: {self.lookback_days}\n'
            f'stop_loss_pct: {self.stop_loss_pct}\n'
            f'trailing_stop_pct: {self.trailing_stop_pct}\n'
            f'take_profit_pct: {self.take_profit_pct}>'
        )