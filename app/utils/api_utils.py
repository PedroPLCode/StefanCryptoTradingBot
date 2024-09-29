import time
from dotenv import load_dotenv
import numpy as np
import pandas as pd
from binance.client import Client
import os
import logging
#from ..bot.bot import symbol

load_dotenv()

API_KEY = os.environ['BINANCE_API_KEY']
API_SECRET = os.environ['BINANCE_API_SECRET']

client = Client(API_KEY, API_SECRET)

def fetch_data(symbol, interval='1h', lookback='30 days'):
    klines = client.get_historical_klines(symbol, interval, lookback)
    df = pd.DataFrame(klines, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                        'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                                        'taker_buy_quote_asset_volume', 'ignore'])
    df['close'] = df['close'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    return df

def place_order(order_type, amount):
    try:
        if order_type == 'buy':
            client.order_market_buy(symbol=symbol, quantity=amount)
        elif order_type == 'sell':
            client.order_market_sell(symbol=symbol, quantity=amount)
        # W przykładowych miejscach w kodzie:
        logging.info(f'Bought {amount} {symbol}')
    except Exception as e:
        print(f"Error placing order: {e}")

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