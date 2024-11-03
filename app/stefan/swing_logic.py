import talib
import pandas as pd
from ..utils.logging import logger
from ..utils.app_utils import send_admin_email

def calculate_swing_indicators(df, df_for_ma, bot_settings):
    try:

        if df.empty:
            logger.error('DataFrame is empty, cannot calculate indicators.')
            return df

        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df['high'] = pd.to_numeric(df['high'], errors='coerce')
        df['low'] = pd.to_numeric(df['low'], errors='coerce')
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce')

        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')

        df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=bot_settings.timeperiod)
        
        df['ema_fast'] = talib.EMA(df['close'], timeperiod=24)
        df['ema_slow'] = talib.EMA(df['close'], timeperiod=48)

        df['rsi'] = talib.RSI(df['close'], timeperiod=bot_settings.timeperiod)

        df.dropna(subset=['close'], inplace=True)

        if len(df) < 26 + 14:
            logger.error('Not enough data points for MACD calculation.')
            return df

        df['macd'], df['macd_signal'], _ = talib.MACD(
            df['close'],
            fastperiod=bot_settings.timeperiod,
            slowperiod=2 * bot_settings.timeperiod,
            signalperiod=bot_settings.timeperiod // 2
        )
        
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        if not df_for_ma.empty:
            df_for_ma['ma_200'] = df_for_ma['close'].rolling(window=200).mean()
            ma_200_column = df_for_ma['ma_200'].tail(len(df)).reset_index(drop=True)
            df['ma_200'] = ma_200_column
              
            df_for_ma['ma_50'] = df_for_ma['close'].rolling(window=50).mean()
            ma_50_column = df_for_ma['ma_50'].tail(len(df)).reset_index(drop=True)
            df['ma_50'] = ma_50_column

        df['upper_band'], df['middle_band'], df['lower_band'] = talib.BBANDS(
            df['close'],
            timeperiod=bot_settings.timeperiod,
            nbdevup=2,
            nbdevdn=2,
            matype=0
        )

        df['cci'] = talib.CCI(
            df['high'],
            df['low'],
            df['close'],
            timeperiod=bot_settings.timeperiod
        )

        df['mfi'] = talib.MFI(
            df['high'],
            df['low'],
            df['close'],
            df['volume'],
            timeperiod=bot_settings.timeperiod
        )

        df['stoch_k'], df['stoch_d'] = talib.STOCH(
            df['high'],
            df['low'],
            df['close'],
            fastk_period=14,
            slowk_period=3,
            slowk_matype=0,
            slowd_period=3,
            slowd_matype=0
        )
        
        columns_to_check = ['macd', 'macd_signal', 'cci', 'upper_band', 'lower_band', 'mfi', 'atr', 'ema', 'stoch_k', 'stoch_d']

        df.dropna(subset=columns_to_check, inplace=True)

        return df
    
    except IndexError as e:
        logger.error(f'IndexError in calculate_swing_indicators bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in calculate_swing_indicators bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in calculate_swing_indicators bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in calculate_swing_indicators bot {bot_settings.id}', str(e))
        return False


def check_swing_buy_signal_v1(df, bot_settings):
    from .logic_utils import is_df_valid
    try:        
        if not is_df_valid(df, bot_settings.id):
            return False
        
        latest_data = df.iloc[-1]
        previous_data = df.iloc[-2]
        
        if (float(latest_data['rsi']) < float(bot_settings.rsi_buy) and
            float(previous_data['macd']) < float(previous_data['macd_signal']) and 
            float(latest_data['macd']) > float(latest_data['macd_signal'])):
            
            return True
        
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_swing_buy_signal bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_swing_buy_signal bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_swing_buy_signal bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_swing_buy_signal bot {bot_settings.id}', str(e))
        return False
    
    
def check_swing_sell_signal_v1(df, bot_settings):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False
        
        latest_data = df.iloc[-1]
        previous_data = df.iloc[-2]
        
        if (float(latest_data['rsi']) > float(bot_settings.rsi_sell) and
            float(previous_data['macd']) > float(previous_data['macd_signal']) and 
            float(latest_data['macd']) < float(latest_data['macd_signal'])):
            
            return True
        
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_swing_sell_signal bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_swing_sell_signal bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_swing_sell_signal bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_swing_sell_signal bot {bot_settings.id}', str(e))
        return False


def check_swing_buy_signal_v2(df, bot_settings):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False

        latest_data = df.iloc[-1]
        previous_data = df.iloc[-2]

        if (float(latest_data['rsi']) < float(bot_settings.rsi_buy) and
            float(previous_data['macd']) < float(previous_data['macd_signal']) and 
            float(latest_data['macd']) > float(latest_data['macd_signal']) and
            float(latest_data['close']) > float(latest_data['ma_200'])):
            
            return True

        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_swing_buy_signal_with_MA200 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_swing_buy_signal_with_MA200 bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_swing_buy_signal_with_MA200 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_swing_buy_signal_with_MA200 bot {bot_settings.id}', str(e))
        return False


def check_swing_sell_signal_v2(df, bot_settings):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False

        latest_data = df.iloc[-1]
        previous_data = df.iloc[-2]

        if (float(latest_data['rsi']) > float(bot_settings.rsi_sell) and
            float(previous_data['macd']) > float(previous_data['macd_signal']) and 
            float(latest_data['macd']) < float(latest_data['macd_signal']) and
            float(latest_data['close']) < float(latest_data['ma_200'])):
            
            return True
        
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_swing_sell_signal_with_MA200 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_swing_sell_signal_with_MA200 bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_swing_sell_signal_with_MA200 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_swing_sell_signal_with_MA200 bot {bot_settings.id}', str(e))
        return False
    
    
