from dotenv import load_dotenv
import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException
from app.models import BotSettings
import os
from ..utils.logging import logger

load_dotenv()

def get_binance_api_credentials(bot_id=None, testnet=False):
    if testnet:
        api_key = os.environ.get('BINANCE_TESTNET_API_KEY')
        api_secret = os.environ.get('BINANCE_TESTNET_API_SECRET')
    else:
        if bot_id:
            api_key = os.environ.get(f'BINANCE_BOT{bot_id}_API_KEY')
            api_secret = os.environ.get(f'BINANCE_BOT{bot_id}_API_SECRET')
        else:
            api_key = os.environ.get('BINANCE_GENERAL_API_KEY')
            api_secret = os.environ.get('BINANCE_GENERAL_API_SECRET')
    
    return api_key, api_secret


def create_binance_client(bot_id=None, testnet=False):
    try:
        api_key, api_secret = get_binance_api_credentials(bot_id, testnet)
        return Client(api_key, api_secret, testnet=testnet)
    except Exception as e:
        from ..utils.app_utils import send_admin_email
        logger.error(f"Exception in create_binance_client: {str(e)}")
        send_admin_email(f'Exception in create_binance_client', str(e))

general_client = create_binance_client(None)


#Not in use.
def get_exchange_info(bot_id):
    try:
        bot_client = create_binance_client(bot_id)
        bot_settings = BotSettings.query.get(bot_id)
        exchange_info = bot_client.get_exchange_info()
        symbol_info = next((s for s in exchange_info['symbols'] if s['symbol'] == bot_settings.symbol), None)

        if symbol_info:
            min_notional = None
            for filter in symbol_info['filters']:
                if filter['filterType'] == 'NOTIONAL':
                    min_notional = float(filter['minNotional'])
                    logger.trade(f'Minimum order amount {bot_settings.symbol}: {min_notional} USDC')
                elif filter['filterType'] == 'LOT_SIZE':
                    min_qty = float(filter['minQty'])
                    logger.trade(f'Minimum order {bot_settings.symbol}: {min_qty}')
        else:
            logger.trade(f'No info for {bot_settings.symbol}')
    except Exception as e:
        from ..utils.app_utils import send_admin_email
        logger.error(f"Exception in get_exchange_info: {str(e)}")
        send_admin_email(f'Exception in get_exchange_info', str(e))


def fetch_data(symbol, interval='1m', lookback='4h'):
    from ..utils.app_utils import send_admin_email
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
        logger.error(f'BinanceAPIException in fetch_full_data: {str(e)}')
        send_admin_email(f'BinanceAPIException in fetch_full_data', str(e))
        return None
    except ConnectionError as e:
        logger.error(f"ConnectionError in fetch_full_data: {str(e)}")
        send_admin_email(f'ConnectionError in fetch_full_data', str(e))
        return None
    except TimeoutError as e:
        logger.error(f"TimeoutError in fetch_full_data: {str(e)}")
        send_admin_email(f'TimeoutError in fetch_full_data', str(e))
        return None
    except Exception as e:
        logger.error(f"Exception in fetch_full_data: {str(e)}")
        send_admin_email(f'Exception in fetch_full_data', str(e))
        return None


def get_account_balance(bot_id, assets):
    from ..utils.app_utils import send_admin_email
    try:
        bot_client = create_binance_client(bot_id)
        account_info = bot_client.get_account()
        balances = {
            balance['asset']: float(balance['free']) 
            for balance in account_info['balances']
        }
        return {asset: balances.get(asset, 0) for asset in assets}

    except BinanceAPIException as e:
        logger.error(f'Bot {bot_id} BinanceAPIException in get_account_balance: {str(e)}')
        send_admin_email(f'Bot {bot_id} BinanceAPIException in get_account_balance', str(e))
        return {asset: 0 for asset in assets}
    except ConnectionError as e:
        logger.error(f"Bot {bot_id} ConnectionError in get_account_balance: {str(e)}")
        send_admin_email(f'Bot {bot_id} ConnectionError in get_account_balance', str(e))
        return {asset: 0 for asset in assets}
    except TimeoutError as e:
        logger.error(f"Bot {bot_id} TimeoutError in get_account_balance: {str(e)}")
        send_admin_email(f'Bot {bot_id} TimeoutError in get_account_balance', str(e))
        return {asset: 0 for asset in assets}
    except Exception as e:
        logger.error(f'Bot {bot_id} Exception in get_account_balance: {str(e)}')
        send_admin_email(f'Bot {bot_id} Exception in get_account_balance', str(e))
        return {asset: 0 for asset in assets}
    
    
