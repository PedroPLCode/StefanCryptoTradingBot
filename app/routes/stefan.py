from flask import redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from ..models import BotSettings, BacktestSettings
from datetime import datetime
from ..utils.logging import logger
from . import main
from ..stefan.logic_utils import execute_sell_order
from ..utils.app_utils import (
    send_email, 
    send_admin_email,
    generate_trade_report,
    stop_all_bots, 
    start_all_bots, 
    start_single_bot, 
    stop_single_bot
)

@main.route('/start/<int:bot_id>')
@login_required
def start_bot(bot_id):
    if not current_user.control_panel_access:
        logger.warning(f'{current_user.login} tried to control Bot without permission.')
        flash(f'Error. User {current_user.login} is not allowed to control the Bot.', 'danger')
        return redirect(url_for('main.user_panel_view'))

    try:
        bot_settings = BotSettings.query.filter_by(id=bot_id).first()

        if bot_settings:
            start_single_bot(bot_settings.id, current_user)
        else:
            flash(f'Settings for bot {bot_id} not found.', 'danger')
            send_admin_email('Bot not started.', f'Settings for bot {bot_id} not found.')

        return redirect(url_for('main.control_panel_view'))

    except Exception as e:
        logger.error(f'Bot {bot_id} Exception in start_bot: {str(e)}')
        flash(f'Error while starting bot {bot_id}.', 'danger')
        send_admin_email(f'Bot {bot_id} Exception in start_bot', str(e))
        return redirect(url_for('main.control_panel_view'))


@main.route('/stop/<int:bot_id>')
@login_required
def stop_bot(bot_id):
    if not current_user.control_panel_access:
        logger.warning(f'{current_user.login} tried to control Bot without permission.')
        flash(f'Error. User {current_user.login} is not allowed to control the Bot.', 'danger')
        return redirect(url_for('main.user_panel_view'))
    
    try:
        bot_settings = BotSettings.query.filter_by(id=bot_id).first()
        
        if bot_settings.bot_current_trade.is_active:
            execute_sell_order(bot_settings, 
                               bot_settings.bot_current_trade, 
                               bot_settings.bot_current_trade.current_price, 
                               False, 
                               False
                               )
            send_admin_email(f'Bot {bot_settings.id} stopped manually.', f'Bot {bot_id} has been stopped manually with active CurrentTrade.\nCheck CurrentTrade in Flask Admin Panel.\nCurrentTrade needs to be deactivated and all params needs to be set on 0.')
        
        if bot_settings:
            stop_single_bot(bot_settings.id, current_user)
        else:
            flash(f'Settings for bot {bot_id} not found.', 'danger')
            send_admin_email('Bot not stopped.', f'Settings for bot {bot_id} not found.')

        return redirect(url_for('main.control_panel_view'))

    except Exception as e:
        logger.error(f'Bot {bot_id} Exception in stop_bot: {str(e)}')
        flash(f'An error occurred while stopping bot {bot_id}.', 'danger')
        send_admin_email(f'Bot {bot_id} Exception in stop_bot', str(e))
        return redirect(url_for('main.control_panel_view'))
    

@main.route('/startall')
@login_required
def start_all():
    if not current_user.control_panel_access:
        logger.warning(f'{current_user.login} tried to control Bot without permission.')
        flash(f'Error. User {current_user.login} is not allowed to control the Bot.', 'danger')
        return redirect(url_for('main.user_panel_view'))
    
    try:
        start_all_bots(current_user)
        return redirect(url_for('main.control_panel_view'))

    except Exception as e:
        logger.error(f'Exception in start_all: {str(e)}')
        flash(f'An error occured while starting bots.', 'danger')
        send_admin_email(f'Exception in start_all', str(e))
        return redirect(url_for('main.control_panel_view'))
    
    
@main.route('/stopall')
@login_required
def stop_all():
    if not current_user.control_panel_access:
        logger.warning(f'{current_user.login} tried to control Bot without permission.')
        flash(f'Error. User {current_user.login} is not allowed to control the Bot.', 'danger')
        return redirect(url_for('main.user_panel_view'))
    
    try:
        stop_all_bots(current_user)
        return redirect(url_for('main.control_panel_view'))

    except Exception as e:
        logger.error(f'Exception in stop_all: {str(e)}')
        flash(f'An error occurred while stopping bots.', 'danger')
        send_admin_email(f'Exception in stop_all.', str(e))
        return redirect(url_for('main.control_panel_view'))


