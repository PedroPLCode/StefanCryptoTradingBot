from flask import flash, current_app
from flask_mail import Message
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import os
from .. import db
from app.models import User, TradesHistory, BotSettings, BotTechnicalAnalysis
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


def get_balance_for_symbol(account_status, cryptocoin_symbol):
    try:
        for balance in account_status:
            if balance['asset'] == cryptocoin_symbol:
                return balance['amount']
        return 0
    
    except Exception as e:
        logger.error(f"Exception in show_account_balance: {str(e)}")
        send_admin_email(f"Exception in show_account_balance", str(e))
        return 0
    

def calculate_profit_percentage(buy_price, sell_price):
    try:
        return ((sell_price - buy_price) / buy_price) * 100
    
    except Exception as e:
        logger.error(f"Exception in calculate_profit_percentage: {str(e)}")
        send_admin_email(f"Exception in calculate_profit_percentage", str(e))
        return 'unknown'


def send_logs_via_email_and_clear_logs():
    from ..utils.logging import logs

    for log in logs:
        log_file_path = os.path.join(os.getcwd(), log)
        now = datetime.now()
        formatted_now = now.strftime('%Y-%m-%d %H:%M:%S')
        today = now.strftime('%Y-%m-%d')
        subject = f"{today} Daily Logs"
        
        try:
            if os.path.exists(log_file_path):
                with open(log_file_path, 'r') as log_file:
                    log_content = log_file.read()
                    
                send_admin_email(
                    f"{subject}: {log}", 
                    f"StafanCryptoTradingBot daily logs.\n{formatted_now}\n\n{log}\n\n{log_content}"
                    )
                logger.info(f"Successfully sent email with log: {log}")
            else:
                logger.warning(f"Log file does not exist: {log_file_path}")
                
        except Exception as e:
            logger.error(f"Exception in send_logs_via_email_and_clear_logs log {log}: {str(e)}")
            send_admin_email(f"Exception in send_logs_via_email_and_clear_logs log {log}", str(e))
            
    clear_logs()


def clear_logs():
    from ..utils.logging import logs
    
    for log in logs:
        log_file_path = os.path.join(os.getcwd(), log)
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
        
        try:
            if os.path.exists(log_file_path):
                with open(log_file_path, 'w') as log_file:
                    log_file.write(
                        f'{timestamp} CLEAN: Log file {log_file_path} cleared succesfully.\n'
                        )
                logger.info(f"Successfully cleared log file: {log_file_path}")
            else:
                logger.warning(f"Log file does not exist: {log_file_path}")
                
        except Exception as e:
            logger.error(f"Exception in clear_logs log {log}: {str(e)}")
            send_admin_email(f"Exception in clear_logs log {log}", str(e))


def generate_trade_report(period):
    now = datetime.now()
    formatted_now = now.strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        if period == '24h':
            last_period = now - timedelta(hours=24)
        elif period == '7d':
            last_period = now - timedelta(days=7)
        else:
            raise ValueError("Unsupported period specified. Use '24h' or '7d'.")

        all_bots = BotSettings.query.all()
        
        report_data = (
            f"StafanCryptoTradingBot {'daily' if period == '24h' else 'requested'} trades report.\n"
            f"{formatted_now}\n\n"
            f"All trades in last {period}.\n\n"
        )

        for single_bot in all_bots:
            trades_in_period = (
                TradesHistory.query
                .filter(TradesHistory.bot_id == single_bot.id)
                .filter(TradesHistory.sell_timestamp >= last_period)
                .order_by(TradesHistory.sell_timestamp.asc())
                .all()
            )
            
            total_trades = len(trades_in_period)

            report_data += (
                f"--\n\nBot {single_bot.id} "
                f"{single_bot.strategy} {single_bot.symbol}.\n"
                f"comment: {single_bot.comment}\n"
            )
            
            if total_trades == 0:
                report_data += f"\nNo transactions in last {period}.\n\n"
            else:
                report_data += f"\nTransactions count in last {period}: {total_trades}\n\n"

                for trade in trades_in_period:
                    profit_percentage = calculate_profit_percentage(
                        trade.buy_price, 
                        trade.sell_price
                        )
                    report_data += (f"id: {trade.trade_id}\n"
                                    f"buy_timestamp: {trade.buy_timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
                                    f"sell_timestamp: {trade.sell_timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
                                    f"amount: {trade.amount} {trade.bot_settings.symbol[:3]}\n"
                                    f"buy_price: {trade.buy_price:.2f} {trade.bot_settings.symbol[-4:]}\n"
                                    f"sell_price: {trade.sell_price:.2f} {trade.bot_settings.symbol[-4:]}\n"
                                    f"stop_loss_price: {trade.stop_loss_price}\n"
                                    f"take_profit_price: {trade.take_profit_price}\n"
                                    f"price_rises_counter: {trade.price_rises_counter}\n"
                                    f"stop_loss_activated: {trade.stop_loss_activated}\n"
                                    f"take_profit_activated: {trade.take_profit_activated}\n"
                                    f"trailing_take_profit_activated: {trade.trailing_take_profit_activated}\n"
                                    f"profit_percentage: {profit_percentage:.2f}%\n\n")
        return report_data
    
    except Exception as e:
        logger.error(f"Exception in generate_trade_report period {period}: {str(e)}")
        send_admin_email(f"Exception in generate_trade_report period {period}", str(e))
    except ValueError as e:
        logger.error(f"ValueError in generate_trade_report period {period}: {str(e)}")
        send_admin_email(f"ValueError in generate_trade_report period {period}", str(e))


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
        logger.error(f"Exception in send_email subject: {subject} email: {email}: {str(e)}")
        send_admin_email(f"Exception in send_email subject: {subject} email: {email}", str(e))
        return False


