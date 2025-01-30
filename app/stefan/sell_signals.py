from ..utils.logging import logger
from ..utils.email_utils import send_admin_email

def trend_sell_signal(trend, bot_settings):
    """
    Determines if a sell signal should be triggered based on the market trend.

    Args:
        trend (str): The current market trend ('uptrend' or 'downtrend').
        bot_settings (object): The bot settings containing trend signal preferences.

    Returns:
        bool: True if a sell signal should be triggered, otherwise False.
    """
    try:
        if bot_settings.trend_signals:
            return (trend == 'downtrend') 
        return True
    
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in trend_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in trend_sell_signal', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in trend_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in trend_sell_signal', str(e))
        return False


def rsi_sell_signal(latest_data, bot_settings):
    """
    Determines if a sell signal should be triggered based on the Relative Strength Index (RSI).

    Args:
        latest_data (dict): The latest market data containing RSI value.
        bot_settings (object): The bot settings containing RSI sell signal preferences.

    Returns:
        bool: True if a sell signal should be triggered, otherwise False.
    """
    try:
        if bot_settings.rsi_signals:
            return float(latest_data['rsi']) >= float(bot_settings.rsi_sell) 
        return True
    
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in rsi_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in rsi_sell_signal', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in rsi_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in rsi_sell_signal', str(e))
        return False


def rsi_divergence_sell_signal(latest_data, averages, bot_settings):
    """
    Determines if a sell signal should be triggered based on RSI divergence.

    Args:
        latest_data (dict): The latest market data containing close price and RSI value.
        averages (dict): The average market data for comparison.
        bot_settings (object): The bot settings containing RSI divergence signal preferences.

    Returns:
        bool: True if a sell signal should be triggered, otherwise False.
    """
    try:
        if bot_settings.rsi_divergence_signals:
            return (float(latest_data['close']) >= float(averages['avg_close']) and
                    float(latest_data['rsi']) <= float(averages['avg_rsi'])) 
        return True
    
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in rsi_divergence_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in rsi_divergence_sell_signal', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in rsi_divergence_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in rsi_divergence_sell_signal', str(e))
        return False


def macd_cross_sell_signal(latest_data, previous_data, bot_settings):
    """
    Determines if a sell signal should be triggered based on MACD crossover.

    Args:
        latest_data (dict): The latest market data containing MACD and MACD signal values.
        previous_data (dict): The previous market data containing MACD and MACD signal values.
        bot_settings (object): The bot settings containing MACD crossover signal preferences.

    Returns:
        bool: True if a sell signal should be triggered, otherwise False.
    """
    try:
        if bot_settings.macd_cross_signals:
            return (float(previous_data['macd']) >= float(previous_data['macd_signal']) and 
                    float(latest_data['macd']) <= float(latest_data['macd_signal'])) 
        return True
    
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in macd_cross_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in macd_cross_sell_signal', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in macd_cross_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in macd_cross_sell_signal', str(e))
        return False


def macd_histogram_sell_signal(latest_data, previous_data, bot_settings):
    """
    Determines if a sell signal should be triggered based on MACD histogram.

    Args:
        latest_data (dict): The latest market data containing MACD histogram value.
        previous_data (dict): The previous market data containing MACD histogram value.
        bot_settings (object): The bot settings containing MACD histogram signal preferences.

    Returns:
        bool: True if a sell signal should be triggered, otherwise False.
    """
    try:
        if bot_settings.macd_histogram_signals:
            return (float(previous_data['macd_histogram']) >= 0 and 
                    float(latest_data['macd_histogram']) <= 0) 
        return True
    
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in macd_histogram_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in macd_histogram_sell_signal', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in macd_histogram_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in macd_histogram_sell_signal', str(e))
        return False


def bollinger_sell_signal(latest_data, bot_settings):
    """
    Determines if a sell signal should be triggered based on Bollinger Bands.

    Args:
        latest_data (dict): The latest market data containing the closing price and upper band value.
        bot_settings (object): The bot settings containing Bollinger Bands signal preferences.

    Returns:
        bool: True if a sell signal should be triggered, otherwise False.
    """
    try:
        if bot_settings.bollinger_signals:
            return float(latest_data['close']) >= float(latest_data['upper_band'])
        return True
    
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in bollinger_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in bollinger_sell_signal', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in bollinger_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in bollinger_sell_signal', str(e))
        return False


