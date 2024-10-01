import time
from flask import current_app
import numpy as np
import pandas as pd
import logging
from binance.client import Client
from ..utils.api_utils import fetch_data, place_order, get_account_balance
from ..utils.app_utils import send_email
from .. import db
from ..models import Settings

# Initial Configuration
symbol = 'BTCUSDT'
stop_loss_pct = 0.005  # 0.5% stop-loss for scalping
trailing_stop_pct = 0.01  # 1% trailing stop
take_profit_pct = 0.01  # 1% take profit for scalping
lookback_days = '30 days'  # Length of historical data

def calculate_indicators(df):
    """Calculate technical indicators for the given DataFrame."""
    delta = df['close'].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()

    df['sma_5'] = df['close'].rolling(window=5).mean()  # Short-term SMA
    df['sma_15'] = df['close'].rolling(window=15).mean()  # Medium-term SMA

    df['sma'] = df['close'].rolling(window=20).mean()
    df['std'] = df['close'].rolling(window=20).std()
    df['upper_band'] = df['sma'] + (df['std'] * 2)
    df['lower_band'] = df['sma'] - (df['std'] * 2)

    df['high_low'] = df['high'] - df['low']
    df['high_close'] = (df['high'] - df['close'].shift()).abs()
    df['low_close'] = (df['low'] - df['close'].shift()).abs()
    df['tr'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
    df['atr'] = df['tr'].rolling(window=14).mean()

    lowest_low = df['low'].rolling(window=14).min()
    highest_high = df['high'].rolling(window=14).max()
    df['stoch'] = 100 * ((df['close'] - lowest_low) / (highest_high - lowest_low))

    df.dropna(inplace=True)

def check_signals(df):
    """Check for trading signals based on RSI and SMAs."""
    latest_data = df.iloc[-1]
    if latest_data['rsi'] < 30 and latest_data['sma_5'] > latest_data['sma_15']:
        return 'buy'
    elif latest_data['rsi'] > 70 and latest_data['sma_5'] < latest_data['sma_15']:
        return 'sell'
    return None

def update_trailing_stop_loss(current_price, trailing_stop_price, atr):
    """Update the trailing stop loss price based on current price and ATR."""
    return max(trailing_stop_price, current_price * (1 - (trailing_stop_pct * (atr / current_price))))

def backtest_strategy(df):
    """Backtest the strategy based on historical data."""
    df['signal'] = np.where(df['close'].shift(-1) > df['close'], 1, 0)
    df['strategy_returns'] = df['signal'].shift(1) * (df['close'].pct_change())
    df['cumulative_strategy_returns'] = (1 + df['strategy_returns']).cumprod()
    return df

def run_trading_logic():
    trailing_stop_price = None
    take_profit_price = None
    stop_loss_price = None
    
    try:
        with current_app.app_context():
            settings = Settings.query.first()
            if settings:
                symbol = settings.symbol
                stop_loss_pct = settings.stop_loss_pct
                trailing_stop_pct = settings.trailing_stop_pct
                take_profit_pct = settings.take_profit_pct
                lookback_days = settings.lookback_days

                if not settings.bot_running:
                    return

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
                amount_to_buy = amount / current_price
                place_order(symbol, 'buy', amount_to_buy)
                logging.info(f'Bought {amount_to_buy} BTC')
                trailing_stop_price = current_price * (1 - trailing_stop_pct)
                take_profit_price = current_price * (1 + take_profit_pct)
                stop_loss_price = current_price * (1 - stop_loss_pct)

            elif signal == 'sell' and trailing_stop_price is not None:
                amount_to_sell = amount / current_price
                place_order(symbol, 'sell', amount_to_sell)
                logging.info(f'Sold {amount_to_sell} BTC')
                trailing_stop_price = None
                take_profit_price = None
                stop_loss_price = None

            if stop_loss_price is not None and current_price <= stop_loss_price:
                amount_to_sell = amount / current_price
                place_order(symbol, 'sell', amount_to_sell)
                logging.info(f'Stop Loss triggered: Sold {amount_to_sell} BTC at {current_price}')
                stop_loss_price = None 
                take_profit_price = None 

            if take_profit_price is not None and current_price >= take_profit_price:
                amount_to_sell = amount / current_price
                place_order(symbol, 'sell', amount_to_sell)
                logging.info(f'Take Profit triggered: Sold {amount_to_sell} BTC at {current_price}')
                take_profit_price = None
                stop_loss_price = None

            if trailing_stop_price is not None:
                trailing_stop_price = update_trailing_stop_loss(current_price, trailing_stop_price, atr)

    except Exception as e:
        with current_app.app_context():
            logging.error(f"An error occurred: {e}", exc_info=True)
            send_email('piotrek.gaszczynski@gmail.com', 'Trading Bot Error', f'An error occurred: {e}')