def check_swing_buy_signal_v3(df, bot_settings):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False

        latest_data = df.iloc[-1]
        previous_data = df.iloc[-2]
        
        if (float(latest_data['rsi']) < float(bot_settings.rsi_buy) and
            float(previous_data['macd']) < float(previous_data['macd_signal']) and 
            float(latest_data['macd']) > float(latest_data['macd_signal']) and
            float(latest_data['close']) > float(latest_data['ma_50'])):
            
            return True

        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_swing_buy_signal_with_MA200 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_swing_buy_signal_with_MA200 bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_swing_buy_signal_with_MA200 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_swing_buy_signal_with_MA200 bot {bot_settings.id}', str(e))
        return False


def check_swing_sell_signal_v3(df, bot_settings):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False

        latest_data = df.iloc[-1]
        previous_data = df.iloc[-2]

        if (float(latest_data['rsi']) > float(bot_settings.rsi_sell) and
            float(previous_data['macd']) > float(previous_data['macd_signal']) and 
            float(latest_data['macd']) < float(latest_data['macd_signal']) and
            float(latest_data['close']) < float(latest_data['ma_50'])):
            
            return True
        
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_swing_sell_signal_with_MA200 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_swing_sell_signal_with_MA200 bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_swing_sell_signal_with_MA200 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_swing_sell_signal_with_MA200 bot {bot_settings.id}', str(e))
        return False
    
    
def check_swing_buy_signal_v4(df, bot_settings):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False

        latest_data = df.iloc[-1]
        
        if (float(latest_data['rsi']) < float(bot_settings.rsi_buy) and
            float(latest_data['close']) < float(latest_data['lower_band']) and
            float(latest_data['close']) > float(latest_data['ma_50'])):
            
            return True

        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_swing_buy_signal_with_MA200 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_swing_buy_signal_with_MA200 bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_swing_buy_signal_with_MA200 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_swing_buy_signal_with_MA200 bot {bot_settings.id}', str(e))
        return False


def check_swing_sell_signal_v4(df, bot_settings):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False

        latest_data = df.iloc[-1]

        if (float(latest_data['rsi']) > float(bot_settings.rsi_sell) and 
            float(latest_data['close']) > float(latest_data['upper_band']) and 
            float(latest_data['close']) < float(latest_data['ma_50'])):
            
            return True
        
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_swing_sell_signal_with_MA200 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_swing_sell_signal_with_MA200 bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_swing_sell_signal_with_MA200 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_swing_sell_signal_with_MA200 bot {bot_settings.id}', str(e))
        return False
    
    
def check_swing_buy_signal_v5(df, bot_settings):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False

        latest_data = df.iloc[-1]
        previous_data = df.iloc[-2]
        
        if (float(previous_data['ema_fast']) < float(previous_data['ema_slow']) and 
            float(latest_data['ema_fast']) > float(latest_data['ema_slow']) and
            float(latest_data['close']) > float(latest_data['ma_50'])):
            
            return True

        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_swing_buy_signal_with_MA200 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_swing_buy_signal_with_MA200 bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_swing_buy_signal_with_MA200 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_swing_buy_signal_with_MA200 bot {bot_settings.id}', str(e))
        return False


def check_swing_sell_signal_v5(df, bot_settings):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False

        latest_data = df.iloc[-1]
        previous_data = df.iloc[-2]

        if (float(previous_data['ema_fast']) > float(previous_data['ema_slow']) and
            float(latest_data['ema_fast']) < float(latest_data['ema_slow']) and 
            float(latest_data['close']) < float(latest_data['ma_50'])):
            
            return True
        
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_swing_sell_signal_with_MA200 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_swing_sell_signal_with_MA200 bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_swing_sell_signal_with_MA200 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_swing_sell_signal_with_MA200 bot {bot_settings.id}', str(e))
        return False
    
def check_swing_buy_signal_v6(df, bot_settings):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False

        latest_data = df.iloc[-1]
        previous_data = df.iloc[-2]
        
        if (float(previous_data['macd']) < float(previous_data['macd_signal']) and 
            float(latest_data['macd']) > float(latest_data['macd_signal']) and
            float(previous_data['ema_fast']) < float(previous_data['ema_slow']) and 
            float(latest_data['ema_fast']) > float(latest_data['ema_slow'])):
            
            return True

        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_swing_buy_signal_with_MA200 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_swing_buy_signal_with_MA200 bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_swing_buy_signal_with_MA200 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_swing_buy_signal_with_MA200 bot {bot_settings.id}', str(e))
        return False


def check_swing_sell_signal_v6(df, bot_settings):
    from .logic_utils import is_df_valid
    try:
        if not is_df_valid(df, bot_settings.id):
            return False

        latest_data = df.iloc[-1]
        previous_data = df.iloc[-2]

        if (float(previous_data['macd']) > float(previous_data['macd_signal']) and 
            float(latest_data['macd']) < float(latest_data['macd_signal']) and 
            float(previous_data['ema_fast']) > float(previous_data['ema_slow']) and
            float(latest_data['ema_fast']) < float(latest_data['ema_slow'])):
            
            return True
        
        return False
    
    except IndexError as e:
        logger.error(f'IndexError in check_swing_sell_signal_with_MA200 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in check_swing_sell_signal_with_MA200 bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in check_swing_sell_signal_with_MA200 bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in check_swing_sell_signal_with_MA200 bot {bot_settings.id}', str(e))
        return False