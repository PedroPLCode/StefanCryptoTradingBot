from datetime import datetime, timedelta
import os
from flask_mail import Message
from app.models import User, TradesHistory, BotSettings
from flask import current_app
from werkzeug.security import generate_password_hash
import logging
from ..utils.logging import logger

def get_ip_address(request):
    if 'X-Forwarded-For' in request.headers:
        return request.headers['X-Forwarded-For'].split(',')[0]
    return request.remote_addr


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
        logger.error(f'Error creating user: {e}')
        send_admin_email('User Creation Error', str(e))
        raise


def calculate_profit_percentage(buy_price, sell_price):
    return ((sell_price - buy_price) / buy_price) * 100


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
            logging.error(f"Error while sending email for log {log}: {str(e)}")
            send_admin_email(f"Error while sending email for log {log}", str(e))


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
            logging.error(f"Error while clearing log file {log}: {str(e)}")
            send_admin_email(f"Error while clearing log file {log}", str(e))


def generate_trade_report(period):
    now = datetime.now()

    if period == '24h':
        last_period = now - timedelta(hours=24)
    elif period == '7d':
        last_period = now - timedelta(days=7)
    else:
        raise ValueError("Unsupported period specified. Use '24h' or '7d'.")

    all_bots = BotSettings.query.all()
    
    report_data = f"Raport okresowy Dnia: {now.strftime('%Y-%m-%d')}\n\n"

    for single_bot in all_bots:
        trades_in_period = (
            single_bot.bot_trades_history
            .filter(TradesHistory.timestamp >= last_period)
            .order_by(TradesHistory.timestamp.asc())
            .all()
        )
        
        total_trades = len(trades_in_period)

        if total_trades == 0:
            report_data += f"Brak transakcji w ciągu ostatnich {period} dla bot_id: {trade.bot_id} {trade.bot_settings.algorithm}.\n"
        else:
            report_data += f"Liczba transakcji w ciągu ostatnich {period} dla bot_id: {trade.bot_id} {trade.bot_settings.algorithm}: {total_trades}\n\n"

            for trade in trades_in_period:
                profit_percentage = calculate_profit_percentage(trade.buy_price, trade.sell_price)
                report_data += (f"id: {trade.id}, bot_id: {trade.bot_id} {trade.bot_settings.algorithm}, {trade.type} {trade.bot_settings.symbol}, "
                                f"amount: {trade.amount} {trade.bot_settings.symbol[:3]}, buy_price: {trade.buy_price:.2f} {trade.bot_settings.symbol[-4:]}, "
                                f"sell_price: {trade.sell_price:.2f} {trade.bot_settings.symbol[-4:]}, profit_percentage: {profit_percentage:.2f}%, "
                                f"timestamp: {trade.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")

    return report_data


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
        logger.error(f'Failed to send email "{subject}" to {email}: {str(e)}')
        return False


def send_report_via_email():
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')
    with current_app.app_context():
        users = User.query.filter_by(email_raports_receiver=True).all()
        report_body = generate_trade_report('24h')
        for user in users:
            success = send_email(user.email, f'{today} Daily Stefan Trades', report_body)
            if not success:
                logger.error(f"Failed to send 24h report to {user.email}.")


def send_admin_email(subject, body):
    with current_app.app_context():
        users = User.query.filter_by(admin_panel_access=True).all()
        for user in users:
            success = send_email(user.email, subject, body)
            if not success:
                logger.error(f"Failed to send email to {user.email}. {subject} {body}")


def show_account_balance(account_status, assets_to_include):
    if not account_status or 'balances' not in account_status:
        return False

    account_balance = [
        {
            'asset': single['asset'],
            'free': float(single['free']),
            'locked': float(single['locked']),
        }
        for single in account_status['balances']
        if single['asset'] in assets_to_include
    ]
    return account_balance