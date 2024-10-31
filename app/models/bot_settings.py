from .. import db

class BotSettings(db.Model):
    __tablename__ = 'bot_settings'
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(16), default="BTCUSDC", nullable=False)
    strategy = db.Column(db.String(16), default="swing", nullable=False)
    algorithm = db.Column(db.Integer, default=1, nullable=False)
    comment = db.Column(db.String(1024), nullable=True, unique=False)
    trailing_stop_pct = db.Column(db.Float, default=0.01, nullable=False)
    cci_buy = db.Column(db.Integer, default=-50, nullable=False)
    cci_sell = db.Column(db.Integer, default=50, nullable=False)
    rsi_buy = db.Column(db.Integer, default=35, nullable=False)
    rsi_sell = db.Column(db.Integer, default=65, nullable=False)
    mfi_buy = db.Column(db.Integer, default=30, nullable=False)
    mfi_sell = db.Column(db.Integer, default=70, nullable=False)
    stoch_buy = db.Column(db.Integer, default=20, nullable=False)
    stoch_sell = db.Column(db.Integer, default=80, nullable=False)
    timeperiod = db.Column(db.Integer, default=5, nullable=False)
    interval = db.Column(db.String(16), default="1m", nullable=False)
    lookback_period = db.Column(db.String(16), default="15m", nullable=False)
    bot_running = db.Column(db.Boolean, default=False, nullable=False)
    
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