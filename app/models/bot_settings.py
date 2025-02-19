from .. import db


class BotSettings(db.Model):
    """
    Represents the configuration settings for the trading bot.

    Attributes:
        id (int): The unique identifier of the bot settings.
        symbol (str): The trading pair symbol (e.g., "BTCUSDC").
        interval (str): The trading time interval (e.g., "1h").
        lookback_period (str): The lookback period for historical data.
        strategy (str): The strategy used by the bot (e.g., "rsi + macd").
        comment (str): A comment or description of the bot's configuration.
        capital_utilization_pct (float): The percentage of capital to be utilized for each trade.
        selected_plot_indicators (list): A list of selected indicators for plotting (e.g., ['rsi', 'macd']).
        days_period_to_clean_history (int): The number of days before cleaning the trade history.
        bot_running (bool): Flag to indicate if the bot is running.
        sell_signal_only_stop_loss_or_take_profit (bool): Flag to indicate if the sell signal is based on stop-loss or take-profit only.
        use_technical_analysis (bool): Flag to indicate if technical analysis should be used.
        use_machine_learning (bool): Flag to indicate if machine learning models should be used.
        use_suspension_after_negative_trade (bool): Flag to enable suspension after a negative trade.
        is_suspended_after_negative_trade (bool): Flag to indicate if the bot is suspended after a negative trade.
        cycles_of_suspension_after_negative_trade (int): The number of suspension cycles after a negative trade.
        suspension_cycles_remaining (int): The number of suspension cycles remaining.
        use_stop_loss (bool): Flag to enable stop loss.
        use_trailing_stop_loss (bool): Flag to enable trailing stop loss.
        stop_loss_pct (float): The percentage for the stop loss trigger.
        trailing_stop_with_atr (bool): Flag to enable trailing stop loss with ATR.
        trailing_stop_atr_calc (float): The ATR value used for calculating trailing stop.
        use_take_profit (bool): Flag to enable take profit.
        use_trailing_take_profit (bool): Flag to enable trailing take profit.
        take_profit_pct (float): The percentage for take profit trigger.
        take_profit_with_atr (bool): Flag to enable take profit with ATR.
        take_profit_atr_calc (float): The ATR value used for calculating take profit.
        trend_signals (bool): Flag to enable trend signals.
        rsi_signals (bool): Flag to enable RSI signals.
        rsi_divergence_signals (bool): Flag to enable RSI divergence signals.
        vol_signals (bool): Flag to enable volume signals.
        macd_cross_signals (bool): Flag to enable MACD cross signals.
        macd_histogram_signals (bool): Flag to enable MACD histogram signals.
        bollinger_signals (bool): Flag to enable Bollinger Bands signals.
        stoch_signals (bool): Flag to enable Stochastic signals.
        stoch_divergence_signals (bool): Flag to enable Stochastic divergence signals.
        stoch_rsi_signals (bool): Flag to enable Stochastic RSI signals.
        ema_cross_signals (bool): Flag to enable EMA cross signals.
        ema_fast_signals (bool): Flag to enable fast EMA signals.
        ema_slow_signals (bool): Flag to enable slow EMA signals.
        di_signals (bool): Flag to enable DI signals.
        cci_signals (bool): Flag to enable CCI signals.
        cci_divergence_signals (bool): Flag to enable CCI divergence signals.
        mfi_signals (bool): Flag to enable MFI signals.
        mfi_divergence_signals (bool): Flag to enable MFI divergence signals.
        atr_signals (bool): Flag to enable ATR signals.
        vwap_signals (bool): Flag to enable VWAP signals.
        psar_signals (bool): Flag to enable PSAR signals.
        ma50_signals (bool): Flag to enable MA50 signals.
        ma200_signals (bool): Flag to enable MA200 signals.
        ma_cross_signals (bool): Flag to enable moving average cross signals.
        general_timeperiod (int): The general time period used for calculations.
        di_timeperiod (int): The DI time period.
        adx_timeperiod (int): The ADX time period.
        rsi_timeperiod (int): The RSI time period.
        atr_timeperiod (int): The ATR time period.
        cci_timeperiod (int): The CCI time period.
        mfi_timeperiod (int): The MFI time period.
        macd_timeperiod (int): The MACD time period.
        macd_signalperiod (int): The MACD signal period.
        bollinger_timeperiod (int): The Bollinger Bands time period.
        bollinger_nbdev (int): The number of deviations for Bollinger Bands.
        stoch_k_timeperiod (int): The Stochastic K time period.
        stoch_d_timeperiod (int): The Stochastic D time period.
        stoch_rsi_timeperiod (int): The Stochastic RSI time period.
        stoch_rsi_k_timeperiod (int): The Stochastic RSI K time period.
        stoch_rsi_d_timeperiod (int): The Stochastic RSI D time period.
        ema_fast_timeperiod (int): The fast EMA time period.
        ema_slow_timeperiod (int): The slow EMA time period.
        psar_acceleration (float): The PSAR acceleration value.
        psar_maximum (float): The PSAR maximum value.
        cci_buy (int): The CCI value for buy signals.
        cci_sell (int): The CCI value for sell signals.
        rsi_buy (int): The RSI value for buy signals.
        rsi_sell (int): The RSI value for sell signals.
        mfi_buy (int): The MFI value for buy signals.
        mfi_sell (int): The MFI value for sell signals.
        stoch_buy (int): The Stochastic value for buy signals.
        stoch_sell (int): The Stochastic value for sell signals.
        atr_buy_treshold (float): The ATR threshold for buy signals.
        avg_volume_period (int): The average volume period.
        avg_close_period (int): The average close period.
        avg_adx_period (int): The average ADX period.
        avg_atr_period (int): The average ATR period.
        avg_di_period (int): The average DI period.
        avg_rsi_period (int): The average RSI period.
        avg_stoch_rsi_period (int): The average Stochastic RSI period.
        avg_macd_period (int): The average MACD period.
        avg_stoch_period (int): The average Stochastic period.
        avg_ema_period (int): The average EMA period.
        avg_cci_period (int): The average CCI period.
        avg_mfi_period (int): The average MFI period.
        avg_psar_period (int): The average PSAR period.
        avg_vwap_period (int): The average VWAP period.
        adx_strong_trend (int): The ADX value for a strong trend.
        adx_weak_trend (int): The ADX value for a weak trend.
        adx_no_trend (int): The ADX value for no trend.
        ml_general_timeperiod (int): The ML general time period.
        ml_macd_timeperiod (int): The ML MACD time period.
        ml_macd_signalperiod (int): The ML MACD signal period.
        ml_bollinger_timeperiod (int): The ML Bollinger Bands time period.
        ml_bollinger_nbdev (int): The ML number of deviations for Bollinger Bands.
        ml_ema_fast_timeperiod (int): The ML fast EMA time period.
        ml_ema_slow_timeperiod (int): The ML slow EMA time period.
        ml_rsi_buy (int): The ML RSI buy value.
        ml_rsi_sell (int): The ML RSI sell value.
        ml_lag_period (int): The ML lag period.
        ml_use_random_forest_model (bool): Flag to use random forest model in ML.
        ml_random_forest_model_filename (str): The filename of the random forest model.
        ml_random_forest_predictions_avg (int): The average number of predictions for random forest.
        ml_random_forest_buy_trigger_pct (float): The percentage threshold for a buy trigger in random forest.
        ml_random_forest_sell_trigger_pct (float): The percentage threshold for a sell trigger in random forest.
        ml_use_xgboost_model (bool): Flag to use XGBoost model in ML.
        ml_xgboost_model_filename (str): The filename of the XGBoost model.
        ml_xgboost_predictions_avg (int): The average number of predictions for XGBoost.
        ml_xgboost_buy_trigger_pct (float): The percentage threshold for a buy trigger in XGBoost.
        ml_xgboost_sell_trigger_pct (float): The percentage threshold for a sell trigger in XGBoost.
        ml_use_lstm_model (bool): Flag to use LSTM model in ML.
        ml_lstm_window_size (int): The LSTM window size.
        ml_lstm_window_lookback (int): The LSTM window lookback period.
        ml_lstm_model_filename (str): The filename of the LSTM model.
        ml_lstm_predictions_avg (int): The average number of predictions for LSTM.
        ml_lstm_buy_trigger_pct (float): The percentage threshold for a buy trigger in LSTM.
        ml_lstm_sell_trigger_pct (float): The percentage threshold for a sell trigger in LSTM.

    Methods:
        __repr__: Returns a string representation of the BotSettings instance.
    """

    __tablename__ = 'bot_settings'
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(128), default="BTCUSDC", nullable=False)
    interval = db.Column(db.String(16), default="1h", nullable=False)
    lookback_period = db.Column(db.String(16), default="2d", nullable=False)
    strategy = db.Column(db.String(128), default="rsi + macd", nullable=False)
    comment = db.Column(db.String(1024), default="swing",
                        nullable=True, unique=False)

    capital_utilization_pct = db.Column(db.Float, default=0.95, nullable=False)
    selected_plot_indicators = db.Column(
        db.JSON, default=['rsi', 'macd'], nullable=False)
    days_period_to_clean_history = db.Column(
        db.Integer, default=30, nullable=False)

    bot_running = db.Column(db.Boolean, default=False, nullable=False)
    sell_signal_only_stop_loss_or_take_profit = db.Column(
        db.Boolean, default=False, nullable=False)
    use_technical_analysis = db.Column(
        db.Boolean, default=False, nullable=False)
    use_machine_learning = db.Column(db.Boolean, default=False, nullable=False)

    use_suspension_after_negative_trade = db.Column(
        db.Boolean, default=False, nullable=False)
    is_suspended_after_negative_trade = db.Column(
        db.Boolean, default=False, nullable=False)
    cycles_of_suspension_after_negative_trade = db.Column(
        db.Integer, default=8, nullable=False)
    suspension_cycles_remaining = db.Column(
        db.Integer, default=0, nullable=False)

    use_stop_loss = db.Column(db.Boolean, default=True, nullable=False)
    use_trailing_stop_loss = db.Column(
        db.Boolean, default=False, nullable=False)
    stop_loss_pct = db.Column(db.Float, default=0.02, nullable=False)
    trailing_stop_with_atr = db.Column(
        db.Boolean, default=False, nullable=False)
    trailing_stop_atr_calc = db.Column(db.Float, default=1, nullable=False)

    use_take_profit = db.Column(db.Boolean, default=True, nullable=False)
    use_trailing_take_profit = db.Column(
        db.Boolean, default=True, nullable=False)
    take_profit_pct = db.Column(db.Float, default=0.03, nullable=False)
    take_profit_with_atr = db.Column(db.Boolean, default=False, nullable=False)
    take_profit_atr_calc = db.Column(db.Float, default=3, nullable=False)

    trend_signals = db.Column(db.Boolean, default=False, nullable=False)
    rsi_signals = db.Column(db.Boolean, default=True, nullable=False)
    rsi_divergence_signals = db.Column(
        db.Boolean, default=False, nullable=False)
    vol_signals = db.Column(db.Boolean, default=True, nullable=False)
    macd_cross_signals = db.Column(db.Boolean, default=True, nullable=False)
    macd_histogram_signals = db.Column(
        db.Boolean, default=False, nullable=False)
    bollinger_signals = db.Column(db.Boolean, default=True, nullable=False)
    stoch_signals = db.Column(db.Boolean, default=True, nullable=False)
    stoch_divergence_signals = db.Column(
        db.Boolean, default=False, nullable=False)
    stoch_rsi_signals = db.Column(db.Boolean, default=False, nullable=False)
    ema_cross_signals = db.Column(db.Boolean, default=False, nullable=False)
    ema_fast_signals = db.Column(db.Boolean, default=False, nullable=False)
    ema_slow_signals = db.Column(db.Boolean, default=False, nullable=False)
    di_signals = db.Column(db.Boolean, default=False, nullable=False)
    cci_signals = db.Column(db.Boolean, default=False, nullable=False)
    cci_divergence_signals = db.Column(
        db.Boolean, default=False, nullable=False)
    mfi_signals = db.Column(db.Boolean, default=False, nullable=False)
    mfi_divergence_signals = db.Column(
        db.Boolean, default=False, nullable=False)
    atr_signals = db.Column(db.Boolean, default=False, nullable=False)
    vwap_signals = db.Column(db.Boolean, default=False, nullable=False)
    psar_signals = db.Column(db.Boolean, default=False, nullable=False)
    ma50_signals = db.Column(db.Boolean, default=False, nullable=False)
    ma200_signals = db.Column(db.Boolean, default=False, nullable=False)
    ma_cross_signals = db.Column(db.Boolean, default=False, nullable=False)

    general_timeperiod = db.Column(db.Integer, default=14, nullable=False)
    di_timeperiod = db.Column(db.Integer, default=14, nullable=False)
    adx_timeperiod = db.Column(db.Integer, default=14, nullable=False)
    rsi_timeperiod = db.Column(db.Integer, default=14, nullable=False)
    atr_timeperiod = db.Column(db.Integer, default=14, nullable=False)
    cci_timeperiod = db.Column(db.Integer, default=20, nullable=False)
    mfi_timeperiod = db.Column(db.Integer, default=14, nullable=False)
    macd_timeperiod = db.Column(db.Integer, default=12, nullable=False)
    macd_signalperiod = db.Column(db.Integer, default=9, nullable=False)
    bollinger_timeperiod = db.Column(db.Integer, default=20, nullable=False)
    bollinger_nbdev = db.Column(db.Integer, default=2, nullable=False)
    stoch_k_timeperiod = db.Column(db.Integer, default=14, nullable=False)
    stoch_d_timeperiod = db.Column(db.Integer, default=3, nullable=False)
    stoch_rsi_timeperiod = db.Column(db.Integer, default=14, nullable=False)
    stoch_rsi_k_timeperiod = db.Column(db.Integer, default=3, nullable=False)
    stoch_rsi_d_timeperiod = db.Column(db.Integer, default=3, nullable=False)
    ema_fast_timeperiod = db.Column(db.Integer, default=9, nullable=False)
    ema_slow_timeperiod = db.Column(db.Integer, default=21, nullable=False)
    psar_acceleration = db.Column(db.Float, default=0.02, nullable=False)
    psar_maximum = db.Column(db.Float, default=0.2, nullable=False)

    cci_buy = db.Column(db.Integer, default=-100, nullable=False)
    cci_sell = db.Column(db.Integer, default=100, nullable=False)
    rsi_buy = db.Column(db.Integer, default=30, nullable=False)
    rsi_sell = db.Column(db.Integer, default=70, nullable=False)
    mfi_buy = db.Column(db.Integer, default=30, nullable=False)
    mfi_sell = db.Column(db.Integer, default=70, nullable=False)
    stoch_buy = db.Column(db.Integer, default=20, nullable=False)
    stoch_sell = db.Column(db.Integer, default=80, nullable=False)
    atr_buy_treshold = db.Column(db.Float, default=0.005, nullable=False)

    avg_volume_period = db.Column(db.Integer, default=1, nullable=False)
    avg_close_period = db.Column(db.Integer, default=3, nullable=False)
    avg_adx_period = db.Column(db.Integer, default=7, nullable=False)
    avg_atr_period = db.Column(db.Integer, default=28, nullable=False)
    avg_di_period = db.Column(db.Integer, default=7, nullable=False)
    avg_rsi_period = db.Column(db.Integer, default=1, nullable=False)
    avg_stoch_rsi_period = db.Column(db.Integer, default=1, nullable=False)
    avg_macd_period = db.Column(db.Integer, default=1, nullable=False)
    avg_stoch_period = db.Column(db.Integer, default=1, nullable=False)
    avg_ema_period = db.Column(db.Integer, default=1, nullable=False)
    avg_cci_period = db.Column(db.Integer, default=1, nullable=False)
    avg_mfi_period = db.Column(db.Integer, default=1, nullable=False)
    avg_psar_period = db.Column(db.Integer, default=1, nullable=False)
    avg_vwap_period = db.Column(db.Integer, default=1, nullable=False)

    adx_strong_trend = db.Column(db.Integer, default=25, nullable=False)
    adx_weak_trend = db.Column(db.Integer, default=20, nullable=False)
    adx_no_trend = db.Column(db.Integer, default=5, nullable=False)

    ml_general_timeperiod = db.Column(db.Integer, default=14, nullable=False)
    ml_macd_timeperiod = db.Column(db.Integer, default=12, nullable=False)
    ml_macd_signalperiod = db.Column(db.Integer, default=9, nullable=False)
    ml_bollinger_timeperiod = db.Column(db.Integer, default=20, nullable=False)
    ml_bollinger_nbdev = db.Column(db.Integer, default=2, nullable=False)
    ml_ema_fast_timeperiod = db.Column(db.Integer, default=9, nullable=False)
    ml_ema_slow_timeperiod = db.Column(db.Integer, default=21, nullable=False)
    ml_rsi_buy = db.Column(db.Integer, default=30, nullable=False)
    ml_rsi_sell = db.Column(db.Integer, default=70, nullable=False)
    ml_lag_period = db.Column(db.Integer, default=7, nullable=False)

    ml_use_random_forest_model = db.Column(
        db.Boolean, default=True, nullable=False)
    ml_random_forest_model_filename = db.Column(
        db.String(128), default="model_btc_1h_random_forest.joblib", nullable=False)
    ml_random_forest_predictions_avg = db.Column(
        db.Integer, default=1, nullable=False)
    ml_random_forest_buy_trigger_pct = db.Column(
        db.Float, default=3, nullable=False)
    ml_random_forest_sell_trigger_pct = db.Column(
        db.Float, default=-2, nullable=False)

    ml_use_xgboost_model = db.Column(db.Boolean, default=True, nullable=False)
    ml_xgboost_model_filename = db.Column(
        db.String(128), default="model_btc_1h_xgboost.model", nullable=False)
    ml_xgboost_predictions_avg = db.Column(
        db.Integer, default=1, nullable=False)
    ml_xgboost_buy_trigger_pct = db.Column(db.Float, default=3, nullable=False)
    ml_xgboost_sell_trigger_pct = db.Column(
        db.Float, default=-2, nullable=False)

    ml_use_lstm_model = db.Column(db.Boolean, default=True, nullable=False)
    ml_lstm_window_size = db.Column(db.Integer, default=30, nullable=False)
    ml_lstm_window_lookback = db.Column(db.Integer, default=14, nullable=False)
    ml_lstm_model_filename = db.Column(
        db.String(128), default="model_btc_1h_lstm.keras", nullable=False)
    ml_lstm_predictions_avg = db.Column(db.Integer, default=1, nullable=False)
    ml_lstm_buy_trigger_pct = db.Column(db.Float, default=3, nullable=False)
    ml_lstm_sell_trigger_pct = db.Column(db.Float, default=-2, nullable=False)

    bot_current_trade = db.relationship(
        'BotCurrentTrade',
        uselist=False,
        back_populates='bot_settings',
        overlaps="settings"
    )

    bot_technical_analysis = db.relationship(
        'BotTechnicalAnalysis',
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

    plot_url = None

    def __repr__(self):
        """Return a string representation of the object."""
        return (f'{self.id} {self.symbol}')
