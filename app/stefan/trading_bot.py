from flask import current_app
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
    calculate_indicators, 
    save_trailing_stop_loss, 
    save_previous_price, 
    update_trailing_stop_loss
)
from .scalping_logic import (
    check_scalping_buy_signal, 
    check_scalping_sell_signal
)
from .swing_logic import (
    check_swing_buy_signal,
    check_swing_sell_signal,
    check_swing_buy_signal_with_MA200,
    check_swing_sell_signal_with_MA200
)

def run_all_scalp_trading_bots():
    run_selected_trading_bots('scalp')

            
def run_all_swing_trading_bots():
    run_selected_trading_bots('swing')


def run_selected_trading_bots(algorithm):
    all_selected_bots = BotSettings.query.filter(BotSettings.algorithm == algorithm).all()
    for bot_settings in all_selected_bots:
        try:
            if bot_settings.bot_current_trade:
                run_single_trading_logic(bot_settings)
            else:
                error_message = f"No current trade found for settings id: {bot_settings.id}"
                send_admin_email(f'Błąd podczas pętli bota {bot_settings.id}', error_message)
                logger.trade(error_message)
        except Exception as e:
            logger.error(f'Błąd w pętli handlowej: {str(e)}')
            send_admin_email('Błąd w pętli handlowej', str(e))


def run_single_trading_logic(bot_settings):
    try:
        with current_app.app_context():
            if bot_settings and bot_settings.bot_running:
                current_trade = bot_settings.bot_current_trade
                symbol = bot_settings.symbol
                trailing_stop_pct = float(bot_settings.trailing_stop_pct)
                interval = bot_settings.interval
                lookback_period = bot_settings.lookback_period
                #logger.info(f'Fetching data for {symbol} with interval {interval} and lookback {lookback_period}')
                df = fetch_data(symbol, interval=interval, lookback=lookback_period)
                #logger.info(f'Data fetched for {symbol}:\n{df.head()}')
                if df.empty or len(df) < 5: 
                    #logger.error(f'Bot {bot_settings.id} DataFrame is empty or has insufficient data for indicators')
                    return 
                calculate_indicators(df, bot_settings)
                #logger.info(df)
                
                current_price = float(0)
                if not df.empty and len(df) > 0:
                    current_price = float(df['close'].iloc[-1])
                else:
                    #logger.error(f'Bot {bot_settings.id} DataFrame is empty or has insufficient data')
                    return

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
                    if bot_settings.algorithm == 'swing':
                        if bot_settings.signals_extended:
                            buy_signal = check_swing_buy_signal_with_MA200(df, bot_settings)
                            sell_signal = check_swing_sell_signal_with_MA200(df, bot_settings)
                        else:
                            buy_signal = check_swing_buy_signal(df, bot_settings)
                            sell_signal = check_swing_sell_signal(df, bot_settings)
                    elif bot_settings.algorithm == 'scalp':
                        buy_signal = check_scalping_buy_signal(df, bot_settings)
                        if bot_settings.signals_extended:
                            sell_signal = check_scalping_sell_signal(df, bot_settings) or current_price <= trailing_stop_price
                        else:
                            sell_signal = current_price <= trailing_stop_price
                    else:
                        logger.error(f'No algorithm {bot_settings.algorithm} found for bot {bot_settings.id}')
                        send_admin_email(f'Error starting bot {bot_settings.id}', f'No algorithm {bot_settings.algorithm} found for bot {bot_settings.id}')
                        return
                
                if not current_trade.is_active and buy_signal:
                    logger.trade(f"{bot_settings.algorithm} buy signal!")
                    place_buy_order(bot_settings)
                    trailing_stop_price = float(current_price) * (1 - float(trailing_stop_pct))
                    
                    logger.debug(f"{bot_settings.algorithm} BUY: current_price type: {type(current_price)}, trailing_stop_pct type: {type(trailing_stop_pct)}")

                    save_trailing_stop_loss(trailing_stop_price, current_trade)
                    save_previous_price(current_price, current_trade)
                elif current_trade.is_active and sell_signal:
                    logger.trade(f"{bot_settings.algorithm} sell signal!")
                    place_sell_order(bot_settings)
                elif current_trade.is_active and price_rises:
                    logger.trade(f"{bot_settings.algorithm} price rises!")
                    trailing_stop_price = update_trailing_stop_loss(
                        current_price,
                        trailing_stop_price,
                        float(df['atr'].iloc[-1])
                    )
                    save_trailing_stop_loss(trailing_stop_price, current_trade)
                    save_previous_price(current_price, current_trade)
                else:
                    logger.trade(f"{bot_settings.algorithm} no trade signal.")

                logger.trade(f"{bot_settings.algorithm.title()} Trading bot {bot_settings.id}: Aktualna cena: {current_price}, Trailing stop loss: {trailing_stop_price}")

    except Exception as e:
        logger.error(f'Błąd w pętli handlowej bota {bot_settings.id}: {str(e)}')
        send_admin_email(f'Błąd w pętli handlowej bota {bot_settings.id}', str(e))
    except BinanceAPIException as e:
        logger.error(f'Błąd w pętli handlowej bota {bot_settings.id}: {str(e)}')
        send_admin_email(f'Błąd w pętli handlowej bota {bot_settings.id}', str(e))
    except ConnectionError as ce:
        logger.error(f'Błąd w pętli handlowej bota {bot_settings.id}: {str(e)}')
        send_admin_email(f'Błąd w pętli handlowej bota {bot_settings.id}', str(e))
    except TimeoutError as e:
        logger.error(f'Błąd w pętli handlowej bota {bot_settings.id}: {str(e)}')
        send_admin_email(f'Błąd w pętli handlowej bota {bot_settings.id}', str(e))