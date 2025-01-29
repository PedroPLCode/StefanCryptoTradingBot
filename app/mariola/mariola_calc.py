import pandas as pd
import numpy as np
import talib
from ..utils.logging import logger
from ..utils.app_utils import send_admin_email

def find_ml_hammer_patterns(df, bot_settings):
    """
    Identifies the Hammer candlestick pattern and adds related features to the DataFrame.

    A Hammer candlestick pattern is identified when the following conditions are met:
    - The distance between the high and close is more than twice the distance between the open and low.
    - The lower shadow (close to low) is more than 60% of the entire candle's range (high to low).
    - The upper shadow (open to high) is more than 60% of the entire candle's range (high to low).

    This function adds the following features to the DataFrame:
    - 'hammer': Boolean indicating the presence of a Hammer pattern.
    - 'is_hammer_morning': Boolean indicating if the Hammer pattern occurred between 9 AM and 12 PM.
    - 'is_hammer_weekend': Boolean indicating if the Hammer pattern occurred on a weekend (Saturday or Sunday).

    Args:
        df (pandas.DataFrame): DataFrame containing candlestick data (open, high, low, close, close_time).

    Returns:
        pandas.DataFrame or None: DataFrame with the 'hammer', 'is_hammer_morning', 
                                   and 'is_hammer_weekend' columns added. Returns None if an error occurs.

    Raises:
        ValueError: If the DataFrame is None or empty.
        Exception: If any error occurs during the pattern identification process.
    """
    try:
        
        if df is None or df.empty:
            raise ValueError("df must be provided and cannot be None or empty.")
        
        df['hammer'] = ((df['high'] - df['close']) > 2 * (df['open'] - df['low'])) & \
                    ((df['close'] - df['low']) / (df['high'] - df['low']) > 0.6) & \
                    ((df['open'] - df['low']) / (df['high'] - df['low']) > 0.6)
                    
        df['is_hammer_morning'] = \
            (df['hammer'] & (df['close_time_hour'] >= 9) & (df['close_time_hour'] <= 12))

        df['is_hammer_weekend'] = \
            (df['hammer'] & df['close_time_weekday'].isin([5, 6]))
            
        return df
    
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in find_hammer_patterns: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in find_hammer_patterns', str(e))
        return None


def find_ml_morning_star_patterns(df, bot_settings):
    """
    Identifies the Morning Star candlestick pattern and adds related features to the DataFrame.

    A Morning Star candlestick pattern is identified when the following conditions are met:
    - The first candle is a bearish candle (close < open).
    - The second candle is a small-bodied candle that gaps down (open < close).
    - The third candle is a bullish candle (close > open).

    This function adds the following features to the DataFrame:
    - 'morning_star': Boolean indicating the presence of a Morning Star pattern.
    - 'is_morning_star_morning': Boolean indicating if the Morning Star pattern occurred between 9 AM and 12 PM.
    - 'is_morning_star_weekend': Boolean indicating if the Morning Star pattern occurred on a weekend (Saturday or Sunday).

    Args:
        df (pandas.DataFrame): DataFrame containing candlestick data (open, close, close_time).

    Returns:
        pandas.DataFrame or None: DataFrame with the 'morning_star', 'is_morning_star_morning', 
                                   and 'is_morning_star_weekend' columns added. Returns None if an error occurs.

    Raises:
        ValueError: If the DataFrame is None or empty.
        Exception: If any error occurs during the pattern identification process.
    """
    try:
        
        if df is None or df.empty:
            raise ValueError("df must be provided and cannot be None or empty.")
        
        df['morning_star'] = ((df['close'].shift(2) < df['open'].shift(2)) &
                            (df['open'].shift(1) < df['close'].shift(1)) &
                            (df['close'] > df['open']))
        
        df['is_morning_star_morning'] = \
            (df['morning_star'] & (df['close_time_hour'] >= 9) & (df['close_time_hour'] <= 12))

        df['is_morning_star_weekend'] = \
            (df['morning_star'] & df['close_time_weekday'].isin([5, 6]))
            
        return df
    
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in find_morning_star_patterns: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in find_morning_star_patterns', str(e))
        return None


