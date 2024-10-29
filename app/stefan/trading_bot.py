from flask import current_app
import pandas as pd
from ..models import BotSettings
from binance.exceptions import BinanceAPIException
from ..utils.logging import logger
from ..utils.app_utils import send_admin_email
from .api_utils import (
    fetch_data,
    place_buy_order, 
    place_sell_order
)
from .logic_utils import (
    update_trailing_stop_loss,
    update_current_trade,
    update_trade_history
)
from .scalping_logic import (
    calculate_scalp_indicators,
    check_scalping_buy_signal, 
    check_scalping_sell_signal,
    check_scalping_buy_signal_extended,
    check_scalping_sell_signal_extended
)
from .swing_logic import (
    calculate_swing_indicators,
    check_swing_buy_signal,
    check_swing_sell_signal,
    check_swing_buy_signal_extended,
    check_swing_sell_signal_extended
)

def run_all_scalp_trading_bots():
    run_selected_strategy_trading_bots('scalp')

            
def run_all_swing_trading_bots():
    run_selected_strategy_trading_bots('swing')


def run_selected_strategy_trading_bots(strategy):
    all_selected_bots = BotSettings.query.filter(BotSettings.strategy == strategy).all()
    for bot_settings in all_selected_bots:
        try:
            if bot_settings.bot_current_trade:
                run_single_trading_logic(bot_settings)
            else:
                error_message = f"No current trade found for settings id: {bot_settings.id}"
                send_admin_email(f'No current trade found for settings id: {bot_settings.id}', error_message)
                logger.trade(error_message)
        except Exception as e:
            logger.error(f'Exception in run_selected_strategy_trading_bots: {str(e)}')
            send_admin_email('Exception in run_selected_strategy_trading_bots', str(e))


