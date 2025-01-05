from ..utils.logging import logger
from ..utils.app_utils import send_admin_email

def trend_sell_signal(trend, bot_settings):
    if bot_settings.trend_signals:
        return (trend == 'downtrend') 
    return True


def rsi_sell_signal(latest_data, bot_settings):
    if bot_settings.rsi_signals:
        return float(latest_data['rsi']) >= float(bot_settings.rsi_sell) 
    return True


def rsi_divergence_sell_signal(latest_data, averages, bot_settings):
    if bot_settings.rsi_divergence_signals:
        return (float(latest_data['close']) >= float(averages['avg_close']) and
                float(latest_data['rsi']) <= float(averages['avg_rsi'])) 
    return True


def macd_cross_sell_signal(latest_data, previous_data, bot_settings):
    if bot_settings.macd_cross_signals:
        return (float(previous_data['macd']) >= float(previous_data['macd_signal']) and 
                float(latest_data['macd']) <= float(latest_data['macd_signal'])) 
    return True


def macd_histogram_sell_signal(latest_data, previous_data, bot_settings):
    if bot_settings.macd_histogram_signals:
        return (float(previous_data['macd_histogram']) >= 0 and 
                float(latest_data['macd_histogram']) <= 0) 
    return True


def boilinger_sell_signal(latest_data, bot_settings):
    if bot_settings.boilinger_signals:
        return float(latest_data['close']) >= float(latest_data['upper_band'])
    return True


def stoch_sell_signal(latest_data, previous_data, bot_settings):
    if bot_settings.stoch_signals:
        return (float(previous_data['stoch_k']) >= float(previous_data['stoch_d']) and
                float(latest_data['stoch_k']) <= float(latest_data['stoch_d']) and
                float(latest_data['stoch_k']) >= float(bot_settings.stoch_sell)) 
    return True


def stoch_divergence_sell_signal(latest_data, averages, bot_settings):
    if bot_settings.stoch_divergence_signals:
        return (float(latest_data['stoch_k']) <= float(averages['avg_stoch_k']) and
                float(latest_data['close']) >= float(averages['avg_close'])) 
    return True


def stoch_rsi_sell_signal(latest_data, bot_settings):
    if bot_settings.stoch_rsi_signals:
        return (float(latest_data['stoch_rsi_k']) >= float(bot_settings.stoch_sell) and 
                float(latest_data['stoch_rsi_k']) <= float(latest_data['stoch_rsi_d'])) 
    return True


def ema_cross_sell_signal(latest_data, previous_data, bot_settings):
    if bot_settings.ema_cross_signals:
        return (float(previous_data['ema_fast']) >= float(previous_data['ema_slow']) and
                float(latest_data['ema_fast']) <= float(latest_data['ema_slow'])) 
    return True


def ema_fast_sell_signal(latest_data, bot_settings):
    if bot_settings.ema_fast_signals:
        return float(latest_data['close']) <= float(latest_data['ema_fast']) 
    return True


def ema_slow_sell_signal(latest_data, bot_settings):
    if bot_settings.ema_slow_signals:
        return float(latest_data['close']) <= float(latest_data['ema_slow']) 
    return True


def di_cross_sell_signal(latest_data, previous_data, bot_settings):
    if bot_settings.di_signals:
        return (float(previous_data['plus_di']) >= float(previous_data['minus_di']) and 
                float(latest_data['plus_di']) <= float(latest_data['minus_di'])) 
    return True


def cci_sell_signal(latest_data, bot_settings):
    if bot_settings.cci_signals:
        return float(latest_data['cci']) >= float(bot_settings.cci_sell) 
    return True


def cci_divergence_buy_signal(latest_data, averages, bot_settings):
    if bot_settings.cci_divergence_signals:
        return (float(latest_data['close']) >= float(averages['avg_close']) and
                float(latest_data['cci']) <= float(averages['avg_cci'])) 
    return True


def mfi_sell_signal(latest_data, bot_settings):
    if bot_settings.mfi_signals:
        return float(latest_data['mfi']) >= float(bot_settings.mfi_sell) 
    return True


def mfi_divergence_sell_signal(latest_data, averages, bot_settings):
    if bot_settings.mfi_divergence_signals:
        return (float(latest_data['close']) >= float(averages['avg_close']) and
                float(latest_data['mfi']) <= float(averages['avg_mfi'])) 
    return True


def atr_sell_signal(latest_data, averages, bot_settings):
    if bot_settings.atr_signals:
        return float(latest_data['atr']) <= float(averages['avg_atr']) 
    return True


def vwap_sell_signal(latest_data, bot_settings):
    if bot_settings.vwap_signals:
        return float(latest_data['close']) <= float(latest_data['vwap']) 
    return True


def psar_sell_signal(latest_data, bot_settings):
    if bot_settings.psar_signals:
        return float(latest_data['close']) <= float(latest_data['psar']) 
    return True


def ma50_sell_signal(latest_data, bot_settings):
    if bot_settings.ma50_signals:
        return float(latest_data['close']) <= float(latest_data['ma_50']) 
    return True


def ma200_sell_signal(latest_data, bot_settings):
    if bot_settings.ma200_signals:
        return float(latest_data['close']) <= float(latest_data['ma_200']) 
    return True


def check_sell_signal(df, bot_settings, trend, averages, latest_data, previous_data):
    from .logic_utils import is_df_valid
    
    if not is_df_valid(df, bot_settings.id):
        return False
    
    try:

        sell_signals = [
            trend_sell_signal(trend, bot_settings),
            rsi_sell_signal(latest_data, bot_settings),
            rsi_divergence_sell_signal(latest_data, averages, bot_settings),
            macd_cross_sell_signal(latest_data, previous_data, bot_settings),
            macd_histogram_sell_signal(latest_data, previous_data, bot_settings),
            boilinger_sell_signal(latest_data, bot_settings),
            stoch_sell_signal(latest_data, previous_data, bot_settings),
            stoch_divergence_sell_signal(latest_data, averages, bot_settings),
            stoch_rsi_sell_signal(latest_data, bot_settings),
            ema_cross_sell_signal(latest_data, previous_data, bot_settings),
            ema_fast_sell_signal(latest_data, bot_settings),
            ema_slow_sell_signal(latest_data, bot_settings),
            di_cross_sell_signal(latest_data, previous_data, bot_settings),
            cci_sell_signal(latest_data, bot_settings),
            cci_divergence_buy_signal(latest_data, averages, bot_settings),
            mfi_sell_signal(latest_data, bot_settings),
            mfi_divergence_sell_signal(latest_data, averages, bot_settings),
            atr_sell_signal(latest_data, averages, bot_settings),
            vwap_sell_signal(latest_data, bot_settings),
            psar_sell_signal(latest_data, bot_settings),
            ma50_sell_signal(latest_data, bot_settings),
            ma200_sell_signal(latest_data, bot_settings),
        ]

        signals_to_check = [bool(signal) for signal in sell_signals]

        if all(signals_to_check):
            return True
        
        return False

    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in check_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in check_sell_signal', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in check_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in check_sell_signal', str(e))
        return False