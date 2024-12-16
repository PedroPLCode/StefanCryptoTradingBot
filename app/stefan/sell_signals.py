from ..utils.logging import logger
from ..utils.app_utils import send_admin_email

def trend_sell_signal(trend, bot_settings):
    return (trend == 'downtrend') if bot_settings.trend_signals else True


def rsi_sell_signal(latest_data, bot_settings):
    return float(latest_data['rsi']) >= float(bot_settings.rsi_sell) if bot_settings.rsi_signals else True


def macd_cross_sell_signal(averages, latest_data, bot_settings):
    return (
        float(averages['avg_macd']) > float(averages['avg_macd_signal']) and
        float(latest_data['macd']) < float(latest_data['macd_signal'])
    ) if bot_settings.macd_cross_signals else True


def macd_histogram_sell_signal(latest_data, previous_data, bot_settings):
    return (
        float(previous_data['macd_histogram']) > 0 and
        float(latest_data['macd_histogram']) < 0
    ) if bot_settings.macd_histogram_signals else True


def boilinger_sell_signal(latest_data, bot_settings):
    return float(latest_data['close']) >= float(latest_data['upper_band']) if bot_settings.boilinger_signals else True


def stoch_sell_signal(averages, latest_data, bot_settings):
    return (
        float(averages['avg_stoch_k']) > float(averages['avg_stoch_d']) and
        float(latest_data['stoch_k']) < float(latest_data['stoch_d']) and
        float(latest_data['stoch_k']) >= float(bot_settings.stoch_sell)
    ) if bot_settings.stoch_signals else True


def stoch_rsi_sell_signal(latest_data, bot_settings):
    return (
        float(latest_data['stoch_rsi_k']) >= float(bot_settings.stoch_sell) and
        float(latest_data['stoch_rsi_k']) < float(latest_data['stoch_rsi_d'])
    ) if bot_settings.stoch_rsi_signals else True


def ema_cross_sell_signal(averages, latest_data, bot_settings):
    return (
        float(averages['avg_ema_fast']) > float(averages['avg_ema_slow']) and
        float(latest_data['ema_fast']) < float(latest_data['ema_slow'])
    ) if bot_settings.ema_cross_signals else True


def ema_fast_sell_signal(latest_data, bot_settings):
    return float(latest_data['close']) <= float(latest_data['ema_fast']) if bot_settings.ema_fast_signals else True


def ema_slow_sell_signal(latest_data, bot_settings):
    return float(latest_data['close']) <= float(latest_data['ema_slow']) if bot_settings.ema_slow_signals else True


def di_cross_sell_signal(averages, latest_data, bot_settings):
    return (
        float(averages['avg_plus_di']) > float(averages['avg_minus_di']) and
        float(latest_data['plus_di']) < float(latest_data['minus_di'])
    ) if bot_settings.di_signals else True


def cci_sell_signal(latest_data, bot_settings):
    return float(latest_data['cci']) >= float(bot_settings.cci_sell) if bot_settings.cci_signals else True


def mfi_sell_signal(latest_data, bot_settings):
    return float(latest_data['mfi']) >= float(bot_settings.mfi_sell) if bot_settings.mfi_signals else True


def atr_sell_signal(latest_data, averages, bot_settings):
    return float(latest_data['atr']) < float(averages['avg_atr']) if bot_settings.atr_signals else True


def vwap_sell_signal(latest_data, bot_settings):
    return float(latest_data['close']) < float(latest_data['vwap']) if bot_settings.vwap_signals else True


def psar_sell_signal(latest_data, bot_settings):
    return float(latest_data['close']) < float(latest_data['psar']) if bot_settings.psar_signals else True


def ma50_sell_signal(latest_data, bot_settings):
    return float(latest_data['close']) <= float(latest_data['ma_50']) if bot_settings.ma50_signals else True


def ma200_sell_signal(latest_data, bot_settings):
    return float(latest_data['close']) <= float(latest_data['ma_200']) if bot_settings.ma200_signals else True


def check_sell_signal(df, bot_settings, trend, averages, latest_data, previous_data):
    from .logic_utils import is_df_valid
    
    if not all([latest_data, previous_data, averages]):
        logger.warning(f"Invalid data for bot {bot_settings.id}")
        return False
    
    try:
        if not is_df_valid(df, bot_settings.id):
            return False

        sell_signals = [
            trend_sell_signal(trend, bot_settings),
            rsi_sell_signal(latest_data, bot_settings),
            macd_cross_sell_signal(averages, latest_data, bot_settings),
            macd_histogram_sell_signal(latest_data, previous_data, bot_settings),
            boilinger_sell_signal(latest_data, bot_settings),
            stoch_sell_signal(averages, latest_data, bot_settings),
            stoch_rsi_sell_signal(latest_data, bot_settings),
            ema_cross_sell_signal(averages, latest_data, bot_settings),
            ema_fast_sell_signal(latest_data, bot_settings),
            ema_slow_sell_signal(latest_data, bot_settings),
            di_cross_sell_signal(averages, latest_data, bot_settings),
            cci_sell_signal(latest_data, bot_settings),
            mfi_sell_signal(latest_data, bot_settings),
            atr_sell_signal(latest_data, averages, bot_settings),
            vwap_sell_signal(latest_data, bot_settings),
            psar_sell_signal(latest_data, bot_settings),
            ma50_sell_signal(latest_data, bot_settings),
            ma200_sell_signal(latest_data, bot_settings),
        ]

        if all(sell_signals):
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