def stoch_sell_signal(latest_data, previous_data, bot_settings):
    """
    Determines if a sell signal should be triggered based on Stochastic Oscillator crossover.

    Args:
        latest_data (dict): The latest market data containing Stochastic %K and %D values.
        previous_data (dict): The previous market data containing Stochastic %K and %D values.
        bot_settings (object): The bot settings containing Stochastic signal preferences.

    Returns:
        bool: True if a sell signal should be triggered, otherwise False.
    """
    try:
        if bot_settings.stoch_signals:
            return (float(previous_data['stoch_k']) >= float(previous_data['stoch_d']) and
                    float(latest_data['stoch_k']) <= float(latest_data['stoch_d']) and
                    float(latest_data['stoch_k']) >= float(bot_settings.stoch_sell)) 
        return True
    
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in stoch_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in stoch_sell_signal', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in stoch_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in stoch_sell_signal', str(e))
        return False


def stoch_divergence_sell_signal(latest_data, averages, bot_settings):
    """
    Determines if a sell signal should be triggered based on Stochastic Oscillator divergence.

    Args:
        latest_data (dict): The latest market data containing Stochastic %K and close price.
        averages (dict): The average market data for comparison.
        bot_settings (object): The bot settings containing Stochastic divergence signal preferences.

    Returns:
        bool: True if a sell signal should be triggered, otherwise False.
    """
    try:
        if bot_settings.stoch_divergence_signals:
            return (float(latest_data['stoch_k']) <= float(averages['avg_stoch_k']) and
                    float(latest_data['close']) >= float(averages['avg_close'])) 
        return True
    
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in stoch_divergence_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in stoch_divergence_sell_signal', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in stoch_divergence_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in stoch_divergence_sell_signal', str(e))
        return False


def stoch_rsi_sell_signal(latest_data, bot_settings):
    """
    Determines if a sell signal should be triggered based on Stochastic RSI.

    Args:
        latest_data (dict): The latest market data containing Stochastic RSI %K and %D values.
        bot_settings (object): The bot settings containing Stochastic RSI signal preferences.

    Returns:
        bool: True if a sell signal should be triggered, otherwise False.
    """
    try:
        if bot_settings.stoch_rsi_signals:
            return (float(latest_data['stoch_rsi_k']) >= float(bot_settings.stoch_sell) and 
                    float(latest_data['stoch_rsi_k']) <= float(latest_data['stoch_rsi_d'])) 
        return True
    
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in stoch_rsi_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in stoch_rsi_sell_signal', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in stoch_rsi_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in stoch_rsi_sell_signal', str(e))
        return False


def ema_cross_sell_signal(latest_data, previous_data, bot_settings):
    """
    Determines if a sell signal should be triggered based on the crossover of two Exponential Moving Averages (EMA).

    Args:
        latest_data (dict): The latest market data containing the fast and slow EMA values.
        previous_data (dict): The previous market data containing the fast and slow EMA values.
        bot_settings (object): The bot settings containing EMA crossover signal preferences.

    Returns:
        bool: True if a sell signal should be triggered, otherwise False.
    """
    try:
        if bot_settings.ema_cross_signals:
            return (float(previous_data['ema_fast']) >= float(previous_data['ema_slow']) and
                    float(latest_data['ema_fast']) <= float(latest_data['ema_slow'])) 
        return True
    
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in ema_cross_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in ema_cross_sell_signal', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in ema_cross_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in ema_cross_sell_signal', str(e))
        return False


def ema_fast_sell_signal(latest_data, bot_settings):
    """
    Determines if a sell signal should be triggered based on the fast Exponential Moving Average (EMA).

    Args:
        latest_data (dict): The latest market data containing the close price and fast EMA value.
        bot_settings (object): The bot settings containing the fast EMA signal preferences.

    Returns:
        bool: True if a sell signal should be triggered, otherwise False.
    """
    try:
        if bot_settings.ema_fast_signals:
            return float(latest_data['close']) <= float(latest_data['ema_fast']) 
        return True
    
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in ema_fast_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in ema_fast_sell_signal', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in ema_fast_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in ema_fast_sell_signal', str(e))
        return False


def ema_slow_sell_signal(latest_data, bot_settings):
    """
    Determines if a sell signal should be triggered based on the slow Exponential Moving Average (EMA).

    Args:
        latest_data (dict): The latest market data containing the close price and slow EMA value.
        bot_settings (object): The bot settings containing the slow EMA signal preferences.

    Returns:
        bool: True if a sell signal should be triggered, otherwise False.
    """
    try:
        if bot_settings.ema_slow_signals:
            return float(latest_data['close']) <= float(latest_data['ema_slow']) 
        return True
    
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in ema_slow_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in ema_slow_sell_signal', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in ema_slow_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in ema_slow_sell_signal', str(e))
        return False


