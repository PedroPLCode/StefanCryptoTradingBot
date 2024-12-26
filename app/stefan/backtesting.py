import pandas as pd
from .. import db
from ..utils.logging import logger
from .api_utils import fetch_data
from .logic_utils import (
    check_trend,
    calculate_averages,
    update_stop_loss,
    update_atr_trailing_stop_loss,
    calculate_take_profit,
    calculate_atr_take_profit
)
from .backtesting_utils import (
    update_trade_log,
    save_backtest_results
)
from .calc_utils import (
    calculate_indicators,
    calculate_averages,
    check_trend
)
from .buy_signals import check_buy_signal
from .sell_signals import check_sell_signal

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
    stop_loss_price = 0
    take_profit_price = 0
    use_trailing_take_profit = True
    current_trade_use_take_profit = True
    current_trade_trailing_take_profit_activated = False
    previous_price = None
    
    trade_log = []
    
    logger.trade(f"Starting backtest with initial balance: {stablecoin_symbol} {usdc_balance}, {cryptocoin_symbol} {crypto_balance}")

    start_index = 200 if bot_settings.ma50_signals or bot_settings.ma200_signals else 50
    end_index = len(df) - 50
    
    try:
        for i in range(start_index, end_index):
            loop_df = pd.DataFrame()
            
            if bot_settings.ma50_signals or bot_settings.ma200_signals:
                if (i - 48) >= start_index and (i - 200) >= 0:
                    loop_df = calculate_indicators(
                        df.iloc[start_index+i-48:start_index+i+1], 
                        df.iloc[start_index+i-200:start_index+i+1], 
                        bot_settings
                        )
                else:
                    continue
            else:
                if (i - 45) >= start_index:
                    loop_df = calculate_indicators(
                        df.iloc[start_index+i-45:start_index+i+1], 
                        None,
                        bot_settings
                        )
                else:
                    continue
            
            latest_data = loop_df.iloc[-1]
            previous_data = loop_df.iloc[-2]
            current_price = float(latest_data['close'])
            
            trend = check_trend(loop_df)
            
            averages = calculate_averages(loop_df, bot_settings)
            
            buy_signal = check_buy_signal(
                df, 
                bot_settings, 
                trend, 
                averages, 
                latest_data, 
                previous_data
                )
            sell_signal = check_sell_signal(
                df, 
                bot_settings, 
                trend, 
                averages, 
                latest_data, 
                previous_data
                )
            
            price_hits_stop_loss = current_price <= stop_loss_price
            price_hits_take_profit = current_price >= take_profit_price
        
            stop_loss_activated = False
            if bot_settings.use_stop_loss and price_hits_stop_loss:
                stop_loss_activated = True
            
            take_profit_activated = False
            if bot_settings.use_take_profit and current_trade_use_take_profit and price_hits_take_profit:
                if use_trailing_take_profit and not current_trade_trailing_take_profit_activated:
                    current_trade_use_take_profit = False
                    current_trade_trailing_take_profit_activated = True
                    bot_settings.use_trailing_stop_loss = True
                    bot_settings.trailing_stop_with_atr = True
                    bot_settings.trailing_stop_atr_calc = 1
                    db.session.commit()
                else:
                    take_profit_activated = True
            
            full_sell_signal = stop_loss_activated or take_profit_activated or sell_signal
            if bot_settings.sell_signal_only_stop_loss_or_take_profit:
                full_sell_signal = stop_loss_activated or take_profit_activated

            atr = loop_df['atr'].iloc[-1] if 'atr' in loop_df.columns else 0
            
            price_rises = current_price > previous_price if previous_price is not None else False
            
            if buy_signal and usdc_balance > 0:
                crypto_balance = usdc_balance / current_price
                usdc_balance = 0
        
                stop_loss_price = 0
                take_profit_price = 0
                
                if bot_settings.use_stop_loss:
                    stop_loss_price = update_stop_loss(
                        current_price, 
                        stop_loss_price, 
                        bot_settings
                    )
                    
                    if bot_settings.trailing_stop_with_atr:
                        stop_loss_price = update_atr_trailing_stop_loss(
                            current_price, 
                            stop_loss_price, 
                            atr,
                            bot_settings
                        )
                    
                if bot_settings.use_take_profit:
                    take_profit_price = calculate_take_profit(
                        current_price, 
                        bot_settings
                        )
                    
                    if bot_settings.take_profit_with_atr:
                        take_profit_price = calculate_atr_take_profit(
                            current_price, 
                            atr, 
                            bot_settings
                            )
                
                update_trade_log(
                    'buy', 
                    trade_log, 
                    current_price, 
                    latest_data, 
                    crypto_balance, 
                    usdc_balance, 
                    stop_loss_price,
                    take_profit_price
                )
        
            elif full_sell_signal and crypto_balance > 0:
                usdc_balance = crypto_balance * current_price
                crypto_balance = 0
                stop_loss_price = 0
                take_profit_price = 0
                
                update_trade_log(
                    'sell', 
                    trade_log, 
                    current_price, 
                    latest_data, 
                    crypto_balance, 
                    usdc_balance, 
                    stop_loss_price,
                    take_profit_price
                )
            
            elif crypto_balance > 0 and price_rises:
                
                stop_loss_price = update_stop_loss(
                    current_price, 
                    stop_loss_price, 
                    bot_settings
                    )
                
                if bot_settings.trailing_stop_with_atr:
                    stop_loss_price = update_atr_trailing_stop_loss(
                        current_price, 
                        stop_loss_price, 
                        atr, 
                        bot_settings
                        )

            previous_price = current_price

        final_balance = usdc_balance + crypto_balance * float(df.iloc[end_index]['close'])
        logger.trade("Backtest complete. Final balance: %f, Profit: %f", final_balance, final_balance - initial_balance)
        
        save_backtest_results(bot_settings, backtest_settings, initial_balance, final_balance, trade_log)
        
    except IndexError as e:
        logger.error(f'Bot {bot_settings.id} IndexError in backtest_strategy: {str(e)}')
    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in backtest_strategy: {str(e)}')