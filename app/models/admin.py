from flask import redirect, url_for, flash
from flask_login import current_user
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView


class MyAdmin(Admin):
    """
    Custom Admin class for managing access to the admin panel.

    Allows access to the admin panel only for authenticated users with admin panel access.
    Redirects unauthenticated or unauthorized users with a flash message.
    """
    @expose('/')
    def index(self):
        """
        The home page of the admin panel.

        If the user is authenticated and has admin panel access, it renders the default index view.
        Otherwise, it redirects the user to the main index page with a warning message.
        """
        if current_user.is_authenticated and current_user.admin_panel_access:
            return super().index()
        else:
            flash('Please log in to access the admin panel.', 'warning')
            return redirect(url_for('main.index'))


class MyAdminIndexView(AdminIndexView):
    """
    Custom view for the admin index page.

    Restricts access to the admin index page to authenticated users with admin panel access.
    """

    def is_accessible(self):
        """
        Check if the current user has access to the admin index page.

        Returns True if the user is authenticated and has admin panel access.
        """
        return current_user.is_authenticated and current_user.admin_panel_access

    def inaccessible_callback(self, name, **kwargs):
        """
        Redirect unauthenticated or unauthorized users to the login page with a flash message.
        """
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('main.login'))


class AdminModelView(ModelView):
    """
    Base model view for managing database models in the admin panel.

    Provides access control for viewing and editing model data.
    """

    def is_accessible(self):
        """
        Check if the current user has access to the model view.

        Returns True if the user is authenticated and has admin panel access.
        """
        return current_user.is_authenticated and current_user.admin_panel_access

    def inaccessible_callback(self, name, **kwargs):
        """
        Redirect unauthenticated or unauthorized users to the login page with a flash message.
        """
        flash('You do not have access to this page.', 'danger')
        return redirect(url_for('main.login'))


class UserAdmin(AdminModelView):
    """
    Admin view for managing user data.

    Allows viewing and editing user details such as login, email, access permissions, and more.
    """
    column_list = (
        'id',
        'login',
        'name',
        'email',
        'telegram_chat_id',
        'comment',
        'control_panel_access',
        'admin_panel_access',
        'email_raports_receiver',
        'email_trades_receiver',
        'telegram_trades_receiver',
        'account_suspended',
        'login_errors',
        'creation_date',
        'last_login'
    )
    column_filters = (
        'login',
        'name',
        'email',
        'telegram_chat_id',
        'control_panel_access',
        'admin_panel_access',
        'email_raports_receiver',
        'telegram_trades_receiver',
        'account_suspended',
        'login_errors'
    )
    form_excluded_columns = ('password_hash',)


class BotSettingsAdmin(AdminModelView):
    """
    Admin view for managing bot settings.

    Allows configuring bot strategies, technical analysis settings, stop-loss and take-profit parameters,
    and more.
    """
    column_list = (
        'id',
        'bot_current_trade',
        'bot_technical_analysis',
        'bot_running',
        'symbol',
        'interval',
        'lookback_period',
        'strategy',
        'comment',
        'capital_utilization_pct',
        'days_period_to_clean_history',
        'selected_plot_indicators',
        'use_suspension_after_negative_trade',
        'is_suspended_after_negative_trade',
        'cycles_of_suspension_after_negative_trade',
        'suspension_cycles_remaining',
        'use_technical_analysis',
        'use_machine_learning',
        'use_gpt_analysis',
        'sell_signal_only_stop_loss_or_take_profit',
        'use_stop_loss',
        'use_trailing_stop_loss',
        'stop_loss_pct',
        'trailing_stop_with_atr',
        'trailing_stop_atr_calc',
        'use_take_profit',
        'use_trailing_take_profit',
        'take_profit_pct',
        'take_profit_with_atr',
        'take_profit_atr_calc',
        'trend_signals',
        'rsi_signals',
        'rsi_divergence_signals',
        'vol_signals',
        'macd_cross_signals',
        'macd_histogram_signals',
        'bollinger_signals',
        'stoch_signals',
        'stoch_divergence_signals',
        'stoch_rsi_signals',
        'ema_cross_signals',
        'ema_fast_signals',
        'ema_slow_signals',
        'di_signals',
        'cci_signals',
        'cci_divergence_signals',
        'mfi_signals',
        'mfi_divergence_signals',
        'atr_signals',
        'vwap_signals',
        'psar_signals',
        'ma50_signals',
        'ma200_signals',
        'ma_cross_signals',
        'cci_buy',
        'cci_sell',
        'rsi_buy',
        'rsi_sell',
        'mfi_buy',
        'mfi_sell',
        'stoch_buy',
        'stoch_sell',
        'atr_buy_treshold',
        'general_timeperiod',
        'di_timeperiod',
        'adx_timeperiod',
        'rsi_timeperiod',
        'atr_timeperiod',
        'cci_timeperiod',
        'mfi_timeperiod',
        'macd_timeperiod',
        'macd_signalperiod',
        'bollinger_timeperiod',
        'bollinger_nbdev',
        'stoch_k_timeperiod',
        'stoch_d_timeperiod',
        'stoch_rsi_timeperiod',
        'stoch_rsi_k_timeperiod',
        'stoch_rsi_d_timeperiod',
        'ema_fast_timeperiod',
        'ema_slow_timeperiod',
        'psar_acceleration',
        'psar_maximum',
        'avg_close_period',
        'avg_volume_period',
        'avg_adx_period',
        'avg_atr_period',
        'avg_di_period',
        'avg_rsi_period',
        'avg_macd_period',
        'avg_stoch_period',
        'avg_ema_period',
        'avg_cci_period',
        'avg_mfi_period',
        'avg_stoch_rsi_period',
        'avg_psar_period',
        'avg_vwap_period',
        'adx_strong_trend',
        'adx_weak_trend',
        'adx_no_trend',
        'ml_general_timeperiod',
        'ml_macd_timeperiod',
        'ml_macd_signalperiod',
        'ml_bollinger_timeperiod',
        'ml_bollinger_nbdev',
        'ml_ema_fast_timeperiod',
        'ml_ema_slow_timeperiod',
        'ml_rsi_buy',
        'ml_rsi_sell',
        'ml_lag_period',
        'ml_use_random_forest_model',
        'ml_random_forest_model_filename',
        'ml_random_forest_predictions_avg',
        'ml_random_forest_buy_trigger_pct',
        'ml_random_forest_sell_trigger_pct',
        'ml_use_xgboost_model',
        'ml_xgboost_model_filename',
        'ml_xgboost_predictions_avg',
        'ml_xgboost_buy_trigger_pct',
        'ml_xgboost_sell_trigger_pct',
        'ml_use_lstm_model',
        'ml_lstm_window_size',
        'ml_lstm_window_lookback',
        'ml_lstm_model_filename',
        'ml_lstm_predictions_avg',
        'ml_lstm_buy_trigger_pct',
        'ml_lstm_sell_trigger_pct',
        'gpt_model',
        'gpt_prompt_with_news',
        'news_limit_per_source',
        'news_total_limit',
        'gpt_prompt_with_last_trades',
        'last_trades_limit',
        'etop_passwd',
    )


