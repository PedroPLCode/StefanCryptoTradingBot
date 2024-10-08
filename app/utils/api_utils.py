#tests 100% ok
import time
from dotenv import load_dotenv
import numpy as np
import pandas as pd
from binance.client import Client
import os
import logging
from ..utils.logging import logger

load_dotenv()

BINANCE_API_KEY = os.environ['BINANCE_API_KEY']
BINANCE_API_SECRET = os.environ['BINANCE_API_SECRET']
client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

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
    account_info = client.futures_account()
    balances = {balance['asset']: float(balance['balance']) for balance in account_info['assets']}
    return {
        'USDC': balances.get('USDC', 0),
        'BTC': balances.get('BTC', 0)
    }
    
def fetch_current_price(symbol):
    ticker = client.get_symbol_ticker(symbol=symbol)
    return float(ticker['price'])

def place_order(symbol, order_type):
    from ..utils.app_utils import send_email
    try:
        balance = get_account_balance()
        usdc_balance = balance['USDC']
        btc_balance = balance['BTC']
        btc_price = fetch_current_price(symbol)
        
        if order_type == 'buy':
            amount_to_buy = (usdc_balance / btc_price) * 0.9
            if amount_to_buy > 0:
                client.order_market_buy(symbol=symbol, quantity=amount_to_buy)
                logger.info(f'Order placed: Buy {amount_to_buy} {symbol}')
            else:
                logger.info(f'Not enough USDC to place a buy order. Available: {usdc_balance}, Needed for 1 BTC: {btc_price}')
        
        elif order_type == 'sell':
            if btc_balance > 0:
                client.order_market_sell(symbol=symbol, quantity=btc_balance)
                logger.info(f'Order placed: Sell {btc_balance} {symbol}')
            else:
                logger.info(f'Not enough BTC to place a sell order. Available: {btc_balance}')
                
    except Exception as e:
        logger.error(f"Error placing order: {e}", exc_info=True)
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