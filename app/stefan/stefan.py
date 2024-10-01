import time
import numpy as np
import pandas as pd
import logging
from binance.client import Client
import talib
from ..utils.api_utils import fetch_data, place_order, get_account_balance
from ..utils.app_utils import send_email
from .. import db
from ..models import Settings

# Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
symbol = 'BTCUSDT'
stop_loss_pct = 0.02  # 2% stop-loss
trailing_stop_pct = 0.01  # 1% trailing stop
take_profit_pct = 0.03  # 3% take profit
lookback_days = '30 days'  # Length of historical data

def calculate_indicators(df):
    df['rsi'] = talib.RSI(df['close'], timeperiod=14)
    df['macd'], df['macd_signal'], _ = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
    df['upper_band'], df['middle_band'], df['lower_band'] = talib.BBANDS(
        df['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    df['sma'] = talib.SMA(df['close'], timeperiod=50)
    df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
    df['stoch'] = talib.STOCHF(df['high'], df['low'], df['close'], fastk_period=14)[0]
    df.dropna(inplace=True)

def check_signals(df):
    latest_data = df.iloc[-1]
    # Simple signal logic based on indicators
    if latest_data['rsi'] < 30:  # Example buy condition
        return 'buy'
    elif latest_data['rsi'] > 70:  # Example sell condition
        return 'sell'
    return None

def update_trailing_stop_loss(current_price, trailing_stop_price, atr):
    return max(trailing_stop_price, current_price * (1 - (trailing_stop_pct * (atr / current_price))))

def backtest_strategy(df):
    df['signal'] = np.where(df['close'].shift(-1) > df['close'], 1, 0)
    df['strategy_returns'] = df['signal'].shift(1) * (df['close'].pct_change())
    df['cumulative_strategy_returns'] = (1 + df['strategy_returns']).cumprod()
    return df

# Main loop
trailing_stop_price = None
take_profit_price = None

while True:
    try:
        settings = Settings.query.first()
        if settings:
            symbol = settings.symbol
            stop_loss_pct = settings.stop_loss_pct
            trailing_stop_pct = settings.trailing_stop_pct
            take_profit_pct = settings.take_profit_pct
            lookback_days = settings.lookback_days

            if not settings.bot_running:
                time.sleep(60)
                continue

        df = fetch_data(symbol, lookback=lookback_days)
        calculate_indicators(df)

        df_backtest = backtest_strategy(df)
        logging.info(f"Cumulative Strategy Returns: {df_backtest['cumulative_strategy_returns'].iloc[-1]}")

        signal = check_signals(df)
        current_price = df['close'].iloc[-1]
        atr = df['atr'].iloc[-1]

        account_balance = get_account_balance()
        amount = account_balance['USDC']

        if signal == 'buy':
            place_order(symbol, 'buy', amount / current_price)
            logging.info(f'Bought {amount / current_price} BTC')
            trailing_stop_price = current_price * (1 - trailing_stop_pct)
            take_profit_price = current_price * (1 + take_profit_pct)

        elif signal == 'sell' and trailing_stop_price is not None:
            place_order(symbol, 'sell', amount / current_price)
            logging.info(f'Sold {amount / current_price} BTC')
            trailing_stop_price = None
            take_profit_price = None

        if take_profit_price is not None and current_price >= take_profit_price:
            place_order(symbol, 'sell', amount / current_price)
            logging.info(f'Take Profit triggered: Sold {amount / current_price} BTC at {current_price}')
            take_profit_price = None

        if trailing_stop_price is not None:
            trailing_stop_price = update_trailing_stop_loss(current_price, trailing_stop_price, atr)

        time.sleep(300)  # Wait for 5 minutes before the next cycle

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        # Send an email with the error details
        send_email('piotrek.gaszczynski@gmail.com', 'Trading Bot Error', f'An error occurred: {e}')
        break  # You can decide to continue or break the loop