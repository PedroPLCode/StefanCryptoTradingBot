import pandas as pd
import numpy as np
import talib
from ..utils.logging import logger
from ..utils.app_utils import send_admin_email

def find_hammer_patterns(df, bot_settings):
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


def find_morning_star_patterns(df, bot_settings):
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


def find_bullish_engulfing_patterns(df, bot_settings):
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
    
    
def add_pct_change_and_lags_calculations(result, column_names_list, bot_settings):
    """
    Adds percentage change and lag features to multiple columns in the DataFrame.

    This function iterates over a list of column names and performs the following operations:
    - Calculates the percentage change for each column and creates a new column for it.
    - Generates lagged versions of each column for a range of lag values (from 'lag_min' to 'lag_max' 
      as specified in the 'settings' dictionary).
    
    Args:
        result (pandas.DataFrame): The DataFrame containing the data.
        column_names_list (list of str): A list of column names to which the percentage change and lag features 
                                         will be added.
        settings (dict): A dictionary containing settings for the function. The keys 'lag_min' and 'lag_max' 
                         define the range of lag values to compute.
    
    Returns:
        pandas.DataFrame or None: The DataFrame with the added columns for percentage change and lags. 
                                   Returns None if an error occurs during the process.

    Raises:
        Exception: If an error occurs during the calculation of percentage change or lag features for any column.
    """
    
    for column_name in column_names_list:
        try:
            lag_min = bot_settings.ml_lag_min
            lag_max = bot_settings.ml_lag_max
        
            result[f'{column_name}_pct_change'] = result[f'{column_name}'].pct_change() * 100
                    
            for lag in range(lag_min, lag_max):
                result[f'{column_name}_lag_{lag}'] = result[f'{column_name}'].shift(lag)
            
        except Exception as e:
            logger.error(f"Bot {bot_settings.id} Exception in add_pct_change_and_lags_calculations: {str(e)}")
            send_admin_email(f'Bot {bot_settings.id} Exception in add_pct_change_and_lags_calculations', str(e))
            return None