def run_single_trading_logic(bot_settings):
    try:
        with current_app.app_context():
            if bot_settings and bot_settings.bot_running:
                current_trade = bot_settings.bot_current_trade
                symbol = bot_settings.symbol
                trailing_stop_pct = float(bot_settings.trailing_stop_pct)
                interval = bot_settings.interval
                lookback_period = bot_settings.lookback_period
                logger.trade(f'Bot {bot_settings.id} {bot_settings.strategy} Fetching data for {symbol} with interval {interval} and lookback {lookback_period}')
                df = fetch_data(symbol, interval=interval, lookback=lookback_period)
                df_for_ma200 = pd.DataFrame()

                if df is None or df.empty or len(df) < 5: 
                    logger.trade(f'Bot {bot_settings.id} DataFrame df is empty or has insufficient data for indicators')
                    return 
                
                if bot_settings.strategy == 'scalp':
                    if bot_settings.signals_extended:
                        df_for_ma50 = fetch_data(symbol, interval="1h", lookback="3d")
                        if df_for_ma50 is None or df_for_ma50.empty or len(df_for_ma50) < 5:
                            logger.trade(f'Bot {bot_settings.id}: DataFrame df_for_ma50 is empty or could not be fetched')
                            return
                    calculate_scalp_indicators(df, df_for_ma50, bot_settings)
                elif bot_settings.strategy == 'swing':
                    if bot_settings.signals_extended:
                        df_for_ma200 = fetch_data(symbol, interval="1d", lookback="200d")
                        if df_for_ma200 is None or df_for_ma200.empty or len(df_for_ma200) < 5:
                            logger.trade(f'Bot {bot_settings.id}: DataFrame df_for_ma200 is empty or could not be fetched')
                            return
                    calculate_swing_indicators(df, df_for_ma200, bot_settings)
                
                logger.trade(f'Data fetched for {symbol} - last close: {df["close"].iloc[-1]}, max: {df["high"].max()}, min: {df["low"].min()}')

                current_price = None
                if not df.empty and len(df) > 0:
                    try:
                        current_price = float(df['close'].iloc[-1])
                        logger.trade(f'Current price for bot {bot_settings.id} is: {current_price}')
                    except IndexError as e:
                        logger.trade(f'Bot {bot_settings.id}: IndexError No closing price available in the DataFrame {str(e)}')
                    except ValueError as e:
                        logger.trade(f'Bot {bot_settings.id}: ValueError converting closing price to float {str(e)}')
                else:
                    logger.trade(f'Bot {bot_settings.id} DataFrame is empty or has insufficient data')

                trailing_stop_price = float(current_trade.trailing_stop_loss)
                previous_price = float(current_trade.previous_price if current_trade.is_active else 0)
                price_rises = current_price >= previous_price if current_trade.is_active else False
                buy_signal = None
                sell_signal = None

                indicators_ok = all([
                    bot_settings.rsi_buy, 
                    bot_settings.rsi_sell, 
                    bot_settings.cci_buy, 
                    bot_settings.cci_sell, 
                    bot_settings.mfi_buy, 
                    bot_settings.mfi_sell,
                    bot_settings.timeperiod
                    ])
                
                if indicators_ok:
                    if bot_settings.strategy == 'swing':
                        if bot_settings.signals_extended:
                            buy_signal = check_swing_buy_signal_extended(df, bot_settings)
                            sell_signal = check_swing_sell_signal_extended(df, bot_settings)
                        else:
                            buy_signal = check_swing_buy_signal(df, bot_settings)
                            sell_signal = check_swing_sell_signal(df, bot_settings)
                    elif bot_settings.strategy == 'scalp':
                        if bot_settings.signals_extended:
                            buy_signal = check_scalping_buy_signal_extended(df, bot_settings)
                            sell_signal = check_scalping_sell_signal_extended(df, bot_settings)
                        else:
                            buy_signal = check_scalping_buy_signal(df, bot_settings)
                            sell_signal = check_scalping_sell_signal(df, bot_settings)
                    else:
                        buy_signal = False
                        sell_signal = False
                        logger.trade(f'No strategy {bot_settings.strategy} found for bot {bot_settings.id}')
                        send_admin_email(f'Error starting bot {bot_settings.id}', f'No strategy {bot_settings.strategy} found for bot {bot_settings.id}')
                else:
                    logger.trade(f'bot {bot_settings.id} {bot_settings.strategy} missing indicators in database')
                    send_admin_email(f'Error starting bot {bot_settings.id}', f'Missing indicators in database for bot {bot_settings.id} {bot_settings.strategy}')
                        
                if current_price <= trailing_stop_price:
                    sell_signal = True
                    
                #buy_signal = True # SZTUCZNA INGERENCJA
                
                if not current_trade.is_active and buy_signal:
                    logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} buy signal.")
                    buy_success, amount = place_buy_order(bot_settings.id)
                    
                    if buy_success: 
                        trailing_stop_price = float(current_price) * (1 - float(trailing_stop_pct))
                        
                        update_current_trade(
                            bot_id=bot_settings.id, 
                            is_active=True,
                            amount=amount,
                            current_price=current_price, 
                            previous_price=current_price, 
                            buy_price=current_price, 
                            trailing_stop_loss=trailing_stop_price
                            )
                        
                        logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} buy process completed.")
                    
                elif current_trade.is_active and sell_signal:
                    logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} sell signal.")
                    
                    sell_success, amount = place_sell_order(bot_settings.id)

                    if sell_success: 
                        update_trade_history(
                            bot_id=bot_settings.id,
                            strategy=bot_settings.strategy,
                            amount=amount,
                            buy_price=current_trade.buy_price,
                            sell_price=current_price
                        )
                        update_current_trade(
                            bot_id=bot_settings.id, 
                            is_active=False,
                            amount=0,
                            current_price=0, 
                            previous_price=0, 
                            buy_price=0, 
                            trailing_stop_loss=0
                            )
                        
                        logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} sell process completed.")
                    
                elif current_trade.is_active and price_rises:
                    logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} price rises.")
                    trailing_stop_price = update_trailing_stop_loss(
                        current_price,
                        trailing_stop_price,
                        float(df['atr'].iloc[-1])
                    )

                    update_current_trade(
                        bot_id=bot_settings.id, 
                        previous_price=current_price, 
                        trailing_stop_loss=trailing_stop_price
                        )
                
                    logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} previous price and trailing stop loss updated.")
                                        
                else:
                    logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} no trade signal.")

                logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} loop completed.")

    except Exception as e:
        logger.error(f'Exception in run_single_trading_logic bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'Exception in run_single_trading_logic bot {bot_settings.id}', str(e))
    except BinanceAPIException as e:
        logger.error(f'BinanceAPIException in run_single_trading_logic bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'BinanceAPIException in run_single_trading_logic bot {bot_settings.id}', str(e))
    except ConnectionError as e:
        logger.error(f'ConnectionError in run_single_trading_logic bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'ConnectionError in run_single_trading_logic bot {bot_settings.id}', str(e))
    except TimeoutError as e:
        logger.error(f'TimeoutError in run_single_trading_logic bot {bot_settings.id}: {str(e)}')
        send_admin_email(f'TimeoutError in run_single_trading_logic bot {bot_settings.id}', str(e))