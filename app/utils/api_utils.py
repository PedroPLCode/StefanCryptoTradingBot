import time
from dotenv import load_dotenv
import numpy as np
import pandas as pd
from binance.client import Client
import os
import logging

load_dotenv()

API_KEY = os.environ['BINANCE_API_KEY']
BINANCE_API_SECRET = os.environ['BINANCE_API_SECRET']

client = Client(API_KEY, BINANCE_API_SECRET, testnet=True)

def fetch_data(symbol, interval='1h', lookback='30 days'):
    klines = client.get_historical_klines(symbol, interval, lookback)
    df = pd.DataFrame(klines, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                        'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                                        'taker_buy_quote_asset_volume', 'ignore'])
    df['close'] = df['close'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    return df


def get_account_balance():
    account_info = client.futures_account()  # For futures account
    # Use client.get_account() if you're accessing spot account instead
    balances = {balance['asset']: float(balance['balance']) for balance in account_info['assets']}
    return {
        'USDC': balances.get('USDC', 0),
        'BTC': balances.get('BTC', 0)
    }


def place_order(symbol, order_type, amount):
    from ..utils.app_utils import send_email
    try:
        if order_type == 'buy':
            client.order_market_buy(symbol=symbol, quantity=amount)
        elif order_type == 'sell':
            client.order_market_sell(symbol=symbol, quantity=amount)
        logging.info(f'Bought {amount} {symbol}' if order_type == 'buy' else f'Sold {amount} {symbol}')
    except Exception as e:
        print(f"Error placing order: {e}")
        send_email('piotrek.gaszczynski@gmail.com', 'Error placing order', str(e))

def fetch_ticker(symbol='BTCUSDT'):
    ticker = client.get_ticker(symbol='BTCUSDT')
    return ticker

def fetch_system_status():
    status = client.get_system_status()
    return status

def fetch_account_status():
    status = client.get_account()
    return status

def fetch_server_time():
    server_time = client.get_server_time()
    return server_time