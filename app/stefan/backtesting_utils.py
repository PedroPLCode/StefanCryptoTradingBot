import pandas as pd
import talib
from .. import db
import json
from app.models import BacktestResult
from ..utils.logging import logger
from .scalping_logic import (
    check_scalping_buy_signal_v1,
    check_scalping_sell_signal_v1,
    check_scalping_buy_signal_v2,
    check_scalping_sell_signal_v2,
    check_scalping_buy_signal_v3,
    check_scalping_sell_signal_v3,
    check_scalping_buy_signal_v4,
    check_scalping_sell_signal_v4,
    check_scalping_buy_signal_v5,
    check_scalping_sell_signal_v5,
    check_scalping_buy_signal_v6,
    check_scalping_sell_signal_v6
)
from .swing_logic import (
    check_swing_buy_signal_v1,
    check_swing_sell_signal_v1,
    check_swing_buy_signal_v2,
    check_swing_sell_signal_v2,
    check_swing_buy_signal_v3,
    check_swing_sell_signal_v3,
    check_swing_buy_signal_v4,
    check_swing_sell_signal_v4,
    check_swing_buy_signal_v5,
    check_swing_sell_signal_v5,
    check_swing_buy_signal_v6,
    check_swing_sell_signal_v6
)

def calculate_backtest_scalp_indicators(df, bot_settings):
    try:
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df['high'] = pd.to_numeric(df['high'], errors='coerce')
        df['low'] = pd.to_numeric(df['low'], errors='coerce')
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce')

        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
        
        df.dropna(subset=['close'], inplace=True)

        if len(df) < (26 + 14):
            logger.trade('Not enough data points for MACD calculation.')
            return df

        df['rsi'] = talib.RSI(df['close'], timeperiod=bot_settings.timeperiod)
        df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=bot_settings.timeperiod)
        df['ema_fast'] = talib.EMA(df['close'], timeperiod=9)
        df['ema_slow'] = talib.EMA(df['close'], timeperiod=21)

        df.dropna(subset=['ema_fast', 'ema_slow'], inplace=True)

        macd, macd_signal, macd_histogram = talib.MACD(
            df['close'],
            fastperiod=bot_settings.timeperiod,
            slowperiod=2 * bot_settings.timeperiod,
            signalperiod=bot_settings.timeperiod // 2
        )
        df['macd'] = macd
        df['macd_signal'] = macd_signal
        df['macd_histogram'] = macd - macd_signal

        upper_band, middle_band, lower_band = talib.BBANDS(
            df['close'],
            timeperiod=bot_settings.timeperiod,
            nbdevup=2,
            nbdevdn=2,
            matype=0
        )
        df['upper_band'] = upper_band
        df['middle_band'] = middle_band
        df['lower_band'] = lower_band
        
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

        stoch_k, stoch_d = talib.STOCH(
            df['high'],
            df['low'],
            df['close'],
            fastk_period=14,
            slowk_period=3,
            slowk_matype=0,
            slowd_period=3,
            slowd_matype=0
        )
        df['stoch_k'] = stoch_k
        df['stoch_d'] = stoch_d
        
        columns_to_check = ['macd', 'macd_signal', 'macd_histogram', 'cci', 'upper_band', 'lower_band', 'mfi', 'atr', 'ema_fast', 'ema_slow', 'stoch_k', 'stoch_d']

        df.dropna(subset=columns_to_check, inplace=True)
        
        return df
    
    except IndexError as e:
        logger.error(f'IndexError in calculate_scalp_indicators bot {bot_settings.id}: {str(e)}')
        return False
    except Exception as e:
        logger.error(f'Exception in calculate_scalp_indicators bot {bot_settings.id}: {str(e)}')
        return False


