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
        'bot_running', 
        'symbol', 
        'strategy',
        'comment',
        'trend_signals',
        'rsi_signals',
        'vol_signals',
        'macd_cross_signals',
        'macd_histogram_signals',
        'boilinger_signals',
        'stoch_signals',
        'stoch_rsi_signals',
        'ema_cross_signals',
        'ema_fast_signals',
        'ema_slow_signals',
        'di_signals',
        'cci_signals',
        'mfi_signals',
        'atr_signals',
        'vmap_signals',
        'psar_signals',
        'ma50_signals',
        'ma200_signals',
        'use_stop_loss',
        'use_trailing_stop_loss',
        'stop_loss_pct', 
        'trailing_stop_with_atr',
        'trailing_stop_atr_calc',
        'use_take_profit',
        'take_profit_pct',
        'take_profit_with_atr',
        'take_profit_atr_calc',
        'sell_signal_only_stop_loss_or_take_profit',
        'cci_buy',
        'cci_sell',
        'rsi_buy',
        'rsi_sell',
        'mfi_buy',
        'mfi_sell',
        'stoch_buy',
        'stoch_sell',
        'atr_treshold',
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
        'avg_vmap_period',
        'adx_strong_trend',
        'adx_weak_trend',
        'adx_no_trend',
        'general_timeperiod',
        'di_timeperiod',
        'adx_timeperiod',
        'rsi_timeperiod',
        'atr_timeperiod',
        'cci_timeperiod',
        'mfi_timeperiod',
        'macd_timeperiod',
        'macd_signalperiod',
        'boilinger_timeperiod',
        'boilinger_nbdev',
        'stoch_k_timeperiod',
        'stoch_d_timeperiod',
        'stoch_rsi_timeperiod',
        'stoch_rsi_k_timeperiod',
        'stoch_rsi_d_timeperiod',
        'ema_fast_timeperiod',
        'ema_slow_timeperiod',
        'psar_acceleration',
        'psar_maximum',
        'interval', 
        'lookback_period', 
        'capital_utilization_pct',
        'days_period_to_clean_history',
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
        'amount', 
        'current_price', 
        'buy_price',
        'previous_price', 
        'stop_loss_price',
        'take_profit_price',
        'price_rises_counter',
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
        'buy_timestamp',
        'sell_timestamp',
    )