def di_cross_sell_signal(latest_data, previous_data, bot_settings):
    """
    Determines if a sell signal should be triggered based on the Directional Indicator (DI) crossover.

    Args:
        latest_data (dict): The latest market data containing the Plus DI and Minus DI values.
        previous_data (dict): The previous market data containing the Plus DI and Minus DI values.
        bot_settings (object): The bot settings containing DI crossover signal preferences.

    Returns:
        bool: True if a sell signal should be triggered, otherwise False.
    """
    try:
        if bot_settings.di_signals:
            return (float(previous_data['plus_di']) >= float(previous_data['minus_di']) and 
                    float(latest_data['plus_di']) <= float(latest_data['minus_di'])) 
        return True
    
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in di_cross_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in di_cross_sell_signal', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in di_cross_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in di_cross_sell_signal', str(e))
        return False


def cci_sell_signal(latest_data, bot_settings):
    """
    Determines if a sell signal should be triggered based on the Commodity Channel Index (CCI).

    Args:
        latest_data (dict): The latest market data containing the CCI value.
        bot_settings (object): The bot settings containing CCI sell signal preferences.

    Returns:
        bool: True if a sell signal should be triggered, otherwise False.
    """
    try:
        if bot_settings.cci_signals:
            return float(latest_data['cci']) >= float(bot_settings.cci_sell) 
        return True
    
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in cci_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in cci_sell_signal', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in cci_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in cci_sell_signal', str(e))
        return False


def cci_divergence_buy_signal(latest_data, averages, bot_settings):
    """
    Determines if a buy signal should be triggered based on CCI divergence.

    Args:
        latest_data (dict): The latest market data containing close price and CCI value.
        averages (dict): The average market data for comparison.
        bot_settings (object): The bot settings containing CCI divergence signal preferences.

    Returns:
        bool: True if a buy signal should be triggered, otherwise False.
    """
    try:
        if bot_settings.cci_divergence_signals:
            return (float(latest_data['close']) >= float(averages['avg_close']) and
                    float(latest_data['cci']) <= float(averages['avg_cci'])) 
        return True
    
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in cci_divergence_buy_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in cci_divergence_buy_signal', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in cci_divergence_buy_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in cci_divergence_buy_signal', str(e))
        return False


def mfi_sell_signal(latest_data, bot_settings):
    """
    Determines if a sell signal should be triggered based on the Money Flow Index (MFI).

    Args:
        latest_data (dict): The latest market data containing the MFI value.
        bot_settings (object): The bot settings containing MFI sell signal preferences.

    Returns:
        bool: True if a sell signal should be triggered, otherwise False.
    """
    try:
        if bot_settings.mfi_signals:
            return float(latest_data['mfi']) >= float(bot_settings.mfi_sell) 
        return True
    
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in mfi_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in mfi_sell_signal', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in mfi_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in mfi_sell_signal', str(e))
        return False


def mfi_divergence_sell_signal(latest_data, averages, bot_settings):
    """
    Determines if a sell signal should be triggered based on MFI divergence.

    Args:
        latest_data (dict): The latest market data containing close price and MFI value.
        averages (dict): The average market data for comparison.
        bot_settings (object): The bot settings containing MFI divergence signal preferences.

    Returns:
        bool: True if a sell signal should be triggered, otherwise False.
    """
    try:
        if bot_settings.mfi_divergence_signals:
            return (float(latest_data['close']) >= float(averages['avg_close']) and
                    float(latest_data['mfi']) <= float(averages['avg_mfi'])) 
        return True
    
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in mfi_divergence_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in mfi_divergence_sell_signal', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in mfi_divergence_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in mfi_divergence_sell_signal', str(e))
        return False


def atr_sell_signal(latest_data, averages, bot_settings):
    """
    Determines if a sell signal should be triggered based on the Average True Range (ATR).

    Args:
        latest_data (dict): The latest market data containing the ATR value.
        averages (dict): The average market data for comparison.
        bot_settings (object): The bot settings containing ATR signal preferences.

    Returns:
        bool: True if a sell signal should be triggered, otherwise False.
    """
    try:
        if bot_settings.atr_signals:
            return float(latest_data['atr']) <= float(averages['avg_atr']) 
        return True
    
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in atr_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in atr_sell_signal', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in atr_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in atr_sell_signal', str(e))
        return False


