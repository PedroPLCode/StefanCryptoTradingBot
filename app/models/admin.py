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
        'algorithm',
        'comment',
        'trailing_stop_pct', 
        'sell_signal_only_trailing_stop',
        'trailing_stop_with_atr',
        'trailing_stop_atr_calc',
        'cci_buy',
        'cci_sell',
        'rsi_buy',
        'rsi_sell',
        'mfi_buy',
        'mfi_sell',
        'stoch_buy',
        'stoch_sell',
        'avg_calc_period',
        'timeperiod',
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
        'algorithm',
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
        'trailing_stop_loss',
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
        'price_rises_counter',
        'buy_timestamp',
        'sell_timestamp',
    )