def add_time_patterns_calculations(df, bot_settings):
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
                                   Returns None if an error occurs during the process.
    
    Raises:
        Exception: If an error occurs during the feature extraction and transformation process.
    """

    try:
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
        df['close_time_hour'] = df['close_time'].dt.hour
        df['close_time_hour_sin'] = np.sin(2 * np.pi * df['close_time_hour'] / 24)
        df['close_time_hour_cos'] = np.cos(2 * np.pi * df['close_time_hour'] / 24)
        df['close_time_weekday'] = df['close_time'].dt.weekday
        df['close_time_weekday_sin'] = np.sin(2 * np.pi * df['close_time_weekday'] / 24)
        df['close_time_weekday_cos'] = np.cos(2 * np.pi * df['close_time_weekday'] / 24)
        df['close_time_month'] = df['close_time'].dt.month
        df['close_time_month_sin'] = np.sin(2 * np.pi * df['close_time_month'] / 24)
        df['close_time_month_cos'] = np.cos(2 * np.pi * df['close_time_month'] / 24)
        df['is_close_time_weekend'] = df['close_time_weekday'].isin([5, 6])
        
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in add_time_patterns_calculations: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in add_time_patterns_calculations', str(e))
        return None
        
        
def calculate_df(df=None, 
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
        
        result = df.copy()
        
        general_timeperiod = bot_settings.ml_general_timeperiod
        bollinger_timeperiod = bot_settings.ml_bollinger_timeperiod
        bollinger_nbdev = bot_settings.ml_bollinger_nbdev
        macd_timeperiod = bot_settings.ml_macd_timeperiod
        macd_signalperiod = bot_settings.ml_macd_signalperiod
        stoch_k_timeperiod = bot_settings.ml_stoch_k_timeperiod
        stoch_d_timeperiod = bot_settings.ml_stoch_d_timeperiod
        stoch_rsi_k_timeperiod = bot_settings.ml_stoch_rsi_k_timeperiod
        stoch_rsi_d_timeperiod = bot_settings.ml_stoch_rsi_d_timeperiod
        ema_fast_timeperiod = bot_settings.ml_ema_fast_timeperiod
        ema_slow_timeperiod = bot_settings.ml_ema_slow_timeperiod
        psar_acceleration = bot_settings.ml_psar_acceleration
        psar_maximum = bot_settings.ml_psar_maximum
        
        result['open'] = pd.to_numeric(result['open'], errors='coerce')
        result['close'] = pd.to_numeric(result['close'], errors='coerce')
        result['volume'] = pd.to_numeric(result['volume'], errors='coerce')
        
        add_time_patterns_calculations(result, bot_settings)
        
        find_hammer_patterns(result, bot_settings)
        find_morning_star_patterns(result, bot_settings)
        find_bullish_engulfing_patterns(result, bot_settings)

        result[f'rsi_{general_timeperiod}'] = talib.RSI(
            result['close'], 
            timeperiod=general_timeperiod
        )
            
        result[f'cci_{general_timeperiod}'] = talib.CCI(
            result['high'],
            result['low'],
            result['close'],
            timeperiod=general_timeperiod
        )
    
        result[f'mfi_{general_timeperiod}'] = talib.MFI(
            result['high'],
            result['low'],
            result['close'],
            result['volume'],
            timeperiod=general_timeperiod
        )
            
        result[f'atr_{general_timeperiod}'] = talib.ATR(
            result['high'], 
            result['low'], 
            result['close'], 
            timeperiod=general_timeperiod
        )
            
        result[f'adx_{general_timeperiod}'] = talib.ADX(
            result['high'],
            result['low'],
            result['close'],
            timeperiod=general_timeperiod
        )
            
        result[f'plus_di_{general_timeperiod}'] = talib.PLUS_DI(
            result['high'],
            result['low'],
            result['close'],
            timeperiod=general_timeperiod
        )
            
        result[f'minus_di_{general_timeperiod}'] = talib.MINUS_DI(
            result['high'],
            result['low'],
            result['close'],
            timeperiod=general_timeperiod
        )

        result[f'ema_{ema_fast_timeperiod}'] = talib.EMA(
            result['close'], 
            timeperiod=ema_fast_timeperiod
            )
        
        result[f'ema_{ema_slow_timeperiod}'] = talib.EMA(
            result['close'], 
            timeperiod=ema_slow_timeperiod
            )

        result[f'macd_{macd_timeperiod}'], result[f'macd_signal_{macd_signalperiod}'], _ = talib.MACD(
            result['close'], 
            fastperiod=macd_timeperiod, 
            slowperiod=macd_timeperiod *2, 
            signalperiod=macd_signalperiod
            )
        result[f'macd_histogram_{macd_timeperiod}'] = \
            result[f'macd_{macd_timeperiod}'] - result[f'macd_signal_{macd_signalperiod}']

        result['upper_band'], result['middle_band'], result['lower_band'] = talib.BBANDS(
                result['close'],
                timeperiod=bollinger_timeperiod,
                nbdevup=bollinger_nbdev,
                nbdevdn=bollinger_nbdev,
                matype=0
            )
        
        result['stoch_k'], result['stoch_d'] = talib.STOCH(
            result['high'],
            result['low'],
            result['close'],
            fastk_period=stoch_k_timeperiod,
            slowk_period=stoch_d_timeperiod,
            slowk_matype=0,
            slowd_period=stoch_d_timeperiod,
            slowd_matype=0
        )
        
        result['stoch_rsi_k'], result['stoch_rsi_d'] = talib.STOCHRSI(
            result['close'],
            timeperiod=stoch_rsi_k_timeperiod,
            fastk_period=stoch_rsi_d_timeperiod,
            fastd_period=stoch_rsi_d_timeperiod,
            fastd_matype=0
        )    
            
        result['typical_price'] = (result['high'] + result['low'] + result['close']) / 3
        result['vwap'] = (result['typical_price'] * result['volume']).cumsum() / result['volume'].cumsum()
        
        result['psar'] = talib.SAR(
            result['high'],
            result['low'],
            acceleration=psar_acceleration,
            maximum=psar_maximum,
        )
        
        result['ma_200'] = result['close'].rolling(window=200).mean()
    
        result['ma_50'] = result['close'].rolling(window=50).mean()
        
        columns_to_calculate_list = [
                    'close', 
                    'volume', 
                    f'rsi_{general_timeperiod}'
                    f'cci_{general_timeperiod}',
                    f'mfi_{general_timeperiod}',
                    f'atr_{general_timeperiod}',
                    f'adx_{general_timeperiod}',
                    f'plus_di_{general_timeperiod}',
                    f'minus_di_{general_timeperiod}',
                    f'ema_{ema_fast_timeperiod}',
                    f'ema_{ema_slow_timeperiod}',
                    f'macd_{macd_timeperiod}', 
                    f'macd_signal_{macd_signalperiod}', 
                    f'macd_histogram_{macd_timeperiod}',
                    'upper_band', 
                    'middle_band', 
                    'lower_band',
                    'stoch_k',
                    'stoch_d',
                    'stoch_rsi_k',
                    'stoch_rsi_d',
                    'psar',
                    'vwap',
                    'ma_200',
                    'ma_50'
                    ],
        add_pct_change_and_lags_calculations(
            result, 
            columns_to_calculate_list,
            bot_settings
            )
        
        columns_to_drop=[
            'open', 
            'low', 
            'high', 
            'open_time', 
            'close_time', 
            'ignore', 
            'typical_price'
            ]
        result.drop(columns=columns_to_drop, inplace=True)
        result.fillna(0, inplace=True)
        result[result.select_dtypes(include=['bool']).columns] = \
            result.select_dtypes(include=['bool']).astype(int)

        return result
    
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in is_hammer: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in is_hammer', str(e))
        return None