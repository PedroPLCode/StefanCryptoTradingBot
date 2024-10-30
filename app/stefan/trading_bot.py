from flask import current_app
from ..models import BotSettings
from binance.exceptions import BinanceAPIException
from ..utils.logging import logger
from ..utils.app_utils import send_admin_email
from .logic_utils import (
    get_current_price,
    handle_scalp_strategy,
    handle_swing_strategy,
    fetch_data_and_validate,
    manage_trading_logic
    
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
            if not bot_settings or not bot_settings.bot_running:
                return
            
            current_trade = bot_settings.bot_current_trade
            symbol = bot_settings.symbol
            trailing_stop_pct = float(bot_settings.trailing_stop_pct)
            interval = bot_settings.interval
            lookback_period = bot_settings.lookback_period
            
            logger.trade(f'Bot {bot_settings.id} {bot_settings.strategy} Fetching data for {symbol} with interval {interval} and lookback {lookback_period}')
            df = fetch_data_and_validate(symbol, interval, lookback_period, bot_settings.id)
            if df is None:
                return
            
            if bot_settings.strategy == 'scalp':
                handle_scalp_strategy(bot_settings, df)
            elif bot_settings.strategy == 'swing':
                handle_swing_strategy(bot_settings, df)
            else:
                logger.trade(f'No strategy {bot_settings.strategy} found for bot {bot_settings.id}')
                send_admin_email(f'Error starting bot {bot_settings.id}', f'No strategy {bot_settings.strategy} found for bot {bot_settings.id}')
                return
            
            current_price = get_current_price(df, bot_settings.id)
            if current_price is None:
                return
            
            manage_trading_logic(bot_settings, current_trade, current_price, trailing_stop_pct, df)

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