def vwap_sell_signal(latest_data, bot_settings):
    """
    Determines if a sell signal should be triggered based on the Volume-Weighted Average Price (VWAP).

    Args:
        latest_data (dict): The latest market data containing the VWAP and close price values.
        bot_settings (object): The bot settings containing VWAP signal preferences.

    Returns:
        bool: True if a sell signal should be triggered, otherwise False.
    """
    try:
        if bot_settings.vwap_signals:
            return float(latest_data['close']) <= float(latest_data['vwap']) 
        return True
    
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in vwap_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in vwap_sell_signal', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in vwap_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in vwap_sell_signal', str(e))
        return False


def psar_sell_signal(latest_data, bot_settings):
    """
    Determines if a sell signal should be triggered based on the Parabolic SAR (PSAR).

    Args:
        latest_data (dict): The latest market data containing the PSAR and close price values.
        bot_settings (object): The bot settings containing PSAR signal preferences.

    Returns:
        bool: True if a sell signal should be triggered, otherwise False.
    """
    try:
        if bot_settings.psar_signals:
            return float(latest_data['close']) <= float(latest_data['psar']) 
        return True
    
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in psar_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in psar_sell_signal', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in psar_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in psar_sell_signal', str(e))
        return False


def ma50_sell_signal(latest_data, bot_settings):
    """
    Determines if a sell signal should be triggered based on the 50-period Moving Average (MA50).

    Args:
        latest_data (dict): The latest market data containing the MA50 and close price values.
        bot_settings (object): The bot settings containing MA50 signal preferences.

    Returns:
        bool: True if a sell signal should be triggered, otherwise False.
    """
    try:
        if bot_settings.ma50_signals:
            return float(latest_data['close']) <= float(latest_data['ma_50']) 
        return True
    
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in ma50_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in ma50_sell_signal', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in ma50_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in ma50_sell_signal', str(e))
        return False


def ma200_sell_signal(latest_data, bot_settings):
    """
    Determines if a sell signal should be triggered based on the 200-period Moving Average (MA200).

    Args:
        latest_data (dict): The latest market data containing the MA200 and close price values.
        bot_settings (object): The bot settings containing MA200 signal preferences.

    Returns:
        bool: True if a sell signal should be triggered, otherwise False.
    """
    try:
        if bot_settings.ma200_signals:
            return float(latest_data['close']) <= float(latest_data['ma_200']) 
        return True
    
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in ma200_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in ma200_sell_signal', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in ma200_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in ma200_sell_signal', str(e))
        return False


def ma_cross_sell_signal(latest_data, previous_data, bot_settings):
    """
    Determines if a sell signal should be triggered based on the crossover of the 50-period and 200-period Moving Averages (MA50 and MA200).

    Args:
        latest_data (dict): The latest market data containing the MA50 and MA200 values.
        previous_data (dict): The previous market data containing the MA50 and MA200 values.
        bot_settings (object): The bot settings containing MA crossover signal preferences.

    Returns:
        bool: True if a sell signal should be triggered, otherwise False.
    """
    try:
        if bot_settings.ma_cross_signals:
            return (float(previous_data['ma_50']) >= float(previous_data['ma_200']) and
                    float(latest_data['ma_50']) <= float(latest_data['ma_200'])) 
        return True
    
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in ma_cross_sell_signal: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in ma_cross_sell_signal', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in calculate_ta_rsi: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in calculate_ta_rsi', str(e))
        return False


def check_classic_ta_sell_signal(
    df, 
    bot_settings, 
    trend, 
    averages, 
    latest_data, 
    previous_data
    ):
    """
    Checks if all classic technical analysis sell signals are triggered based on the provided data.

    This function evaluates a series of sell signals including trend, RSI, MACD, Bollinger Bands,
    Stochastic, EMA, DI, CCI, MFI, ATR, VWAP, PSAR, and moving averages (MA50, MA200). If all signals 
    return `True`, a sell signal is triggered. If any of the signals fail, no sell signal is triggered.

    Args:
        df (DataFrame): A DataFrame containing historical market data.
        bot_settings (object): The bot settings containing preferences for each technical signal.
        trend (object): The current market trend data used for trend-based sell signal evaluation.
        averages (dict): The average market data for comparison (e.g., moving averages).
        latest_data (dict): The most recent market data for evaluation of technical indicators.
        previous_data (dict): The previous market data for evaluating changes in indicators.

    Returns:
        bool: True if all sell signals are triggered, otherwise False.

    Exceptions:
        IndexError: If there is an issue with accessing data from the DataFrame.
        Exception: For any other unexpected errors during signal evaluation.

    Sends an email notification to the admin in case of an error.
    """
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
            bollinger_sell_signal(latest_data, bot_settings),
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
            ma_cross_sell_signal(latest_data, previous_data, bot_settings)
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