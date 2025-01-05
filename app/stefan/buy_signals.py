from ..utils.logging import logger
from ..utils.app_utils import send_admin_email

def trend_buy_signal(trend, bot_settings):
    if bot_settings.trend_signals:
        return (trend == 'uptrend')
    return True


def rsi_buy_signal(latest_data, averages, bot_settings):
    if bot_settings.rsi_signals:
        return (float(latest_data['rsi']) <= float(bot_settings.rsi_buy) and
                float(latest_data['rsi']) >= float(averages['avg_rsi'])) 
    return True


def rsi_divergence_buy_signal(latest_data, averages, bot_settings):
    if bot_settings.rsi_divergence_signals:
        return (float(latest_data['close']) <= float(averages['avg_close']) and
                float(latest_data['rsi']) >= float(averages['avg_rsi'])) 
    return True


def vol_rising(latest_data, averages, bot_settings):
    if bot_settings.vol_signals:
        return float(latest_data['volume']) >= float(averages['avg_volume']) 
    return True


def macd_cross_buy_signal(latest_data, previous_data, bot_settings):
    if bot_settings.macd_cross_signals:
        return (float(previous_data['macd']) <= float(previous_data['macd_signal']) and
                float(latest_data['macd']) >= float(latest_data['macd_signal'])) 
    return True


def macd_histogram_buy_signal(latest_data, previous_data, bot_settings):
    if bot_settings.macd_histogram_signals:
        return (float(previous_data['macd_histogram']) <= 0 and
                float(latest_data['macd_histogram']) >= 0) 
    return True


def boilinger_buy_signal(latest_data, bot_settings):
    if bot_settings.boilinger_signals:
        return float(latest_data['close']) <= float(latest_data['lower_band'])
    return True


def stoch_buy_signal(latest_data, previous_data, bot_settings):
    if bot_settings.stoch_signals:
        return (float(previous_data['stoch_k']) <= float(previous_data['stoch_d']) and
                float(latest_data['stoch_k']) >= float(latest_data['stoch_d']) and
                float(latest_data['stoch_k']) <= float(bot_settings.stoch_buy)) 
    return True


def stoch_divergence_buy_signal(latest_data, averages, bot_settings):
    if bot_settings.stoch_divergence_signals:
        return (float(latest_data['stoch_k']) >= float(averages['avg_stoch_k']) and
                float(latest_data['close']) <= float(averages['avg_close'])) 
    return True


def stoch_rsi_buy_signal(latest_data, averages, bot_settings):
    if bot_settings.stoch_rsi_signals:
        return (float(latest_data['stoch_rsi_k']) <= float(bot_settings.stoch_buy) and
                float(latest_data['stoch_rsi_k']) >= float(averages['avg_stoch_rsi_k'])) 
    return True


def ema_cross_buy_signal(latest_data, previous_data, bot_settings):
    if bot_settings.ema_cross_signals:
        return (float(previous_data['ema_fast']) <= float(previous_data['ema_slow']) and
                float(latest_data['ema_fast']) >= float(latest_data['ema_slow'])) 
    return True


def ema_fast_buy_signal(latest_data, averages, bot_settings):
    if bot_settings.ema_fast_signals:
        return float(latest_data['close']) >= float(averages['avg_ema_fast']) 
    return True


def ema_slow_buy_signal(latest_data, averages, bot_settings):
    if bot_settings.ema_slow_signals:
        return float(latest_data['close']) >= float(averages['avg_ema_slow']) 
    return True


def di_cross_buy_signal(latest_data, previous_data, bot_settings):
    if bot_settings.di_signals:
        return (float(previous_data['plus_di']) <= float(previous_data['minus_di']) and
                    float(latest_data['plus_di']) >= float(latest_data['minus_di'])) 
    return True


def cci_buy_signal(latest_data, averages, bot_settings):
    if bot_settings.cci_signals:
        return (float(latest_data['cci']) <= float(bot_settings.cci_buy) and
                float(latest_data['cci']) >= float(averages['avg_cci']))  
    return True


def cci_divergence_buy_signal(latest_data, averages, bot_settings):
    if bot_settings.cci_divergence_signals:
        return (float(latest_data['close']) <= float(averages['avg_close']) and
                float(latest_data['cci']) >= float(averages['avg_cci'])) 
    return True


def mfi_buy_signal(latest_data, averages, bot_settings):
    if bot_settings.mfi_signals:
        return (float(latest_data['mfi']) <= float(bot_settings.mfi_buy) and
                float(latest_data['mfi']) >= float(averages['avg_mfi'])) 
    return True


def mfi_divergence_buy_signal(latest_data, averages, bot_settings):
    if bot_settings.mfi_divergence_signals:
        return (float(latest_data['close']) <= float(averages['avg_close']) and
                float(latest_data['mfi']) >= float(averages['avg_mfi'])) 
    return True


def atr_buy_signal(latest_data, averages, bot_settings):
    if bot_settings.atr_signals:
        atr_buy_level = bot_settings.atr_buy_treshold * float(latest_data['close'])
        return (float(latest_data['atr']) >= float(averages['avg_atr']) and
                float(latest_data['atr']) >= float(atr_buy_level))
    return True


def vwap_buy_signal(latest_data, bot_settings):
    if bot_settings.vwap_signals:
        return float(latest_data['close']) >= float(latest_data['vwap']) 
    return True


def psar_buy_signal(latest_data, previous_data, bot_settings):
    if bot_settings.psar_signals:
        return (float(previous_data['psar']) >= float(previous_data['close']) and
                float(latest_data['psar']) <= float(latest_data['close'])) 
    return True


def ma50_buy_signal(latest_data, bot_settings):
    if bot_settings.ma50_signals:
        return float(latest_data['close']) >= float(latest_data['ma_50']) 
    return True


def ma200_buy_signal(latest_data, bot_settings):
    if bot_settings.ma200_signals:
        return float(latest_data['close']) >= float(latest_data['ma_200']) 
    return True

    
def check_buy_signal(df, bot_settings, trend, averages, latest_data, previous_data):
    from .logic_utils import is_df_valid
    
    if not is_df_valid(df, bot_settings.id):
        return False
    
    try:
        
        if trend == 'downtrend':
            return False

        buy_signals = [
            trend_buy_signal(trend, bot_settings),
            rsi_buy_signal(latest_data, averages, bot_settings),
            rsi_divergence_buy_signal(latest_data, averages, bot_settings),
            vol_rising(latest_data, averages, bot_settings),
            macd_cross_buy_signal(latest_data, previous_data, bot_settings),
            macd_histogram_buy_signal(latest_data, previous_data, bot_settings),
            boilinger_buy_signal(latest_data, bot_settings),
            stoch_buy_signal(latest_data, previous_data, bot_settings),
            stoch_divergence_buy_signal(latest_data, averages, bot_settings),
            stoch_rsi_buy_signal(latest_data, averages, bot_settings),
            ema_cross_buy_signal(latest_data, previous_data, bot_settings),
            ema_fast_buy_signal(latest_data, averages, bot_settings),
            ema_slow_buy_signal(latest_data, averages, bot_settings),
            di_cross_buy_signal(latest_data, previous_data, bot_settings),
            cci_buy_signal(latest_data, averages, bot_settings),
            cci_divergence_buy_signal(latest_data, averages, bot_settings),
            mfi_buy_signal(latest_data, averages, bot_settings),
            mfi_divergence_buy_signal(latest_data, averages, bot_settings),
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