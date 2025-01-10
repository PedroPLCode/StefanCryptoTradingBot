from tensorflow.keras.models import load_model
from ..utils.logging import logger
from ..utils.app_utils import send_admin_email
from ..mariola.mariola_calc import calculate_df
from ..mariola.mariola_utils import (
    normalize_df, 
    handle_pca, 
    create_sequences
)

def check_model_ml_trade_signal(df, signal_type, bot_settings):
    try:

        if signal_type not in ['buy', 'sell']:
            raise ValueError(f"Unsupported signal_type: {signal_type}")

        model_predictions = {
            period: price_change_pct_predict(
                df, 
                getattr(bot_settings, f"ml_model_{period}_filename"), 
                getattr(bot_settings, f"ml_predictions_{period}_avg"), 
                bot_settings
            ) if getattr(bot_settings, f"ml_use_regresion_on_next_{period}", False) else False
            for period in bot_settings.ml_predictions_periods
        }

        if signal_type == 'buy':
            result = any(
                model_predictions.get(period, 0) >= getattr(bot_settings, f"ml_buy_trigger_{period}_pct", float('inf'))
                for period in model_predictions
            )
            logger.trade(f"ML Buy signal: {result}, model predictions: {model_predictions}")
            return result
        elif signal_type == 'sell':
            result = any(
                model_predictions.get(period, 0) <= getattr(bot_settings, f"ml_sell_trigger_{period}_pct", float('-inf'))
                for period in model_predictions
            )
            logger.trade(f"ML Sell signal: {result}, model predictions: {model_predictions}")
            return result

    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in check_model_ml_trade_signal: {str(e)}")
        send_admin_email(f"Bot {bot_settings.id} Exception in check_model_ml_trade_signal", str(e))
        return None


def price_change_pct_predict(
    df, 
    model_filename, 
    avg_predictions_period, 
    bot_settings
    ):

    try:
            
        calculated_df = calculate_df(
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
            bot_settings.ml_window_lookback, 
            bot_settings.ml_window_size,
            bot_settings
            )
        
        loaded_model = load_model(f'app/mariola/models/{model_filename}')
        y_pred = loaded_model.predict(X)
        
        return y_pred[-avg_predictions_period]
    
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in mariola_predict: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in mariola_predict', str(e))
        return None