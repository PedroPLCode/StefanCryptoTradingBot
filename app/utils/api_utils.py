from dotenv import load_dotenv
import pandas as pd
from ..utils.app_utils import send_admin_email
from binance.client import Client
from binance.exceptions import BinanceAPIException
import os
from ..utils.logging import logger

load_dotenv()

BINANCE_GENERAL_API_KEY = os.environ['BINANCE_GENERAL_API_KEY']
BINANCE_GENERAL_API_SECRET = os.environ['BINANCE_GENERAL_API_SECRET']
general_client = Client(BINANCE_GENERAL_API_KEY, BINANCE_GENERAL_API_SECRET)

def fetch_data(symbol, interval='1m', lookback='4h'):
    klines = general_client.get_historical_klines(symbol, interval, lookback)
    df = pd.DataFrame(klines, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                        'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                                        'taker_buy_quote_asset_volume', 'ignore'])
    df['close'] = df['close'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    return df

def get_account_balance(bot_id, assets=None):
    if assets is None:
        assets = ['USDC', 'BTC', 'ETH', 'SOL', 'BNB']

    try:
        BINANCE_CURRENT_BOT_API_KEY = os.environ[f'BINANCE_BOT{bot_id}_API_KEY']
        BINANCE_CURRENT_BOT_API_SECRET = os.environ[f'BINANCE_BOT{bot_id}_API_SECRET']
        bot_client = Client(BINANCE_CURRENT_BOT_API_KEY, BINANCE_CURRENT_BOT_API_SECRET)
        
        account_info = bot_client.futures_account()
        
        balances = {balance['asset']: float(balance['balance']) for balance in account_info['assets']}
        
        return {asset: balances.get(asset, 0) for asset in assets}

    except BinanceAPIException as e:
        print(f'Błąd API Binance: {e.message}')
        return {asset: 0 for asset in assets}
    except Exception as e:
        print(f'Inny błąd: {str(e)}')
        return {asset: 0 for asset in assets}
    
    
def fetch_current_price(symbol):
    ticker = general_client.get_symbol_ticker(symbol=symbol)
    return float(ticker['price'])


def place_buy_order(symbol, current_trade):
    from ..utils.stefan_utils import save_active_trade, save_trade_to_history
    bot_id = current_trade.id
    crypto = symbol[:3]
    BINANCE_CURRENT_BOT_API_KEY = os.environ[f'BINANCE_BOT{bot_id}_API_KEY']
    BINANCE_CURRENT_BOT_API_SECRET = os.environ[f'BINANCE_BOT{bot_id}_API_SECRET']
    bot_client = Client(BINANCE_CURRENT_BOT_API_KEY, BINANCE_CURRENT_BOT_API_SECRET)
    try:
        balance = get_account_balance(bot_id)
        usdc_balance = balance.get('USDC', 0)
        price = fetch_current_price(symbol)
        
        if usdc_balance <= 0:
            logger.info(f'Brak środków USDC na zakup {crypto}.')
            return

        amount_to_buy = (usdc_balance * 0.9) / price
        if amount_to_buy > 0:
            bot_client.order_market_buy(symbol=symbol, quantity=amount_to_buy)
            logger.info(f'Kupiono {amount_to_buy} {crypto} po cenie {price}')
            save_active_trade(current_trade, order_type='buy', amount=amount_to_buy, price=price)
            save_trade_to_history(current_trade, symbol, order_type='buy', amount=amount_to_buy, price=price)
        else:
            logger.info('Za mało USDC na zakup BTC.')
                
    except ConnectionError as ce:
        logger.error(f"Błąd połączenia: {str(ce)}")
        send_admin_email('Błąd połączenia przy składaniu zlecenia kupna', str(ce))
    except Exception as e:
        logger.error(f"Błąd podczas składania zlecenia kupna: {str(e)}")
        send_admin_email('Błąd przy składaniu zlecenia kupna', str(e))
        
        
def place_sell_order(symbol, current_trade):
    from ..utils.stefan_utils import save_trade_to_history, save_deactivated_trade
    bot_id = current_trade.id
    crypto = symbol[:3]
    BINANCE_CURRENT_BOT_API_KEY = os.environ[f'BINANCE_BOT{bot_id}_API_KEY']
    BINANCE_CURRENT_BOT_API_SECRET = os.environ[f'BINANCE_BOT{bot_id}_API_SECRET']
    bot_client = Client(BINANCE_CURRENT_BOT_API_KEY, BINANCE_CURRENT_BOT_API_SECRET)
    try:
        balance = get_account_balance(bot_id)
        btc_balance = balance.get(crypto, 0)
        price = fetch_current_price(symbol)

        if btc_balance <= 0:
            logger.info(f'Brak {crypto} do sprzedaży.')
            return

        bot_client.order_market_sell(symbol=symbol, quantity=btc_balance)
        logger.info(f'Sprzedano {btc_balance} {crypto} po cenie {price}')
        save_deactivated_trade(current_trade)
        save_trade_to_history(current_trade, symbol, order_type='sell', amount=btc_balance, price=price)
                
    except ConnectionError as ce:
        logger.error(f"Błąd połączenia: {str(ce)}")
        send_admin_email('Błąd połączenia przy składaniu zlecenia sprzedaży', str(ce))
    except Exception as e:
        logger.error(f"Błąd podczas składania zlecenia sprzedaży: {str(e)}")
        send_admin_email('Błąd przy składaniu zlecenia sprzedaży', str(e))


def fetch_system_status():
    status = general_client.get_system_status()
    return status


def fetch_account_status(bot_id=None):
    if not bot_id:
        status = general_client.get_account()
        return status
    else:
        BINANCE_CURRENT_BOT_API_KEY = os.environ[f'BINANCE_BOT{bot_id}_API_KEY']
        BINANCE_CURRENT_BOT_API_SECRET = os.environ[f'BINANCE_BOT{bot_id}_API_SECRET']
        bot_client = Client(BINANCE_CURRENT_BOT_API_KEY, BINANCE_CURRENT_BOT_API_SECRET)
        status = bot_client.get_account()
        return status


def fetch_server_time():
    server_time = general_client.get_server_time()
    return server_time