from flask import current_app
from sqlalchemy import and_
import pandas as pd
from ..models import BotSettings
from binance.exceptions import BinanceAPIException
from ..utils.logging import logger
from ..utils.app_utils import send_admin_email
from .logic_utils import (
    get_current_price,
    fetch_data_and_validate,
    manage_trading_logic
    
)

def initial_run_all_trading_bots():
    run_all_scalp_1m_trading_bots()
    run_all_scalp_3m_trading_bots()
    run_all_scalp_5m_trading_bots()
    run_all_scalp_15m_trading_bots()
    run_all_swing_30m_trading_bots()
    run_all_swing_1h_trading_bots()
    run_all_swing_4h_trading_bots()
    run_all_swing_1d_trading_bots()
    logger.trade('All trading bots initial run completed.')

def run_all_scalp_1m_trading_bots():
    run_selected_trading_bots('1m')
    logger.trade('1m interval bots run completed.')
    
def run_all_scalp_3m_trading_bots():
    run_selected_trading_bots('3m')
    logger.trade('3m interval bots run completed.')
    
def run_all_scalp_5m_trading_bots():
    run_selected_trading_bots('5m')
    logger.trade('5m interval bots run completed.')
    
def run_all_scalp_15m_trading_bots():
    run_selected_trading_bots('15m')
    logger.trade('15m interval bots run completed.')

def run_all_swing_30m_trading_bots():
    run_selected_trading_bots('30m')
    logger.trade('30m interval bots run completed.')
    
def run_all_swing_1h_trading_bots():
    run_selected_trading_bots('1h')
    logger.trade('1h interval bots run completed.')
    
def run_all_swing_4h_trading_bots():
    run_selected_trading_bots('4h')
    logger.trade('4h interval bots run completed.')
    
def run_all_swing_1d_trading_bots():
    run_selected_trading_bots('1d')
    logger.trade('1d interval bots run completed.')
    

def run_selected_trading_bots(interval):
    all_selected_bots = BotSettings.query.filter(BotSettings.interval == interval).all()
    
    for bot_settings in all_selected_bots:
        try:
            if bot_settings.bot_running:
                if bot_settings.bot_current_trade and bot_settings.bot_technical_analysis:
                    run_single_trading_logic(bot_settings)
                else:
                    error_message = f"No BotCurrentTrade or BotTechnicalAnalysis found for Bot: {bot_settings.id}"
                    send_admin_email(f'Error starting bot {bot_settings.id}', error_message)
                    logger.trade(error_message)
                    
        except Exception as e:
            logger.error(f'Exception in run_selected_trading_bots: {str(e)}')
            send_admin_email('Exception in run_selected_trading_bots', str(e))


def run_single_trading_logic(bot_settings):
    
    try:
        with current_app.app_context():
            if not bot_settings:
                return
            
            current_trade = bot_settings.bot_current_trade
            symbol = bot_settings.symbol
            interval = bot_settings.interval
            lookback_period = bot_settings.lookback_period
            lookback_extended = f'{int(bot_settings.interval[:-1]) * 205}{bot_settings.interval[-1:]}'
            
            logger.trade(f'Bot {bot_settings.id} {bot_settings.strategy} Fetching data for {symbol} with interval {interval} and lookback {lookback_period}')
            df = fetch_data_and_validate(
                symbol, 
                interval, 
                lookback_extended, 
                bot_settings.id
                )
            
            if df is None:
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