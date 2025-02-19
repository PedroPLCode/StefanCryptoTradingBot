from dotenv import load_dotenv
from datetime import datetime, timedelta
import pandas as pd
from binance.client import Client
from app.models import BotSettings
import os
from ..utils.logging import logger
from ..utils.exception_handlers import exception_handler

load_dotenv()


def get_binance_api_credentials(bot_id=None, testnet=False):
    """
    Retrieves Binance API credentials from environment variables.

    Args:
        bot_id (str, optional): The bot identifier to retrieve specific API credentials.
        testnet (bool, optional): Whether to use the testnet credentials. Default is False.

    Returns:
        tuple: A tuple containing the API key and API secret.
    """
    if testnet:
        api_key = os.environ.get("BINANCE_TESTNET_API_KEY")
        api_secret = os.environ.get("BINANCE_TESTNET_API_SECRET")
    else:
        if bot_id:
            api_key = os.environ.get(f"BINANCE_BOT{bot_id}_API_KEY")
            api_secret = os.environ.get(f"BINANCE_BOT{bot_id}_API_SECRET")
        else:
            api_key = os.environ.get("BINANCE_GENERAL_API_KEY")
            api_secret = os.environ.get("BINANCE_GENERAL_API_SECRET")

    return api_key, api_secret


@exception_handler()
def create_binance_client(bot_id=None, testnet=False):
    """
    Creates a Binance client instance using the provided API credentials.

    Args:
        bot_id (str, optional): The bot identifier to retrieve specific API credentials.
        testnet (bool, optional): Whether to use the testnet environment. Default is False.

    Returns:
        Client: The Binance client instance.

    Raises:
        Exception: If there is an issue creating the client, an exception is logged and an email is sent to the admin.
    """
    api_key, api_secret = get_binance_api_credentials(bot_id, testnet)
    return Client(api_key, api_secret, testnet=testnet)


general_client = create_binance_client(None)


@exception_handler()
def fetch_data(symbol, interval="1m", lookback="4h", start_str=None, end_str=None):
    """
    Fetch historical kline (candlestick) data for a specific trading symbol.

    Args:
        symbol (str): The trading pair symbol (e.g., 'BTCUSDT').
        interval (str, optional): The interval between each candlestick. Default is '1m'.
        lookback (str, optional): The lookback period for historical data. Can be in hours (e.g., '4h'), days (e.g., '2d'), or minutes (e.g., '30m'). Default is '4h'.
        start_str (str, optional): The start time for the historical data. If None, it uses the lookback period.
        end_str (str, optional): The end time for the historical data. If None, it uses the current time.

    Returns:
        pd.DataFrame: A DataFrame containing the historical kline data.

    Raises:
        BinanceAPIException: If there is an error from the Binance API.
        ConnectionError: If there is a connection error.
        TimeoutError: If there is a timeout error.
        ValueError: If an invalid lookback period format is provided.
        Exception: For any other exception, an email is sent to the admin.
    """
    klines = None
    if not start_str and not end_str:
        if lookback[-1] == "h":
            hours = int(lookback[:-1])
            start_time = datetime.utcnow() - timedelta(hours=hours)
        elif lookback[-1] == "d":
            days = int(lookback[:-1])
            start_time = datetime.utcnow() - timedelta(days=days)
        elif lookback[-1] == "m":
            minutes = int(lookback[:-1])
            start_time = datetime.utcnow() - timedelta(minutes=minutes)
        else:
            raise ValueError("Unsupported lookback period format.")

        start_str = start_time.strftime("%Y-%m-%d %H:%M:%S")

        klines = general_client.get_historical_klines(
            symbol=symbol, interval=interval, start_str=start_str
        )
    else:
        klines = general_client.get_historical_klines(
            symbol=symbol,
            interval=interval,
            start_str=str(start_str),
            end_str=str(end_str),
        )

    df = pd.DataFrame(
        klines,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base_asset_volume",
            "taker_buy_quote_asset_volume",
            "ignore",
        ],
    )
    df["close"] = df["close"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)

    return df


@exception_handler(default_return=0)
def get_account_balance(bot_id, assets):
    """
    Retrieves the balance of specified assets from the Binance account.

    Args:
        bot_id (str): The bot identifier to retrieve account balance for.
        assets (list): A list of asset symbols (e.g., ['BTC', 'USDT']) to retrieve the balances for.

    Returns:
        dict: A dictionary with asset symbols as keys and the available balance as values.

    Raises:
        BinanceAPIException: If there is an error from the Binance API.
        ConnectionError: If there is a connection error.
        TimeoutError: If there is a timeout error.
        Exception: For any other exception, an email is sent to the admin.
    """
    bot_client = create_binance_client(bot_id)
    account_info = bot_client.get_account()
    balances = {
        balance["asset"]: float(balance["free"]) for balance in account_info["balances"]
    }

    return {asset: balances.get(asset, 0) for asset in assets}


