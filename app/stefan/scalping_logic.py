import pandas as pd
import talib
from ..utils.logging import logger
from ..utils.app_utils import send_admin_email

def calculate_scalp_indicators(df, bot_settings):
    try:
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df['high'] = pd.to_numeric(df['high'], errors='coerce')
        df['low'] = pd.to_numeric(df['low'], errors='coerce')
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
        
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
            
        df['rsi'] = talib.RSI(df['close'], timeperiod=bot_settings.rsi_timeperiod)

        df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=bot_settings.atr_timeperiod)

        df['ema_fast'] = talib.EMA(df['close'], timeperiod=bot_settings.ema_fast_timeperiod)
        df['ema_slow'] = talib.EMA(df['close'], timeperiod=bot_settings.ema_slow_timeperiod)

        df.dropna(subset=['close'], inplace=True)
        
        if len(df) < 26 + 14:
            logger.trade('Not enough data points for MACD calculation.')
            return df

        df['macd'], df['macd_signal'], _ = talib.MACD(
            df['close'],
            fastperiod=bot_settings.macd_timeperiod,
            slowperiod=bot_settings.macd_timeperiod * 2,
            signalperiod=bot_settings.macd_signalperiod
        )
        
        df['macd_histogram'] = df['macd'] - df['macd_signal']

        df['upper_band'], df['middle_band'], df['lower_band'] = talib.BBANDS(
            df['close'],
            timeperiod=bot_settings.boilinger_timeperiod,
            nbdevup=bot_settings.boilinger_nbdev,
            nbdevdn=bot_settings.boilinger_nbdev,
            matype=0
        )
        
        df['cci'] = talib.CCI(
            df['high'],
            df['low'],
            df['close'],
            timeperiod=bot_settings.cci_timeperiod
        )

        df['mfi'] = talib.MFI(
            df['high'],
            df['low'],
            df['close'],
            df['volume'],
            timeperiod=bot_settings.mfi_timeperiod
        )
        
        df['stoch_k'], df['stoch_d'] = talib.STOCH(
            df['high'],
            df['low'],
            df['close'],
            fastk_period=bot_settings.stock_k_timeperiod,
            slowk_period=bot_settings.stock_d_timeperiod,
            slowk_matype=0,
            slowd_period=bot_settings.stock_d_timeperiod,
            slowd_matype=0
        )
        
        df['psar'] = talib.SAR(
            df['high'],
            df['low'],
            acceleration=bot_settings.psar_acceleration,
            maximum=bot_settings.psar_maximum
        )

        df['vwap'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()

        columns_to_check = ['macd', 'macd_signal', 'cci', 'upper_band', 'lower_band', 'mfi', 'atr', 'stoch_k', 'stoch_d', 'psar']

        df.dropna(subset=columns_to_check, inplace=True)
        
        return df
    
    except IndexError as e:
        logger.error(f'IndexError in calculate_scalp_indicators bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in calculate_scalp_indicators bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in calculate_scalp_indicators bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in calculate_scalp_indicators bot {bot_settings.id}', str(e))
        return False


def check_scalping_buy_signal_v1(df, bot_settings):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False
        
        latest_data = df.iloc[-1]
        previous_data = df.iloc[-2]
        
        # Primary - Buy Signal:
        # - RSI indicates potential upward movement (oversold)
        # - MACD crosses the signal line from below (confirmation of trend strength)
        if (float(latest_data['rsi']) < float(bot_settings.rsi_buy) and
            float(previous_data['macd']) < float(previous_data['macd_signal']) and 
            float(latest_data['macd']) > float(latest_data['macd_signal'])):
            
            return True
            
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_scalping_buy_signal bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_scalping_buy_signal bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_scalping_buy_signal bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_scalping_buy_signal bot {bot_settings.id}', str(e))
        return False
    
    
def check_scalping_sell_signal_v1(df, bot_settings):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False
        
        latest_data = df.iloc[-1]
        previous_data = df.iloc[-2]

        # Primary - Sell Signal:
        # - RSI is indicates overheated market
        # - MACD crosses the signal line from above (weakening of the upward trend)
        if (float(latest_data['rsi']) > float(bot_settings.rsi_sell) and
            float(previous_data['macd']) > float(previous_data['macd_signal']) and 
            float(latest_data['macd']) < float(latest_data['macd_signal'])):
            
            return True
        
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_scalping_sell_signal bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_scalping_sell_signal bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_scalping_sell_signal bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_scalping_sell_signal bot {bot_settings.id}', str(e))
        return False
            
            
def check_scalping_buy_signal_v2(df, bot_settings):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False
        
        latest_data = df.iloc[-1]
        previous_data = df.iloc[-2]

        # Secondary - Buy Signal:
        # Current price is below the lower Bollinger Band, suggesting an oversold condition.
        # Stochastic K crosses above the Stochastic D, indicating a potential bullish reversal.
        # Stochastic K is below the specified buy threshold, confirming the possibility of an upward move.
        if (float(latest_data['close']) < float(latest_data['lower_band']) and
            float(previous_data['stoch_k']) < float(previous_data['stoch_d']) and
            float(latest_data['stoch_k']) > float(latest_data['stoch_d']) and
            float(latest_data['stoch_k']) < float(bot_settings.stoch_buy)):
            
            return True
            
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_scalping_buy_signal bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_scalping_buy_signal bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_scalping_buy_signal bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_scalping_buy_signal bot {bot_settings.id}', str(e))
        return False
    
    
def check_scalping_sell_signal_v2(df, bot_settings):
    from .logic_utils import is_df_valid
    try:        
        if not is_df_valid(df, bot_settings.id):
            return False

        latest_data = df.iloc[-1]
        previous_data = df.iloc[-2]
        
        # Secondary - Sell Signal:
        # Current price is above the upper Bollinger Band, indicating an overbought condition.
        # Stochastic K crosses below the Stochastic D, suggesting a potential bearish reversal.
        # Stochastic K is above the specified sell threshold, confirming the possibility of a downward move.
        if (float(latest_data['close']) > float(latest_data['upper_band']) and
            float(previous_data['stoch_k']) > float(previous_data['stoch_d']) and
            float(latest_data['stoch_k']) < float(latest_data['stoch_d']) and
            float(latest_data['stoch_k']) > float(bot_settings.stoch_sell)):
            
            return True
        
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_scalping_sell_signal bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_scalping_sell_signal bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_scalping_sell_signal bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_scalping_sell_signal bot {bot_settings.id}', str(e))
        return False
    
            
def check_scalping_buy_signal_v3(df, bot_settings):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False
        
        latest_data = df.iloc[-1]
        previous_data = df.iloc[-2]

        # Bullish uptrend - Buy Signal:
        # - RSI indicates potential upward movement (oversold)
        # - Closing price is above the fast EMA and slow EMA
        # - MACD crosses the signal line from below (confirmation of trend strength)
        if (float(latest_data['rsi']) < float(bot_settings.rsi_buy) and
            float(latest_data['close']) > float(latest_data['ema_fast']) and
            float(latest_data['close']) > float(latest_data['ema_slow']) and
            float(previous_data['macd']) < float(previous_data['macd_signal']) and 
            float(latest_data['macd']) > float(latest_data['macd_signal'])):
            
            return True
            
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_scalping_buy_signal bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_scalping_buy_signal bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_scalping_buy_signal bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_scalping_buy_signal bot {bot_settings.id}', str(e))
        return False
    
    
def check_scalping_sell_signal_v3(df, bot_settings):
    from .logic_utils import is_df_valid
    try:        
        if not is_df_valid(df, bot_settings.id):
            return False

        latest_data = df.iloc[-1]
        previous_data = df.iloc[-2]
        
        # Bullish uptrend - Sell Signal:
        # - RSI indicates overheated market
        # - Closing price drops below the fast EMA and slow EMA
        # - MACD crosses the signal line from above (weakening of the upward trend)
        if (float(latest_data['rsi']) > float(bot_settings.rsi_sell) and
            float(latest_data['close']) < float(latest_data['ema_fast']) and
            float(latest_data['close']) < float(latest_data['ema_slow']) and
            float(previous_data['macd']) > float(previous_data['macd_signal']) and 
            float(latest_data['macd']) < float(latest_data['macd_signal'])):
            
            return True
        
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_scalping_sell_signal bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_scalping_sell_signal bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_scalping_sell_signal bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_scalping_sell_signal bot {bot_settings.id}', str(e))
        return False
    
    
def check_scalping_buy_signal_v4(df, bot_settings):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False
        
        latest_data = df.iloc[-1]
        previous_data = df.iloc[-2]
        
        # Bearish downtrend - Buy Signal:
        # - RSI is indicates potential upward movement (oversold)
        # - MACD crosses the signal line from below (confirmation of trend strength)
        # - Stochastic K is above D 
        # - Current price above VWAP
        if (float(latest_data['rsi']) < float(bot_settings.rsi_buy) and
            float(previous_data['macd']) < float(previous_data['macd_signal']) and
            float(latest_data['macd']) > float(latest_data['macd_signal']) and
            float(latest_data['stoch_k']) > float(latest_data['stoch_d']) and
            float(latest_data['close']) > float(latest_data['vwap'])):
            
            return True
            
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_scalping_buy_signal bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_scalping_buy_signal bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_scalping_buy_signal bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_scalping_buy_signal bot {bot_settings.id}', str(e))
        return False

    
def check_scalping_sell_signal_v4(df, bot_settings):
    from .logic_utils import is_df_valid
    try:        
        if not is_df_valid(df, bot_settings.id):
            return False

        latest_data = df.iloc[-1]
        previous_data = df.iloc[-2]
        
        # Bearish downtrend - Sell Signal:
        # - RSI is indicates overheated market
        # - MACD crosses the signal line from above (weakening of the upward trend)
        # - Stochastic K is lower than D
        # - Current price below VWAP
        if (float(latest_data['rsi']) > float(bot_settings.rsi_sell) and
            float(previous_data['macd']) > float(previous_data['macd_signal']) and
            float(latest_data['macd']) < float(latest_data['macd_signal']) and
            float(latest_data['stoch_k']) < float(latest_data['stoch_d']) and
            float(latest_data['close']) < float(latest_data['vwap'])):
            
            return True
        
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_scalping_sell_signal bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_scalping_sell_signal bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_scalping_sell_signal bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_scalping_sell_signal bot {bot_settings.id}', str(e))
        return False
    
    
def check_scalping_buy_signal_v5(df, bot_settings):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False
        
        latest_data = df.iloc[-1]
        previous_data = df.iloc[-2]

        # Sideways trend - Buy Signal:
        # - RSI indicates potential upward movement (oversold)
        # - Price approaches the lower Bollinger Band
        # - Stochastic K crosses above D from below
        # - Price is above the VWAP
        if (float(latest_data['rsi']) < float(bot_settings.rsi_buy) and
            float(latest_data['close']) <= float(latest_data['lower_band']) and
            float(previous_data['stoch_k']) < float(previous_data['stoch_d']) and 
            float(latest_data['stoch_k']) > float(latest_data['stoch_d']) and
            float(latest_data['close']) > float(latest_data['vwap'])):
            
            return True
            
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_scalping_buy_signal bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_scalping_buy_signal bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_scalping_buy_signal bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_scalping_buy_signal bot {bot_settings.id}', str(e))
        return False
    
    
def check_scalping_sell_signal_v5(df, bot_settings):
    from .logic_utils import is_df_valid
    try:        
        if not is_df_valid(df, bot_settings.id):
            return False

        latest_data = df.iloc[-1]
        previous_data = df.iloc[-2]
        
        # Sideways trend - Sell Signal:
        # - RSI is indicates overheated market
        # - Price approaches the upper Bollinger Band
        # - Stochastic K crosses below D from above
        # - Price is below the VWAP
        if (float(latest_data['rsi']) > float(bot_settings.rsi_sell) and
            float(latest_data['close']) >= float(latest_data['upper_band']) and
            float(previous_data['stoch_k']) > float(previous_data['stoch_d']) and
            float(latest_data['stoch_k']) < float(latest_data['stoch_d']) and
            float(latest_data['close']) < float(latest_data['vwap'])):
            
            return True
        
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_scalping_sell_signal bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_scalping_sell_signal bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_scalping_sell_signal bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_scalping_sell_signal bot {bot_settings.id}', str(e))
        return False
    
    
def check_scalping_buy_signal_v6(df, bot_settings):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False

        latest_data = df.iloc[-1]
        previous_data = df.iloc[-2]
        
        # Bearish downtrend simplified - Buy Signal:
        # - RSI is indicates potential upward movement (oversold)
        # - Current close price above fast EMA
        # - Current price above VWAP
        if (float(latest_data['rsi']) < float(bot_settings.rsi_buy) and
            float(latest_data['close']) > float(latest_data['ema_fast']) and
            float(latest_data['close']) > float(latest_data['vwap'])):
            
            return True
        
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_scalping_buy_signal bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_scalping_buy_signal bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_scalping_buy_signal bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_scalping_buy_signal bot {bot_settings.id}', str(e))
        return False

    
    
def check_scalping_sell_signal_v6(df, bot_settings):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False

        latest_data = df.iloc[-1]
        previous_data = df.iloc[-2]

        # Bearish downtrend simplified - Sell Signal:
        # - RSI is indicates overheated market
        # - Current close below fast EMA
        # - Current price below VWAP
        if (float(latest_data['rsi']) > float(bot_settings.rsi_sell) and
            float(latest_data['close']) < float(latest_data['ema_fast']) and
            float(latest_data['close']) < float(latest_data['vwap'])):
            
            return True
        
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_scalping_sell_signal bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_scalping_sell_signal bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_scalping_sell_signal bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_scalping_sell_signal bot {bot_settings.id}', str(e))
        return False