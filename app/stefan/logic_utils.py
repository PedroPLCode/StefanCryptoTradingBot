import talib
import pandas as pd
from .. import db
from ..models import TradesHistory
from ..utils.logging import logger
from ..utils.app_utils import send_admin_email

def calculate_indicators(df, bot_settings):
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df['high'] = pd.to_numeric(df['high'], errors='coerce')
    df['low'] = pd.to_numeric(df['low'], errors='coerce')
    df['volume'] = pd.to_numeric(df['volume'], errors='coerce')

    df['rsi'] = talib.RSI(df['close'], timeperiod=bot_settings.timeperiod)
    df['macd'], df['macd_signal'], _ = talib.MACD(
        df['close'], 
        fastperiod=bot_settings.timeperiod,
        slowperiod=2 * bot_settings.timeperiod, 
        signalperiod=1
    )
    df['upper_band'], df['middle_band'], df['lower_band'] = talib.BBANDS(
        df['close'], 
        timeperiod=bot_settings.timeperiod, 
        nbdevup=2, 
        nbdevdn=2, 
        matype=0
    )
    df['cci'] = talib.CCI(
        df['high'], 
        df['low'], 
        df['close'], 
        timeperiod=bot_settings.timeperiod
    )
    df['mfi'] = talib.MFI(
        df['high'], 
        df['low'], 
        df['close'], 
        df['volume'], 
        timeperiod=bot_settings.timeperiod
    )
    df['ma_200'] = talib.SMA(df['close'], timeperiod=200)

    df.dropna(inplace=True)
    return df


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
    try:
        current_price = float(current_price)
        trailing_stop_price = float(trailing_stop_price)
        atr = float(atr)

        dynamic_trailing_stop = max(
            trailing_stop_price, 
            current_price * (1 - (0.5 * atr / current_price))
        )
        minimal_trailing_stop = current_price * 0.98

        return max(dynamic_trailing_stop, minimal_trailing_stop)

    except ValueError as e:
        logger.error(f"Invalid value for price or ATR: {e}")
        return trailing_stop_price


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
            algorithm=current_trade.bot_settings.algorithm,
            amount=amount, 
            buy_price=buy_price,
            sell_price=sell_price
        )
        db.session.add(trade)
        db.session.commit()
        logger.info(
            f'Transaction {trade.id}: bot: {current_trade.id} {order_type}, algorithm: {current_trade.bot_settings.algorithm}'
            f'amount: {amount}, symbol: {current_trade.bot_settings.symbol}, timestamp: {trade.timestamp}'
        )
    except Exception as e:
        db.session.rollback()
        logger.error(f'Błąd podczas dodawania transakcji do historii: {str(e)}')
        send_admin_email("Błąd podczas dodawania transakcji do historii", str(e))