@exception_handler()
def fetch_current_price(symbol):
    """
    Retrieves the current price of a specific trading symbol from Binance.

    Args:
        symbol (str): The trading pair symbol (e.g., 'BTCUSDT').

    Returns:
        float: The current price of the symbol.

    Raises:
        BinanceAPIException: If there is an error from the Binance API.
        ConnectionError: If there is a connection error.
        TimeoutError: If there is a timeout error.
        Exception: For any other exception, an email is sent to the admin.
    """
    ticker = general_client.get_symbol_ticker(symbol=symbol)
    return float(ticker["price"])


@exception_handler(default_return=(None, 0))
def get_minimum_order_quantity(bot_id, symbol):
    """
    Fetches the minimum order quantity and step size for a given symbol on Binance.

    Args:
        bot_id (int): The ID of the bot.
        symbol (str): The trading symbol (e.g., 'BTCUSDT').

    Returns:
        tuple: A tuple containing the minimum order quantity and step size.
               Returns (0, 0) if not found.
    """
    bot_client = create_binance_client(bot_id)
    exchange_info = bot_client.get_symbol_info(symbol)
    filters = exchange_info["filters"]
    for f in filters:
        if f["filterType"] == "LOT_SIZE":
            min_qty = float(f["minQty"])
            step_size = float(f["stepSize"])
            return min_qty, step_size
    return 0, 0


@exception_handler()
def get_minimum_order_value(bot_id, symbol):
    """
    Fetches the minimum order value (notional) for a given symbol on Binance.

    Args:
        bot_id (int): The ID of the bot.
        symbol (str): The trading symbol (e.g., 'BTCUSDT').

    Returns:
        float or None: The minimum notional value for the symbol, or None if not found.
    """
    bot_client = create_binance_client(bot_id)
    exchange_info = bot_client.get_symbol_info(symbol)
    filters = exchange_info["filters"]

    for f in filters:
        if f["filterType"] == "NOTIONAL":
            return float(f["minNotional"])
    return None


@exception_handler(default_return=(False, False))
def place_buy_order(bot_id):
    """
    Places a market buy order for a specified symbol on Binance using available stablecoin balance.

    The function calculates the amount of cryptocurrency to buy based on available capital
    and the minimum order requirements. It checks for sufficient balance, order size, and notional
    value before placing the buy order.

    Args:
        bot_id (int): The ID of the bot placing the order.

    Returns:
        tuple: A tuple containing a boolean indicating success or failure and the amount purchased,
               or False if the order couldn't be placed.
    """
    from .calc_utils import round_down_to_step_size
    from ..utils.email_utils import send_admin_email

    binance_min_order_amount = 0.0001

    bot_settings = BotSettings.query.get(bot_id)
    symbol = bot_settings.symbol
    capital_utilization_pct = float(bot_settings.capital_utilization_pct)
    bot_client = create_binance_client(
        bot_id=bot_id
    )  # add testnet=True for binance api sandbox
    cryptocoin_symbol = symbol[:3]
    stablecoin_symbol = symbol[-4:]

    balance = get_account_balance(bot_id, [stablecoin_symbol, cryptocoin_symbol])
    stablecoin_balance = float(balance.get(stablecoin_symbol, "0.0"))
    price = float(fetch_current_price(symbol))

    logger.trade(
        f"place_buy_order() Bot {bot_id} Fetched stablecoin balance: {stablecoin_balance}"
    )
    logger.trade(f"place_buy_order() Bot {bot_id} Fetched price for {symbol}: {price}")

    affordable_amount = (stablecoin_balance * capital_utilization_pct) / price
    min_qty, step_size = get_minimum_order_quantity(bot_id, symbol)
    amount_to_buy = float(round_down_to_step_size(affordable_amount, step_size))

    if min_qty is None or step_size is None:
        logger.trade(
            f"place_buy_order() Bot {bot_id} Invalid minimum order quantity or step size for symbol: {symbol}."
        )
        return False, False

    min_notional = get_minimum_order_value(bot_id, symbol)
    min_notional = min_notional if min_notional is not None else 0.0

    logger.trade(f"place_buy_order() Bot {bot_id} Amount_to_buy: {amount_to_buy}")

    required_stablecoin = amount_to_buy * price
    not_enough_stablecoins = bool(required_stablecoin > stablecoin_balance)

    amount_to_buy_too_small = bool(amount_to_buy < binance_min_order_amount)

    if not_enough_stablecoins or amount_to_buy_too_small:
        logger.trade(
            f"place_buy_order() Bot {bot_id} Not enough {stablecoin_symbol} to buy {cryptocoin_symbol}. Required: {required_stablecoin}, Available: {stablecoin_balance}."
        )
        send_admin_email(
            f"Bot {bot_id} Not enough {stablecoin_symbol} in place_buy_order",
            f"place_buy_order() Bot {bot_id} Not enough {stablecoin_symbol} to buy {cryptocoin_symbol}. Required: {required_stablecoin}, Available: {stablecoin_balance}.",
        )
        return False, False

    if amount_to_buy > 0 and amount_to_buy >= min_qty:
        if required_stablecoin >= min_notional:
            order_response = bot_client.order_market_buy(
                symbol=symbol, quantity=amount_to_buy
            )
            order_id = order_response["orderId"] or None
            order_status = order_response["status"] or None
            logger.trade(
                f"place_buy_order() Bot {bot_id} Buy {amount_to_buy} {cryptocoin_symbol} at price {price}."
            )

            if order_status == "FILLED":
                logger.trade(
                    f"place_buy_order() Bot {bot_id} Order {order_id} filled successfully."
                )
                return True, amount_to_buy
            else:
                logger.trade(
                    f'place_buy_order() Bot {bot_id} Order {order_id} not filled. Status: {order_response["status"]}.'
                )
                return False, False

        else:
            logger.trade(
                f"place_buy_order() Bot {bot_id} Not enough {stablecoin_symbol} to buy {cryptocoin_symbol}. Minimum order value is {min_notional}."
            )
            return False, False
    else:
        logger.trade(
            f"place_buy_order() Bot {bot_id} Not enough {stablecoin_symbol} to buy {cryptocoin_symbol}. Minimum order quantity is {min_qty}."
        )
        return False, False


