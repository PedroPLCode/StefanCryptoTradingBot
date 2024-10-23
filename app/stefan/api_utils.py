from dotenv import load_dotenv
import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException
import os
from ..utils.logging import logger

load_dotenv()

def get_binance_api_credentials(bot_id=None):
    if bot_id:
        api_key = os.environ.get(f'BINANCE_BOT{bot_id}_API_KEY')
        api_secret = os.environ.get(f'BINANCE_BOT{bot_id}_API_SECRET')
    else:
        api_key = os.environ.get('BINANCE_GENERAL_API_KEY')
        api_secret = os.environ.get('BINANCE_GENERAL_API_SECRET')
    
    return api_key, api_secret


def create_binance_client(bot_id=None):
    api_key, api_secret = get_binance_api_credentials(bot_id)
    return Client(api_key, api_secret)

general_client = create_binance_client(None)


def fetch_data(symbol, interval='1m', lookback='4h'):
    try: 
        klines = general_client.get_historical_klines(symbol, interval, lookback)
        df = pd.DataFrame(
            klines, 
            columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume', 
                'close_time', 'quote_asset_volume', 'number_of_trades', 
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 
                'ignore'
            ]
        )
        df['close'] = df['close'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        return df
    
    except BinanceAPIException as e:
        logger.error(f'Binance API error: {e}')
        return None
    except ConnectionError as e:
        logger.error(f"Connection error occurred: {e}")
        return None
    except TimeoutError as e:
        logger.error(f"Request timed out: {e}")
        return None
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None


def get_account_balance(bot_id, assets=None):
    if assets is None:
        assets = ['USDC', 'BTC', 'ETH', 'SOL', 'LTC', 'ADA', 'BNB']

    try:
        bot_client = create_binance_client(bot_id)
        account_info = bot_client.futures_account()
        balances = {
            balance['asset']: float(balance['balance']) 
            for balance in account_info['assets']
        }
        return {asset: balances.get(asset, 0) for asset in assets}

    except BinanceAPIException as e:
        logger.error(f'Bot {bot_id} Błąd API Binance: {e.message}')
        return {asset: 0 for asset in assets}
    except ConnectionError as e:
        logger.error(f"Bot {bot_id} Connection error occurred: {e}")
        return {asset: 0 for asset in assets}
    except TimeoutError as e:
        logger.error(f"Bot {bot_id} Request timed out: {e}")
        return {asset: 0 for asset in assets}
    except Exception as e:
        logger.error(f'Bot {bot_id} Inny błąd: {str(e)}')
        return {asset: 0 for asset in assets}
    
    
def fetch_current_price(symbol):
    try:
        ticker = general_client.get_symbol_ticker(symbol=symbol)
        return float(ticker['price'])
    except BinanceAPIException as e:
        logger.error(f'Binance API error: {e}')
        return None
    except ConnectionError as e:
        logger.error(f"Connection error occurred: {e}")
        return None
    except TimeoutError as e:
        logger.error(f"Request timed out: {e}")
        return None
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None


def place_buy_order(bot_settings):
    from .logic_utils import save_active_trade
    from ..utils.app_utils import send_admin_email
    
    symbol = bot_settings.symbol
    current_trade = bot_settings.bot_current_trade
    bot_id = bot_settings.id
    bot_client = create_binance_client(bot_id)
    cryptocoin_symbol = symbol[:3]
    stablecoin_symbol = symbol[-4:]

    try:
        balance = get_account_balance(bot_id)
        stablecoin_balance = float(balance.get(stablecoin_symbol, 0))
        price = float(fetch_current_price(symbol))
        
        if stablecoin_balance <= 0:
            logger.info(f'Bot {bot_settings.id} Not enough {stablecoin_symbol} to buy {cryptocoin_symbol}.')
            return

        amount_to_buy = (stablecoin_balance * 0.9) / price
        if amount_to_buy > 0:
            bot_client.order_market_buy(symbol=symbol, quantity=amount_to_buy)
            logger.info(f'Bot {bot_settings.id} Buy {amount_to_buy} {cryptocoin_symbol} at price {price}')
            save_active_trade(
                current_trade, 
                amount=amount_to_buy, 
                price=price,
                buy_price=price
            )
        else:
            logger.info(f'Bot {bot_settings.id} Not enough {stablecoin_symbol} to buy {cryptocoin_symbol}.')

    except BinanceAPIException as e:
        logger.error(f'Bot {bot_id} Binance API error: {e}')
        send_admin_email(f'Bot {bot_settings.id} Binance API error', str(e))
    except ConnectionError as ce:
        logger.error(f"Bot {bot_settings.id} Błąd połączenia: {str(ce)}")
        send_admin_email(f'Bot {bot_settings.id} Błąd połączenia przy składaniu zlecenia kupna', str(ce))
    except TimeoutError as e:
        logger.error(f"Bot {bot_settings.id}. Request timed out: {e}")
        send_admin_email(f"Bot {bot_settings.id}. Request timed out", str(e))
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Błąd podczas składania zlecenia kupna: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Błąd przy składaniu zlecenia kupna', str(e))


def place_sell_order(bot_settings):
    from .logic_utils import save_trade_to_history, save_deactivated_trade
    from ..utils.app_utils import send_admin_email
    
    symbol = bot_settings.symbol
    current_trade = bot_settings.bot_current_trade
    bot_id = bot_settings.id
    bot_client = create_binance_client(bot_id)
    cryptocoin_symbol = symbol[:3]

    try:
        balance = get_account_balance(bot_id)
        crypto_balance = float(balance.get(cryptocoin_symbol, 0))
        price = float(fetch_current_price(symbol))

        if crypto_balance <= 0:
            logger.info(f'Bot {bot_settings.id} Not enough {cryptocoin_symbol} to sell.')
            return

        bot_client.order_market_sell(symbol=symbol, quantity=crypto_balance)
        logger.info(f'Bot {bot_settings.id} Sell {crypto_balance} {cryptocoin_symbol} at price {price}')
        save_deactivated_trade(current_trade)
        save_trade_to_history(
            current_trade, 
            amount=crypto_balance, 
            buy_price=bot_settings.bot_current_trade.buy_price,
            sell_price=price
        )
    except BinanceAPIException as e:
        logger.error(f'Bot {bot_id} Binance API error: {e}')
        send_admin_email(f'Bot {bot_settings.id} Binance API error', str(e))
    except ConnectionError as ce:
        logger.error(f"Bot {bot_settings.id} Błąd połączenia: {str(ce)}")
        send_admin_email(f'Bot {bot_settings.id} Błąd połączenia przy składaniu zlecenia sprzedaży', str(ce))
    except TimeoutError as e:
        logger.error(f"Bot {bot_settings.id}. Request timed out: {e}")
        send_admin_email(f"Bot {bot_settings.id}. Request timed out", str(e))
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Błąd podczas składania zlecenia sprzedaży: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Błąd przy składaniu zlecenia sprzedaży', str(e))


def fetch_system_status():
    try:
        status = general_client.get_system_status()
        return status
    except BinanceAPIException as e:
        logger.error(f'Binance API error: {e}')
        return None
    except ConnectionError as e:
        logger.error(f"Connection error occurred: {e}")
        return None
    except TimeoutError as e:
        logger.error(f"Request timed out: {e}")
        return None
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None


def fetch_account_status(bot_id=None):
    try:
        if not bot_id:
            status = general_client.get_account()
            return status
        else:
            bot_client = create_binance_client(bot_id)
            status = bot_client.get_account()
            return status
    except BinanceAPIException as e:
        logger.error(f'Bot {bot_id} Błąd API Binance: {e}')
        return None
    except ConnectionError as e:
        logger.error(f"Connection error occurred: {e}")
        return None
    except TimeoutError as e:
        logger.error(f"Request timed out: {e}")
        return None
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None


def fetch_server_time():
    try:
        server_time = general_client.get_server_time()
        return server_time
    except BinanceAPIException as e:
        logger.error(f'Błąd API Binance: {e}')
        return None
    except ConnectionError as e:
        logger.error(f"Connection error occurred: {e}")
        return None
    except TimeoutError as e:
        logger.error(f"Request timed out: {e}")
        return None
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None