from flask import render_template, redirect, url_for, flash, request, session
from flask_login import current_user
import json
import pandas as pd
from ..models import BotSettings, BacktestResult
from .. import db
from ..utils.logging import logger
from . import main
from ..stefan.api_utils import (
    fetch_system_status, 
    fetch_account_status, 
    fetch_server_time
)
from ..utils.app_utils import (
    show_account_balance, 
    send_admin_email
)

@main.route('/')
def user_panel_view():
    if current_user.is_authenticated:
        try:
            binance_status = fetch_system_status()
            account_status = fetch_account_status()
            server_time = fetch_server_time()
            return render_template(
                'user_panel.html',
                user=current_user, 
                account_status=account_status, 
                binance_status=binance_status, 
                server_time=server_time
            )
            
        except Exception as e:
            logger.error(f'Exception in user_panel_view: {str(e)}')
            send_admin_email('Exception in user_panel_view', str(e))
            flash('An error occurred while fetching account data. Please try again later.', 'danger')
            return redirect(url_for('main.login'))
    else:
        flash('Please log in to access the app.', 'warning')
        return redirect(url_for('main.login'))

    
@main.route('/control')
def control_panel_view():
    if not current_user.is_authenticated:
        flash('Please log in to access the control panel.', 'warning')
        return redirect(url_for('main.login'))

    if not current_user.control_panel_access:
        logger.warning(f'{current_user.login} tried to access the Control Panel without permission.')
        flash(f'Error. User {current_user.login} is not allowed to access the Control Panel.', 'danger')
        return redirect(url_for('main.user_panel_view'))

    try:
        all_bots_settings = BotSettings.query.all()
        
        for bot_info in all_bots_settings:
            account_status = fetch_account_status(bot_info.id)
            cryptocoin_symbol = bot_info.symbol[:3]
            stablecoin_symbol = bot_info.symbol[-4:]
            balance = show_account_balance(
                bot_info.symbol,
                account_status, 
                {cryptocoin_symbol, stablecoin_symbol})
            bot_info.balance = balance

        return render_template(
            'control_panel.html', 
            user=current_user, 
            all_bots_settings=all_bots_settings, 
        )

    except Exception as e:
        logger.error(f'Exception in control_panel_view: {str(e)}')
        send_admin_email('Exception in control_panel_view', str(e))
        flash('An error occurred while loading the control panel. The admin has been notified.', 'danger')
        return redirect(url_for('main.user_panel_view'))
    
    
@main.route('/analysis', methods=['GET', 'POST'])
def analysis_panel_view():
    from ..utils.plot_utils import plot_all_indicators
    
    if not current_user.is_authenticated:
        flash('Please log in to access the technical analysis panel.', 'warning')
        return redirect(url_for('main.login'))

    if not current_user.control_panel_access:
        logger.warning(f'{current_user.login} tried to access the Technical Analysis Panel without permission.')
        flash(f'Error. User {current_user.login} is not allowed to access the Technical Analysis Panel.', 'danger')
        return redirect(url_for('main.user_panel_view'))

    try:
        all_bots_info = BotSettings.query.all()

        for bot_info in all_bots_info:
            
            indicators = bot_info.selected_plot_indicators or ['rsi', 'macd']
            
            if request.method == 'POST':
                bot_id = request.form.get('bot_id')
                if str(bot_id) == str(bot_info.id):
                    indicators = request.form.getlist('indicators')
                    bot_info.selected_plot_indicators = indicators
                    db.session.commit()

            technical_analysis_data = bot_info.bot_technical_analysis
            df = technical_analysis_data.get_df()
            
            if df.empty:
                logger.warning(f'Bot {bot_info.symbol} returned an empty DataFrame.')
                bot_info.plot_url = None
                continue
            
            bot_info.plot_url = plot_all_indicators(
                df, 
                indicators,
                bot_info,
                bot_info.lookback_period
                )

        return render_template(
            'technical_analysis.html', 
            user=current_user, 
            all_bots_info=all_bots_info,
            selected_indicators=indicators
        )

    except Exception as e:
        logger.error(f'Exception in analysis_panel_view: {str(e)}')
        send_admin_email('Exception in analysis_panel_view', str(e))
        flash('An error occurred while loading the technical analysis panel. The admin has been notified.', 'danger')
        return redirect(url_for('main.user_panel_view'))
    
    