def calculate_backtest_swing_indicators(df, df_for_ma, bot_settings):
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

        if len(df) < (26 + 14):
            logger.error('Not enough data points for MACD calculation.')
            return df

        macd, macd_signal, _ = talib.MACD(
            df['close'],
            fastperiod=bot_settings.timeperiod,
            slowperiod=2 * bot_settings.timeperiod,
            signalperiod=bot_settings.timeperiod // 2
        )
        df['macd'] = macd
        df['macd_signal'] = macd_signal
        df['macd_histogram'] = df['macd'] - df['macd_signal']

        if not df_for_ma.empty:
            df_for_ma['ma_200'] = df_for_ma['close'].rolling(window=200).mean()
            df.loc[:, 'ma_200'] = df_for_ma['ma_200'].tail(len(df)).reset_index(drop=True)

            df_for_ma['ma_50'] = df_for_ma['close'].rolling(window=50).mean()
            df.loc[:, 'ma_50'] = df_for_ma['ma_50'].tail(len(df)).reset_index(drop=True)

        upper_band, middle_band, lower_band = talib.BBANDS(
            df['close'],
            timeperiod=bot_settings.timeperiod,
            nbdevup=2,
            nbdevdn=2,
            matype=0
        )
        df['upper_band'] = upper_band
        df['middle_band'] = middle_band
        df['lower_band'] = lower_band

        df['cci'] = talib.CCI(df['high'], df['low'], df['close'], timeperiod=bot_settings.timeperiod)
        df['mfi'] = talib.MFI(df['high'], df['low'], df['close'], df['volume'], timeperiod=bot_settings.timeperiod)

        stoch_k, stoch_d = talib.STOCH(
            df['high'],
            df['low'],
            df['close'],
            fastk_period=14,
            slowk_period=3,
            slowk_matype=0,
            slowd_period=3,
            slowd_matype=0
        )
        df['stoch_k'] = stoch_k
        df['stoch_d'] = stoch_d

        columns_to_check = ['macd', 'macd_signal', 'cci', 'upper_band', 'lower_band', 'mfi', 'atr', 'ema_fast', 'ema_slow', 'stoch_k', 'stoch_d']
        df.dropna(subset=columns_to_check, inplace=True)

        return df

    except IndexError as e:
        logger.error(f'IndexError in calculate_swing_indicators bot {bot_settings.id}: {str(e)}')
        return False
    except Exception as e:
        logger.error(f'Exception in calculate_swing_indicators bot {bot_settings.id}: {str(e)}')
        return False


def select_signals_checkers(bot_settings):
    strategy_map = {
        'swing': {
            1: (check_swing_buy_signal_v1, check_swing_sell_signal_v1),
            2: (check_swing_buy_signal_v2, check_swing_sell_signal_v2),
            3: (check_swing_buy_signal_v3, check_swing_sell_signal_v3),
            4: (check_swing_buy_signal_v4, check_swing_sell_signal_v4),
            5: (check_swing_buy_signal_v5, check_swing_sell_signal_v5),
            6: (check_swing_buy_signal_v6, check_swing_sell_signal_v6),
        },
        'scalp': {
            1: (check_scalping_buy_signal_v1, check_scalping_sell_signal_v1),
            2: (check_scalping_buy_signal_v2, check_scalping_sell_signal_v2),
            3: (check_scalping_buy_signal_v3, check_scalping_sell_signal_v3),
            4: (check_scalping_buy_signal_v4, check_scalping_sell_signal_v4),
            5: (check_scalping_buy_signal_v5, check_scalping_sell_signal_v5),
            6: (check_scalping_buy_signal_v6, check_scalping_sell_signal_v6),
        }
    }
    buy_signal_func, sell_signal_func = strategy_map[bot_settings.strategy][bot_settings.algorithm]
    return buy_signal_func, sell_signal_func


def update_trade_log(action, trade_log, current_price, latest_data, crypto_balance, usdc_balance, trailing_stop_loss):
    trade_log.append({
        'action': action,
        'price': float(current_price),
        'time': int(latest_data['open_time']),
        'crypto_balance': float(crypto_balance),
        'usdc_balance': float(usdc_balance),
        'trailing_stop_loss': float(trailing_stop_loss)
    })
    
    
def save_backtest_results(bot_settings, backtest_settings, initial_balance, final_balance, trade_log):
    new_backtest = BacktestResult(
        bot_id = bot_settings.id,
        symbol = bot_settings.symbol,
        strategy = bot_settings.strategy,
        algorithm = bot_settings.algorithm,
        start_date = backtest_settings.start_date,
        end_date = backtest_settings.end_date,
        initial_balance = initial_balance,
        final_balance = final_balance,
        profit = final_balance - initial_balance,
        trade_log=json.dumps(trade_log)
    )
    db.session.add(new_backtest)
    db.session.commit()