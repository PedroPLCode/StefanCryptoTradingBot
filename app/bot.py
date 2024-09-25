import time
import numpy as np
import pandas as pd
from binance.client import Client
import talib

# Konfiguracja
API_KEY = 'YOUR_API_KEY'
API_SECRET = 'YOUR_API_SECRET'
client = Client(API_KEY, API_SECRET)

symbol = 'BTCUSDT'
stop_loss_pct = 0.02  # 2% stop-loss
trailing_stop_pct = 0.01  # 1% trailing stop

# Funkcja do pobierania danych
def fetch_data(symbol, interval='1h', lookback='1 day'):
    klines = client.get_historical_klines(symbol, interval, lookback)
    df = pd.DataFrame(klines, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                        'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                                        'taker_buy_quote_asset_volume', 'ignore'])
    df['close'] = df['close'].astype(float)
    return df

# Funkcja do obliczania wskaźników
def calculate_indicators(df):
    df['rsi'] = talib.RSI(df['close'], timeperiod=14)
    df['macd'], df['macd_signal'], _ = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)

# Funkcja do sprawdzania sygnałów
def check_signals(df):
    latest_rsi = df['rsi'].iloc[-1]
    latest_macd = df['macd'].iloc[-1]
    latest_macd_signal = df['macd_signal'].iloc[-1]

    if latest_rsi < 30 and latest_macd > latest_macd_signal:  # Kupno
        return 'buy'
    elif latest_rsi > 70 and latest_macd < latest_macd_signal:  # Sprzedaż
        return 'sell'
    return None

# Funkcja do składania zamówienia
def place_order(order_type, amount):
    if order_type == 'buy':
        client.order_market_buy(symbol=symbol, quantity=amount)
    elif order_type == 'sell':
        client.order_market_sell(symbol=symbol, quantity=amount)

# Funkcja do aktualizacji trailing stop-loss
def update_trailing_stop_loss(current_price, trailing_stop_price):
    if current_price > trailing_stop_price:
        return current_price * (1 - trailing_stop_pct)
    return trailing_stop_price

# Główna pętla
trailing_stop_price = None
while True:
    df = fetch_data(symbol)
    calculate_indicators(df)

    signal = check_signals(df)
    current_price = df['close'].iloc[-1]

    if signal == 'buy':
        amount = 0.001  # Ilość do zakupu
        place_order('buy', amount)
        print(f'Bought {amount} {symbol}')
        trailing_stop_price = current_price * (1 - trailing_stop_pct)  # Ustawienie trailing stop-loss
    
    elif signal == 'sell' and trailing_stop_price is not None:
        amount = 0.001  # Ilość do sprzedaży
        place_order('sell', amount)
        print(f'Sold {amount} {symbol}')
        trailing_stop_price = None  # Reset trailing stop-loss

    # Aktualizacja trailing stop-loss
    if trailing_stop_price is not None:
        trailing_stop_price = update_trailing_stop_loss(current_price, trailing_stop_price)

    time.sleep(3600)  # Czekaj godzinę przed kolejnym cyklem