@exception_handler(default_return=(False, False))
def place_sell_order(bot_id):
    """
    Places a sell order for a specified bot. The function fetches the account balance for the specified cryptocurrency
    symbol, calculates the amount to sell based on the available balance and step size, and places a market sell order.

    Args:
        bot_id (int): The ID of the bot for which the sell order is placed.

    Returns:
        tuple: A tuple containing a boolean indicating the success of the order and the amount of cryptocurrency sold.
               Returns (False, False) if the order couldn't be placed or there isn't enough balance to sell.
    """
    from ..utils.email_utils import send_admin_email
    from .calc_utils import round_down_to_step_size

    bot_settings = BotSettings.query.get(bot_id)
    symbol = bot_settings.symbol
    bot_client = create_binance_client(
        bot_id=bot_id
    )  # add testnet=True for binance api sandbox
    cryptocoin_symbol = symbol[:3]
    stablecoin_symbol = symbol[-4:]

    balance = get_account_balance(bot_id, [stablecoin_symbol, cryptocoin_symbol])
    crypto_balance = float(balance.get(cryptocoin_symbol, 0))
    price = float(fetch_current_price(symbol))

    logger.trade(
        f"place_sell_order() Bot {bot_id} Fetched balance for {cryptocoin_symbol}: {crypto_balance}"
    )
    logger.trade(f"place_sell_order() Bot {bot_id} Fetched price for {symbol}: {price}")

    min_qty, step_size = get_minimum_order_quantity(bot_id, symbol)
    min_qty = min_qty if min_qty is not None else 0

    if crypto_balance >= min_qty:
        amount_to_sell = float(round_down_to_step_size(crypto_balance, step_size))

        logger.trade(f"crypto_balance {crypto_balance}")
        logger.trade(f"min_qty {min_qty}")
        logger.trade(f"step_size {step_size}")
        logger.trade(f"amount_to_sell {amount_to_sell}")

        order_response = bot_client.order_market_sell(
            symbol=symbol, quantity=amount_to_sell
        )  # quantity=crypto_balance
        order_id = order_response["orderId"] or None
        order_status = order_response["status"] or None
        logger.trade(
            f"place_sell_order() Bot {bot_id} Sell {amount_to_sell} {cryptocoin_symbol} at price {price}."
        )

        if order_status == "FILLED":
            logger.trade(
                f"place_sell_order() Bot {bot_id} Order {order_id} filled successfully."
            )
            return True, amount_to_sell
        else:
            logger.trade(
                f'place_sell_order() Bot {bot_id} Order {order_id} not filled. Status: {order_response["status"]}.'
            )
            return False, False

    else:
        logger.trade(
            f"place_sell_order() Bot {bot_id} Not enough {cryptocoin_symbol} to sell. Minimum order quantity is {min_qty}."
        )
        return False, False


@exception_handler()
def fetch_system_status():
    """
    Fetches the current system status from the Binance API.

    Returns:
        dict: A dictionary containing the system status if the request is successful, otherwise returns None.
    """
    status = general_client.get_system_status()
    return status


@exception_handler()
def fetch_account_status(bot_id=None):
    """
    Fetches the account status of the bot's associated Binance account.

    Args:
        bot_id (int, optional): The ID of the bot. If no bot_id is provided, it fetches the status for the general account.

    Returns:
        dict: A dictionary containing the account status if the request is successful, otherwise returns None.
    """
    if not bot_id:
        status = general_client.get_account()
        return status
    else:
        bot_client = create_binance_client(bot_id)
        status = bot_client.get_account()
        return status


@exception_handler()
def fetch_server_time():
    """
    Fetches the current server time from the Binance API.

    Returns:
        dict: A dictionary containing the server time if the request is successful, otherwise returns None.
    """
    server_time = general_client.get_server_time()
    return server_time
