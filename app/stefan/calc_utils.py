import talib
import pandas as pd
from ..utils.logging import logger
from ..utils.email_utils import send_admin_email
from ..utils.exception_handlers import exception_handler

@exception_handler(default_return=False)
def handle_ta_df_initial_praparation(df, bot_settings):
    """
    Prepares the DataFrame for technical analysis by converting relevant columns to numeric 
    types and handling missing values.

    Args:
        df (pandas.DataFrame): The raw DataFrame containing market data.
        bot_settings (object): The bot's settings containing configuration for analysis.

    Returns:
        pandas.DataFrame: The cleaned DataFrame with numeric conversion and missing values handled.
        bool: False if an error occurs.
    """
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df['high'] = pd.to_numeric(df['high'], errors='coerce')
    df['low'] = pd.to_numeric(df['low'], errors='coerce')
    df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
    
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
    
    df.dropna(subset=['close'], inplace=True)
    
    return df


@exception_handler(default_return=False)
def calculate_ta_rsi(df, bot_settings):
    """
    Calculates the Relative Strength Index (RSI) using the 'close' price.

    Args:
        df (pandas.DataFrame): The DataFrame containing market data.
        bot_settings (object): The bot's settings containing RSI time period configuration.

    Returns:
        pandas.DataFrame: The DataFrame with the RSI values added.
        bool: False if an error occurs.
    """
    df['rsi'] = talib.RSI(
        df['close'], 
        timeperiod=bot_settings.rsi_timeperiod
        )
    
    return df
        

@exception_handler(default_return=False)
def calculate_ta_cci(df, bot_settings):
    """
    Calculates the Commodity Channel Index (CCI) using 'high', 'low', and 'close' prices.

    Args:
        df (pandas.DataFrame): The DataFrame containing market data.
        bot_settings (object): The bot's settings containing CCI time period configuration.

    Returns:
        pandas.DataFrame: The DataFrame with the CCI values added.
        bool: False if an error occurs.
    """
    df['cci'] = talib.CCI(
        df['high'],
        df['low'],
        df['close'],
        timeperiod=bot_settings.cci_timeperiod
        )
    
    return df


@exception_handler(default_return=False)
def calculate_ta_mfi(df, bot_settings):
    """
    Calculates the Money Flow Index (MFI) using 'high', 'low', 'close', and 'volume' data.

    Args:
        df (pandas.DataFrame): The DataFrame containing market data.
        bot_settings (object): The bot's settings containing MFI time period configuration.

    Returns:
        pandas.DataFrame: The DataFrame with the MFI values added.
        bool: False if an error occurs.
    """
    df['mfi'] = talib.MFI(
        df['high'],
        df['low'],
        df['close'],
        df['volume'],
        timeperiod=bot_settings.mfi_timeperiod
        )
    
    return df


@exception_handler(default_return=False)
def calculate_ta_adx(df, bot_settings):
    """
    Calculates the Average Directional Index (ADX) using 'high', 'low', and 'close' prices.

    Args:
        df (pandas.DataFrame): The DataFrame containing market data.
        bot_settings (object): The bot's settings containing ADX time period configuration.

    Returns:
        pandas.DataFrame: The DataFrame with the ADX values added.
        bool: False if an error occurs.
    """

    df['adx'] = talib.ADX(
        df['high'],
        df['low'],
        df['close'],
        timeperiod=bot_settings.adx_timeperiod
        )
    
    return df


@exception_handler(default_return=False)
def calculate_ta_atr(df, bot_settings):
    """
    Calculates the Average True Range (ATR) using 'high', 'low', and 'close' prices.

    Args:
        df (pandas.DataFrame): The DataFrame containing market data.
        bot_settings (object): The bot's settings containing ATR time period configuration.

    Returns:
        pandas.DataFrame: The DataFrame with the ATR values added.
        bool: False if an error occurs.
    """
    df['atr'] = talib.ATR(
        df['high'],
        df['low'],
        df['close'],
        timeperiod=bot_settings.atr_timeperiod
        )
    
    return df
    

