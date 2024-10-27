from datetime import datetime, timedelta
import os
from flask_mail import Message
from app.models import User, TradesHistory, BotSettings
from werkzeug.security import generate_password_hash
import logging
from flask import flash, current_app
from .. import db
from .logging import logger
from ..stefan.api_utils import (
    place_sell_order,
    fetch_current_price
)

def get_ip_address(request):
    try:
        if 'X-Forwarded-For' in request.headers:
            return request.headers['X-Forwarded-For'].split(',')[0]
        return request.remote_addr
    except Exception as e:
        logger.error(f"Exception in get_ip_address: {str(e)}")
        send_admin_email('Exception in get_ip_address', str(e))
        return 'unknown'


def create_new_user(form):
    try:
        new_user = User(
            login=form.login.data,
            name=form.name.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
        )
        return new_user
    except Exception as e:
        logger.error(f"Exception in create_new_user: {str(e)}")
        send_admin_email('Exception in create_new_user', str(e))
        raise


def show_account_balance(symbol, account_status, assets_to_include):
    if not account_status or 'balances' not in account_status:
        return False
    
    try:

        asset_price = fetch_current_price(symbol)
        
        account_balance = [
            {
                'asset': single['asset'],
                'amount': float(single['free']) + float(single['locked']),
                'value': (float(single['free']) + float(single['locked'])) * float(asset_price)
            }
            for single in account_status['balances']
            if single['asset'] in assets_to_include
        ]
        return account_balance
    
    except Exception as e:
        logger.error(f"Exception in show_account_balance: {str(e)}")
        send_admin_email(f"Exception in show_account_balance", str(e))


def calculate_profit_percentage(buy_price, sell_price):
    try:
        return ((sell_price - buy_price) / buy_price) * 100
    except Exception as e:
        logger.error(f"Exception in calculate_profit_percentage: {str(e)}")
        send_admin_email(f"Exception in calculate_profit_percentage", str(e))
        return 'unknown'


def send_logs_via_email():
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')
    subject = f"{today} Daily Stefan Logs"
    from ..utils.logging import logs

    for log in logs:
        log_file_path = os.path.join(os.getcwd(), log)
        
        try:
            if os.path.exists(log_file_path):
                with open(log_file_path, 'r') as log_file:
                    log_content = log_file.read()
                    
                send_admin_email(f"{subject + log} - {log}", log_content)
                logging.info(f"Successfully sent email with log: {log}")
            else:
                logging.warning(f"Log file does not exist: {log_file_path}")
        except Exception as e:
            logging.error(f"Exception in send_logs_via_email log {log}: {str(e)}")
            send_admin_email(f"Exception in send_logs_via_email log {log}", str(e))


def clear_logs():
    from ..utils.logging import logs
    
    for log in logs:
        log_file_path = os.path.join(os.getcwd(), log)
        
        try:
            if os.path.exists(log_file_path):
                with open(log_file_path, 'w') as log_file:
                    log_file.write('Log file cleared.')
                logging.info(f"Successfully cleared log file: {log_file_path}")
            else:
                logging.warning(f"Log file does not exist: {log_file_path}")
        except Exception as e:
            logging.error(f"Exception in clear_logs log {log}: {str(e)}")
            send_admin_email(f"Exception in clear_logs log {log}", str(e))


def generate_trade_report(period):
    now = datetime.now()
    
    try:

        if period == '24h':
            last_period = now - timedelta(hours=24)
        elif period == '7d':
            last_period = now - timedelta(days=7)
        else:
            raise ValueError("Unsupported period specified. Use '24h' or '7d'.")

        all_bots = BotSettings.query.all()
        
        report_data = f"{period} Raport: Date {now.strftime('%Y-%m-%d')}\n\n"

        for single_bot in all_bots:
            trades_in_period = (
                single_bot.bot_trades_history
                .filter(TradesHistory.timestamp >= last_period)
                .order_by(TradesHistory.timestamp.asc())
                .all()
            )
            
            total_trades = len(trades_in_period)

            if total_trades == 0:
                report_data += f"No transactions in last {period} bot {trade.bot_id} {trade.bot_settings.strategy}.\n"
            else:
                report_data += f"Transactions count in last {period} bot {trade.bot_id} {trade.bot_settings.strategy}: {total_trades}\n\n"

                for trade in trades_in_period:
                    profit_percentage = calculate_profit_percentage(trade.buy_price, trade.sell_price)
                    report_data += (f"id: {trade.id}, bot_id: {trade.bot_id} {trade.bot_settings.strategy}, {trade.type} {trade.bot_settings.symbol}, "
                                    f"amount: {trade.amount} {trade.bot_settings.symbol[:3]}, buy_price: {trade.buy_price:.2f} {trade.bot_settings.symbol[-4:]}, "
                                    f"sell_price: {trade.sell_price:.2f} {trade.bot_settings.symbol[-4:]}, profit_percentage: {profit_percentage:.2f}%, "
                                    f"timestamp: {trade.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")

        return report_data
    
    except Exception as e:
        logging.error(f"Exception in generate_trade_report log period {period}: {str(e)}")
        send_admin_email(f"Exception in generate_trade_report log period {period}", str(e))
    except ValueError as e:
        logging.error(f"ValueError in generate_trade_report log period {period}: {str(e)}")
        send_admin_email(f"ValueError in generate_trade_report log period {period}", str(e))


