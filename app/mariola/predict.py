from ..utils.logging import logger
from ..utils.exception_handlers import exception_handler
from .df_utils import prepare_ml_df


@exception_handler()
def check_ml_trade_signal(df, signal_type, bot_settings):
    """
    Checks if the given ML model's trade signal (buy or sell) meets the trigger percentage.

    Args:
        df (DataFrame): The input data frame containing market data.
        signal_type (str): The type of signal ('buy' or 'sell').
        bot_settings (object): The bot settings object containing model and trigger values.

    Returns:
        bool: Whether the signal meets the model's buy/sell trigger.
        None: If an error occurs.
    """
    if signal_type not in ["buy", "sell"]:
        raise ValueError(f"Unsupported signal_type: {signal_type}")

    model_predictions = None
    model_name = None
    buy_trigger_pct = None
    sell_trigger_pct = None

    if bot_settings.ml_use_random_forest_model:
        model_name = "RandomForestRegressor"
        buy_trigger_pct = bot_settings.ml_random_forest_buy_trigger_pct
        sell_trigger_pct = bot_settings.ml_random_forest_sell_trigger_pct
        model_predictions = random_forest_price_change_pct_predict(df, bot_settings)
    elif bot_settings.ml_use_xgboost_model:
        model_name = "XGBoostRegressor"
        buy_trigger_pct = bot_settings.ml_xgboost_buy_trigger_pct
        sell_trigger_pct = bot_settings.ml_xgboost_sell_trigger_pct
        model_predictions = xgboost_price_change_pct_predict(df, bot_settings)
    elif bot_settings.ml_use_lstm_model:
        model_name = "LSTM"
        buy_trigger_pct = bot_settings.ml_lstm_buy_trigger_pct
        sell_trigger_pct = bot_settings.ml_lstm_sell_trigger_pct
        model_predictions = lstm_price_change_pct_predict(df, bot_settings)
    else:
        raise ValueError("No ML model is enabled in bot settings")

    if signal_type == "buy":
        result = (
            model_predictions >= buy_trigger_pct
            if model_predictions is not None
            else False
        )
    elif signal_type == "sell":
        result = (
            model_predictions <= sell_trigger_pct
            if model_predictions is not None
            else False
        )

    logger.trade(
        f"ML {model_name if model_name else 'ModelNameUndefined'} {signal_type.capitalize()} signal: {result}, "
        f"model predictions: {model_predictions}, trigger_pct: {buy_trigger_pct if signal_type == 'buy' else sell_trigger_pct}"
    )
    return result


@exception_handler()
def lstm_price_change_pct_predict(df, bot_settings):
    """
    Predicts the price change percentage using an LSTM model.

    Args:
        df (DataFrame): The input data frame containing market data.
        bot_settings (object): The bot settings object containing LSTM model configuration.

    Returns:
        float: The predicted price change percentage from the LSTM model.
        None: If an error occurs.
    """
    from tensorflow.keras.models import load_model
    from .ml_utils import normalize_df, handle_pca, create_sequences

    calculated_df = prepare_ml_df(df, bot_settings)

    df_normalized = normalize_df(calculated_df, bot_settings)

    df_reduced = handle_pca(df_normalized, bot_settings)

    X = create_sequences(
        df_reduced,
        bot_settings.ml_lstm_window_lookback,
        bot_settings.ml_lstm_window_size,
        bot_settings,
    )

    model_filename = bot_settings.ml_lstm_model_filename
    model_path = f"app/mariola/models/{model_filename}"
    loaded_model = load_model(model_path)

    y_pred = loaded_model.predict(X)

    avg_predictions_period = bot_settings.ml_lstm_predictions_avg

    return y_pred[-avg_predictions_period:].mean()


@exception_handler()
def xgboost_price_change_pct_predict(df, bot_settings):
    """
    Predicts the price change percentage using an XGBoost model.

    Args:
        df (DataFrame): The input data frame containing market data.
        bot_settings (object): The bot settings object containing XGBoost model configuration.

    Returns:
        float: The predicted price change percentage from the XGBoost model.
        None: If an error occurs.
    """
    import numpy as np
    import xgboost as xgb
    from sklearn.preprocessing import StandardScaler

    calculated_df = prepare_ml_df(df, bot_settings)

    X = calculated_df.fillna(0)
    X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model_filename = bot_settings.ml_xgboost_model_filename
    model_path = f"app/mariola/models/{model_filename}"
    model = xgb.Booster()
    model.load_model(model_path)

    if isinstance(X_scaled, tuple):
        X_scaled = X_scaled[0]
    X_scaled = X_scaled.reshape(X_scaled.shape[0], -1)
    dmatrix = xgb.DMatrix(X_scaled)

    y_pred = model.predict(dmatrix)

    avg_predictions_period = bot_settings.ml_xgboost_predictions_avg

    return y_pred[-avg_predictions_period:].mean()


@exception_handler()
def random_forest_price_change_pct_predict(df, bot_settings):
    """
    Predicts the price change percentage using a Random Forest model.

    Args:
        df (DataFrame): The input data frame containing market data.
        bot_settings (object): The bot settings object containing Random Forest model configuration.

    Returns:
        float: The predicted price change percentage from the Random Forest model.
        None: If an error occurs.
    """
    import joblib
    import numpy as np
    from sklearn.preprocessing import StandardScaler

    calculated_df = prepare_ml_df(df, bot_settings)

    model_filename = bot_settings.ml_random_forest_model_filename
    model_path = f"app/mariola/models/{model_filename}"
    model = joblib.load(model_path)

    X_new = calculated_df
    X_new = np.nan_to_num(X_new, nan=0.0, posinf=0.0, neginf=0.0)

    scaler = StandardScaler()
    X_new = scaler.fit_transform(X_new)

    y_pred = model.predict(X_new)

    avg_predictions_period = bot_settings.ml_random_forest_predictions_avg

    return y_pred[-avg_predictions_period:].mean()