@exception_handler(default_return=False)
def calculate_ta_di(df, bot_settings):
    """
    Calculates the Directional Indicators (DI) including the Plus DI and Minus DI 
    using 'high', 'low', and 'close' prices.

    Args:
        df (pandas.DataFrame): The DataFrame containing market data.
        bot_settings (object): The bot's settings containing DI time period configuration.

    Returns:
        pandas.DataFrame: The DataFrame with the Plus DI and Minus DI values added.
        bool: False if an error occurs.
    """
    df['plus_di'] = talib.PLUS_DI(
        df['high'],
        df['low'],
        df['close'],
        timeperiod=bot_settings.di_timeperiod
        )
    
    df['minus_di'] = talib.MINUS_DI(
        df['high'],
        df['low'],
        df['close'],
        timeperiod=bot_settings.di_timeperiod
        )
    
    return df


@exception_handler(default_return=False)
def calculate_ta_stochastic(df, bot_settings):
    """
    Calculates the Stochastic Oscillator using 'high', 'low', and 'close' prices.

    Args:
        df (pandas.DataFrame): The DataFrame containing market data.
        bot_settings (object): The bot's settings containing Stochastic parameters.

    Returns:
        pandas.DataFrame: The DataFrame with the Stochastic K and D values added.
        bool: False if an error occurs.
    """
    df['stoch_k'], df['stoch_d'] = talib.STOCH(
        df['high'],
        df['low'],
        df['close'],
        fastk_period=bot_settings.stoch_k_timeperiod,
        slowk_period=bot_settings.stoch_d_timeperiod,
        slowk_matype=0,
        slowd_period=bot_settings.stoch_d_timeperiod,
        slowd_matype=0
    )
    
    return df


@exception_handler(default_return=False)
def calculate_ta_bollinger_bands(df, bot_settings):
    """
    Calculates the Bollinger Bands using 'close' price.

    Args:
        df (pandas.DataFrame): The DataFrame containing market data.
        bot_settings (object): The bot's settings containing Bollinger Bands parameters.

    Returns:
        pandas.DataFrame: The DataFrame with the upper, middle, and lower bands added.
        bool: False if an error occurs.
    """
    df['upper_band'], df['middle_band'], df['lower_band'] = talib.BBANDS(
        df['close'],
        timeperiod=bot_settings.bollinger_timeperiod,
        nbdevup=bot_settings.bollinger_nbdev,
        nbdevdn=bot_settings.bollinger_nbdev,
        matype=0
    )
    
    return df


@exception_handler(default_return=False)
def calculate_ta_vwap(df, bot_settings):
    """
    Calculate the Volume Weighted Average Price (VWAP) for the given DataFrame.

    Args:
        df (DataFrame): The DataFrame containing the price and volume data.
        bot_settings (object): The bot settings object containing relevant configuration for the calculation.

    Returns:
        DataFrame: The original DataFrame with the calculated VWAP.
        bool: False if an error occurs during calculation.
    """
    df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
    df['vwap'] = (df['typical_price'] * df['volume']).cumsum() / df['volume'].cumsum()
    
    return df

    
@exception_handler(default_return=False)
def calculate_ta_psar(df, bot_settings):
    """
    Calculate the Parabolic SAR (PSAR) for the given DataFrame using bot settings.

    Args:
        df (DataFrame): The DataFrame containing the price data.
        bot_settings (object): The bot settings object containing the acceleration and maximum values for PSAR calculation.

    Returns:
        DataFrame: The original DataFrame with the calculated PSAR.
        bool: False if an error occurs during calculation.
    """
    df['psar'] = talib.SAR(
        df['high'],
        df['low'],
        acceleration=bot_settings.psar_acceleration,
        maximum=bot_settings.psar_maximum
    )
    
    return df

    
@exception_handler(default_return=False)
def calculate_ta_macd(df, bot_settings):
    """
    Calculate the Moving Average Convergence Divergence (MACD) for the given DataFrame.

    Args:
        df (DataFrame): The DataFrame containing the closing price data.
        bot_settings (object): The bot settings object containing configuration for MACD calculation.

    Returns:
        DataFrame: The original DataFrame with the calculated MACD and MACD signal.
        bool: False if not enough data points are available or if an error occurs.
    """
    if len(df) < bot_settings.macd_timeperiod * 2:
        logger.trade('Not enough data points for MACD calculation.')
        return df
    
    df['macd'], df['macd_signal'], _ = talib.MACD(
        df['close'],
        fastperiod=bot_settings.macd_timeperiod,
        slowperiod=bot_settings.macd_timeperiod * 2,
        signalperiod=bot_settings.macd_signalperiod
    )
    
    df['macd_histogram'] = df['macd'] - df['macd_signal']
    
    return df

    
