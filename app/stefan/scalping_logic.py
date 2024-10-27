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

        df['rsi'] = talib.RSI(df['close'], timeperiod=bot_settings.timeperiod)

        df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=bot_settings.timeperiod)

        df.dropna(subset=['close'], inplace=True)
        
        #logger.trade("Data length before calculating MACD: %d", len(df))
        
        if len(df) < 26 + 14:
            logger.error('Not enough data points for MACD calculation.')
            return df

        df['macd'], df['macd_signal'], _ = talib.MACD(
            df['close'],
            fastperiod=bot_settings.timeperiod,
            slowperiod=2 * bot_settings.timeperiod,
            signalperiod=bot_settings.timeperiod // 2
        )

        df['upper_band'], df['middle_band'], df['lower_band'] = talib.BBANDS(
            df['close'],
            timeperiod=bot_settings.timeperiod,
            nbdevup=2,
            nbdevdn=2,
            matype=0
        )
        
        #logger.trade("Before calculating indicators:\n%s", df.tail())
        
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

        #logger.trade("After calculating indicators:\n%s", df.tail())

        df.dropna(subset=['macd', 'macd_signal', 'cci', 'mfi', 'atr'], inplace=True)
        
        return df
    except IndexError as e:
        logger.error(f'IndexError in calculate_scalp_indicators bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'IndexError in calculate_scalp_indicators bot {bot_settings.id}', str(e))
        return False
    except Exception as e:
        logger.error(f'Exception in calculate_scalp_indicators bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in calculate_scalp_indicators bot {bot_settings.id}', str(e))
        return False


def check_scalping_buy_signal(df, bot_settings):
    try:
        if df.empty or len(df) < 1:
            logger.error(f'DataFrame is empty or too short for bot {bot_settings.id}.')
            return False
        
        latest_data = df.iloc[-1]

        if pd.isna(latest_data['macd']) or pd.isna(latest_data['macd_signal']):
            logger.error(f'MACD or MACD signal is NaN for bot {bot_settings.id}. Latest data: {latest_data}')
            return False
        
        if (latest_data['rsi'] < bot_settings.rsi_buy and
            latest_data['macd'] < latest_data['macd_signal'] and
            latest_data['cci'] < bot_settings.cci_buy and
            latest_data['mfi'] < bot_settings.mfi_buy and
            latest_data['close'] < latest_data['lower_band']):
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
            

def check_scalping_sell_signal(df, bot_settings):
    try:
        if df.empty:
            logger.error(f'DataFrame is empty for bot {bot_settings.id}.')
            return False
        
        latest_data = df.iloc[-1]
        logger.trade(f'DataFrame is ok bot {bot_settings.id}.')

        if (latest_data['rsi'] > bot_settings.rsi_sell and
            latest_data['macd'] > latest_data['macd_signal'] and
            latest_data['cci'] > bot_settings.cci_sell and
            latest_data['mfi'] > bot_settings.mfi_sell and
            latest_data['close'] > latest_data['upper_band']):
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