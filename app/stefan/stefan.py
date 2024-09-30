import time
import numpy as np
import pandas as pd
from binance.client import Client
import talib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib  # Import joblib for saving/loading models
import logging
from ..utils.api_utils import fetch_data, place_order

#configuracja
symbol = 'BTCUSDT'
stop_loss_pct = 0.02  # 2% stop-loss
trailing_stop_pct = 0.01  # 1% trailing stop

# Funkcja do obliczania wskaźników
def calculate_indicators(df):
    df['rsi'] = talib.RSI(df['close'], timeperiod=14)
    df['macd'], df['macd_signal'], _ = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
    df['upper_band'], df['middle_band'], df['lower_band'] = talib.BBANDS(df['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    df['sma'] = talib.SMA(df['close'], timeperiod=50)
    df.dropna(inplace=True)

# Funkcja do przygotowania danych dla modelu ML
def prepare_data(df):
    features = df[['rsi', 'macd', 'macd_signal', 'upper_band', 'middle_band', 'lower_band', 'sma']]
    target = (df['close'].shift(-1) > df['close']).astype(int)  # 1 if price goes up, else 0
    return features[:-1], target[:-1]  # Exclude last row for prediction

# Funkcja do trenowania modelu
def train_model(df):
    X, y = prepare_data(df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    print(f'Model accuracy: {model.score(X_test, y_test)}')
    
    # Zapisz model i scaler
    joblib.dump(model, 'trading_model.pkl')
    joblib.dump(scaler, 'scaler.pkl')
    
    return model, scaler

# Funkcja do ładowania modelu
def load_model():
    model = joblib.load('trading_model.pkl')
    scaler = joblib.load('scaler.pkl')
    return model, scaler

# Funkcja do sprawdzania sygnałów
def check_signals(df, model, scaler):
    latest_data = df.iloc[-1][['rsi', 'macd', 'macd_signal', 'upper_band', 'middle_band', 'lower_band', 'sma']].values.reshape(1, -1)
    latest_data_scaled = scaler.transform(latest_data)
    prediction = model.predict(latest_data_scaled)[0]
    
    if prediction == 1:  # Kupno
        return 'buy'
    elif prediction == 0:  # Sprzedaż
        return 'sell'
    return None
        
        
def update_trailing_stop_loss(current_price, trailing_stop_price):
    return max(trailing_stop_price, current_price * (1 - trailing_stop_pct))


# Główna pętla
trailing_stop_price = None
model = None
scaler = None

# Załaduj model i scaler, jeśli istnieją
try:
    model, scaler = load_model()
    print("Loaded existing model and scaler.")
except FileNotFoundError:
    print("Model or scaler not found, training a new model.")

while True:
    df = fetch_data(symbol)
    calculate_indicators(df)

    # Train the model if it's not loaded yet
    if model is None:
        model, scaler = train_model(df)

    signal = check_signals(df, model, scaler)
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