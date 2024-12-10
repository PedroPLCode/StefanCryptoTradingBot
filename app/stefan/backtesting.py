import pandas as pd
from ..utils.logging import logger
from .api_utils import fetch_data
from .logic_utils import (
    check_trend,
    calculate_averages,
    update_trailing_stop_loss,
    update_atr_trailing_stop_loss
)
from .backtesting_utils import (
    calculate_backtest_scalp_indicators,
    calculate_backtest_swing_indicators,
    select_signals_checkers,
    update_trade_log,
    save_backtest_results
)

def fetch_and_save_data(backtest_settings, bot_settings):
    symbol = str(bot_settings.symbol)
    interval = str(bot_settings.interval)
    start_str = str(backtest_settings.start_date)
    end_str = str(backtest_settings.end_date)

    df = fetch_data(
        symbol=symbol, 
        interval=interval, 
        start_str=start_str, 
        end_str=end_str
        )
    
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
    current_price = None
    trailing_stop_loss = 0
    previous_price = None
    trade_log = []
    
    logger.trade(f"Starting backtest with initial balance: {stablecoin_symbol} {usdc_balance}, {cryptocoin_symbol} {crypto_balance}")

    start_index = 50 if bot_settings.strategy == 'scalp' else 200
    end_index = len(df) - 50
    
    try:
        for i in range(start_index, end_index):
            loop_df = pd.DataFrame()
            
            if bot_settings.strategy == 'scalp':
                if (i - 45) >= start_index:
                    loop_df = calculate_backtest_scalp_indicators(
                        df.iloc[start_index+i-45:start_index+i+1], 
                        bot_settings
                        )
                else:
                    continue
                
            elif bot_settings.strategy == 'swing':
                if (i - 48) >= start_index and (i - 200) >= 0:
                    loop_df = calculate_backtest_swing_indicators(
                        df.iloc[start_index+i-48:start_index+i+1], 
                        df.iloc[start_index+i-200:start_index+i+1], 
                        bot_settings
                        )
                else:
                    continue
            
            latest_data = loop_df.iloc[-1]
            previous_data = loop_df.iloc[-2]
            current_price = float(latest_data['close'])
            buy_signal_func, sell_signal_func = select_signals_checkers(bot_settings)
            trend = check_trend(loop_df)
            averages = calculate_averages(loop_df, bot_settings)
            buy_signal = buy_signal_func(
                loop_df, 
                bot_settings, 
                trend, 
                averages, 
                latest_data, 
                previous_data
                )
            sell_signal = sell_signal_func(
                loop_df, 
                bot_settings, 
                trend, 
                averages, 
                latest_data, 
                previous_data
                )
            stop_loss_activated = current_price <= trailing_stop_loss
            
            full_sell_signal = stop_loss_activated or sell_signal
            if bot_settings.sell_signal_only_trailing_stop:
                full_sell_signal = stop_loss_activated

            atr = loop_df['atr'].iloc[-1] if 'atr' in loop_df.columns else 0
            price_rises = current_price >= previous_price if previous_price is not None else False
            
            if buy_signal and usdc_balance > 0:
                crypto_balance = usdc_balance / current_price
                usdc_balance = 0
                trailing_stop_loss = update_trailing_stop_loss(
                    current_price, 
                    trailing_stop_loss, 
                    bot_settings
                )
                update_trade_log(
                    'buy', 
                    trade_log, 
                    current_price, 
                    latest_data, 
                    crypto_balance, 
                    usdc_balance, 
                    trailing_stop_loss
                )
        
            elif full_sell_signal and crypto_balance > 0:
                usdc_balance = crypto_balance * current_price
                crypto_balance = 0
                trailing_stop_loss = 0
                update_trade_log(
                    'sell', 
                    trade_log, 
                    current_price, 
                    latest_data, 
                    crypto_balance, 
                    usdc_balance, 
                    trailing_stop_loss
                )
            
            elif crypto_balance > 0 and price_rises:
                trailing_stop_loss = update_trailing_stop_loss(
                    current_price, 
                    trailing_stop_loss, 
                    bot_settings
                    )
                if bot_settings.trailing_stop_with_atr:
                    trailing_stop_loss = update_atr_trailing_stop_loss(
                        current_price, 
                        trailing_stop_loss, 
                        atr, 
                        bot_settings
                        )

            previous_price = current_price

        final_balance = usdc_balance + crypto_balance * float(df.iloc[end_index]['close'])
        logger.trade("Backtest complete. Final balance: %f, Profit: %f", final_balance, final_balance - initial_balance)
        
        save_backtest_results(bot_settings, backtest_settings, initial_balance, final_balance, trade_log)
        
    except IndexError as e:
        logger.error(f'IndexError in backtest_strategy: {str(e)}')
    except Exception as e:
        logger.error(f'Exception in backtest_strategy: {str(e)}')