def fetch_current_price(symbol):
    from ..utils.app_utils import send_admin_email
    try:
        ticker = general_client.get_symbol_ticker(symbol=symbol)
        return float(ticker['price'])
    except BinanceAPIException as e:
        logger.error(f'BinanceAPIException in fetch_current_price: {str(e)}')
        send_admin_email(f'BinanceAPIException in fetch_current_price', str(e))
        return None
    except ConnectionError as e:
        logger.error(f"ConnectionError in fetch_current_price: {str(e)}")
        send_admin_email(f'ConnectionError in fetch_current_price', str(e))
        return None
    except TimeoutError as e:
        logger.error(f"TimeoutError in fetch_current_price: {str(e)}")
        send_admin_email(f'TimeoutError in fetch_current_price', str(e))
        return None
    except Exception as e:
        logger.error(f"Exception in fetch_current_price: {str(e)}")
        send_admin_email(f'Exception in fetch_current_price', str(e))
        return None


def get_minimum_order_quantity(bot_id, symbol):
    from ..utils.app_utils import send_admin_email
    try: 
        bot_client = create_binance_client(bot_id)
        exchange_info = bot_client.get_symbol_info(symbol)
        filters = exchange_info['filters']
        for f in filters:
            if f['filterType'] == 'LOT_SIZE':
                min_qty = float(f['minQty'])
                step_size = float(f['stepSize'])
                logger.trade(f'step_size: {step_size}')
                decimal_places = len(str(step_size).split('.')[-1]) if '.' in str(step_size) else 0
                logger.trade(f'decimal_places: {decimal_places}')
                return min_qty, step_size
        return None, 0
    except BinanceAPIException as e:
        logger.error(f'BinanceAPIException in get_minimum_order_quantity: {str(e)}')
        send_admin_email(f'BinanceAPIException in get_minimum_order_quantity', str(e))
        return None
    except ConnectionError as e:
        logger.error(f"ConnectionError in get_minimum_order_quantity: {str(e)}")
        send_admin_email(f'ConnectionError in get_minimum_order_quantity', str(e))
        return None
    except TimeoutError as e:
        logger.error(f"TimeoutError in get_minimum_order_quantity: {str(e)}")
        send_admin_email(f'TimeoutError in get_minimum_order_quantity', str(e))
        return None
    except Exception as e:
        logger.error(f"Exception in get_minimum_order_quantity: {str(e)}")
        send_admin_email(f'Exception in get_minimum_order_quantity', str(e))
        return None
    
    
def get_minimum_order_value(bot_id, symbol):
    from ..utils.app_utils import send_admin_email
    try:
        bot_client = create_binance_client(bot_id)
        exchange_info = bot_client.get_symbol_info(symbol)
        filters = exchange_info['filters']
        
        for f in filters:
            if f['filterType'] == 'NOTIONAL':
                return float(f['minNotional'])
        return None
    except BinanceAPIException as e:
        logger.error(f'BinanceAPIException in get_minimum_order_value: {str(e)}')
        send_admin_email(f'BinanceAPIException in get_minimum_order_value', str(e))
        return None
    except ConnectionError as e:
        logger.error(f"ConnectionError in get_minimum_order_value: {str(e)}")
        send_admin_email(f'ConnectionError in get_minimum_order_value', str(e))
        return None
    except TimeoutError as e:
        logger.error(f"TimeoutError in get_minimum_order_value: {str(e)}")
        send_admin_email(f'TimeoutError in get_minimum_order_value', str(e))
        return None
    except Exception as e:
        logger.error(f"Exception in get_minimum_order_value: {str(e)}")
        send_admin_email(f'Exception in get_minimum_order_value', str(e))
        return None