class BacktestSettingsAdmin(AdminModelView):
    """
    Admin view for managing backtest settings.

    Allows configuring backtesting parameters such as date range, initial balance, and more.
    """
    column_list = (
        'id',
        'bot_id',
        'start_date',
        'end_date',
        'csv_file_path',
        'initial_balance',
        'crypto_balance',
    )


class BacktestResultsAdmin(AdminModelView):
    """
    Admin view for managing backtest results.

    Displays results such as profit, final balance, and other backtest metrics.
    """
    column_list = (
        'id',
        'bot_id',
        'symbol',
        'strategy',
        'start_date',
        'end_date',
        'initial_balance',
        'final_balance',
        'profit',
    )


class BotCurrentTradeAdmin(AdminModelView):
    """
    Admin view for managing the current trade of the bot.

    Displays information about the active trade, such as buy price, stop-loss price, and more.
    """
    column_list = (
        'id',
        'bot_settings',
        'is_active',
        'trailing_take_profit_activated',
        'amount',
        'current_price',
        'buy_price',
        'previous_price',
        'stop_loss_price',
        'take_profit_price',
        'price_rises_counter',
        'use_take_profit',
        'buy_timestamp',
    )


class TradesHistoryAdmin(AdminModelView):
    """
    Admin view for managing the history of trades.

    Allows viewing trade details such as amount, buy and sell prices, and timestamps.
    """
    column_list = (
        'id',
        'bot_id',
        'strategy',
        'amount',
        'buy_price',
        'sell_price',
        'stablecoin_balance',
        'stop_loss_price',
        'take_profit_price',
        'price_rises_counter',
        'stop_loss_activated',
        'take_profit_activated',
        'trailing_take_profit_activated',
        'buy_timestamp',
        'sell_timestamp',
    )


class BotTechnicalAnalysisAdmin(AdminModelView):
    """
    Admin view for managing the bot's technical analysis data.

    Displays various indicators like RSI, MACD, ATR, and more.
    """
    column_list = (
        'id',
        'bot_settings',
        'current_trend',
        'current_close',
        'current_high',
        'current_low',
        'current_volume',
        'current_rsi',
        'current_cci',
        'current_mfi',
        'current_ema_fast',
        'current_ema_slow',
        'current_macd',
        'current_macd_signal',
        'current_macd_histogram',
        'current_ma_50',
        'current_ma_200',
        'current_upper_band',
        'current_lower_band',
        'current_stoch_k',
        'current_stoch_d',
        'current_stoch_rsi',
        'current_stoch_rsi_k',
        'current_stoch_rsi_d',
        'current_atr',
        'current_psar',
        'current_vwap',
        'current_adx',
        'current_plus_di',
        'current_minus_di',
        'avg_close',
        'avg_volume',
        'avg_rsi',
        'avg_cci',
        'avg_mfi',
        'avg_atr',
        'avg_stoch_rsi_k',
        'avg_macd',
        'avg_macd_signal',
        'avg_stoch_k',
        'avg_stoch_d',
        'avg_ema_fast',
        'avg_ema_slow',
        'avg_plus_di',
        'avg_minus_di',
        'avg_psar',
        'avg_vwap',
        'last_updated_timestamp'
    )
