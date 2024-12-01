from datetime import datetime, timedelta
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from flask_mail import Message
from app.models import User, TradesHistory, BotSettings
from werkzeug.security import generate_password_hash
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
                'value': (float(single['free']) + float(single['locked'])) * float(asset_price),
                'price': float(asset_price)
            }
            for single in account_status['balances']
            if single['asset'] in assets_to_include
        ]
        return account_balance
    
    except Exception as e:
        logger.error(f"Exception in show_account_balance: {str(e)}")
        send_admin_email(f"Exception in show_account_balance", str(e))
        return False


def calculate_profit_percentage(buy_price, sell_price):
    try:
        return ((sell_price - buy_price) / buy_price) * 100
    except Exception as e:
        logger.error(f"Exception in calculate_profit_percentage: {str(e)}")
        send_admin_email(f"Exception in calculate_profit_percentage", str(e))
        return 'unknown'
    

def create_balance_plot(df):
    try:
        if df.empty or df['stablecoin_balance'].isnull().all():
            logger.warning("create_balance_plot: No data available in the DataFrame to plot.")
            return None 

        fig, ax = plt.subplots(figsize=(14, 6))

        color_increase = '#2ca02c'  # Green
        color_decrease = '#d62728'  # Red

        for i in range(1, len(df)):
            x_values = [df['trade_id'].iloc[i - 1], df['trade_id'].iloc[i]]
            y_values = [df['stablecoin_balance'].iloc[i - 1], df['stablecoin_balance'].iloc[i]]
            
            color = color_increase if y_values[1] > y_values[0] else color_decrease
            ax.plot(x_values, y_values, marker='o', color=color, linestyle='-', linewidth=4)

        df['moving_avg'] = df['stablecoin_balance'].rolling(window=5).mean()
        ax.plot(df['trade_id'], df['moving_avg'], color='blue', linestyle='--', linewidth=4)

        ax.grid(True)
        ax.legend()

        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)

        img = BytesIO()
        fig.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        plt.close(fig)
        
        plot_url = base64.b64encode(img.getvalue()).decode('utf8')
        return plot_url

    except Exception as e:
        logger.error(f"Exception in create_balance_plot: {str(e)}")
        send_admin_email("Exception in create_balance_plot", str(e))
        return None


def send_logs_via_email_and_clear_logs():
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
                    
                send_admin_email(f"{subject}: {log}", log_content)
                logger.info(f"Successfully sent email with log: {log}")
            else:
                logger.warning(f"Log file does not exist: {log_file_path}")
        except Exception as e:
            logger.error(f"Exception in send_logs_via_email log {log}: {str(e)}")
            send_admin_email(f"Exception in send_logs_via_email log {log}", str(e))
    clear_logs()


def clear_logs():
    from ..utils.logging import logs
    
    for log in logs:
        log_file_path = os.path.join(os.getcwd(), log)
        
        try:
            if os.path.exists(log_file_path):
                with open(log_file_path, 'w') as log_file:
                    log_file.write('Log file cleared.\n')
                logger.info(f"Successfully cleared log file: {log_file_path}")
            else:
                logger.warning(f"Log file does not exist: {log_file_path}")
        except Exception as e:
            logger.error(f"Exception in clear_logs log {log}: {str(e)}")
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
        
        report_data = f"{period} Report: Date {now.strftime('%Y-%m-%d')}\n\n"

        for single_bot in all_bots:
            trades_in_period = (
                TradesHistory.query
                .filter(TradesHistory.bot_id == single_bot.id)
                .filter(TradesHistory.sell_timestamp >= last_period)
                .order_by(TradesHistory.sell_timestamp.asc())
                .all()
            )
            
            total_trades = len(trades_in_period)

            if total_trades == 0:
                report_data += f"No transactions in last {period} for bot {single_bot.id} {single_bot.strategy}.\n"
            else:
                report_data += f"Bot {single_bot.id} {single_bot.strategy.upper()}\nTransactions count in last {period}: {total_trades}\n\n"

                for trade in trades_in_period:
                    profit_percentage = calculate_profit_percentage(trade.buy_price, trade.sell_price)
                    report_data += (f"id: {trade.id} {trade.bot_settings.symbol} {trade.bot_settings.strategy.upper()}\nbuy_timestamp: {trade.buy_timestamp.strftime('%Y-%m-%d %H:%M:%S')}\nsell_timestamp: {trade.sell_timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
                                    f"amount: {trade.amount} {trade.bot_settings.symbol[:3]}\nbuy_price: {trade.buy_price:.2f} {trade.bot_settings.symbol[-4:]}\nsell_price: {trade.sell_price:.2f} {trade.bot_settings.symbol[-4:]}\n"
                                    f"price_rises_counter: {trade.price_rises_counter}\nprofit_percentage: {profit_percentage:.2f}%\n")

        return report_data
    
    except Exception as e:
        logger.error(f"Exception in generate_trade_report log period {period}: {str(e)}")
        send_admin_email(f"Exception in generate_trade_report log period {period}", str(e))
    except ValueError as e:
        logger.error(f"ValueError in generate_trade_report log period {period}: {str(e)}")
        send_admin_email(f"ValueError in generate_trade_report log period {period}", str(e))