@exception_handler(default_return=False)
def calculate_ta_ma(df, bot_settings):
    """
    Calculate the 200-period and 50-period Moving Averages (MA) for the given DataFrame.

    Args:
        df (DataFrame): The DataFrame containing the closing price data.
        bot_settings (object): The bot settings object (not used in this function).

    Returns:
        DataFrame: The original DataFrame with the calculated 200-period and 50-period MAs.
        bool: False if an error occurs during calculation.
    """
    df['ma_200'] = df['close'].rolling(window=200).mean()
    df['ma_50'] = df['close'].rolling(window=50).mean()
    
    return df

    
@exception_handler(default_return=False)
def calculate_ta_ema(df, bot_settings):
    """
    Calculate the Fast and Slow Exponential Moving Averages (EMA) for the given DataFrame.

    Args:
        df (DataFrame): The DataFrame containing the closing price data.
        bot_settings (object): The bot settings object containing the time periods for the fast and slow EMAs.

    Returns:
        DataFrame: The original DataFrame with the calculated fast and slow EMAs.
        bool: False if an error occurs during calculation.
    """
    df['ema_fast'] = talib.EMA(
        df['close'], 
        timeperiod=bot_settings.ema_fast_timeperiod
        )
    
    df['ema_slow'] = talib.EMA(
        df['close'], 
        timeperiod=bot_settings.ema_slow_timeperiod
        )
    
    return df

    
@exception_handler(default_return=False)
def calculate_ta_stochastic_rsi(df, bot_settings):
    """
    Calculate the Stochastic RSI (Relative Strength Index) for the given DataFrame.

    Args:
        df (DataFrame): The DataFrame containing the RSI data.
        bot_settings (object): The bot settings object containing the time periods for Stochastic RSI calculation.

    Returns:
        DataFrame: The original DataFrame with the calculated Stochastic RSI and its %K and %D values.
        bool: False if an error occurs during calculation.
    """
    df['stoch_rsi'] = talib.RSI(
        df['rsi'], 
        timeperiod=bot_settings.stoch_rsi_timeperiod
        )
    
    df['stoch_rsi_k'], df['stoch_rsi_d'] = talib.STOCH(
        df['stoch_rsi'],
        df['stoch_rsi'],
        df['stoch_rsi'],
        fastk_period=bot_settings.stoch_rsi_k_timeperiod,
        slowk_period=bot_settings.stoch_rsi_d_timeperiod,
        slowk_matype=0,
        slowd_period=bot_settings.stoch_rsi_d_timeperiod,
        slowd_matype=0
    )
    
    return df

    
@exception_handler(default_return=False)
def handle_ta_df_final_cleaning(df, columns_to_check, bot_settings):
    """
    Clean the final DataFrame by removing rows with missing values in the specified columns.

    Args:
        df (DataFrame): The DataFrame to clean.
        columns_to_check (list): A list of column names to check for missing values.
        bot_settings (object): The bot settings object (not used in this function).

    Returns:
        DataFrame: The cleaned DataFrame.
        bool: False if an error occurs during cleaning.
    """
    df.dropna(subset=columns_to_check, inplace=True)
    
    return df

    
@exception_handler(default_return=False)
def calculate_ta_indicators(df, bot_settings):
    """
    Calculates various technical analysis indicators on the given DataFrame.

    This function applies multiple technical indicators (RSI, CCI, MFI, etc.) to the input DataFrame
    and returns the updated DataFrame with the calculated values. It ensures the DataFrame is properly
    prepared and cleaned before returning the results.

    Args:
        df (pandas.DataFrame): The DataFrame containing the market data.
        bot_settings (object): The settings for the bot, including parameters for the indicators.

    Returns:
        pandas.DataFrame: The updated DataFrame with calculated technical indicators, or False if an error occurs.
    """
    if df.empty:
        logger.error('DataFrame is empty, cannot calculate indicators.')
        return df

    handle_ta_df_initial_praparation(df, bot_settings)

    calculate_ta_rsi(df, bot_settings)
    calculate_ta_cci(df, bot_settings)
    calculate_ta_mfi(df, bot_settings)
    calculate_ta_stochastic(df, bot_settings)
    calculate_ta_stochastic_rsi(df, bot_settings)
    calculate_ta_bollinger_bands(df, bot_settings)
    calculate_ta_ema(df, bot_settings)
    calculate_ta_macd(df, bot_settings)
    calculate_ta_ma(df, bot_settings)
    calculate_ta_atr(df, bot_settings)
    calculate_ta_psar(df, bot_settings)
    calculate_ta_vwap(df, bot_settings)
    calculate_ta_adx(df, bot_settings)
    calculate_ta_di(df, bot_settings)
    
    columns_to_check = [
        'macd', 
        'macd_signal', 
        'cci', 
        'upper_band', 
        'lower_band', 
        'mfi', 
        'atr', 
        'stoch_k', 
        'stoch_d', 
        'psar'
    ]
    handle_ta_df_final_cleaning(df, columns_to_check, bot_settings)

    return df


