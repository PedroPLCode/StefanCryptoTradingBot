from flask import flash, current_app
import talib
from datetime import datetime, timedelta
from .. import db
from ..models import BotSettings, TradesHistory, BotCurrentTrade
from .logging import logger
from ..utils.app_utils import send_admin_email
from ..utils.api_utils import place_sell_order

#dostosować
def calculate_indicators(df):
    df['rsi'] = talib.RSI(df['close'], timeperiod=3)
    df['macd'], df['macd_signal'], _ = talib.MACD(
        df['close'], 
        fastperiod=3, 
        slowperiod=10, 
        signalperiod=3
    )
    df['upper_band'], df['middle_band'], df['lower_band'] = talib.BBANDS(
        df['close'], 
        timeperiod=10, 
        nbdevup=2, 
        nbdevdn=2, 
        matype=0
    )
    df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=5)
    df['cci'] = talib.CCI(df['high'], df['low'], df['close'], timeperiod=5)
    df['slowk'], df['slowd'] = talib.STOCH(
        df['high'], 
        df['low'], 
        df['close'], 
        fastk_period=5, 
        slowk_period=3, 
        slowd_period=3
    )
    df['vwap'] = (df['volume'] * df['close']).cumsum() / df['volume'].cumsum()
    df['adx'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=10)
    df.dropna(inplace=True)

#dostosować
def check_buy_signal(df):
    latest_data = df.iloc[-1]
    mfi = talib.MFI(df['high'], df['low'], df['close'], df['volume'], timeperiod=3)
    
    if (latest_data['rsi'] < 35 and
        latest_data['macd'] > latest_data['macd_signal'] and 
        latest_data['cci'] < -50 and
        mfi.iloc[-1] < 30 and
        latest_data['close'] < latest_data['lower_band']):
        return True
    return False

#dostosować
def check_sell_signal(df):
    latest_data = df.iloc[-1]
    mfi = talib.MFI(df['high'], df['low'], df['close'], df['volume'], timeperiod=3)
    
    if (latest_data['rsi'] > 65 and
        latest_data['macd'] < latest_data['macd_signal'] and 
        latest_data['cci'] > 50 and
        mfi.iloc[-1] > 70 and
        latest_data['close'] > latest_data['upper_band']):
        return True
    return False


def save_active_trade(current_trade, amount, price, buy_price):
    current_trade.is_active = True
    current_trade.amount = amount
    current_trade.price = price
    current_trade.buy_price = buy_price
    db.session.commit()


def save_deactivated_trade(current_trade):
    current_trade.is_active = False
    current_trade.amount = None
    current_trade.buy_price = None
    current_trade.price = None
    current_trade.previous_price = None
    current_trade.trailing_stop_loss = None
    db.session.commit()


def update_trailing_stop_loss(current_price, trailing_stop_price, atr):
    dynamic_trailing_stop = max(
        trailing_stop_price, 
        current_price * (1 - (0.5 * atr / current_price))
    )
    minimal_trailing_stop = current_price * 0.98
    return max(dynamic_trailing_stop, minimal_trailing_stop)


def save_trailing_stop_loss(trailing_stop_price, current_trade):
    if current_trade:
        current_trade.trailing_stop_loss = trailing_stop_price
        db.session.commit()


def save_previous_price(price, current_trade):
    if current_trade:
        current_trade.previous_price = price
        db.session.commit()


def save_trade_to_history(current_trade, order_type, amount, buy_price, sell_price):
    try:
        trade = TradesHistory(
            bot_id=current_trade.id, 
            amount=amount, 
            buy_price=buy_price,
            sell_price=sell_price
        )
        db.session.add(trade)
        db.session.commit()
        logger.info(
            f'Transaction {trade.id}: bot: {current_trade.id} {order_type}, '
            f'amount: {amount}, symbol: {current_trade.bot_settings.symbol}, timestamp: {trade.timestamp}'
        )
    except Exception as e:
        db.session.rollback()
        logger.error(f'Błąd podczas dodawania transakcji do historii: {str(e)}')


def clear_old_trade_history():
    try:
        one_month_ago = datetime.now() - timedelta(days=30)
        db.session.query(TradesHistory).filter(
            TradesHistory.timestamp < one_month_ago
        ).delete()
        db.session.commit()
        logger.info("Trade history older than one month cleared successfully.")
    except Exception as e:
        logger.error(f"Error clearing old trade history: {str(e)}")
        db.session.rollback()


def start_single_bot(bot_settings, current_user):
    if bot_settings.bot_running:
        flash(f'Bot {bot_settings.id} is already running.', 'info')
    else:
        bot_settings.bot_running = True
        db.session.commit()
        flash(f'Bot {bot_settings.id} has been started.', 'success')
        send_admin_email('Bot started.', f'Bot {bot_settings.id} has been started by {current_user.login}.')


def stop_single_bot(bot_settings, current_user):
    if not bot_settings.bot_running:
        flash(f'Bot {bot_settings.id} is already stopped.', 'info')
    else:
        bot_settings.bot_running = False
        db.session.commit()
        flash(f'Bot {bot_settings.id} has been stopped.', 'success')
        send_admin_email('Bot stopped.', f'Bot {bot_settings.id} has been stopped by {current_user.login if current_user.login else current_user}.')


def stop_all_bots(current_user):
    all_bots_settings = BotSettings.query.all()
    
    with current_app.app_context():
        for bot_settings in all_bots_settings:
            try:
                
                if bot_settings.bot_current_trade.is_active:
                    place_sell_order(bot_settings)
            
                stop_single_bot(bot_settings, current_user)
                
            except Exception as e:
                logger.error(f'Błąd podczas rozruchu botów: {str(e)}')
                send_admin_email('Błąd podczas rozruchu botów', str(e))
            

def start_all_bots(current_user='undefined'):
    all_bots_settings = BotSettings.query.all()
        
    with current_app.app_context():
        for bot_settings in all_bots_settings:
            try:
                start_single_bot(bot_settings, current_user)         
            except Exception as e:
                logger.error(f'Błąd podczas rozruchu botów: {str(e)}')
                send_admin_email('Błąd podczas rozruchu botów', str(e))