def place_buy_order(bot_id):
    from .logic_utils import round_to_step_size
    from ..utils.app_utils import send_admin_email
    
    try:    
        bot_settings = BotSettings.query.get(bot_id)
        symbol = bot_settings.symbol
        bot_client = create_binance_client(bot_id=bot_id, testnet=True)
        cryptocoin_symbol = symbol[:3]
        stablecoin_symbol = symbol[-4:]

        balance = get_account_balance(bot_id, [stablecoin_symbol, cryptocoin_symbol])
        stablecoin_balance = float(balance.get(stablecoin_symbol, '0.0'))
        price = float(fetch_current_price(symbol))
        
        logger.trade(f'place_buy_order() Bot {bot_settings.id} Fetched stablecoin balance: {stablecoin_balance}')
        logger.trade(f'place_buy_order() Bot {bot_settings.id} Fetched price for {symbol}: {price}')

        amount_to_buy = (stablecoin_balance * 0.9) / price
        
        min_qty, step_size = get_minimum_order_quantity(bot_settings.id, symbol)
        min_qty = min_qty if min_qty is not None else 0
                
        min_notional = get_minimum_order_value(bot_settings.id, symbol)
        min_notional = min_notional if min_notional is not None else 0.0
        
        amount_to_buy = round_to_step_size(amount_to_buy, step_size)
        
        logger.trade(f"place_buy_order() Bot {bot_settings.id} Amount_to_buy: {amount_to_buy}")

        required_stablecoin = amount_to_buy * price
        if required_stablecoin > stablecoin_balance:
            logger.trade(f'place_buy_order() Bot {bot_settings.id} Not enough {stablecoin_symbol} to buy {cryptocoin_symbol}. Required: {required_stablecoin}, Available: {stablecoin_balance}.')
            return False, False

        if amount_to_buy >= min_qty:
            if required_stablecoin >= min_notional:
                bot_client.order_market_buy(symbol=symbol, quantity=amount_to_buy)
                logger.trade(f'place_buy_order() Bot {bot_settings.id} Buy {amount_to_buy} {cryptocoin_symbol} at price {price}. Completed.')
                return True, amount_to_buy
      
            else:
                logger.trade(f'place_buy_order() Bot {bot_settings.id} Not enough {stablecoin_symbol} to buy {cryptocoin_symbol}. Minimum order value is {min_notional}.')
                return False, False
        else:
            logger.trade(f'place_buy_order() Bot {bot_settings.id} Not enough {stablecoin_symbol} to buy {cryptocoin_symbol}. Minimum order quantity is {min_qty}.')
            return False, False

    except BinanceAPIException as e:
        logger.error(f'Bot {bot_id} BinanceAPIException in place_buy_order: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} BinanceAPIException in place_buy_order', str(e))
    except ConnectionError as e:
        logger.error(f"Bot {bot_settings.id} ConnectionError in place_buy_order: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Connection Error in place_buy_order', str(e))
    except TimeoutError as e:
        logger.error(f"Bot {bot_settings.id} TimeoutError in place_buy_order:  {str(e)}")
        send_admin_email(f"Bot {bot_settings.id} TimeoutError in place_buy_order", str(e))
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in place_buy_order: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in place_buy_order', str(e))


def place_sell_order(bot_id):
    from ..utils.app_utils import send_admin_email

    try:
        bot_settings = BotSettings.query.get(bot_id)
        symbol = bot_settings.symbol
        bot_client = create_binance_client(bot_id=bot_id, testnet=True)
        cryptocoin_symbol = symbol[:3]
        stablecoin_symbol = symbol[-4:]

        balance = get_account_balance(bot_id, [stablecoin_symbol, cryptocoin_symbol])
        crypto_balance = float(balance.get(cryptocoin_symbol, 0))
        price = float(fetch_current_price(symbol))

        logger.trade(f'place_sell_order() Bot {bot_settings.id} Fetched balance for {cryptocoin_symbol}: {crypto_balance}')
        logger.trade(f'place_sell_order() Bot {bot_settings.id} Fetched price for {symbol}: {price}')

        min_qty, step_size = get_minimum_order_quantity(bot_settings.id, symbol)
        min_qty = min_qty if min_qty is not None else 0

        if crypto_balance >= min_qty:
            bot_client.order_market_sell(symbol=symbol, quantity=crypto_balance)
            logger.trade(f'place_sell_order() Bot {bot_settings.id} Sell {crypto_balance} {cryptocoin_symbol} at price {price}. Completed.')
            return True, crypto_balance
            
        else:
            logger.trade(f'place_sell_order() Bot {bot_settings.id} Not enough {cryptocoin_symbol} to sell. Minimum order quantity is {min_qty}.')
            return False, False

    except BinanceAPIException as e:
        logger.error(f'Bot {bot_id} BinanceAPIException in place_sell_order: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} BinanceAPIException in place_sell_order', str(e))
    except ConnectionError as e:
        logger.error(f"Bot {bot_settings.id} ConnectionError in place_sell_order: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} ConnectionError in place_sell_order', str(e))
    except TimeoutError as e:
        logger.error(f"Bot {bot_settings.id} TimeoutError in place_sell_order: {str(e)}")
        send_admin_email(f"Bot {bot_settings.id} TimeoutError in place_sell_order", str(e))
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in place_sell_order: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in place_sell_order', str(e))


def fetch_system_status():
    from ..utils.app_utils import send_admin_email
    try:
        status = general_client.get_system_status()
        return status
    except BinanceAPIException as e:
        logger.error(f'BinanceAPIException in fetch_system_status: {str(e)}')
        send_admin_email(f'BinanceAPIException in fetch_system_status', str(e))
        return None
    except ConnectionError as e:
        logger.error(f"ConnectionError in fetch_system_status: {str(e)}")
        send_admin_email(f'ConnectionError in fetch_system_status', str(e))
        return None
    except TimeoutError as e:
        logger.error(f"TimeoutError in fetch_system_status: {str(e)}")
        send_admin_email(f'TimeoutError in fetch_system_status', str(e))
        return None
    except Exception as e:
        logger.error(f"Exception in fetch_system_status: {str(e)}")
        send_admin_email(f'Exception in fetch_system_status', str(e))
        return None


def fetch_account_status(bot_id=None):
    from ..utils.app_utils import send_admin_email
    try:
        if not bot_id:
            status = general_client.get_account()
            return status
        else:
            bot_client = create_binance_client(bot_id)
            status = bot_client.get_account()
            return status
    except BinanceAPIException as e:
        logger.error(f'BinanceAPIException in fetch_account_status: {str(e)}')
        send_admin_email(f'BinanceAPIException in fetch_account_status', str(e))
        return None
    except ConnectionError as e:
        logger.error(f"ConnectionError in fetch_account_status: {str(e)}")
        send_admin_email(f'ConnectionError in fetch_account_status', str(e))
        return None
    except TimeoutError as e:
        logger.error(f"TimeoutError in fetch_account_status: {str(e)}")
        send_admin_email(f'TimeoutError in fetch_account_status', str(e))
        return None
    except Exception as e:
        logger.error(f"Exception in fetch_account_status: {str(e)}")
        send_admin_email(f'Exception in fetch_account_status', str(e))
        return None


def fetch_server_time():
    from ..utils.app_utils import send_admin_email
    try:
        server_time = general_client.get_server_time()
        return server_time
    except BinanceAPIException as e:
        logger.error(f'BinanceAPIException in fetch_server_time: {str(e)}')
        send_admin_email(f'BinanceAPIException in fetch_server_time', str(e))
        return None
    except ConnectionError as e:
        logger.error(f"ConnectionError in fetch_server_time: {str(e)}")
        send_admin_email(f'ConnectionError in fetch_server_time', str(e))
        return None
    except TimeoutError as e:
        logger.error(f"TimeoutError in fetch_server_time: {str(e)}")
        send_admin_email(f'TimeoutError in fetch_server_time', str(e))
        return None
    except Exception as e:
        logger.error(f"Exception in fetch_server_time: {str(e)}")
        send_admin_email(f'Exception in fetch_server_time', str(e))
        return None