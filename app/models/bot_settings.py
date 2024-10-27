from .. import db

class BotSettings(db.Model):
    __tablename__ = 'bot_settings'
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(16), default="BTCUSDC", nullable=True)
    comment = db.Column(db.String(1024), nullable=True, unique=False)
    strategy = db.Column(db.String(16), default="swing", nullable=True)
    trailing_stop_pct = db.Column(db.Float, default=0.01, nullable=True)
    cci_buy = db.Column(db.Integer, default=-50, nullable=True)
    cci_sell = db.Column(db.Integer, default=50, nullable=True)
    rsi_buy = db.Column(db.Integer, default=35, nullable=True)
    rsi_sell = db.Column(db.Integer, default=65, nullable=True)
    mfi_buy = db.Column(db.Integer, default=30, nullable=True)
    mfi_sell = db.Column(db.Integer, default=70, nullable=True)
    timeperiod = db.Column(db.Integer, default=5, nullable=True)
    interval = db.Column(db.String(16), default="1m", nullable=True)
    lookback_period = db.Column(db.String(16), default="15m", nullable=True)
    signals_extended = db.Column(db.Boolean, default=False, nullable=True)
    bot_running = db.Column(db.Boolean, default=False, nullable=True)
    
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