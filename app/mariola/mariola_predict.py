from ..utils.logging import logger
from ..utils.app_utils import send_admin_email
from ..mariola.mariola_calc import prepare_df

def check_ml_trade_signal(df, signal_type, bot_settings):
    try:

        if signal_type not in ['buy', 'sell']:
            raise ValueError(f"Unsupported signal_type: {signal_type}")

        model_predictions = None
        model_name = None
        buy_trigger_pct = None
        sell_trigger_pct = None

        if bot_settings.ml_use_random_forest_model:
            model_name= 'RandomForestRegressor'
            buy_trigger_pct = bot_settings.ml_random_forest_buy_trigger_pct
            sell_trigger_pct = bot_settings.ml_random_forest_sell_trigger_pct
            model_predictions = random_forest_price_change_pct_predict(df, bot_settings)
        elif bot_settings.ml_use_xgboost_model:
            model_name= 'XGBoostRegressor'
            buy_trigger_pct = bot_settings.ml_xgboost_buy_trigger_pct
            sell_trigger_pct = bot_settings.ml_xgboost_sell_trigger_pct
            model_predictions = xgboost_price_change_pct_predict(df, bot_settings)
        elif bot_settings.ml_use_lstm_model:
            model_name= 'LSTM'
            buy_trigger_pct = bot_settings.ml_lstm_buy_trigger_pct
            sell_trigger_pct = bot_settings.ml_lstm_sell_trigger_pct
            model_predictions = lstm_price_change_pct_predict(df, bot_settings)
        else:
            raise ValueError("No ML model is enabled in bot settings")
        
        if signal_type == 'buy':
            result = model_predictions >= buy_trigger_pct if model_predictions is not None else False
        elif signal_type == 'sell':
            result = model_predictions <= sell_trigger_pct if model_predictions is not None else False

        logger.trade(
            f"ML {model_name if model_name else 'UNDEFINED'} {signal_type.capitalize()} signal: {result}, "
            f"model predictions: {model_predictions}, trigger_pct: {buy_trigger_pct if signal_type == 'buy' else sell_trigger_pct}"
        )
        return result

    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in check_ml_trade_signal: {str(e)}")
        send_admin_email(f"Bot {bot_settings.id} Exception in check_ml_trade_signal", str(e))
        return None


def lstm_price_change_pct_predict(
    df, 
    bot_settings
    ):
    from tensorflow.keras.models import load_model
    from ..mariola.mariola_utils import (
        normalize_df, 
        handle_pca, 
        create_sequences
    )

    try:
            
        calculated_df = prepare_df(
            df, 
            bot_settings
            )

        df_normalized = normalize_df(
            calculated_df,
            bot_settings
            )

        df_reduced = handle_pca(
            df_normalized, 
            bot_settings
            )

        X = create_sequences(
            df_reduced, 
            bot_settings.ml_lstm_window_lookback, 
            bot_settings.ml_lstm_window_size,
            bot_settings
            )
        
        model_filename = bot_settings.ml_lstm_model_filename
        model_path = f'app/mariola/models/{model_filename}'
        loaded_model = load_model(model_path)
        
        y_pred = loaded_model.predict(X)
        
        avg_predictions_period = bot_settings.ml_lstm_predictions_avg
        
        return y_pred[-avg_predictions_period:].mean()
    
    except FileNotFoundError as e:
        logger.error(f"Bot {bot_settings.id} lstm_price_change_pct_predict. LSTM Model file not found: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} LSTM Model file not found', f'Exception in lstm_price_change_pct_predict.\nLSTM Model file not found: {model_filename}\nError: {str(e)}')
        return None
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in lstm_price_change_pct_predict: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in lstm_price_change_pct_predict', str(e))
        return None
    
    
def xgboost_price_change_pct_predict(
    df, 
    bot_settings
    ):
    import numpy as np
    import xgboost as xgb
    from sklearn.preprocessing import StandardScaler
    
    try:
            
        calculated_df = prepare_df(
            df, 
            bot_settings
            )

        X = calculated_df.fillna(0)
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        model_filename = bot_settings.ml_lstm_model_filename
        model_path = f'app/mariola/models/{model_filename}'
        model = xgb.Booster()
        model.load_model(model_path)
        
        if isinstance(X_scaled, tuple):
            X_scaled = X_scaled[0]
        X_scaled = X_scaled.reshape(X_scaled.shape[0], -1)
        dmatrix = xgb.DMatrix(X_scaled)
        
        y_pred = model.predict(dmatrix)
        
        avg_predictions_period = bot_settings.ml_xgboost_predictions_avg
        
        return y_pred[-avg_predictions_period:].mean()
    
    except FileNotFoundError as e:
        logger.error(f"Bot {bot_settings.id} xgboost_price_change_pct_predict. XGBoost Model file not found: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} XGBoost Model file not found', f'Exception in xgboost_price_change_pct_predict.\nXGBoost Model file not found: {model_filename}\nError: {str(e)}')
        return None
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in xgboost_price_change_pct_predict: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in xgboost_price_change_pct_predict', str(e))
        return None
    
    
def random_forest_price_change_pct_predict(
    df, 
    bot_settings
    ):
    import joblib
    import numpy as np
    from sklearn.preprocessing import StandardScaler

    try:
            
        calculated_df = prepare_df(
            df, 
            bot_settings
            )

        model_filename = bot_settings.ml_lstm_model_filename
        model_path = f'app/mariola/models/{model_filename}'
        model = joblib.load(model_path)

        X_new = calculated_df
        X_new = np.nan_to_num(X_new, nan=0.0, posinf=0.0, neginf=0.0)
        
        scaler = StandardScaler()
        X_new = scaler.fit_transform(X_new)
        
        y_pred = model.predict(X_new)
        
        avg_predictions_period = bot_settings.ml_random_forest_predictions_avg
        
        return y_pred[-avg_predictions_period:].mean()
    
    except FileNotFoundError as e:
        logger.error(f"Bot {bot_settings.id} random_forest_price_change_pct_predict. RandomForest  Model file not found: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} RandomForest Model file not found', f'Exception in random_forest_price_change_pct_predict.\nRandomForest  Model file not found: {model_filename}\nError: {str(e)}')
        return None
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in random_forest_price_change_pct_predict: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in random_forest_price_change_pct_predict', str(e))
        return None