@exception_handler()
def calculate_ta_averages(df, bot_settings):
    """
    Calculates the average values for various technical analysis indicators.

    This function computes the average of specific columns in the DataFrame over a defined period,
    based on the bot settings. The calculated averages are returned as a dictionary.

    Args:
        df (pandas.DataFrame): The DataFrame containing the market data.
        bot_settings (object): The settings for the bot, including the periods for averaging the indicators.

    Returns:
        dict: A dictionary containing the average values of technical indicators, or None if an error occurs.
    """
    averages = {}
    
    average_mappings = {
        'avg_volume': ('volume', bot_settings.avg_volume_period),
        'avg_rsi': ('rsi', bot_settings.avg_rsi_period),
        'avg_cci': ('cci', bot_settings.avg_cci_period),
        'avg_mfi': ('mfi', bot_settings.avg_mfi_period),
        'avg_atr': ('atr', bot_settings.avg_atr_period),
        'avg_stoch_rsi_k': ('stoch_rsi_k', bot_settings.avg_stoch_rsi_period),
        'avg_macd': ('macd', bot_settings.avg_macd_period),
        'avg_macd_signal': ('macd_signal', bot_settings.avg_macd_period),
        'avg_stoch_k': ('stoch_k', bot_settings.avg_stoch_period),
        'avg_stoch_d': ('stoch_d', bot_settings.avg_stoch_period),
        'avg_ema_fast': ('ema_fast', bot_settings.avg_ema_period),
        'avg_ema_slow': ('ema_slow', bot_settings.avg_ema_period),
        'avg_plus_di': ('plus_di', bot_settings.avg_di_period),
        'avg_minus_di': ('minus_di', bot_settings.avg_di_period),
        'avg_psar': ('psar', bot_settings.avg_psar_period),
        'avg_vwap': ('vwap', bot_settings.avg_vwap_period),
        'avg_close': ('close', bot_settings.avg_close_period),
    }

    for avg_name, (column, period) in average_mappings.items():
        averages[avg_name] = df[column].iloc[-period:].mean()

    return averages


@exception_handler(default_return='none')
def check_ta_trend(df, bot_settings):
    """
    Checks the market trend based on technical analysis indicators.

    This function evaluates the current market trend (uptrend, downtrend, or horizontal)
    by analyzing various indicators such as ADX, DI, RSI, and ATR. It returns a string
    representing the trend ('uptrend', 'downtrend', 'horizontal', or 'none').

    Args:
        df (pandas.DataFrame): The DataFrame containing the market data.
        bot_settings (object): The settings for the bot, including the thresholds for trend identification.

    Returns:
        str: The market trend ('uptrend', 'downtrend', 'horizontal', or 'none').
    """
    latest_data = df.iloc[-1]
    
    avg_adx_period = bot_settings.avg_adx_period
    avg_adx = df['adx'].iloc[-avg_adx_period:].mean()
    
    adx_trend = (
        float(latest_data['adx']) > float(bot_settings.adx_strong_trend) or 
        float(latest_data['adx']) > float(avg_adx)
        )
    
    avg_di_period = bot_settings.avg_di_period
    avg_plus_di = df['plus_di'].iloc[-avg_di_period:].mean()
    avg_minus_di = df['minus_di'].iloc[-avg_di_period:].mean()
    
    di_difference_increasing = (
        abs(float(latest_data['plus_di']) - float(latest_data['minus_di'])) > 
        abs(float(avg_plus_di) - float(avg_minus_di)))
    
    significant_move = (
        (float(latest_data['high']) - float(latest_data['low'])) > 
        float(latest_data['atr']))
    
    is_rsi_bullish = float(latest_data['rsi']) < float(bot_settings.rsi_sell)
    is_rsi_bearish = float(latest_data['rsi']) > float(bot_settings.rsi_buy)
    
    is_strong_plus_di = float(latest_data['plus_di']) > float(bot_settings.adx_weak_trend)
    is_strong_minus_di = float(latest_data['minus_di']) > float(bot_settings.adx_weak_trend)

    uptrend = (
        is_rsi_bullish and 
        adx_trend and 
        di_difference_increasing and 
        is_strong_plus_di and 
        significant_move and 
        float(latest_data['plus_di']) > float(avg_minus_di)
        )

    downtrend = (
        is_rsi_bearish and 
        adx_trend and 
        di_difference_increasing and 
        is_strong_minus_di and 
        significant_move and 
        float(latest_data['plus_di']) < float(avg_minus_di)
        )      

    horizontal = (
        float(latest_data['adx']) < avg_adx or 
        avg_adx < float(bot_settings.adx_weak_trend) or 
        abs(float(latest_data['plus_di']) - float(latest_data['minus_di'])) < 
        float(bot_settings.adx_no_trend)
    )

    if uptrend:
        logger.trade(f"Bot {bot_settings.id} {bot_settings.strategy} have BULLISH UPTREND")
        return 'uptrend'
    elif downtrend:
        logger.trade(f"Bot {bot_settings.id} {bot_settings.strategy} have BEARISH DOWNTREND")
        return 'downtrend'
    elif horizontal:
        logger.trade(f"Bot {bot_settings.id} {bot_settings.strategy} have HORIZONTAL TREND")
        return 'horizontal'
        
    
