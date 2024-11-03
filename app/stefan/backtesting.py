import json
from .. import db
from ..utils.logging import logger
from app.models import BacktestResult
from .api_utils import fetch_data
from .logic_utils import update_trailing_stop_loss
from .backtesting_utils import (
    calculate_backtest_scalp_indicators,
    calculate_backtest_swing_indicators,
    select_signals_checkers
)

def fetch_and_save_data(backtest_settings, bot_settings):
    symbol = str(bot_settings.symbol)
    interval = str(bot_settings.interval)
    start_str = str(backtest_settings.start_date)
    end_str = str(backtest_settings.end_date)

    df = fetch_data(symbol=symbol, interval=interval, start_str=start_str, end_str=end_str)
    
    if df is not None and not df.empty:
        csv_file_path = backtest_settings.csv_file_path
        df.to_csv(csv_file_path, index=False)
        logger.trade(f"Data for backtest {bot_settings.symbol} saved in {csv_file_path}")
    else:
        logger.trade(f"Failed to fetch data for {symbol}. Dataframe is None or empty.")

    return df


def backtest_strategy(df, bot_settings, backtest_settings):
    symbol = bot_settings.symbol
    cryptocoin_symbol = symbol[:3]
    stablecoin_symbol = symbol[-4:]
    initial_balance = backtest_settings.initial_balance
    crypto_balance = backtest_settings.crypto_balance
    usdc_balance = initial_balance
    trailing_stop_pct = float(bot_settings.trailing_stop_pct)
    current_price = None
    trailing_stop_loss = 0
    previous_price = None
    trade_log = []
    
    logger.trade(f"Starting backtest with initial balance: {stablecoin_symbol} {usdc_balance}, {cryptocoin_symbol} {crypto_balance}")

    start_index = 50 if bot_settings.strategy == 'scalp' else 200
    end_index = len(df) - 50
    try:
        for i in range(start_index, end_index):
            latest_data = df.iloc[i]
            current_price = float(latest_data['close'])
            
            if bot_settings.strategy == 'scalp':
                df_for_this_loop = calculate_backtest_scalp_indicators(df.iloc[:start_index+i+1], bot_settings)
            elif bot_settings.strategy == 'swing':
                df_for_this_loop = calculate_backtest_swing_indicators(df.iloc[:start_index+i+1], df.iloc[:start_index+i+1], bot_settings)

            buy_signal_func, sell_signal_func = select_signals_checkers(bot_settings)
            buy_signal = buy_signal_func(df_for_this_loop, bot_settings)
            sell_signal = sell_signal_func(df_for_this_loop, bot_settings) or (current_price <= trailing_stop_loss)

            atr = df_for_this_loop['atr'].iloc[i] if 'atr' in df_for_this_loop.columns else 0
            price_rises = current_price >= previous_price if previous_price is not None else False

            if crypto_balance > 0:
                trailing_stop_loss = update_trailing_stop_loss(current_price, trailing_stop_loss, atr, bot_settings)

            if buy_signal and usdc_balance > 0:
                crypto_balance = usdc_balance / current_price
                usdc_balance = 0
                trailing_stop_loss = current_price * (1 - trailing_stop_pct)
                trade_log.append({
                    'action': 'buy',
                    'price': float(current_price),
                    'time': int(latest_data['open_time']),
                    'crypto_balance': float(crypto_balance),
                    'usdc_balance': float(usdc_balance),
                    'trailing_stop_loss': float(trailing_stop_loss)
                })
                logger.trade("Backtest. Buy at price %f. Crypto balance: %f, USDC balance: %f", current_price, crypto_balance, usdc_balance)

            elif sell_signal and crypto_balance > 0:
                usdc_balance = crypto_balance * current_price
                crypto_balance = 0
                trailing_stop_loss = 0
                trade_log.append({
                    'action': 'sell',
                    'price': float(current_price),
                    'time': int(latest_data['close_time']),
                    'crypto_balance': float(crypto_balance),
                    'usdc_balance': float(usdc_balance)
                })
                logger.trade("Backtest. Sell at price %f. Crypto balance: %f, USDC balance: %f", current_price, crypto_balance, usdc_balance)
            
            elif crypto_balance > 0 and price_rises:
                trailing_stop_loss = update_trailing_stop_loss(current_price, trailing_stop_loss, atr, bot_settings)

            previous_price = current_price

        final_balance = usdc_balance + crypto_balance * float(df.iloc[-1]['close'])
        logger.info("Backtest complete. Final balance: %f, Profit: %f", final_balance, final_balance - initial_balance)
        
        new_backtest = BacktestResult(
            bot_id = bot_settings.id,
            start_date = backtest_settings.start_date,
            end_date = backtest_settings.end_date,
            initial_balance = initial_balance,
            final_balance = final_balance,
            profit = final_balance - initial_balance,
            trade_log=json.dumps(trade_log)
        )
        db.session.add(new_backtest)
        db.session.commit()
                
        return {
            'initial_balance': initial_balance,
            'final_balance': final_balance,
            'profit': final_balance - initial_balance,
            'trade_log': trade_log
        }
        
    except IndexError as e:
        logger.error(f'IndexError when accessing index: {str(e)} in backtest_strategy')
    except Exception as e:
        logger.error(f'Exception in backtest_strategy: {str(e)}')