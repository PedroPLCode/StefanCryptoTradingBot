from flask import redirect, url_for, flash
from flask_login import current_user
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView

class MyAdmin(Admin):
    @expose('/')
    def index(self):
        if current_user.is_authenticated and current_user.admin_panel_access:
            return super().index()
        else:
            flash('Please log in to access the admin panel.', 'warning')
            return redirect(url_for('main.index'))
        
        
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.admin_panel_access

    def inaccessible_callback(self, name, **kwargs):
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('main.login'))
    
    
class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.admin_panel_access

    def inaccessible_callback(self, name, **kwargs):
        flash('You do not have access to this page.', 'danger')
        return redirect(url_for('main.login'))


class UserAdmin(AdminModelView):
    column_list = (
        'id', 
        'login', 
        'name', 
        'email', 
        'comment',
        'control_panel_access',
        'admin_panel_access', 
        'email_raports_receiver', 
        'email_trades_receiver',
        'account_suspended', 
        'login_errors', 
        'creation_date', 
        'last_login'
    )
    column_filters = (
        'login', 
        'name', 
        'email', 
        'control_panel_access', 
        'admin_panel_access', 
        'email_raports_receiver', 
        'account_suspended', 
        'login_errors'
    )
    form_excluded_columns = ('password_hash',)


class BotSettingsAdmin(AdminModelView):
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
        
        'use_technical_analysis',
        'use_machine_learning',
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
        'ml_stoch_k_timeperiod',
        'ml_stoch_d_timeperiod',
        'ml_stoch_rsi_k_timeperiod',
        'ml_stoch_rsi_d_timeperiod',
        'ml_ema_fast_timeperiod',
        'ml_ema_slow_timeperiod',
        'ml_psar_acceleration',
        'ml_psar_maximum',
        
        'ml_lag_min',
        'ml_lag_max',
        'ml_window_size',
        'ml_window_lookback',
        'ml_predictions_periods',
        
        'ml_use_regresion_on_next_7',
        'ml_model_7_filename',
        'ml_predictions_7_avg',
        'ml_buy_trigger_7_pct',
        'ml_sell_trigger_7_pct',
        
        'ml_use_regresion_on_next_14',
        'ml_model_14_filename',
        'ml_predictions_14_avg',
        'ml_buy_trigger_14_pct',
        'ml_sell_trigger_14_pct',
        
        'ml_use_regresion_on_next_28',
        'ml_model_28_filename',
        'ml_predictions_28_avg',
        'ml_buy_trigger_28_pct',
        'ml_sell_trigger_28_pct',
    )
    
    
class BacktestSettingsAdmin(AdminModelView):
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