from .. import db

class BotSettings(db.Model):
    __tablename__ = 'bot_settings'
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(16), default="BTCUSDC", nullable=False)
    strategy = db.Column(db.String(16), default="scalp", nullable=False)
    algorithm = db.Column(db.Integer, default=1, nullable=False)
    comment = db.Column(db.String(1024), nullable=True, unique=False)
    
    trailing_stop_pct = db.Column(db.Float, default=0.03, nullable=False)
    sell_signal_only_trailing_stop = db.Column(db.Boolean, default=False, nullable=False)
    trailing_stop_with_atr = db.Column(db.Boolean, default=True, nullable=False)
    trailing_stop_atr_calc = db.Column(db.Float, default=2, nullable=False)
    
    cci_buy = db.Column(db.Integer, default=-100, nullable=False)
    cci_sell = db.Column(db.Integer, default=100, nullable=False)
    rsi_buy = db.Column(db.Integer, default=30, nullable=False)
    rsi_sell = db.Column(db.Integer, default=70, nullable=False)
    mfi_buy = db.Column(db.Integer, default=30, nullable=False)
    mfi_sell = db.Column(db.Integer, default=70, nullable=False)
    stoch_buy = db.Column(db.Integer, default=20, nullable=False)
    stoch_sell = db.Column(db.Integer, default=80, nullable=False)
    
    avg_adx_period = db.Column(db.Integer, default=7, nullable=False)
    avg_atr_period = db.Column(db.Integer, default=28, nullable=False)
    avg_di_period = db.Column(db.Integer, default=7, nullable=False)
    avg_rsi_period = db.Column(db.Integer, default=3, nullable=False)
    avg_volume_period = db.Column(db.Integer, default=3, nullable=False)
    avg_stoch_rsi_period = db.Column(db.Integer, default=3, nullable=False)
    avg_macd_period = db.Column(db.Integer, default=3, nullable=False)
    avg_stoch_period = db.Column(db.Integer, default=3, nullable=False)
    avg_ema_period = db.Column(db.Integer, default=3, nullable=False)
    avg_cci_period = db.Column(db.Integer, default=3, nullable=False)
    avg_mfi_period = db.Column(db.Integer, default=3, nullable=False)
    
    adx_strong_trend = db.Column(db.Integer, default=25, nullable=False)
    adx_weak_trend = db.Column(db.Integer, default=20, nullable=False)
    adx_no_trend = db.Column(db.Integer, default=5, nullable=False)
    
    general_timeperiod = db.Column(db.Integer, default=14, nullable=False)
    di_timeperiod = db.Column(db.Integer, default=14, nullable=False)
    adx_timeperiod = db.Column(db.Integer, default=14, nullable=False)
    rsi_timeperiod = db.Column(db.Integer, default=7, nullable=False)
    atr_timeperiod = db.Column(db.Integer, default=14, nullable=False)
    cci_timeperiod = db.Column(db.Integer, default=14, nullable=False)
    mfi_timeperiod = db.Column(db.Integer, default=14, nullable=False)
    macd_timeperiod = db.Column(db.Integer, default=6, nullable=False)
    macd_signalperiod = db.Column(db.Integer, default=5, nullable=False)
    boilinger_timeperiod = db.Column(db.Integer, default=20, nullable=False)
    boilinger_nbdev = db.Column(db.Integer, default=2, nullable=False)
    stoch_k_timeperiod = db.Column(db.Integer, default=7, nullable=False)
    stoch_d_timeperiod = db.Column(db.Integer, default=3, nullable=False)
    stoch_rsi_timeperiod = db.Column(db.Integer, default=7, nullable=False)
    stoch_rsi_k_timeperiod = db.Column(db.Integer, default=7, nullable=False)
    stoch_rsi_d_timeperiod = db.Column(db.Integer, default=3, nullable=False)
    ema_fast_timeperiod = db.Column(db.Integer, default=9, nullable=False)
    ema_slow_timeperiod = db.Column(db.Integer, default=21, nullable=False)
    psar_acceleration = db.Column(db.Float, default=0.02, nullable=False)
    psar_maximum = db.Column(db.Float, default=0.2, nullable=False)
    
    interval = db.Column(db.String(16), default="5m", nullable=False)
    lookback_period = db.Column(db.String(16), default="4h", nullable=False)
    
    capital_utilization_pct = db.Column(db.Float, default=0.95, nullable=False)
    days_period_to_clean_history = db.Column(db.Integer, default=30, nullable=False)
    
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