@main.route('/backtest')
def backtest_panel_view():
    if not current_user.is_authenticated:
        flash('Please log in to access the backtest panel.', 'warning')
        return redirect(url_for('main.login'))

    if not current_user.control_panel_access:
        logger.warning(f'{current_user.login} tried to access the backtest Panel without permission.')
        flash(f'Error. User {current_user.login} is not allowed to access the backtest Panel.', 'danger')
        return redirect(url_for('main.user_panel_view'))

    try:
        all_backtest_results = BacktestResult.query.all()
        for result in all_backtest_results:
            result.trade_log = json.loads(result.trade_log)

        return render_template(
            'backtest_panel.html', 
            user=current_user, 
            all_backtest_results=all_backtest_results,
        )

    except Exception as e:
        logger.error(f'Exception in backtest_panel_view: {str(e)}')
        send_admin_email('Exception in backtest_panel_view', str(e))
        flash('An error occurred while loading the control panel. The admin has been notified.', 'danger')
        return redirect(url_for('main.user_panel_view'))
    
    
@main.route('/trades')
def current_trades_view():
    from ..utils.plot_utils import create_balance_plot

    if not current_user.is_authenticated:
        flash('Please log in to access the trades panel.', 'warning')
        return redirect(url_for('main.login'))

    if not current_user.control_panel_access:
        logger.warning(f'{current_user.login} tried to access the Trades Panel without permission.')
        flash(f'Error. User {current_user.login} is not allowed to access the Trades Panel.', 'danger')
        return redirect(url_for('main.user_panel_view'))

    try:
        all_bots = BotSettings.query.all()

        for bot in all_bots:
            valid_trades = [trade for trade in bot.bot_trades_history if trade.stablecoin_balance]
            if valid_trades:
                bot.transaction_data = {
                    'trade_id': [trade.trade_id for trade in valid_trades],
                    'stablecoin_balance': [trade.stablecoin_balance for trade in valid_trades]
                }
                df = pd.DataFrame(bot.transaction_data)
                if not df.empty and df['stablecoin_balance'].sum() > 0:
                    bot.plot_url = create_balance_plot(df)
                else:
                    bot.plot_url = None
            else:
                bot.plot_url = None

        return render_template(
            'trades_history.html', 
            user=current_user, 
            all_bots=all_bots
        )

    except Exception as e:
        logger.error(f'Exception in current_trades_view: {str(e)}')
        send_admin_email('Exception in current_trades_view', str(e))
        flash('An error occurred while loading the trades panel. The admin has been notified.', 'danger')
        return redirect(url_for('main.user_panel_view'))


@main.route('/admin')
def admin_panel_view():
    if not current_user.is_authenticated:
        flash('Please log in to access the admin panel.', 'warning')
        return redirect(url_for('main.login'))

    if not current_user.admin_panel_access:
        logger.warning(f'{current_user.login} tried to access the Admin Panel without permission.')
        flash(f'Error. User {current_user.login} is not allowed to access the Admin Panel.', 'danger')
        return redirect(url_for('main.user_panel_view'))

    try:
        return redirect(url_for('admin.index'))

    except Exception as e:
        logger.error(f'Exception in admin_panel_view: {str(e)}')
        send_admin_email('Exception in admin_panel_view', str(e))
        flash('An error occurred while accessing the admin panel. The admin has been notified.', 'danger')
        return redirect(url_for('main.user_panel_view'))