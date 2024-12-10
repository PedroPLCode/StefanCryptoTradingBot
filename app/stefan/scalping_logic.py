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
            fastk_period=bot_settings.stoch_k_timeperiod,
            slowk_period=bot_settings.stoch_d_timeperiod,
            slowk_matype=0,
            slowd_period=bot_settings.stoch_d_timeperiod,
            slowd_matype=0
        )
        
        df['stoch_rsi'] = talib.RSI(df['rsi'], timeperiod=bot_settings.stoch_rsi_timeperiod)
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
        
        df['psar'] = talib.SAR(
            df['high'],
            df['low'],
            acceleration=bot_settings.psar_acceleration,
            maximum=bot_settings.psar_maximum
        )
        
        df['adx'] = talib.ADX(
            df['high'],
            df['low'],
            df['close'],
            timeperiod=bot_settings.adx_timeperiod
        )
        
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

        df['vwap'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()

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


def check_scalping_buy_signal_v1(df, bot_settings, trend, averages, latest_data, previous_data):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False
        
        if (trend != 'downtrend' and 
            float(latest_data['rsi']) <= float(bot_settings.rsi_buy) and
            float(latest_data['rsi']) >= float(averages['avg_rsi']) and
            (float(averages['avg_macd']) <= float(averages['avg_macd_signal']) or 
            float(previous_data['macd']) <= float(previous_data['macd_signal'])) and
            float(latest_data['macd']) >= float(latest_data['macd_signal']) and
            float(latest_data['volume']) >= float(averages['avg_volume'])):

            return True
            
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_scalping_buy_signal_v1 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_scalping_buy_signal_v1 bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_scalping_buy_signal_v1 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_scalping_buy_signal_v1 bot {bot_settings.id}', str(e))
        return False
    
    
def check_scalping_sell_signal_v1(df, bot_settings, trend, averages, latest_data, previous_data):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False

        if (float(latest_data['rsi']) >= float(bot_settings.rsi_sell) and
            (float(averages['avg_macd']) >= float(averages['avg_macd_signal']) or 
            float(previous_data['macd']) >= float(previous_data['macd_signal'])) and
            float(latest_data['macd']) <= float(latest_data['macd_signal'])):

            return True
        
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_scalping_sell_signal_v1 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_scalping_sell_signal_v1 bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_scalping_sell_signal_v1 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_scalping_sell_signal_v1 bot {bot_settings.id}', str(e))
        return False
            
            
def check_scalping_buy_signal_v2(df, bot_settings, trend, averages, latest_data, previous_data):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False

        if (trend != 'downtrend' and 
            float(latest_data['close']) <= float(latest_data['lower_band']) and
            (float(averages['avg_stoch_k']) <= float(averages['avg_stoch_d']) or
            float(previous_data['stoch_k']) <= float(previous_data['stoch_d'])) and
            float(latest_data['stoch_k']) >= float(latest_data['stoch_d']) and
            float(latest_data['stoch_k']) <= float(bot_settings.stoch_buy) and
            float(latest_data['volume']) >= float(averages['avg_volume'])):
            
            return True
            
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_scalping_buy_signal_v2 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_scalping_buy_signal_v2 bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_scalping_buy_signal_v2 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_scalping_buy_signal_v2 bot {bot_settings.id}', str(e))
        return False
    
    
def check_scalping_sell_signal_v2(df, bot_settings, trend, averages, latest_data, previous_data):
    from .logic_utils import is_df_valid
    try:        
        if not is_df_valid(df, bot_settings.id):
            return False
        
        if (float(latest_data['close']) >= float(latest_data['upper_band']) and
            (float(averages['avg_stoch_k']) >= float(averages['avg_stoch_d']) or
            float(previous_data['stoch_k']) >= float(previous_data['stoch_d'])) and
            float(latest_data['stoch_k']) <= float(latest_data['stoch_d']) and
            float(latest_data['stoch_k']) >= float(bot_settings.stoch_sell)):
            
            return True
        
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_scalping_sell_signal_v2 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_scalping_sell_signal_v2 bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_scalping_sell_signal_v2 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_scalping_sell_signal_v2 bot {bot_settings.id}', str(e))
        return False
    
            
def check_scalping_buy_signal_v3(df, bot_settings, trend, averages, latest_data, previous_data):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False

        if (trend != 'downtrend' and 
            float(latest_data['close']) <= float(latest_data['lower_band']) and
            float(latest_data['stoch_rsi_k']) <= float(bot_settings.stoch_buy) and
            float(latest_data['stoch_rsi_k']) >= float(averages['avg_stoch_rsi_k']) and 
            float(latest_data['stoch_rsi_k']) >= float(latest_data['stoch_rsi_d']) and
            float(latest_data['volume']) >= float(averages['avg_volume'])):
            
            return True
            
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_scalping_buy_signal_v3 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_scalping_buy_signal_v3 bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_scalping_buy_signal_v3 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_scalping_buy_signal_v3 bot {bot_settings.id}', str(e))
        return False
    
    
def check_scalping_sell_signal_v3(df, bot_settings, trend, averages, latest_data, previous_data):
    from .logic_utils import is_df_valid
    try:        
        if not is_df_valid(df, bot_settings.id):
            return False
        
        if (float(latest_data['close']) >= float(latest_data['upper_band']) and
            float(latest_data['stoch_rsi_k']) >= float(bot_settings.stoch_sell) and
            float(latest_data['stoch_rsi_k']) <= float(latest_data['stoch_rsi_d'])):
            
            return True
        
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_scalping_sell_signal_v3 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_scalping_sell_signal_v3 bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_scalping_sell_signal_v3 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_scalping_sell_signal_v3 bot {bot_settings.id}', str(e))
        return False
    
    
def check_scalping_buy_signal_v4(df, bot_settings, trend, averages, latest_data, previous_data):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False

        if (trend != 'downtrend' and 
            float(latest_data['rsi']) <= float(bot_settings.rsi_buy) and
            float(latest_data['rsi']) >= float(averages['avg_rsi']) and
            (float(averages['avg_ema_fast']) <= float(averages['avg_ema_slow']) or
            float(previous_data['ema_fast']) <= float(previous_data['ema_slow'])) and 
            float(latest_data['ema_fast']) >= float(latest_data['ema_slow']) and
            float(latest_data['volume']) >= float(averages['avg_volume'])):
            
            return True
            
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_scalping_buy_signal_v4 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_scalping_buy_signal_v4 bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_scalping_buy_signal_v4 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_scalping_buy_signal_v4 bot {bot_settings.id}', str(e))
        return False

    
def check_scalping_sell_signal_v4(df, bot_settings, trend, averages, latest_data, previous_data):
    from .logic_utils import is_df_valid
    try:        
        if not is_df_valid(df, bot_settings.id):
            return False
        
        if (float(latest_data['rsi']) >= float(bot_settings.rsi_sell) and
            (float(averages['avg_ema_fast']) >= float(averages['avg_ema_slow']) or
            float(previous_data['ema_fast']) >= float(previous_data['ema_slow'])) and 
            float(latest_data['ema_fast']) <= float(latest_data['ema_slow'])):
            
            return True
        
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_scalping_sell_signal_v4 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_scalping_sell_signal_v4 bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_scalping_sell_signal_v4 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_scalping_sell_signal_v4 bot {bot_settings.id}', str(e))
        return False
    
    
def check_scalping_buy_signal_v5(df, bot_settings, trend, averages, latest_data, previous_data):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False
        
        if (trend == 'uptrend' and 
            float(latest_data['rsi']) <= float(bot_settings.rsi_buy) and
            float(latest_data['rsi']) >= float(averages['avg_rsi']) and
            (float(averages['avg_macd']) <= float(averages['avg_macd_signal']) or 
            float(previous_data['macd']) <= float(previous_data['macd_signal'])) and
            float(latest_data['macd']) >= float(latest_data['macd_signal']) and
            float(latest_data['volume']) >= float(averages['avg_volume'])):
            
            return True
        
        elif (trend != 'downtrend' and 
            float(latest_data['close']) <= float(latest_data['lower_band']) and
            (float(averages['avg_stoch_k']) <= float(averages['avg_stoch_d']) or
            float(previous_data['stoch_k']) <= float(previous_data['stoch_d'])) and
            float(latest_data['stoch_k']) >= float(latest_data['stoch_d']) and
            float(latest_data['stoch_k']) <= float(bot_settings.stoch_buy) and
            float(latest_data['volume']) >= float(averages['avg_volume'])):
            
            return True
            
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_scalping_buy_signal_v5 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_scalping_buy_signal_v5 bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_scalping_buy_signal_v5 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_scalping_buy_signal_v5 bot {bot_settings.id}', str(e))
        return False
    
    
def check_scalping_sell_signal_v5(df, bot_settings, trend, averages, latest_data, previous_data):
    from .logic_utils import is_df_valid
    try:        
        if not is_df_valid(df, bot_settings.id):
            return False
        
        if (trend == 'uptrend' and 
            float(latest_data['rsi']) >= float(bot_settings.rsi_sell) and
            (float(averages['avg_macd']) >= float(averages['avg_macd_signal']) or 
            float(previous_data['macd']) >= float(previous_data['macd_signal'])) and
            float(latest_data['macd']) <= float(latest_data['macd_signal'])):
            
            return True

        elif (trend == 'horizontal' and 
            float(latest_data['close']) >= float(latest_data['upper_band']) and
            (float(averages['avg_stoch_k']) >= float(averages['avg_stoch_d']) or
            float(previous_data['stoch_k']) >= float(previous_data['stoch_d'])) and
            float(latest_data['stoch_k']) <= float(latest_data['stoch_d']) and
            float(latest_data['stoch_k']) >= float(bot_settings.stoch_sell)):
            
            return True
        
        elif (trend == 'downtrend' and 
            float(latest_data['rsi']) >= float(bot_settings.rsi_sell) and
            float(latest_data['close']) >= float(latest_data['upper_band'])):
            
            return True
        
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_scalping_sell_signal_v5 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_scalping_sell_signal_v5 bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_scalping_sell_signal_v5 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_scalping_sell_signal_v5 bot {bot_settings.id}', str(e))
        return False
    
    
def check_scalping_buy_signal_v6(df, bot_settings, trend, averages, latest_data, previous_data):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False
        
        if (trend == 'uptrend' and 
            float(latest_data['rsi']) <= float(bot_settings.rsi_buy) and
            float(latest_data['rsi']) >= float(averages['avg_rsi']) and
            float(latest_data['close']) >= float(latest_data['ema_fast']) and
            float(latest_data['close']) >= float(latest_data['ema_slow']) and
            (float(averages['avg_macd']) <= float(averages['avg_macd_signal']) or 
            float(previous_data['macd']) <= float(previous_data['macd_signal'])) and
            float(latest_data['macd']) >= float(latest_data['macd_signal']) and
            float(latest_data['volume']) >= float(averages['avg_volume'])):
            
            return True
        
        elif (trend != 'downtrend' and 
            float(latest_data['rsi']) <= float(bot_settings.rsi_buy) and
            float(latest_data['rsi']) >= float(averages['avg_rsi']) and
            float(latest_data['close']) <= float(latest_data['lower_band']) and
            (float(averages['avg_stoch_k']) <= float(averages['avg_stoch_d']) or
            float(previous_data['stoch_k']) <= float(previous_data['stoch_d'])) and
            float(latest_data['stoch_k']) >= float(latest_data['stoch_d']) and
            float(latest_data['stoch_k']) <= float(bot_settings.stoch_buy) and
            float(latest_data['volume']) >= float(averages['avg_volume'])):
            
            return True
        
        return False
        
    
    except IndexError as e:
        logger.error(f'IndexError in check_scalping_buy_signal_v6 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_scalping_buy_signal_v6 bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_scalping_buy_signal_v6 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_scalping_buy_signal_v6 bot {bot_settings.id}', str(e))
        return False

    
def check_scalping_sell_signal_v6(df, bot_settings, trend, averages, latest_data, previous_data):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False

        if (trend == 'uptrend' and 
            float(latest_data['rsi']) >= float(bot_settings.rsi_sell) and
            float(latest_data['close']) <= float(latest_data['ema_fast']) and
            (float(averages['avg_macd']) >= float(averages['avg_macd_signal']) or 
            float(previous_data['macd']) >= float(previous_data['macd_signal'])) and
            float(latest_data['macd']) <= float(latest_data['macd_signal'])):
            
            return True

        elif (trend == 'horizontal' and 
            float(latest_data['rsi']) >= float(bot_settings.rsi_sell) and
            float(latest_data['close']) >= float(latest_data['upper_band']) and
            (float(averages['avg_stoch_k']) >= float(averages['avg_stoch_d']) or
            float(previous_data['stoch_k']) >= float(previous_data['stoch_d'])) and
            float(latest_data['stoch_k']) <= float(latest_data['stoch_d']) and
            float(latest_data['stoch_k']) >= float(bot_settings.stoch_sell)):
            
            return True
        
        elif (trend == 'downtrend' and 
            float(latest_data['rsi']) >= float(bot_settings.rsi_sell) and
            float(latest_data['close']) >= float(latest_data['upper_band'])):
            return True
        
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_scalping_sell_signal_v6 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_scalping_sell_signal_v6 bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_scalping_sell_signal_v6 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_scalping_sell_signal_v6 bot {bot_settings.id}', str(e))
        return False
    
    
def check_scalping_buy_signal_v7(df, bot_settings, trend, averages, latest_data, previous_data):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False
        
        if (trend == 'uptrend' and 
            (float(averages['avg_plus_di']) <= float(averages['avg_minus_di']) or
            float(previous_data['plus_di']) <= float(previous_data['minus_di'])) and 
            float(latest_data['plus_di']) >= float(latest_data['minus_di']) and
            float(latest_data['volume']) >= float(averages['avg_volume'])):
            
            return True
            
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_scalping_buy_signal_v7 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_scalping_buy_signal_v7 bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_scalping_buy_signal_v7 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_scalping_buy_signal_v7 bot {bot_settings.id}', str(e))
        return False
    
    
def check_scalping_sell_signal_v7(df, bot_settings, trend, averages, latest_data, previous_data):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False
        
        if (trend == 'downtrend' and
            (float(averages['avg_plus_di']) >= float(averages['avg_minus_di']) or
            float(previous_data['plus_di']) >= float(previous_data['minus_di'])) and 
            float(latest_data['plus_di']) <= float(latest_data['minus_di'])):
            
            return True
        
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_scalping_sell_signal_v7 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_scalping_sell_signal_v7 bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_scalping_sell_signal_v7 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_scalping_sell_signal_v7 bot {bot_settings.id}', str(e))
        return False
    
    
def check_scalping_buy_signal_v8(df, bot_settings, trend, averages, latest_data, previous_data):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False

        if (trend != 'downtrend' and 
            float(latest_data['cci']) < float(bot_settings.cci_buy) and
            (float(latest_data['cci']) >= float(averages['avg_cci']) or
            float(latest_data['cci']) >= float(previous_data['cci'])) and
            float(latest_data['mfi']) < float(bot_settings.mfi_buy) and
            (float(latest_data['mfi']) >= float(averages['avg_mfi']) or 
            float(latest_data['mfi']) >= float(previous_data['mfi'])) and
            float(latest_data['volume']) >= float(averages['avg_volume'])):
            
            return True
            
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_scalping_buy_signal_v8 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_scalping_buy_signal_v8 bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_scalping_buy_signal_v8 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_scalping_buy_signal_v8 bot {bot_settings.id}', str(e))
        return False

    
def check_scalping_sell_signal_v8(df, bot_settings, trend, averages, latest_data, previous_data):
    from .logic_utils import is_df_valid
    try:        
        if not is_df_valid(df, bot_settings.id):
            return False
        
        if (float(latest_data['cci']) >= float(bot_settings.cci_sell) and
            float(latest_data['mfi']) >= float(bot_settings.mfi_sell)):
            
            return True
        
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_scalping_sell_signal_v8 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_scalping_sell_signal_v8 bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_scalping_sell_signal_v8 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_scalping_sell_signal_v8 bot {bot_settings.id}', str(e))
        return False
    

def check_scalping_buy_signal_v9(df, bot_settings, trend, averages, latest_data, previous_data):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False

        if (trend != 'downtrend' and 
            float(latest_data['close']) <= float(latest_data['lower_band']) and
            float(latest_data['atr']) >= float(averages['avg_atr']) and
            float(latest_data['volume']) >= float(averages['avg_volume'])):
            
            return True
            
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_scalping_buy_signal_v9 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_scalping_buy_signal_v9 bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_scalping_buy_signal_v9 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_scalping_buy_signal_v9 bot {bot_settings.id}', str(e))
        return False
    
    
def check_scalping_sell_signal_v9(df, bot_settings, trend, averages, latest_data, previous_data):
    from .logic_utils import is_df_valid
    try:        
        if not is_df_valid(df, bot_settings.id):
            return False
        
        if float(latest_data['close']) >= float(latest_data['upper_band']):
            
            return True
        
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_scalping_sell_signal_v9 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_scalping_sell_signal_v9 bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_scalping_sell_signal_v9 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_scalping_sell_signal_v9 bot {bot_settings.id}', str(e))
        return False