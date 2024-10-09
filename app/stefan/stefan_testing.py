# poprawić algorytmy i machine learning - zeby sie uczyl i to wykozystywał to co wie do podejmowania przyszłych decyzji.
# TESTS NEEDED
import time
import numpy as np
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
import pandas as pd
import logging
from binance.client import Client
import talib
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import joblib
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from ..utils.api_utils import fetch_data, place_order
from ..utils.app_utils import send_email
from .. import db
from ..utils.logging import logger
from ..models import Settings

symbol = 'BTCUSDT'
stop_loss_pct = 0.02
trailing_stop_pct = 0.01
take_profit_pct = 0.03
lookback_days = '30 days'

def create_lstm_model(input_shape):
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=input_shape))
    model.add(Dropout(0.2))
    model.add(LSTM(50))
    model.add(Dropout(0.2))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

def train_lstm_model(X, y):
    model = create_lstm_model((X.shape[1], 1))
    model.fit(X, y, epochs=50, batch_size=32)
    return model

def calculate_indicators(df):
    try:
        df['rsi'] = talib.RSI(df['close'], timeperiod=14)
        df['macd'], df['macd_signal'], _ = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
        df['upper_band'], df['middle_band'], df['lower_band'] = talib.BBANDS(
            df['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        df['sma'] = talib.SMA(df['close'], timeperiod=50)
        df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
        df['stoch'] = talib.STOCHF(df['high'], df['low'], df['close'], fastk_period=14)[0]
        df.dropna(inplace=True)
    except Exception as e:
        logger.error(f'Błąd podczas obliczania wskaźników: {str(e)}')

def prepare_data(df):
    try:
        features = df[['rsi', 'macd', 'macd_signal', 'upper_band',
                       'middle_band', 'lower_band', 'sma', 'atr', 'stoch']]
        target = (df['close'].shift(-1) > df['close']).astype(int)
        return features[:-1], target[:-1]
    except KeyError as e:
        logger.error(f'Brak danych w DataFrame: {str(e)}')
        return None, None

def train_model(df):
    X, y = prepare_data(df)
    if X is None or y is None:
        return None, None
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    model = GradientBoostingClassifier()
    param_grid = {
        'n_estimators': [100, 200],
        'learning_rate': [0.01, 0.1],
        'max_depth': [3, 5, 7],
    }
    grid_search = GridSearchCV(model, param_grid, cv=3)
    grid_search.fit(X_train, y_train)

    best_model = grid_search.best_estimator_
    logger.trade(f'Najlepsze parametry modelu: {grid_search.best_params_}')
    logger.trade(f'Skuteczność modelu: {best_model.score(X_test, y_test)}')

    joblib.dump(best_model, 'model.pkl')
    joblib.dump(scaler, 'scaler.pkl')

    return best_model, scaler

def load_model():
    try:
        model = joblib.load('model.pkl')
        scaler = joblib.load('scaler.pkl')
        logger.trade("Załadowano istniejący model i scaler.")
    except FileNotFoundError:
        logger.trade("Nie znaleziono modelu ani scalera. Tworzę nowy.")
        scaler = StandardScaler()
        model = LinearRegression()
        X_train, y_train = load_initial_training_data()
        scaler.fit(X_train)
        model.fit(X_train, y_train)
        joblib.dump(model, 'model.pkl')
        joblib.dump(scaler, 'scaler.pkl')
        logger.trade("Stworzono i zapisano nowy model i scaler.")
    return model, scaler

def load_initial_training_data():
    X_train = np.random.rand(100, 10)
    y_train = np.random.rand(100)
    return X_train, y_train

def check_signals(df, model, scaler):
    if model is None or scaler is None:
        logger.error("Model lub scaler nie jest załadowany. Nie można sprawdzić sygnałów.")
        return None
    try:
        latest_data = df.iloc[-1][['rsi', 'macd', 'macd_signal', 'upper_band',
                                   'middle_band', 'lower_band', 'sma', 'atr', 'stoch']].values.reshape(1, -1)
        latest_data_scaled = scaler.transform(latest_data)
        prediction = model.predict(latest_data_scaled)[0]
        return 'buy' if prediction == 1 else 'sell' if prediction == 0 else None
    except Exception as e:
        logger.error(f'Błąd przy sprawdzaniu sygnałów: {str(e)}')
        return None

def update_trailing_stop_loss(current_price, trailing_stop_price, atr):
    return max(trailing_stop_price, current_price * (1 - (trailing_stop_pct * (atr / current_price))))

def backtest_strategy(df):
    try:
        df['signal'] = np.where(df['close'].shift(-1) > df['close'], 1, 0)
        df['strategy_returns'] = df['signal'].shift(1) * (df['close'].pct_change())
        df['cumulative_strategy_returns'] = (1 + df['strategy_returns']).cumprod()
        return df
    except Exception as e:
        logger.error(f'Błąd w trakcie backtestingu: {str(e)}')
        return df

def generate_report(current_price, profit_loss, cumulative_returns):
    report = f"""
    Raport Tradingu:
    Aktualna cena: {current_price}
    Zysk/Strata: {profit_loss}
    Skumulowane zwroty strategii: {cumulative_returns}
    """
    logger.trade(report)

trailing_stop_price = None
take_profit_price = None
model, scaler = load_model()

def run_trading_logic():
    try:
        with current_app.app_context():
            settings = Settings.query.first()
            if settings:
                symbol = settings.symbol
                stop_loss_pct = settings.stop_loss_pct
                trailing_stop_pct = settings.trailing_stop_pct
                take_profit_pct = settings.take_profit_pct
                lookback_days = settings.lookback_days
                
                if not settings.bot_running:
                    return

        df = fetch_data(symbol='BTCUSDT', interval='1h', lookback='30 days')
        if df.empty:
            logger.error("Nie udało się pobrać danych z Binance.")
        else:
            logger.info(f"Pobrano dane dla {symbol}")

        calculate_indicators(df)
        signal = check_signals(df, model, scaler)
        current_price = df['close'].iloc[-1]

        if signal == 'buy':
            logger.trade(f"Sygnał kupna przy cenie: {current_price}")
            trailing_stop_price = current_price * (1 - trailing_stop_pct)
            place_order('BTCUSDT', 'buy')

        elif signal == 'sell':
            logger.trade(f"Sygnał sprzedaży przy cenie: {current_price}")
            place_order('BTCUSDT', 'sell')

        if trailing_stop_price:
            trailing_stop_price = update_trailing_stop_loss(current_price, trailing_stop_price, df['atr'].iloc[-1])
            logger.trade(f"Nowa cena trailing stop loss: {trailing_stop_price}")

        profit_loss = (current_price - trailing_stop_price) if trailing_stop_price else 0
        df = backtest_strategy(df)
        cumulative_returns = df['cumulative_strategy_returns'].iloc[-1]
        generate_report(current_price, profit_loss, cumulative_returns)

        time.sleep(60)

    except Exception as e:
        logger.error(f'Błąd w pętli głównej: {str(e)}')
        time.sleep(60)