def send_email(email, subject, body):
    from app import mail
    try:
        with current_app.app_context():
            message = Message(subject=subject, recipients=[email])
            message.body = body
            mail.send(message)
            logger.info(f'Email "{subject}" to {email} sent succesfully.')
            return True
    except Exception as e:
        logger.error(f"Exception in send_email subject {subject} email {email}: {str(e)}")
        send_admin_email(f"Exception in send_email subject {subject} email {email}", str(e))
        return False


def send_trade_report_via_email():
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
        logger.error(f"Exception in send_trade_report_via_email email {user.email}: {str(e)}")
        send_admin_email(f"Exception in send_trade_report_via_email email {user.email}", str(e))


def send_admin_email(subject, body):
    try:
        with current_app.app_context():
            users = User.query.filter_by(admin_panel_access=True).all()
            for user in users:
                success = send_email(user.email, subject, body)
                if not success:
                    logger.error(f"Failed to send admin email to {user.email}. {subject} {body}")
    except Exception as e:
        logger.error(f"Exception in send_admin_email: {str(e)}")
        

def send_trade_email(subject, body):
    try:
        with current_app.app_context():
            users = User.query.filter_by(email_trades_receiver=True).all()
            for user in users:
                success = send_email(user.email, subject, body)
                if not success:
                    logger.error(f"Failed to send trade info email to {user.email}. {subject} {body}")
    except Exception as e:
        logger.error(f"Exception in send_trade_email: {str(e)}")


def clear_old_trade_history():
    try:
        all_bot_settings = BotSettings.query.all()
        errors = []
        summary_logs = []
        
        for bot_settings in all_bot_settings:
            days_to_clean_history = bot_settings.days_period_to_clean_history
            
            if not days_to_clean_history or not isinstance(days_to_clean_history, int) or days_to_clean_history <= 0:
                error_message = (
                    f"Bot {bot_settings.id} has invalid 'days_period_to_clean_history': {days_to_clean_history}"
                )
                logger.warning(error_message)
                errors.append(error_message)
                continue
            
            period_to_clean = datetime.now() - timedelta(days=days_to_clean_history)
            
            deleted_count = db.session.query(TradesHistory).filter(
                TradesHistory.bot_id == bot_settings.id,
                TradesHistory.sell_timestamp < period_to_clean
            ).delete(synchronize_session=False)
            
            log_message = (
                f"Bot {bot_settings.id}: {deleted_count} trades older than {days_to_clean_history} days cleared succesfully."
            )
            logger.trade(log_message)
            summary_logs.append(log_message)

        db.session.commit()

        if summary_logs:
            summary_message = "\n".join(summary_logs)
            logger.trade("Trade history cleaning completed:\n" + summary_message)
            send_admin_email("Trade History Cleaning Summary", summary_message)

        if errors:
            error_message = "\n".join(errors)
            logger.error("Errors during trade history cleaning:\n" + error_message)
            send_admin_email("Errors in Trade History Cleaning", error_message)
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Exception in clear_old_trade_history: {str(e)}")
        send_admin_email("Exception in clear_old_trade_history", str(e))


def start_single_bot(bot_id, current_user):
    try:
        bot_settings = BotSettings.query.get(bot_id)
        if bot_settings.bot_running:
            flash(f'Bot {bot_settings.id} is already running.', 'info')
        else:
            bot_settings.bot_running = True
            db.session.commit()
            logger.trade(f'Bot {bot_settings.id} {bot_settings.symbol} {bot_settings.strategy} has been started.')
            flash(f'Bot {bot_settings.id} has been started.', 'success')
            send_admin_email(f'Bot {bot_settings.id} started.', f'Bot {bot_settings.id} {bot_settings.symbol} {bot_settings.strategy} has been started by {current_user.login}.\nComment: {bot_settings.comment}')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Exception in start_single_bot bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in start_single_bot bot {bot_settings.id}', str(e))
        

def stop_single_bot(bot_id, current_user):
    try:
        bot_settings = BotSettings.query.get(bot_id)
        if not bot_settings.bot_running:
            flash(f'Bot {bot_settings.id} is already stopped.', 'info')
        else:
            bot_settings.bot_running = False
            db.session.commit()
            logger.trade(f'Bot {bot_settings.id} {bot_settings.symbol} {bot_settings.strategy} has been stopped.')
            flash(f'Bot {bot_settings.id} has been stopped.', 'success')
            send_admin_email(f'Bot {bot_settings.id} stopped.', f'Bot {bot_settings.id} {bot_settings.symbol} {bot_settings.strategy} has been stopped by {current_user.login if current_user.login else current_user}.')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Exception in stop_single_bot bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in stop_single_bot bot {bot_settings.id}', str(e))


def stop_all_bots(current_user):
    all_bots_settings = BotSettings.query.all()
    with current_app.app_context():
        for bot_settings in all_bots_settings:
            try:
                bot_id = bot_settings.id
                if bot_settings.bot_current_trade.is_active:
                    place_sell_order(bot_id)
                stop_single_bot(bot_id, current_user)
            except Exception as e:
                logger.error(f'Exception in stop_all_bots: {str(e)}')
                send_admin_email('Exception in stop_all_bots', str(e))
            

def start_all_bots(current_user='undefined'):
    all_bots_settings = BotSettings.query.all()
    with current_app.app_context():
        for bot_settings in all_bots_settings:
            try:
                bot_id = bot_settings.id
                start_single_bot(bot_id, current_user)         
            except Exception as e:
                logger.error(f'Exception in start_all_bots: {str(e)}')
                send_admin_email('Exception in start_all_bots', str(e))