@main.route('/refresh')
@login_required
def refresh():
    if not current_user.control_panel_access:
        logger.warning(f'{current_user.login} tried to Refresh control panel without permission.')
        flash(f'Error. User {current_user.login} is not allowed to control Bot.', 'danger')
        return redirect(url_for('main.user_panel_view'))
    
    try:
        flash('Binance API refreshed.', 'success')
        return redirect(url_for('main.control_panel_view'))

    except Exception as e:
        logger.error(f'Exception in refresh: {str(e)}')
        send_admin_email('Exception in refresh', str(e))
        flash('An error occurred while refreshing the Binance API. The admin has been notified.', 'danger')
        return redirect(url_for('main.control_panel_view'))


@main.route('/report')
@login_required
def report():
    if not current_user.email_raports_receiver:
        logger.warning(f'{current_user.login} tried to get email rapirt without permission.')
        flash(f'Error. User {current_user.login} is not allowed receiving email raports.', 'danger')
        return redirect(url_for('main.user_panel_view'))
    
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')
    email = current_user.email
    subject = f'{today} Stefan Trades Report'
    report_body = generate_trade_report('7d')
    
    try:
        with current_app.app_context():
            send_email(email, subject, report_body)
            flash(f'Email to {email} sent successfully.', 'success')
    except Exception as e:
        logger.error(f'Exception in report email: {email}: {str(e)}')
        flash('An error occurred while sending the email. The admin has been notified.', 'danger')
        send_admin_email(f'Exception in report email: {email}', str(e))
    
    return redirect(url_for('main.control_panel_view'))


@main.route('/load_data_for_backtest')
@login_required
def fetch_and_save_data_for_backtest():
    from ..stefan.backtesting import fetch_and_save_data
    if not current_user.control_panel_access:
        logger.warning(f'{current_user.login} tried to Load data for backtest control panel without permission.')
        flash(f'Error. User {current_user.login} is not allowed to control Bot.', 'danger')
        return redirect(url_for('main.user_panel_view'))
    
    try:
        backtest_settings = BacktestSettings.query.first()
        bot_settings = BotSettings.query.filter(BotSettings.id == backtest_settings.bot_id).first()
        if bot_settings:
            fetch_and_save_data(backtest_settings, bot_settings)
            flash(f'Data for backtest {bot_settings.symbol} fetched and saved in {backtest_settings.csv_file_path}.', 'success')
        else:
            flash(f'Bot {backtest_settings.bot_id} not found. Data not loaded', 'danger')
        return redirect(url_for('main.backtest_panel_view'))

    except Exception as e:
        logger.error(f'Exception in fetch_and_save_data_for_backtest: {str(e)}')
        send_admin_email('Exception in fetch_and_save_data_for_backtest', str(e))
        flash('An error occurred while Loading data for backtest. The admin has been notified.', 'danger')
        return redirect(url_for('main.backtest_panel_view'))
    

@main.route('/run_backtest')
@login_required
def run_backtest():
    from ..stefan.backtesting import backtest_strategy
    from ..stefan.logic_utils import is_df_valid
    if not current_user.control_panel_access:
        logger.warning(f'{current_user.login} tried to run backtest control panel without permission.')
        flash(f'Error. User {current_user.login} is not allowed to control Bot.', 'danger')
        return redirect(url_for('main.user_panel_view'))
    
    try:
        backtest_settings = BacktestSettings.query.first()
        bot_settings = BotSettings.query.filter(BotSettings.id == backtest_settings.bot_id).first()
        if bot_settings:
            df = pd.read_csv(backtest_settings.csv_file_path)
            if is_df_valid(df, bot_settings.id):
                df['time'] = pd.to_datetime(df['close_time'])
                backtest_strategy(df, bot_settings, backtest_settings)
                flash('Backtest completed. Read log file', 'success')
            else:
                flash('Backtest error. Dataframe empty or too short', 'danger')
        else:
            flash(f'Bot {backtest_settings.bot_id} not found. Cant run backtest', 'danger')
        return redirect(url_for('main.backtest_panel_view'))

    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in run_backtest: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in run_backtest', str(e))
        flash('An error occurred while running backtest. The admin has been notified.', 'danger')
        return redirect(url_for('main.backtest_panel_view'))
    
    
@main.route('/get_df/', methods=['GET'])
@login_required
def get_df():
    
    try:
        all_bots_info = BotSettings.query.all()
        if not all_bots_info:
            return jsonify({"error": f"Bots not found"}), 404
        
        all_bots_df = [bot.bot_technical_analysis.df for bot in all_bots_info]

        return jsonify({"all_bots_df": all_bots_df}), 200

    except SQLAlchemyError as e:
        logger.error(f"Database error get_bots_info: {str(e)}")
        send_admin_email(f"Database error get_bots_info", str(e))
        return jsonify({"error": "Internal Server Error"}), 500

    except Exception as e:
        logger.error(f'Exception in get_bots_info: {str(e)}')
        send_admin_email(f'Exception in get_bots_info', str(e))
        flash('An error occurred while sending df. The admin has been notified.', 'danger')
        return jsonify({"error": "Internal Server Error"}), 500