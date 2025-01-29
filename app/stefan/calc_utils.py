import talib
import pandas as pd
from ..utils.logging import logger
from ..utils.app_utils import send_admin_email

def handle_ta_df_initial_praparation(df, bot_settings):
    try:
        
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df['high'] = pd.to_numeric(df['high'], errors='coerce')
        df['low'] = pd.to_numeric(df['low'], errors='coerce')
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
        
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
        
        df.dropna(subset=['close'], inplace=True)
        
        return df
        
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in initial_ta_df_praparation: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in initial_ta_df_praparation', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in initial_ta_df_praparation: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in initial_ta_df_praparation', str(e))
        return False
    
    
def calculate_ta_rsi(df, bot_settings):
    try:
        
        df['rsi'] = talib.RSI(
            df['close'], 
            timeperiod=bot_settings.rsi_timeperiod
            )
        
        return df
        
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in calculate_ta_rsi: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in calculate_ta_rsi', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in calculate_ta_rsi: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in calculate_ta_rsi', str(e))
        return False
    
    
def calculate_ta_cci(df, bot_settings):
    try:
        
        df['cci'] = talib.CCI(
            df['high'],
            df['low'],
            df['close'],
            timeperiod=bot_settings.cci_timeperiod
        )
        
        return df
        
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in calculate_ta_cci: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in calculate_ta_cci', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in calculate_ta_cci: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in calculate_ta_cci', str(e))
        return False
    
    
def calculate_ta_mfi(df, bot_settings):
    try:
        
        df['mfi'] = talib.MFI(
            df['high'],
            df['low'],
            df['close'],
            df['volume'],
            timeperiod=bot_settings.mfi_timeperiod
        )
        
        return df
        
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in calculate_ta_mfi: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in calculate_ta_mfi', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in calculate_ta_mfi: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in calculate_ta_mfi', str(e))
        return False
    
    
def calculate_ta_adx(df, bot_settings):
    try:
        
        df['adx'] = talib.ADX(
            df['high'],
            df['low'],
            df['close'],
            timeperiod=bot_settings.adx_timeperiod
        )
        
        return df
        
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in calculate_ta_adx: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in calculate_ta_adx', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in calculate_ta_adx: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in calculate_ta_adx', str(e))
        return False
    
    
def calculate_ta_atr(df, bot_settings):
    try:
        
        df['atr'] = talib.ATR(
            df['high'], 
            df['low'], 
            df['close'], 
            timeperiod=bot_settings.atr_timeperiod
            )
        
        return df
    
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in calculate_ta_atr: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in calculate_ta_atr', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in calculate_ta_atr: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in calculate_ta_atr', str(e))
        return False
    
    
def calculate_ta_di(df, bot_settings):
    try:
        
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
        
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in calculate_ta_di: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in calculate_ta_di', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in calculate_ta_di: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in calculate_ta_di', str(e))
        return False
    
    
def calculate_ta_stochastic(df, bot_settings):
    try:
        
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
        
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in calculate_ta_stochastic: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in calculate_ta_stochastic', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in calculate_ta_stochastic: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in calculate_ta_stochastic', str(e))
        return False
    
    
def calculate_ta_bollinger_bands(df, bot_settings):
    try:
        
        df['upper_band'], df['middle_band'], df['lower_band'] = talib.BBANDS(
            df['close'],
            timeperiod=bot_settings.bollinger_timeperiod,
            nbdevup=bot_settings.bollinger_nbdev,
            nbdevdn=bot_settings.bollinger_nbdev,
            matype=0
        )
        
        return df
        
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in calculate_ta_bollinger_bands: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in calculate_ta_bollinger_bands', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in calculate_ta_bollinger_bands: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in calculate_ta_bollinger_bands', str(e))
        return False
    
    
def calculate_ta_vwap(df, bot_settings):
    try:
        
        df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
        df['vwap'] = (df['typical_price'] * df['volume']).cumsum() / df['volume'].cumsum()
        
        return df
        
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in calculate_ta_vwap: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in calculate_ta_vwap', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in calculate_ta_vwap: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in calculate_ta_vwap', str(e))
        return False
    
    
def calculate_ta_psar(df, bot_settings):
    try:
        
        df['psar'] = talib.SAR(
            df['high'],
            df['low'],
            acceleration=bot_settings.psar_acceleration,
            maximum=bot_settings.psar_maximum
        )
        
        return df
        
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in calculate_ta_psar: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in calculate_ta_psar', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in calculate_ta_psar: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in calculate_ta_psar', str(e))
        return False
    
    
def calculate_ta_macd(df, bot_settings):
    try:
        
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
        
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in calculate_ta_macd: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in calculate_ta_macd', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in calculate_ta_macd: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in calculate_ta_macd', str(e))
        return False
    
    
def calculate_ta_ma(df, bot_settings):
    try:
        
        df['ma_200'] = df['close'].rolling(window=200).mean()
        df['ma_50'] = df['close'].rolling(window=50).mean()
        
        return df
        
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in calculate_ta_ma: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in calculate_ta_ma', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in calculate_ta_ma: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in calculate_ta_ma', str(e))
        return False
    
    
def calculate_ta_ema(df, bot_settings):
    try:
        
        df['ema_fast'] = talib.EMA(
            df['close'], 
            timeperiod=bot_settings.ema_fast_timeperiod
            )
        
        df['ema_slow'] = talib.EMA(
            df['close'], 
            timeperiod=bot_settings.ema_slow_timeperiod
            )
        
        return df
        
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in calculate_ta_ema: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in calculate_ta_ema', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in calculate_ta_ema: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in calculate_ta_ema', str(e))
        return False
    
    
def calculate_ta_stochastic_rsi(df, bot_settings):
    try:
        
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
        
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in calculate_ta_stochastic_rsi: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in calculate_ta_stochastic_rsi', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in calculate_ta_stochastic_rsi: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in calculate_ta_stochastic_rsi', str(e))
        return False
    
    
def handle_ta_df_final_cleaning(df, columns_to_check, bot_settings):
    try:
        
        df.dropna(subset=columns_to_check, inplace=True)
        
        return df
        
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in initial_ta_df_praparation: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in initial_ta_df_praparation', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in initial_ta_df_praparation: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in initial_ta_df_praparation', str(e))
        return False
    
    
def calculate_ta_indicators(df, bot_settings):
    try:

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
    
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in calculate_indicators: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} IndexError in calculate_indicators', str(e))
        return False
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in calculate_indicators: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in calculate_indicators', str(e))
        return False
    
    
def calculate_ta_averages(df, bot_settings):
    try:
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

    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in calculate_averages: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in calculate_averages', str(e))
        return None

    
def check_ta_trend(df, bot_settings):
    try:
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
        
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in check_trend: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in check_trend', str(e))
        return 'none'