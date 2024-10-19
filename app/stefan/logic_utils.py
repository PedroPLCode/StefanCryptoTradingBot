import talib
from .. import db
from ..models import TradesHistory
from ..utils.logging import logger
from ..utils.app_utils import send_admin_email

def calculate_indicators(df):
    df['rsi'] = talib.RSI(df['close'], timeperiod=5)
    df['macd'], df['macd_signal'], _ = talib.MACD(
        df['close'], 
        fastperiod=5,
        slowperiod=10, 
        signalperiod=5
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
    df['ma_200'] = talib.SMA(df['close'], timeperiod=200)
    df.dropna(inplace=True)


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