def send_trade_report_via_email():
    try:
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        with current_app.app_context():
            users = User.query.filter_by(email_raports_receiver=True).all()
            report_body = generate_trade_report('24h')
            for user in users:
                success = send_email(user.email, f'{today} Daily Trades Report', report_body)
                if not success:
                    logger.error(f"Failed to send 24h report to {user.email}.")
                    
    except Exception as e:
        logger.error(f"Exception in send_trade_report_via_email email: {user.email}: {str(e)}")
        send_admin_email(f"Exception in send_trade_report_via_email email: {user.email}", str(e))


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
    now = datetime.now()
    formatted_now = now.strftime('%Y-%m-%d %H:%M:%S')
    today = now.strftime('%Y-%m-%d')
    
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
            
            period_to_clean = now - timedelta(days=days_to_clean_history)
            
            deleted_count = db.session.query(TradesHistory).filter(
                TradesHistory.bot_id == bot_settings.id,
                TradesHistory.sell_timestamp < period_to_clean
            ).delete(synchronize_session=False)
            
            log_message = ""
            days_count_string = f'{days_to_clean_history} day' if days_to_clean_history == 1 else f'{days_to_clean_history} days'
            if deleted_count > 0:
                log_message = (
                    f"Bot {bot_settings.id}: {deleted_count} trades "
                    f"older than {days_count_string} cleared succesfully."
                )
            else:
                log_message = (
                    f"Bot {bot_settings.id}: No trades older than "
                    f"{days_count_string} found. Nothing to clean."
                )
                
            logger.trade(log_message)
            summary_logs.append(log_message)

        db.session.commit()

        summary_message = (
            f"StafanCryptoTradingBot daily cleaning report.\n"
            f"{formatted_now}\n\nDays to clean history: {days_to_clean_history}\n\n"
        )
        error_message = (
            f"StafanCryptoTradingBot daily cleaning.\n"
            f"Errors during trade history cleaning.\n"
            f"{formatted_now}\n\n"
        )
        
        if summary_logs:
            summary_message += "\n".join(summary_logs)
            logger.trade("Trade history cleaning completed:\n" + summary_message)
            send_admin_email(f'{today} Daily Cleaning Report', summary_message)

        if errors:
            error_message += "\n".join(errors)
            logger.error("Errors during trade history cleaning:\n" + error_message)
            send_admin_email(f"{today} Errors in Daily Trade History Cleaning", error_message)
    
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
            send_admin_email(f'Bot {bot_settings.id} started.', f'Bot {bot_settings.id} has been started by {current_user.name}.\n\nSymbol: {bot_settings.symbol}\nStrategy: {bot_settings.strategy}\nLookback period: {bot_settings.lookback_period}\nInterval: {bot_settings.interval}\n\nComment: {bot_settings.comment}')
    
    except Exception as e:
        db.session.rollback()
        logger.error(f'Bot {bot_id} Exception in start_single_bot: {str(e)}')
        send_admin_email(f'Bot {bot_id} Exception in start_single_bot', str(e))
        

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
        logger.error(f'Bot {bot_id} Exception in stop_single_bot: {str(e)}')
        send_admin_email(f'Bot {bot_id} Exception in stop_single_bot', str(e))


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
                
                
def update_technical_analysis_data(bot_settings, df, trend, averages, latest_data):
    try:
        technical_analysis = BotTechnicalAnalysis.query.filter_by(id=bot_settings.id).first()
        
        technical_analysis.set_df(df)

        technical_analysis.current_trend = trend

        latest_data_fields = [
            'close', 'high', 'low', 'volume', 'rsi', 'cci', 'mfi', 'ema_fast', 'ema_slow',
            'macd', 'macd_signal', 'macd_histogram', 'upper_band', 'lower_band', 'stoch_k',
            'stoch_d', 'stoch_rsi', 'stoch_rsi_k', 'stoch_rsi_d', 'atr', 'psar', 'vwap',
            'adx', 'plus_di', 'minus_di'
        ]

        for field in latest_data_fields:
            setattr(technical_analysis, f"current_{field}", latest_data.get(field, 0))

        technical_analysis.current_ma_50 = latest_data['ma_50'] if bot_settings.ma50_signals else 0
        technical_analysis.current_ma_200 = latest_data['ma_200'] if bot_settings.ma200_signals else 0

        averages_fields = [
            'avg_close', 'avg_volume', 'avg_rsi', 'avg_cci', 'avg_mfi', 'avg_atr',
            'avg_stoch_rsi_k', 'avg_macd', 'avg_macd_signal', 'avg_stoch_k', 'avg_stoch_d',
            'avg_ema_fast', 'avg_ema_slow', 'avg_plus_di', 'avg_minus_di', 'avg_psar', 'avg_vwap'
        ]

        for field in averages_fields:
            setattr(technical_analysis, field, averages.get(field, 0))

        technical_analysis.last_updated_timestamp = datetime.now()

        db.session.commit()
        logger.trade(f'BotTechnicalAnalysis {technical_analysis.id}: bot: {bot_settings.id} updated in database.')

    except Exception as e:
        db.session.rollback()
        logger.error(f"Bot {bot_settings.id} Exception in update_technical_analysis_data: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in update_technical_analysis_data', str(e))