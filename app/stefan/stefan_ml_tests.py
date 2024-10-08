#TESTS NEEDED
import time
import numpy as np
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
from ..utils.api_utils import fetch_data, place_order, get_account_balance
from ..utils.app_utils import send_email
from .. import db
from ..utils.logging import logger
from ..models import Settings

# Configuration
symbol = 'BTCUSDT'
stop_loss_pct = 0.02  # 2% stop-loss
trailing_stop_pct = 0.01  # 1% trailing stop
take_profit_pct = 0.03  # 3% take profit
lookback_days = '30 days'  # Length of historical data

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
    df['rsi'] = talib.RSI(df['close'], timeperiod=14)
    df['macd'], df['macd_signal'], _ = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
    df['upper_band'], df['middle_band'], df['lower_band'] = talib.BBANDS(
        df['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    df['sma'] = talib.SMA(df['close'], timeperiod=50)
    df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
    df['stoch'] = talib.STOCHF(df['high'], df['low'], df['close'], fastk_period=14)[0]
    df.dropna(inplace=True)

def prepare_data(df):
    features = df[['rsi', 'macd', 'macd_signal', 'upper_band',
                   'middle_band', 'lower_band', 'sma', 'atr', 'stoch']]
    target = (df['close'].shift(-1) > df['close']).astype(int)
    return features[:-1], target[:-1]

def train_model(df):
    X, y = prepare_data(df)
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
    logger.trade(f'Best model parameters: {grid_search.best_params_}')
    logger.trade(f'Model accuracy: {best_model.score(X_test, y_test)}')

    joblib.dump(best_model, 'trading_model.pkl')
    joblib.dump(scaler, 'scaler.pkl')

    return best_model, scaler

def load_model():
    try:
        model = joblib.load('model.pkl')
        scaler = joblib.load('scaler.pkl')
        logger.trade("Loaded existing model and scaler.")
    except FileNotFoundError:
        logger.trade("Model or scaler not found, creating new model and scaler.")

        # Create a new scaler and model
        scaler = StandardScaler()
        model = LinearRegression()

        # Load initial training data (you need to implement this function)
        X_train, y_train = load_initial_training_data()  # Implement this function to get your initial data

        # Fit the scaler on the training data
        scaler.fit(X_train)

        # Train the model
        model.fit(X_train, y_train)

        # Save the new model and scaler for future use
        joblib.dump(model, 'model.pkl')
        joblib.dump(scaler, 'scaler.pkl')
        logger.trade("Created and saved new model and scaler.")

    return model, scaler

def load_initial_training_data():
    # Load your initial training data here
    # This is just a placeholder example; replace it with your actual data loading logic
    X_train = np.random.rand(100, 10)  # Example feature data
    y_train = np.random.rand(100)       # Example target data
    return X_train, y_train

def check_signals(df, model, scaler):
    if not hasattr(scaler, 'scale_'):
        logger.trade("Scaler is not fitted yet. Cannot transform new data.")
        return None
    latest_data = df.iloc[-1][['rsi', 'macd', 'macd_signal', 'upper_band',
                               'middle_band', 'lower_band', 'sma', 'atr', 'stoch']].values.reshape(1, -1)
    latest_data_scaled = scaler.transform(latest_data)
    prediction = model.predict(latest_data_scaled)[0]

    return 'buy' if prediction == 1 else 'sell' if prediction == 0 else None

def update_trailing_stop_loss(current_price, trailing_stop_price, atr):
    return max(trailing_stop_price, current_price * (1 - (trailing_stop_pct * (atr / current_price))))

def backtest_strategy(df):
    df['signal'] = np.where(df['close'].shift(-1) > df['close'], 1, 0)
    df['strategy_returns'] = df['signal'].shift(1) * (df['close'].pct_change())
    df['cumulative_strategy_returns'] = (1 + df['strategy_returns']).cumprod()
    return df

# Main loop
trailing_stop_price = None
take_profit_price = None
model, scaler = load_model()

while True:
    try:
        settings = Settings.query.first()
        if settings:
            symbol = settings.symbol
            stop_loss_pct = settings.stop_loss_pct
            trailing_stop_pct = settings.trailing_stop_pct
            take_profit_pct = settings.take_profit_pct
            lookback_days = settings.lookback_days

            if not settings.bot_running:
                time.sleep(60)
                continue

        df = fetch_data(symbol, lookback=lookback_days)
        calculate_indicators(df)

        if model is None:
            X, y = prepare_data(df)
            model = train_lstm_model(X, y)

        df_backtest = backtest_strategy(df)
        logger.trade(f"Cumulative Strategy Returns: {df_backtest['cumulative_strategy_returns'].iloc[-1]}")

        signal = check_signals(df, model, scaler)
        current_price = df['close'].iloc[-1]
        atr = df['atr'].iloc[-1]

        account_balance = get_account_balance()
        amount = account_balance['USDC']

        if signal == 'buy':
            place_order(symbol, 'buy', amount / current_price)
            logger.trade(f'Bought {amount / current_price} BTC')
            trailing_stop_price = current_price * (1 - trailing_stop_pct)
            take_profit_price = current_price * (1 + take_profit_pct)

        elif signal == 'sell' and trailing_stop_price is not None:
            place_order(symbol, 'sell', amount / current_price)
            logger.trade(f'Sold {amount / current_price} BTC')
            trailing_stop_price = None
            take_profit_price = None

        if take_profit_price is not None and current_price >= take_profit_price:
            place_order(symbol, 'sell', amount / current_price)
            logger.trade(f'Take Profit triggered: Sold {amount / current_price} BTC at {current_price}')
            take_profit_price = None

        if trailing_stop_price is not None:
            trailing_stop_price = update_trailing_stop_loss(current_price, trailing_stop_price, atr)

        time.sleep(300)  # Wait for 5 minutes before the next cycle

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        # Send an email with the error details
        send_email('piotrek.gaszczynski@gmail.com', 'Trading Bot Error', f'An error occurred: {e}')
        # Optionally, you can decide to continue or break the loop
        #continue
        break