def find_ml_bullish_engulfing_patterns(df, bot_settings):
    """
    Identifies the Bullish Engulfing candlestick pattern and adds related features to the DataFrame.

    A Bullish Engulfing candlestick pattern is identified when the following conditions are met:
    - The previous candle is a bearish candle (open > close).
    - The current candle is a bullish candle (open < close).
    - The current candle engulfs the previous candle's body (current open < previous close, current close > previous open).

    This function adds the following features to the DataFrame:
    - 'bullish_engulfing': Boolean indicating the presence of a Bullish Engulfing pattern.
    - 'is_bullish_engulfing_morning': Boolean indicating if the Bullish Engulfing pattern occurred between 9 AM and 12 PM.
    - 'is_bullish_engulfing_weekend': Boolean indicating if the Bullish Engulfing pattern occurred on a weekend (Saturday or Sunday).

    Args:
        df (pandas.DataFrame): DataFrame containing candlestick data (open, close, close_time).

    Returns:
        pandas.DataFrame or None: DataFrame with the 'bullish_engulfing', 'is_bullish_engulfing_morning', 
                                   and 'is_bullish_engulfing_weekend' columns added. Returns None if an error occurs.

    Raises:
        ValueError: If the DataFrame is None or empty.
        Exception: If any error occurs during the pattern identification process.
    """
    try:
        
        if df is None or df.empty:
            raise ValueError("df must be provided and cannot be None or empty.")
        
        df['bullish_engulfing'] = (df['open'].shift(1) > df['close'].shift(1)) & \
                                (df['open'] < df['close']) & \
                                (df['open'] < df['close'].shift(1)) & \
                                (df['close'] > df['open'].shift(1))
                                
        df['is_bullish_engulfing_morning'] = \
            (df['bullish_engulfing'] & (df['close_time_hour'] >= 9) & (df['close_time_hour'] <= 12))

        df['is_bullish_engulfing_weekend'] = \
            (df['bullish_engulfing'] & df['close_time_weekday'].isin([5, 6]))
            
        return df
    
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in find_bullish_engulfing_patterns: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in find_bullish_engulfing_patterns', str(e))
        return None
    
    
def calculate_ml_pct_change_and_lags(df, column_names_list, bot_settings):
    """
    Adds percentage change and lag features to multiple columns in the DataFrame.

    This function iterates over a list of column names and performs the following operations:
    - Calculates the percentage change for each column and creates a new column for it.
    - Generates lagged versions of each column for a range of lag values (from 'lag_min' to 'lag_max' 
      as specified).

    Args:
        result (pandas.DataFrame): The DataFrame containing the data.
        column_names_list (list of str): A list of column names to which the percentage change and lag features 
                                         will be added.
        lag_min (int): The minimum lag value to compute.
        lag_max (int): The maximum lag value to compute.

    Returns:
        pandas.DataFrame or None: The DataFrame with the added columns for percentage change and lags. 
                                   Returns None if an error occurs during the process.

    Raises:
        Exception: If an error occurs during the calculation of percentage change or lag features for any column.
    """
    try:
        
        lag_period = bot_settings.ml_lag_period
        
        for column_name in column_names_list:
        
            df[f'{column_name}_pct_change'] = df[f'{column_name}'].pct_change() * 100
            df[f'{column_name}_lag_{lag_period}'] = df[f'{column_name}'].shift(lag_period)
            
        return df
            
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in calculate_pct_change_and_lags: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in calculate_pct_change_and_lags', str(e))
        return None


def calculate_ml_momentum_signals(df, bot_settings):
    """
    Adds momentum-related signals to the DataFrame based on the close price.

    This function calculates whether a price is in support or resistance based on a rolling window,
    and adds boolean columns indicating the direction of momentum (positive or negative).
    It also adds a signal for trend reversal, defined when the sign of the close price change reverses.

    Args:
        df (pandas.DataFrame): The DataFrame containing the candlestick data.
        general_timeperiod (int): The rolling window used to calculate support and resistance.

    Returns:
        pandas.DataFrame or None: The DataFrame with the added momentum-related signals.
                                   Returns None if an error occurs during the calculation.
    """
    try:
        
        general_timeperiod = bot_settings.ml_general_timeperiod
        
        df['is_support'] = df['close'] == df['close'].rolling(window=general_timeperiod).min()
        df['is_resistance'] = df['close'] == df['close'].rolling(window=general_timeperiod).max()

        df['momentum_positive'] = df['close_pct_change'] > 0
        df['momentum_negative'] = df['close_pct_change'] < 0
        
        df['trend_reversal_signal'] = df['close_pct_change'].shift(1) * df['close_pct_change'] < 0
        
        return df
        
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in calculate_momentum_signals: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in calculate_momentum_signals', str(e))
        return None
    
    
