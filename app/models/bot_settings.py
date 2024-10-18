from .. import db

class BotSettings(db.Model):
    __tablename__ = 'bot_settings'
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(16), default="BTCUSDC")
    comment = db.Column(db.String(1024), nullable=True, unique=False)
    algorithm = db.Column(db.String(16), default="undefined")
    trailing_stop_pct = db.Column(db.Float, default=0.01)
    interval = db.Column(db.String(16), default="1m")
    lookback_period = db.Column(db.String(16), default="4h")
    sell_signal_extended = db.Column(db.Boolean, default=False)
    bot_running = db.Column(db.Boolean, default=False)
    
    bot_current_trade = db.relationship(
        'BotCurrentTrade',
        uselist=False,
        back_populates='bot_settings',
        overlaps="settings"
    )
    
    bot_trades_history = db.relationship(
        'TradesHistory', 
        backref='bot_settings', 
        lazy=True, 
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return (f'{self.id} {self.symbol}')