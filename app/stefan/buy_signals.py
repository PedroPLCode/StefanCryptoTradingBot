from ..utils.logging import logger
from ..utils.app_utils import send_admin_email

def trend_buy_signal(trend, bot_settings):
    return (trend == 'uptrend') if bot_settings.trend_signals else True


def rsi_buy_signal(latest_data, averages, bot_settings):
    return (float(latest_data['rsi']) <= float(bot_settings.rsi_buy) and
            float(latest_data['rsi']) > float(averages['avg_rsi'])) if bot_settings.rsi_signals else True


def vol_rising(latest_data, averages, bot_settings):
    return float(latest_data['volume']) > float(averages['avg_volume']) if bot_settings.vol_signals else True


def macd_cross_buy_signal(latest_data, averages, bot_settings):
    return ((float(averages['avg_macd']) < float(averages['avg_macd_signal']) and
             float(latest_data['macd']) > float(latest_data['macd_signal'])) if bot_settings.macd_cross_signals else True)


def macd_histogram_buy_signal(latest_data, previous_data, bot_settings):
    return (float(previous_data['macd_histogram']) < 0 and
            float(latest_data['macd_histogram']) > 0) if bot_settings.macd_histogram_signals else True


def boilinger_buy_signal(latest_data, bot_settings):
    return float(latest_data['close']) <= float(latest_data['lower_band']) if bot_settings.boilinger_signals else True


def stoch_buy_signal(latest_data, averages, bot_settings):
    return ((float(averages['avg_stoch_k']) < float(averages['avg_stoch_d']) and
             float(latest_data['stoch_k']) > float(latest_data['stoch_d']) and
             float(latest_data['stoch_k']) <= float(bot_settings.stoch_buy)) if bot_settings.stoch_signals else True)


def stoch_rsi_buy_signal(latest_data, averages, bot_settings):
    return (float(latest_data['stoch_rsi_k']) <= float(bot_settings.stoch_buy) and
            float(latest_data['stoch_rsi_k']) > float(averages['avg_stoch_rsi_k'])) if bot_settings.stoch_rsi_signals else True


def ema_cross_buy_signal(latest_data, averages, bot_settings):
    return (float(averages['avg_ema_fast']) < float(averages['avg_ema_slow']) and
            float(latest_data['ema_fast']) > float(latest_data['ema_slow'])) if bot_settings.ema_cross_signals else True


def ema_fast_buy_signal(latest_data, averages, bot_settings):
    return float(latest_data['close']) >= float(averages['avg_ema_fast']) if bot_settings.ema_fast_signals else True


def ema_slow_buy_signal(latest_data, averages, bot_settings):
    return float(latest_data['close']) >= float(averages['avg_ema_slow']) if bot_settings.ema_slow_signals else True


def di_cross_buy_signal(latest_data, averages, bot_settings):
    return (float(averages['avg_plus_di']) < float(averages['avg_minus_di']) and
                float(latest_data['plus_di']) > float(latest_data['minus_di'])) if bot_settings.di_signals else True


def cci_buy_signal(latest_data, averages, bot_settings):
    return (float(latest_data['cci']) <= float(bot_settings.cci_buy) and
            float(latest_data['cci']) > float(averages['avg_cci'])) if bot_settings.cci_signals else True


def mfi_buy_signal(latest_data, averages, bot_settings):
    return (float(latest_data['mfi']) <= float(bot_settings.mfi_buy) and
            float(latest_data['mfi']) > float(averages['avg_mfi'])) if bot_settings.mfi_signals else True


def atr_buy_signal(latest_data, averages, bot_settings):
    return (float(latest_data['atr']) > float(averages['avg_atr']) and
            float(latest_data['atr']) > bot_settings.atr_treshold * float(latest_data['close'])) if bot_settings.atr_signals else True


def vwap_buy_signal(latest_data, bot_settings):
    return float(latest_data['close']) > float(latest_data['vwap']) if bot_settings.vwap_signals else True


def psar_buy_signal(latest_data, previous_data, bot_settings):
    return (float(previous_data['psar']) > float(previous_data['close']) and
            float(latest_data['psar']) < float(latest_data['close'])) if bot_settings.psar_signals else True


def ma50_buy_signal(latest_data, bot_settings):
    return float(latest_data['close']) >= float(latest_data['ma_50']) if bot_settings.ma50_signals else True


def ma200_buy_signal(latest_data, bot_settings):
    return float(latest_data['close']) >= float(latest_data['ma_200']) if bot_settings.ma200_signals else True

    
def check_buy_signal(df, bot_settings, trend, averages, latest_data, previous_data):
    from .logic_utils import is_df_valid
    
    if not is_df_valid(df, bot_settings.id):
        return False

    if not latest_data:
        logger.warning(f"Missing or invalid 'latest_data' for bot {bot_settings.id}")
        return False
    
    if not previous_data:
        logger.warning(f"Missing or invalid 'previous_data' for bot {bot_settings.id}")
        return False
    
    if not trend:
        logger.warning(f"Missing or invalid 'trend' for bot {bot_settings.id}")
        return False
    
    #if not isinstance(averages, dict):
    #    logger.warning(f"'averages' is not a valid dictionary for bot {bot_settings.id}")
    #    return False
    
    try:
        
        if trend == 'downtrend':
            return False

        buy_signals = [
            trend_buy_signal(trend, bot_settings),
            rsi_buy_signal(latest_data, averages, bot_settings),
            vol_rising(latest_data, averages, bot_settings),
            macd_cross_buy_signal(latest_data, averages, bot_settings),
            macd_histogram_buy_signal(latest_data, previous_data, bot_settings),
            boilinger_buy_signal(latest_data, bot_settings),
            stoch_buy_signal(latest_data, averages, bot_settings),
            stoch_rsi_buy_signal(latest_data, averages, bot_settings),
            ema_cross_buy_signal(latest_data, averages, bot_settings),
            ema_fast_buy_signal(latest_data, averages, bot_settings),
            ema_slow_buy_signal(latest_data, averages, bot_settings),
            di_cross_buy_signal(latest_data, averages, bot_settings),
            cci_buy_signal(latest_data, averages, bot_settings),
            mfi_buy_signal(latest_data, averages, bot_settings),
            atr_buy_signal(latest_data, averages, bot_settings),
            vwap_buy_signal(latest_data, bot_settings),
            psar_buy_signal(latest_data, previous_data, bot_settings),
            ma50_buy_signal(latest_data, bot_settings),
            ma200_buy_signal(latest_data, bot_settings)
        ]
        
        signals_to_check = [bool(signal) for signal in buy_signals]

        if all(signals_to_check):
            return True
        
        return False

    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in check_buy_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in check_buy_signal', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in check_buy_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in check_buy_signal', str(e))
        return False