def calculate_ml_rsi(df, bot_settings):
    """
    Calculates the Relative Strength Index (RSI) and generates buy/sell signals.

    This function calculates the RSI based on the closing prices and the given time period.
    It adds columns for the RSI and generates buy/sell signals based on predefined thresholds.

    Args:
        df (pandas.DataFrame): The DataFrame containing the candlestick data.
        general_timeperiod (int): The time period for calculating the RSI.
        rsi_buy_value (float): The RSI value below which a buy signal is generated.
        rsi_sell_value (float): The RSI value above which a sell signal is generated.

    Returns:
        pandas.DataFrame or None: The DataFrame with the calculated RSI and buy/sell signals.
                                   Returns None if an error occurs during the calculation.
    """
    try:
        
        general_timeperiod = bot_settings.ml_general_timeperiod
        rsi_buy_value = bot_settings.ml_rsi_buy
        rsi_sell_value = bot_settings.ml_rsi_sell
        
        df[f'rsi_{general_timeperiod}'] = talib.RSI(
            df['close'], 
            timeperiod=general_timeperiod
        )
        
        df[f'rsi_{general_timeperiod}_buy_signal'] = df[f'rsi_{general_timeperiod}'] < rsi_buy_value
        df[f'rsi_{general_timeperiod}_sell_signal'] = df[f'rsi_{general_timeperiod}'] > rsi_sell_value
        
        return df

    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in calculate_ml_rsi: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in calculate_ml_rsi', str(e))
        return None


def calculate_ml_ema(df, bot_settings):
    """
    Calculates the Exponential Moving Averages (EMA) and generates buy/sell signals.

    This function calculates the fast and slow EMAs based on the closing prices and adds buy/sell signals 
    based on the crossovers between the fast and slow EMAs.

    Args:
        df (pandas.DataFrame): The DataFrame containing the candlestick data.
        ema_fast_timeperiod (int): The time period for the fast EMA.
        ema_slow_timeperiod (int): The time period for the slow EMA.

    Returns:
        pandas.DataFrame or None: The DataFrame with the calculated EMAs and buy/sell signals.
                                   Returns None if an error occurs during the calculation.
    """
    try:
        
        ema_fast_timeperiod = bot_settings.ml_ema_fast_timeperiod
        ema_slow_timeperiod = bot_settings.ml_ema_slow_timeperiod
        
        df[f'ema_{ema_fast_timeperiod}'] = talib.EMA(
            df['close'], 
            timeperiod=ema_fast_timeperiod
        )
        
        df[f'ema_{ema_slow_timeperiod}'] = talib.EMA(
            df['close'], 
            timeperiod=ema_slow_timeperiod
        )
        
        df['ema_buy_signal'] = df[f'ema_{ema_fast_timeperiod}'] > df[f'ema_{ema_slow_timeperiod}']
        df['ema_sell_signal'] = df[f'ema_{ema_fast_timeperiod}'] < df[f'ema_{ema_slow_timeperiod}']
        
        return df

    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in calculate_ml_ema: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in calculate_ml_ema', str(e))
        return None


def calculate_ml_macd(df, bot_settings):
    """
    Calculates the Moving Average Convergence Divergence (MACD) and generates buy/sell signals.

    This function calculates the MACD and its signal line, and generates buy/sell signals based on 
    the MACD line crossing above or below the signal line. It also calculates the MACD histogram.

    Args:
        df (pandas.DataFrame): The DataFrame containing the candlestick data.
        macd_timeperiod (int): The time period for calculating the MACD.
        macd_signalperiod (int): The time period for the MACD signal line.

    Returns:
        pandas.DataFrame or None: The DataFrame with the calculated MACD and buy/sell signals.
                                   Returns None if an error occurs during the calculation.
    """
    try:
        
        macd_timeperiod = bot_settings.ml_macd_timeperiod
        macd_signalperiod = bot_settings.ml_macd_signalperiod
        
        df[f'macd_{macd_timeperiod}'], df[f'macd_signal_{macd_signalperiod}'], _ = talib.MACD(
            df['close'], 
            fastperiod=macd_timeperiod, 
            slowperiod=macd_timeperiod * 2, 
            signalperiod=macd_signalperiod
        )
        
        df[f'macd_histogram_{macd_timeperiod}'] = \
            df[f'macd_{macd_timeperiod}'] - df[f'macd_signal_{macd_signalperiod}']
        
        df['macd_buy_signal'] = df[f'macd_{macd_timeperiod}'] > df[f'macd_signal_{macd_signalperiod}']
        df['macd_sell_signal'] = df[f'macd_{macd_timeperiod}'] < df[f'macd_signal_{macd_signalperiod}']
        
        return df

    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in calculate_ml_macd: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in calculate_ml_macd', str(e))
        return None


