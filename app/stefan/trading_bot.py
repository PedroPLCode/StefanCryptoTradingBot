from flask import current_app
from sqlalchemy import and_
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

def run_all_scalp_1m_trading_bots():
    run_selected_strategy_trading_bots('scalp', '1m')
    
def run_all_scalp_3m_trading_bots():
    run_selected_strategy_trading_bots('scalp', '3m')
    
def run_all_scalp_5m_trading_bots():
    run_selected_strategy_trading_bots('scalp', '5m')
    
def run_all_scalp_15m_trading_bots():
    run_selected_strategy_trading_bots('scalp', '15m')

def run_all_swing_30m_trading_bots():
    run_selected_strategy_trading_bots('swing', '30m')
    
def run_all_swing_1h_trading_bots():
    run_selected_strategy_trading_bots('swing', '1h')
    
def run_all_swing_4h_trading_bots():
    run_selected_strategy_trading_bots('swing', '4h')
    
def run_all_swing_1d_trading_bots():
    run_selected_strategy_trading_bots('swing', '1d')
    

def run_selected_strategy_trading_bots(strategy, interval):
    all_selected_bots = BotSettings.query.filter(
        and_(BotSettings.strategy == strategy, BotSettings.interval == interval)
    ).all()
    
    for bot_settings in all_selected_bots:
        try:
            if bot_settings.bot_running:
                if bot_settings.bot_current_trade:
                    run_single_trading_logic(bot_settings)
                else:
                    error_message = f"No current trade found for settings id: {bot_settings.id}"
                    send_admin_email(f'Error starting bot {bot_settings.id}', error_message)
                    logger.trade(error_message)
                    
        except Exception as e:
            logger.error(f'Exception in run_selected_strategy_trading_bots: {str(e)}')
            send_admin_email('Exception in run_selected_strategy_trading_bots', str(e))


def run_single_trading_logic(bot_settings):
    try:
        with current_app.app_context():
            if not bot_settings:
                return
            
            current_trade = bot_settings.bot_current_trade
            symbol = bot_settings.symbol
            interval = bot_settings.interval
            lookback_period = bot_settings.lookback_period
            
            logger.trade(f'Bot {bot_settings.id} {bot_settings.strategy} Fetching data for {symbol} with interval {interval} and lookback {lookback_period}')
            df = fetch_data_and_validate(
                symbol, 
                interval, 
                lookback_period, 
                bot_settings.id
                )
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
            
            manage_trading_logic(bot_settings, current_trade, current_price, df)

    except Exception as e:
        logger.error(f'Bot {bot_settings.id} Exception in run_single_trading_logic: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} Exception in run_single_trading_logic', str(e))
    except BinanceAPIException as e:
        logger.error(f'Bot {bot_settings.id} BinanceAPIException in run_single_trading_logic bot: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} BinanceAPIException in run_single_trading_logic', str(e))
    except ConnectionError as e:
        logger.error(f'Bot {bot_settings.id} ConnectionError in run_single_trading_logic: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} ConnectionError in run_single_trading_logic', str(e))
    except TimeoutError as e:
        logger.error(f'Bot {bot_settings.id} TimeoutError in run_single_trading_logic: {str(e)}')
        send_admin_email(f'Bot {bot_settings.id} TimeoutError in run_single_trading_logic', str(e))