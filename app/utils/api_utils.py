#tests
from dotenv import load_dotenv
from .. import db
from ..models import Settings, CurrentTrade
import numpy as np
import pandas as pd
from ..utils.app_utils import send_email
from ..utils.stefan_utils import save_trade, save_trade_to_history, load_current_trade, delete_trade
from binance.client import Client
import os
from ..utils.logging import logger

load_dotenv()

BINANCE_API_KEY = os.environ['BINANCE_API_KEY']
BINANCE_API_SECRET = os.environ['BINANCE_API_SECRET']
client = Client(BINANCE_API_KEY, BINANCE_API_SECRET) #, testnet=True)

def fetch_data(symbol, interval='1m', lookback='30 days'):
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
    try:
        balance = get_account_balance()
        usdc_balance = balance['USDC']
        btc_balance = balance['BTC']
        btc_price = fetch_current_price(symbol)
        
        if order_type == 'buy':
            amount_to_buy = (usdc_balance * 0.9) / btc_price
            if amount_to_buy > 0:
                client.order_market_buy(symbol=symbol, quantity=amount_to_buy)
                logger.info(f'Kupiono {amount_to_buy} {symbol} po cenie {btc_price}')
                save_trade(order_type='buy', amount=amount_to_buy, price=btc_price)
                save_trade_to_history(order_type='buy', amount=amount_to_buy, price=btc_price)
            else:
                logger.info('Za mało USDC na zakup BTC.')

        elif order_type == 'sell':
            if btc_balance > 0:
                client.order_market_sell(symbol=symbol, quantity=btc_balance)
                logger.info(f'Sprzedano {btc_balance} {symbol} po cenie {btc_price}')
                delete_trade()
                save_trade_to_history(order_type='sell', amount=btc_balance, price=btc_price)
            else:
                logger.info('Za mało BTC na sprzedaż.')
                
    except Exception as e:
        logger.error(f"Błąd podczas składania zlecenia: {str(e)}")
        send_email('twój_email@gmail.com', 'Błąd przy składaniu zlecenia', str(e))


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