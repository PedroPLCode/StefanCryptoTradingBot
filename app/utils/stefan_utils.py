# TESTS NEEDED
import talib
from .. import db
from ..models import TradesHistory, CurrentTrade
from .logging import logger

def calculate_indicators(df):
    df['rsi'] = talib.RSI(df['close'], timeperiod=14)
    df['macd'], df['macd_signal'], _ = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
    df['upper_band'], df['middle_band'], df['lower_band'] = talib.BBANDS(df['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
    df['cci'] = talib.CCI(df['high'], df['low'], df['close'], timeperiod=20)
    df['slowk'], df['slowd'] = talib.STOCH(df['high'], df['low'], df['close'], fastk_period=14, slowk_period=3, slowd_period=3)
    df.dropna(inplace=True)


def check_signals(df):
    latest_data = df.iloc[-1]
    if latest_data['rsi'] < 30 and latest_data['macd'] > latest_data['macd_signal'] and latest_data['cci'] < -100:
        return 'buy'
    elif latest_data['rsi'] > 70 and latest_data['macd'] < latest_data['macd_signal'] and latest_data['cci'] > 100:
        return 'sell'
    return None


def save_trade(order_type, amount, price):
    trade = CurrentTrade(type=order_type, amount=amount, price=price)
    db.session.add(trade)
    db.session.commit()
    
    
def delete_trade():
    db.session.query(CurrentTrade).delete()
    db.session.commit()


def load_current_trade():
    return CurrentTrade.query.first() or None


def update_trailing_stop_loss(current_price, trailing_stop_price, atr):
    dynamic_trailing_stop = max(trailing_stop_price, current_price * (1 - (0.5 * atr / current_price)))
    return float(dynamic_trailing_stop)


def save_trailing_stop_loss(trailing_stop_price):
    current_trade = load_current_trade()
    if current_trade:
        current_trade.trailing_stop_loss = trailing_stop_price
        db.session.commit()
        

def save_trade_to_history(order_type, amount, price):
    try:
        trade = TradesHistory(type=order_type, amount=amount, price=price)
        db.session.add(trade)
        db.session.commit()
        logger.info(f'Transaction {trade.id}: {order_type}, amount: {amount}, price: {price}, timestamp: {trade.timestamp}')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Błąd podczas dodawania transakcji do historii: {str(e)}')
    

def clear_trade_history_db():
    try:
        db.session.query(TradesHistory).delete()
        db.session.commit()
        logger.info("All trade history cleared successfully.")
    except Exception as e:
        logger.error(f"Error clearing trade history: {str(e)}")
        db.session.rollback()