def round_down_to_step_size(amount, step_size):
    """
    Rounds down a given amount to the nearest multiple of the specified step size.

    This function ensures that the amount is a multiple of the step size by rounding it down 
    to the nearest valid value. If the step size is 0 or less, the original amount is returned.

    Args:
        amount (float): The amount to be rounded.
        step_size (float): The step size to which the amount will be rounded down.

    Returns:
        float: The rounded amount, or the original amount if the step size is 0 or less.

    Raises:
        Exception: If an error occurs during the rounding process, it logs the exception and returns the original amount.
    """
    from decimal import Decimal
    
    try:
        if step_size > 0:
            amount_decimal = Decimal(str(amount))
            step_size_decimal = Decimal(str(step_size))
            rounded_amount = (amount_decimal // step_size_decimal) * step_size_decimal
            return float(rounded_amount)
        return float(amount)
    
    except Exception as e:
            logger.error(f"Exception in round_down_to_step_size: {str(e)}")
            send_admin_email(f'Exception in round_down_to_step_size', str(e))
            return float(amount)
        
        
@exception_handler()
def calculate_take_profit(current_price, bot_settings):
    """
    Calculates the take profit price based on the current market price and the bot's take profit percentage.

    The take profit price is calculated as the current price increased by the percentage specified in 
    the bot's settings. If the percentage is not valid (not between 0 and 1), a ValueError will be raised.

    Args:
        current_price (float): The current market price of the asset.
        bot_settings (object): The settings of the bot, which includes the take profit percentage (take_profit_pct).

    Returns:
        float: The calculated take profit price.
        None: If an error occurs during the calculation, it returns None.

    Raises:
        ValueError: If bot_settings.take_profit_pct is not between 0 and 1.
        Exception: If any other unexpected error occurs.
    """
    current_price = float(current_price)

    if not (0 < bot_settings.take_profit_pct < 1):
        raise ValueError("bot_settings.take_profit_pct must be between 0 and 1.")

    take_profit_price = current_price + (current_price * (bot_settings.take_profit_pct))
    logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} "
                    f"Calculated take profit: current_price={current_price}, "
                    f"take_profit_pct={bot_settings.take_profit_pct}, "
                    f"take_profit_price={take_profit_price}")
    return take_profit_price


