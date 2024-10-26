import talib
import pandas as pd
from ..utils.logging import logger

def calculate_swing_indicators(df, df_for_ma200, bot_settings):
    # Sprawdź, czy DataFrame nie jest pusty
    if df.empty:
        logger.error('DataFrame is empty, cannot calculate indicators.')
        return df

    # Konwersja kolumn do typów numerycznych
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df['high'] = pd.to_numeric(df['high'], errors='coerce')
    df['low'] = pd.to_numeric(df['low'], errors='coerce')
    df['volume'] = pd.to_numeric(df['volume'], errors='coerce')

    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')

    # Obliczanie MA200
    if not df_for_ma200.empty:
        logger.trade(f"Liczba wierszy w DataFrame: {len(df_for_ma200)}")
        logger.trade(df_for_ma200['close'])
        logger.trade(df_for_ma200['close'].head(10))
        df_for_ma200['ma_200'] = df_for_ma200['close'].rolling(window=200).mean()
        df['ma_200'] = df_for_ma200['ma_200']
        logger.trade('teraz tu ma200')
        logger.trade(df_for_ma200['ma_200'])

    # Obliczanie ATR
    df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=bot_settings.timeperiod)

    # Obliczanie RSI
    df['rsi'] = talib.RSI(df['close'], timeperiod=bot_settings.timeperiod)

    # Usunięcie NaN
    df.dropna(subset=['close'], inplace=True)

    logger.trade("Data length before calculating MACD: %d", len(df))

    # Sprawdzenie długości danych dla MACD
    if len(df) < 26 + 14:
        logger.error('Not enough data points for MACD calculation.')
        return df

    # Obliczanie MACD
    df['macd'], df['macd_signal'], _ = talib.MACD(
        df['close'],
        fastperiod=bot_settings.timeperiod,
        slowperiod=2 * bot_settings.timeperiod,
        signalperiod=bot_settings.timeperiod // 2
    )

    # Obliczanie Bollinger Bands
    df['upper_band'], df['middle_band'], df['lower_band'] = talib.BBANDS(
        df['close'],
        timeperiod=bot_settings.timeperiod,
        nbdevup=2,
        nbdevdn=2,
        matype=0
    )

    # Obliczanie CCI i MFI
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

    logger.trade(f"\n{df}")
    
    # Ustal kolumny do usunięcia
    columns_to_check = ['macd', 'macd_signal', 'cci', 'mfi', 'atr']
    if not df_for_ma200.empty:
        columns_to_check.append('ma_200')

    df.dropna(subset=columns_to_check, inplace=True)
    
    if 'ma_200' in df.columns:
        logger.trade(f"DataFrame zawiera kolumnę ma_200:\n{df['ma_200']}")
    else:
        logger.trade("DataFrame nie zawiera kolumny ma_200.")

    return df


def check_swing_buy_signal(df, bot_settings):
    try:
        if df.empty or len(df) < 1:
            logger.error(f'DataFrame is empty or too short for bot {bot_settings.id}.')
            return False
        
        latest_data = df.iloc[-1]
        mfi = talib.MFI(df['high'], df['low'], df['close'], df['volume'], timeperiod=bot_settings.timeperiod)

        if (latest_data['rsi'] < bot_settings.rsi_buy and
            latest_data['macd'] > latest_data['macd_signal'] and
            latest_data['cci'] < bot_settings.cci_buy and
            mfi.iloc[-1] < bot_settings.mfi_buy and
            latest_data['close'] < latest_data['lower_band']):
            return True
        
        return False
    
    except IndexError as ie:
        logger.error(f'IndexError in check_scalping_buy_signal for bot {bot_settings.id}: {str(ie)}')
        return False
    except Exception as e:
        logger.error(f'Error in check_scalping_buy_signal for bot {bot_settings.id}: {str(e)}')
        return False


def check_swing_buy_signal_with_MA200(df, bot_settings):
    try:
        if df.empty or len(df) < 1:
            logger.error(f'DataFrame is empty or too short for bot {bot_settings.id}.')
            return False
        
        logger.trade(f'DataFrame contents: {df.head()}')
        
        # Upewnij się, że jest wystarczająco dużo danych
        if len(df) < 1:
            logger.error(f'DataFrame does not have enough data points for bot {bot_settings.id}.')
            return False
            
        latest_data = df.iloc[-1]
        
        if 'ma_200' not in df.columns:
            logger.trade(f"{bot_settings.algorithm} missing ma_200 in df column.")
            return False

        mfi_value = talib.MFI(df['high'], df['low'], df['close'], df['volume'], timeperiod=bot_settings.timeperiod).iloc[-1]

        if (latest_data['close'] > latest_data['ma_200'] and
            latest_data['rsi'] < bot_settings.rsi_buy and
            latest_data['macd'] > latest_data['macd_signal'] and
            latest_data['cci'] < bot_settings.cci_buy and
            mfi_value < bot_settings.mfi_buy and
            latest_data['close'] < latest_data['lower_band']):
            return True

        return False
    
    except IndexError as ie:
        logger.error(f'IndexError in check_scalping_buy_signal for bot {bot_settings.id}: {str(ie)}')
        return False
    except Exception as e:
        logger.error(f'Error in check_scalping_buy_signal for bot {bot_settings.id}: {str(e)}')
        return False


def check_swing_sell_signal(df, bot_settings):
    try:
        if df.empty or len(df) < 1:
            logger.error(f'DataFrame is empty or too short for bot {bot_settings.id}.')
            return False
        
        latest_data = df.iloc[-1]
        mfi = talib.MFI(df['high'], df['low'], df['close'], df['volume'], timeperiod=bot_settings.timeperiod)

        if (latest_data['rsi'] > bot_settings.rsi_sell and
            latest_data['macd'] < latest_data['macd_signal'] and
            latest_data['cci'] > bot_settings.cci_sell and
            mfi.iloc[-1] > bot_settings.mfi_sell and
            latest_data['close'] > latest_data['upper_band']):
            return True
        
        return False
    
    except IndexError as ie:
        logger.error(f'IndexError in check_scalping_buy_signal for bot {bot_settings.id}: {str(ie)}')
        return False
    except Exception as e:
        logger.error(f'Error in check_scalping_buy_signal for bot {bot_settings.id}: {str(e)}')
        return False


def check_swing_sell_signal_with_MA200(df, bot_settings):
    try:
        if df.empty or len(df) < 1:
            logger.error(f'DataFrame is empty or too short for bot {bot_settings.id}.')
            return False
        
        latest_data = df.iloc[-1]

        if (latest_data['close'] < latest_data['ma_200'] and
            latest_data['rsi'] > bot_settings.rsi_sell and
            latest_data['macd'] < latest_data['macd_signal'] and
            latest_data['cci'] > bot_settings.cci_sell and
            talib.MFI(df['high'], df['low'], df['close'], df['volume'], timeperiod=bot_settings.timeperiod).iloc[-1] > bot_settings.mfi_sell and
            latest_data['close'] > latest_data['upper_band']):
            return True
        
        return False
    
    except IndexError as ie:
        logger.error(f'IndexError in check_scalping_buy_signal for bot {bot_settings.id}: {str(ie)}')
        return False
    except Exception as e:
        logger.error(f'Error in check_scalping_buy_signal for bot {bot_settings.id}: {str(e)}')
        return False