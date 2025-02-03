from .. import db
import pandas as pd

class BotTechnicalAnalysis(db.Model):
    """
    Represents the technical analysis data for a trading bot.

    Attributes:
        id (int): The unique identifier for the technical analysis record.
        df (str, optional): JSON-encoded pandas DataFrame storing historical price data.
        current_trend (str, optional): The current market trend (default: "undefined").
        current_close (float, optional): The latest closing price (default: 0).
        current_high (float, optional): The latest highest price (default: 0).
        current_low (float, optional): The latest lowest price (default: 0).
        current_volume (float, optional): The latest trading volume (default: 0).
        current_rsi (float, optional): The current Relative Strength Index (RSI) value (default: 0).
        current_cci (float, optional): The current Commodity Channel Index (CCI) value (default: 0).
        current_mfi (float, optional): The current Money Flow Index (MFI) value (default: 0).
        current_ema_fast (float, optional): The fast Exponential Moving Average (EMA) value (default: 0).
        current_ema_slow (float, optional): The slow Exponential Moving Average (EMA) value (default: 0).
        current_macd (float, optional): The current MACD value (default: 0).
        current_macd_signal (float, optional): The current MACD signal line value (default: 0).
        current_macd_histogram (float, optional): The current MACD histogram value (default: 0).
        current_ma_50 (float, optional): The 50-period Moving Average (MA) value (default: 0).
        current_ma_200 (float, optional): The 200-period Moving Average (MA) value (default: 0).
        current_upper_band (float, optional): The upper Bollinger Band value (default: 0).
        current_lower_band (float, optional): The lower Bollinger Band value (default: 0).
        current_stoch_k (float, optional): The %K value of the Stochastic Oscillator (default: 0).
        current_stoch_d (float, optional): The %D value of the Stochastic Oscillator (default: 0).
        current_stoch_rsi (float, optional): The Stochastic RSI value (default: 0).
        current_stoch_rsi_k (float, optional): The %K value of the Stochastic RSI (default: 0).
        current_stoch_rsi_d (float, optional): The %D value of the Stochastic RSI (default: 0).
        current_atr (float, optional): The Average True Range (ATR) value (default: 0).
        current_psar (float, optional): The Parabolic SAR value (default: 0).
        current_vwap (float, optional): The Volume Weighted Average Price (VWAP) value (default: 0).
        current_adx (float, optional): The Average Directional Index (ADX) value (default: 0).
        current_plus_di (float, optional): The Positive Directional Indicator (+DI) (default: 0).
        current_minus_di (float, optional): The Negative Directional Indicator (-DI) (default: 0).
        avg_volume (float, optional): The average trading volume (default: 0).
        avg_rsi (float, optional): The average RSI value (default: 0).
        avg_cci (float, optional): The average CCI value (default: 0).
        avg_mfi (float, optional): The average MFI value (default: 0).
        avg_atr (float, optional): The average ATR value (default: 0).
        avg_stoch_rsi_k (float, optional): The average %K value of the Stochastic RSI (default: 0).
        avg_macd (float, optional): The average MACD value (default: 0).
        avg_macd_signal (float, optional): The average MACD signal line value (default: 0).
        avg_stoch_k (float, optional): The average %K value of the Stochastic Oscillator (default: 0).
        avg_stoch_d (float, optional): The average %D value of the Stochastic Oscillator (default: 0).
        avg_ema_fast (float, optional): The average fast EMA value (default: 0).
        avg_ema_slow (float, optional): The average slow EMA value (default: 0).
        avg_plus_di (float, optional): The average +DI value (default: 0).
        avg_minus_di (float, optional): The average -DI value (default: 0).
        avg_psar (float, optional): The average PSAR value (default: 0).
        avg_vwap (float, optional): The average VWAP value (default: 0).
        avg_close (float, optional): The average closing price (default: 0).
        last_updated_timestamp (datetime, optional): The timestamp of the last update (default: current timestamp).
        bot_settings_id (int): The foreign key referencing the bot settings.

    Methods:
        set_df(df: pd.DataFrame): Stores a pandas DataFrame as a JSON string in the database.
        get_df() -> pd.DataFrame: Retrieves and converts the stored JSON string back into a pandas DataFrame.
        __repr__(): Returns a string representation of the technical analysis object.
    """

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
        """Stores a pandas DataFrame as a JSON string in the database."""
        self.df = df.to_json(orient="records")


    def get_df(self):
        """Retrieves the stored JSON string and converts it back into a pandas DataFrame."""
        return pd.read_json(self.df, orient="records") if self.df else pd.DataFrame()

    
    def __repr__(self):
        """Return a string representation of the object."""
        return f'{self.id}'