@exception_handler()
def calculate_atr_take_profit(current_price, atr, bot_settings):
    """
    Calculates the take profit price based on the current market price and the ATR (Average True Range) value.

    The take profit price is calculated as the current price increased by the ATR multiplied by a specified 
    multiplier from the bot's settings. If the ATR or multiplier is not valid (not positive), a ValueError will be raised.

    Args:
        current_price (float): The current market price of the asset.
        atr (float): The Average True Range (ATR) value used to calculate the volatility-based take profit.
        bot_settings (object): The settings of the bot, which includes the ATR multiplier for take profit calculation.

    Returns:
        float: The calculated take profit price.
        None: If an error occurs during the calculation, it returns None.

    Raises:
        ValueError: If bot_settings.take_profit_atr_calc or ATR is not positive.
        Exception: If any other unexpected error occurs.
    """
    current_price = float(current_price)
    atr = float(atr)

    if bot_settings.take_profit_atr_calc <= 0:
        raise ValueError("bot_settings.take_profit_atr_calc must be a positive value.")
    if atr <= 0:
        raise ValueError("ATR must be a positive value.")

    take_profit_price = current_price + (atr * bot_settings.take_profit_atr_calc)
    logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} "
                f"Calculated ATR-based take profit: {take_profit_price}, "
                f"current_price={current_price}, atr={atr}, multiplier={bot_settings.take_profit_atr_calc}")
    return take_profit_price


def calculate_stop_loss(
    current_price, 
    trailing_stop_price, 
    bot_settings
    ):
    """
    Calculates the stop loss price based on the current market price and the bot's stop loss percentage.

    The function calculates the new stop loss price as the current price decreased by the percentage 
    specified in the bot's settings. It then compares this new stop price with the existing trailing stop 
    price and returns the higher of the two to ensure the stop loss moves only upward.

    Args:
        current_price (float): The current market price of the asset.
        trailing_stop_price (float): The current trailing stop price to be updated.
        bot_settings (object): The settings of the bot, which includes the stop loss percentage (stop_loss_pct).

    Returns:
        float: The updated stop loss price, which is the higher of the trailing stop price and the newly calculated stop price.

    Raises:
        ValueError: If invalid values are provided for current_price or trailing_stop_price.
        Exception: If any other unexpected error occurs.
    """
    try:
        trailing_stop_price = float(trailing_stop_price)
        current_price = float(current_price)
        new_stop_price = current_price * (1 - bot_settings.stop_loss_pct)

        return max(trailing_stop_price, new_stop_price)

    except ValueError as e:
        logger.error(f"Bot {bot_settings.id} ValueError in update_stop_loss: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} ValueError in update_stop_loss', str(e))
        return trailing_stop_price
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in update_stop_loss: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in update_stop_loss', str(e))
        return trailing_stop_price


def calculate_atr_trailing_stop_loss(
    current_price, 
    trailing_stop_price, 
    atr, 
    bot_settings
    ):
    """
    Calculates the trailing stop loss price based on the current market price, the ATR (Average True Range) value, 
    and the bot's settings for ATR-based trailing stop calculation.

    The function calculates a dynamic trailing stop based on the ATR value, adjusting the stop loss price according 
    to the market's volatility. It then compares the newly calculated trailing stop price with a minimal stop loss 
    price (based on the bot's stop loss percentage) and returns the higher of the two. This ensures that the trailing 
    stop moves only upward and accounts for both volatility and user-defined risk tolerance.

    Args:
        current_price (float): The current market price of the asset.
        trailing_stop_price (float): The current trailing stop price to be updated.
        atr (float): The Average True Range (ATR) value, which is used to calculate the dynamic trailing stop.
        bot_settings (object): The settings of the bot, which includes the trailing stop multiplier (trailing_stop_atr_calc) 
                               and the stop loss percentage (stop_loss_pct).

    Returns:
        float: The updated trailing stop loss price, which is the higher of the dynamic trailing stop and the minimal stop 
              loss price.

    Raises:
        ValueError: If invalid values are provided for current_price, trailing_stop_price, or atr.
        Exception: If any other unexpected error occurs.
    """
    try:
        current_price = float(current_price)
        trailing_stop_price = float(trailing_stop_price)
        atr = float(atr)
        
        dynamic_trailing_stop = current_price * (1 - (bot_settings.trailing_stop_atr_calc * atr / current_price))
        minimal_trailing_stop = current_price * (1 - bot_settings.stop_loss_pct)
        new_trailing_stop = max(dynamic_trailing_stop, minimal_trailing_stop)

        return max(trailing_stop_price, new_trailing_stop)

    except ValueError as e:
        logger.error(f"Bot {bot_settings.id} ValueError in update_atr_trailing_stop_loss: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} ValueError in update_atr_trailing_stop_loss', str(e))
        return trailing_stop_price
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in update_atr_trailing_stop_loss: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in update_atr_trailing_stop_loss', str(e))
        return trailing_stop_price