def calculate_ml_bollinger_bands(df, bot_settings):
    """
    Calculates Bollinger Bands and generates buy/sell signals.

    This function calculates the upper and lower Bollinger Bands based on the closing prices, 
    and generates buy/sell signals when the price crosses the bands.

    Args:
        df (pandas.DataFrame): The DataFrame containing the candlestick data.
        bollinger_timeperiod (int): The time period for calculating the Bollinger Bands.
        bollinger_nbdev (int): The number of standard deviations for the bands.

    Returns:
        pandas.DataFrame or None: The DataFrame with the calculated Bollinger Bands and buy/sell signals.
                                   Returns None if an error occurs during the calculation.
    """
    try:
        
        bollinger_timeperiod = bot_settings.ml_bollinger_timeperiod
        bollinger_nbdev = bot_settings.ml_bollinger_nbdev
        
        df['upper_band'], df['middle_band'], df['lower_band'] = talib.BBANDS(
            df['close'],
            timeperiod=bollinger_timeperiod,
            nbdevup=bollinger_nbdev,
            nbdevdn=bollinger_nbdev,
            matype=0
        )
        
        df['bollinger_buy_signal'] = df['close'] < df['lower_band']
        df['bollinger_sell_signal'] = df['close'] > df['upper_band']
        
        return df
        
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in calculate_ml_bollinger_bands: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in calculate_ml_bollinger_bands', str(e))
        return None
    
    