def send_email(email, subject, body):
    from app import mail
    try:
        with current_app.app_context():
            message = Message(subject=subject, recipients=[email])
            message.body = body
            mail.send(message)
            logger.info(f'Email "{subject}" sent to {email}.')
            return True
    except Exception as e:
        logger.error(f"Exception in send_email subject {subject} email {email}: {str(e)}")
        send_admin_email(f"Exception in send_email subject {subject} email {email}", str(e))
        return False


def send_report_via_email():
    try:
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        with current_app.app_context():
            users = User.query.filter_by(email_raports_receiver=True).all()
            report_body = generate_trade_report('24h')
            for user in users:
                success = send_email(user.email, f'{today} Daily Stefan Trades', report_body)
                if not success:
                    logger.error(f"Failed to send 24h report to {user.email}.")
    except Exception as e:
        logger.error(f"Exception in send_report_via_email email {user.email}: {str(e)}")
        send_admin_email(f"Exception in send_report_via_email email {user.email}", str(e))


def send_admin_email(subject, body):
    try:
        with current_app.app_context():
            users = User.query.filter_by(admin_panel_access=True).all()
            for user in users:
                success = send_email(user.email, subject, body)
                if not success:
                    logger.error(f"Failed to send email to {user.email}. {subject} {body}")
    except Exception as e:
        logger.error(f"Exception in send_admin_email: {str(e)}")


def clear_old_trade_history():
    try:
        one_month_ago = datetime.now() - timedelta(days=30)
        db.session.query(TradesHistory).filter(
            TradesHistory.timestamp < one_month_ago
        ).delete()
        db.session.commit()
        logger.info("Trade history older than one month cleared successfully.")
    except Exception as e:
        logger.error(f"Exception in clear_old_trade_history: {str(e)}")
        send_admin_email(f"Exception in clear_old_trade_history", str(e))
        db.session.rollback()


def start_single_bot(bot_settings, current_user):
    try:
        if bot_settings.bot_running:
            flash(f'Bot {bot_settings.id} is already running.', 'info')
        else:
            bot_settings.bot_running = True
            db.session.commit()
            flash(f'Bot {bot_settings.id} has been started.', 'success')
            send_admin_email('Bot started.', f'Bot {bot_settings.id} has been started by {current_user.login}.')
    except Exception as e:
        logger.error(f'Exception in start_single_bot bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in start_single_bot bot {bot_settings.id}', str(e))
        

def stop_single_bot(bot_settings, current_user):
    try:
        if not bot_settings.bot_running:
            flash(f'Bot {bot_settings.id} is already stopped.', 'info')
        else:
            bot_settings.bot_running = False
            db.session.commit()
            flash(f'Bot {bot_settings.id} has been stopped.', 'success')
            send_admin_email('Bot stopped.', f'Bot {bot_settings.id} has been stopped by {current_user.login if current_user.login else current_user}.')
    except Exception as e:
        logger.error(f'Exception in stop_single_bot bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in stop_single_bot bot {bot_settings.id}', str(e))


def stop_all_bots(current_user):
    all_bots_settings = BotSettings.query.all()
    with current_app.app_context():
        for bot_settings in all_bots_settings:
            try:
                if bot_settings.bot_current_trade.is_active:
                    place_sell_order(bot_settings)
                stop_single_bot(bot_settings, current_user)
            except Exception as e:
                logger.error(f'Exception in stop_all_bots: {str(e)}')
                send_admin_email('Exception in stop_all_bots', str(e))
            

def start_all_bots(current_user='undefined'):
    all_bots_settings = BotSettings.query.all()
    with current_app.app_context():
        for bot_settings in all_bots_settings:
            try:
                start_single_bot(bot_settings, current_user)         
            except Exception as e:
                logger.error(f'Exception in start_all_bots: {str(e)}')
                send_admin_email('Exception in start_all_bots', str(e))