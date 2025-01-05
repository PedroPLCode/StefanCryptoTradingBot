from .. import db
import pandas as pd

class BotTechnicalAnalysis(db.Model):
    __tablename__ = 'bot_technical_analysis'
    id = db.Column(db.Integer, primary_key=True)
    
    df = db.Column(db.Text, nullable=True)
    
    current_trend = db.Column(db.String(16), default="undefined", nullable=True)
    
    current_close = db.Column(db.Float, default=0, nullable=True)
    current_high = db.Column(db.Float, default=0, nullable=True)
    current_low = db.Column(db.Float, default=0, nullable=True)
    current_volume = db.Column(db.Float, default=0, nullable=True)

    current_rsi = db.Column(db.Float, default=0, nullable=True)
    current_cci = db.Column(db.Float, default=0, nullable=True)
    current_mfi = db.Column(db.Float, default=0, nullable=True)
    
    current_ema_fast = db.Column(db.Float, default=0, nullable=True)
    current_ema_slow = db.Column(db.Float, default=0, nullable=True)
    
    current_macd = db.Column(db.Float, default=0, nullable=True)
    current_macd_signal = db.Column(db.Float, default=0, nullable=True)
    current_macd_histogram = db.Column(db.Float, default=0, nullable=True)
    
    current_ma_50 = db.Column(db.Float, default=0, nullable=True)
    current_ma_200 = db.Column(db.Float, default=0, nullable=True)
    
    current_upper_band = db.Column(db.Float, default=0, nullable=True)
    current_lower_band = db.Column(db.Float, default=0, nullable=True)
    
    current_stoch_k = db.Column(db.Float, default=0, nullable=True)
    current_stoch_d = db.Column(db.Float, default=0, nullable=True)
    
    current_stoch_rsi = db.Column(db.Float, default=0, nullable=True)
    current_stoch_rsi_k = db.Column(db.Float, default=0, nullable=True)
    current_stoch_rsi_d = db.Column(db.Float, default=0, nullable=True)
    
    current_atr = db.Column(db.Float, default=0, nullable=True)
    current_psar = db.Column(db.Float, default=0, nullable=True)
    current_vwap = db.Column(db.Float, default=0, nullable=True)
    current_adx = db.Column(db.Float, default=0, nullable=True)
    current_plus_di = db.Column(db.Float, default=0, nullable=True)
    current_minus_di = db.Column(db.Float, default=0, nullable=True)
    
    avg_volume = db.Column(db.Float, default=0, nullable=True)
    avg_rsi = db.Column(db.Float, default=0, nullable=True)
    avg_cci = db.Column(db.Float, default=0, nullable=True)
    avg_mfi = db.Column(db.Float, default=0, nullable=True)
    avg_atr = db.Column(db.Float, default=0, nullable=True)
    avg_stoch_rsi_k = db.Column(db.Float, default=0, nullable=True)
    avg_macd = db.Column(db.Float, default=0, nullable=True)
    avg_macd_signal = db.Column(db.Float, default=0, nullable=True)
    avg_stoch_k = db.Column(db.Float, default=0, nullable=True)
    avg_stoch_d = db.Column(db.Float, default=0, nullable=True)
    avg_ema_fast = db.Column(db.Float, default=0, nullable=True)
    avg_ema_slow = db.Column(db.Float, default=0, nullable=True)
    avg_plus_di = db.Column(db.Float, default=0, nullable=True)
    avg_minus_di = db.Column(db.Float, default=0, nullable=True)
    avg_psar = db.Column(db.Float, default=0, nullable=True)
    avg_vwap = db.Column(db.Float, default=0, nullable=True)
    avg_close = db.Column(db.Float, default=0, nullable=True)
    
    last_updated_timestamp = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=True)
    
    bot_settings_id = db.Column(db.Integer, db.ForeignKey('bot_settings.id'), nullable=False)
    bot_settings = db.relationship(
        'BotSettings',
        back_populates='bot_technical_analysis',
        overlaps="bot_technical_analysis"
    )
    
    def set_df(self, df):
        self.df = df.to_json(orient="records")

    def get_df(self):
        return pd.read_json(self.df)
    
    def __repr__(self):
        return (f'{self.id}')