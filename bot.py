from binance.client import Client
import os
import config

BINANCE_API_KEY = os.environ['BINANCE_API_KEY']
BINANCE_API_SECRET = os.environ['BINANCE_API_SECRET']

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

def place_buy_order(symbol, quantity, price):
    try:
        order = client.order_limit_buy(
            symbol=symbol,
            quantity=quantity,
            price=price)
        return order
    except Exception as e:
        print(f"Error placing buy order: {e}")
        return None

def place_sell_order(symbol, quantity, price):
    try:
        order = client.order_limit_sell(
            symbol=symbol,
            quantity=quantity,
            price=price)
        return order
    except Exception as e:
        print(f"Error placing sell order: {e}")
        return None

def check_balance(asset):
    try:
        balance = client.get_asset_balance(asset=asset)
        return balance
    except Exception as e:
        print(f"Error checking balance: {e}")
        return None