def calculate_ml_time_patterns(df, bot_settings):
    """
    Adds time-based features to the DataFrame based on the 'close_time' column.

    This function creates new features based on the 'close_time' column:
    - Extracts the hour, weekday, and month from 'close_time'.
    - Computes cyclic (sinusoidal and cosinusoidal) transformations for hour, weekday, and month 
      to capture cyclical patterns in time.
    - Adds a boolean feature indicating whether the 'close_time' corresponds to a weekend (Saturday or Sunday).

    Args:
        df (pandas.DataFrame): The DataFrame containing the 'close_time' column.
    
    Returns:
        pandas.DataFrame or None: The DataFrame with additional time-based features. 
                                   Returns None if an error occurs during the calculation.
    """
    try:
        
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
        
        df['close_time_hour'] = df['close_time'].dt.hour
        df['close_time_weekday'] = df['close_time'].dt.weekday
        df['close_time_month'] = df['close_time'].dt.month

        df['hour_sin'] = np.sin(2 * np.pi * df['close_time_hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['close_time_hour'] / 24)
        df['weekday_sin'] = np.sin(2 * np.pi * df['close_time_weekday'] / 7)
        df['weekday_cos'] = np.cos(2 * np.pi * df['close_time_weekday'] / 7)
        df['month_sin'] = np.sin(2 * np.pi * df['close_time_month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['close_time_month'] / 12)

        df['is_weekend'] = df['close_time_weekday'].isin([5, 6])
        
        return df

    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in calculate_ml_time_patterns: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in calculate_ml_time_patterns', str(e))
        return None
        
        
def calculate_ml_rsi_macd_ratio_and_diff(df, bot_settings):
    """
    Preprocesses the input DataFrame for use in a Random Forest model.

    The function performs the following steps:
        1. Calculates the 'rsi_macd_ratio' by dividing the RSI (Relative Strength Index) by the MACD histogram, with a small epsilon to prevent division by zero.
        2. Computes the 'macd_signal_diff' as the difference between the MACD signal line and the MACD histogram.

    Arguments:
        df (pandas.DataFrame): The input DataFrame containing columns 'rsi_14', 'macd_histogram_12', and 'macd_signal_9' that will be used for feature calculation.

    Returns:
        pandas.DataFrame: The processed DataFrame with new columns 'rsi_macd_ratio' and 'macd_signal_diff', or None if an error occurs.

    Example:
        df = preprocess_df_for_random_forest(df)
    """
    try:
        
        general_timeperiod = bot_settings.ml_general_timeperiod
        macd_timeperiod = bot_settings.ml_macd_timeperiod
        macd_signalperiod = bot_settings.ml_macd_signalperiod
        
        epsilon = 1e-10
        df['rsi_macd_ratio'] = df[f'rsi_{general_timeperiod}'] / (df[f'macd_histogram_{macd_timeperiod}'] + epsilon)
        df['macd_signal_diff'] = df[f'macd_signal_{macd_signalperiod}'] - df[f'macd_histogram_{macd_timeperiod}']
        
        return df
        
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in calculate_ml_rsi_macd_ratio_and_diff: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in calculate_ml_rsi_macd_ratio_and_diff', str(e))
        return None
    
    
def handle_initial_ml_df_preparaition(df, bot_settings):
    """
    Prepares the initial DataFrame by converting specific columns to numeric types.

    This function ensures that the columns 'open', 'low', 'high', 'close', and 'volume' 
    in the given DataFrame are converted to numeric types. Non-numeric values are coerced 
    to NaN. If an exception occurs during processing, it is logged, and the function 
    returns None.

    Parameters:
        df (pandas.DataFrame): The input DataFrame containing market data with columns 
        'open', 'low', 'high', 'close', and 'volume'.

    Returns:
        pandas.DataFrame: The modified DataFrame with specified columns converted to numeric types.
        Returns None if an exception occurs.

    Raises:
        None: All exceptions are handled and logged internally.
    """
    try:
        
        df['open'] = pd.to_numeric(df['open'], errors='coerce')
        df['low'] = pd.to_numeric(df['low'], errors='coerce')
        df['high'] = pd.to_numeric(df['high'], errors='coerce')
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
        
        return df
        
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in handle_initial_ml_df_preparaition: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in handle_initial_ml_df_preparaition', str(e))
        return None
    

def handle_final_ml_df_cleaninig(df, columns_to_drop, bot_settings):
    """
    Performs final cleaning on the DataFrame.

    This function removes specified columns, fills missing values with 0, 
    and converts boolean columns to integer type for further processing.

    Parameters:
        df (pandas.DataFrame): The input DataFrame to be cleaned.
        columns_to_drop (list): A list of column names to be dropped from the DataFrame.

    Returns:
        pandas.DataFrame: The cleaned DataFrame with specified columns dropped, 
        missing values filled with 0, and boolean columns converted to integers.
        Returns None if an exception occurs.

    Raises:
        None: All exceptions are handled and logged internally.
    """
    try:
        
        df.drop(columns=columns_to_drop, inplace=True)
        df.fillna(0, inplace=True)
        df[df.select_dtypes(include=['bool']).columns] = \
            df.select_dtypes(include=['bool']).astype(int)
            
        return df
        
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in handle_final_ml_df_cleaninig: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in handle_final_ml_df_cleaninig', str(e))
        return None
        
        
def prepare_df(df=None, 
               bot_settings=None, 
               ):
    """
    Prepares the dataframe by calculating technical indicators such as 
    moving averages, RSI, MACD, volume trends, etc., and returns the modified dataframe.

    Parameters:
        - df (pd.DataFrame): The input dataframe containing market data. 
        - regresion (bool): Flag to indicate if the dataframe is being prepared for regression (not used in the code right now).
        - clasification (bool): Flag to indicate if the dataframe is being prepared for classification (not used in the code right now).

    Returns:
        - pd.DataFrame: The modified dataframe with technical indicators added as new columns.
    """
    
    if bot_settings is None:
        raise ValueError("bot_settings must be provided and cannot be None or empty.")
    
    try:
        
        if df is None or df.empty:
            raise ValueError("df must be provided and cannot be None or empty.")
        
        result_df = df.copy()
        
        handle_initial_ml_df_preparaition(result_df, bot_settings)
        
        calculate_ml_rsi(result_df, bot_settings)
        calculate_ml_macd(result_df, bot_settings)
        calculate_ml_ema(result_df, bot_settings)
        calculate_ml_bollinger_bands(result_df, bot_settings)
        calculate_ml_rsi_macd_ratio_and_diff(result_df, bot_settings)
        
        calculate_ml_time_patterns(result_df, bot_settings)
        find_ml_hammer_patterns(result_df, bot_settings)
        find_ml_morning_star_patterns(result_df, bot_settings)
        find_ml_bullish_engulfing_patterns(result_df, bot_settings)
        
        columns_to_calc = ['close', 'volume', f'rsi_{bot_settings.ml_general_timeperiod}']
        calculate_ml_pct_change_and_lags(result_df, columns_to_calc, bot_settings)
        
        calculate_ml_momentum_signals(result_df, bot_settings)

        columns_to_drop=[
            'open_time', 
            'close_time', 
            'ignore', 
            'quote_asset_volume', 
            'number_of_trades',
            'taker_buy_base_asset_volume', 
            'taker_buy_quote_asset_volume',
            ]
        handle_final_ml_df_cleaninig(result_df, columns_to_drop, bot_settings)

        return result_df
    
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in is_hammer: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in is_hammer', str(e))
        return None