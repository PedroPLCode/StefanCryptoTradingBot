from flask import flash, current_app
import datetime as dt
from .. import db
from app.models import BotSettings
from ..utils.logging import logger
from ..utils.exception_handlers import exception_handler
from ..utils.email_utils import (
    send_admin_email,
    send_trade_email
)
from ..stefan.api_utils import place_sell_order

@exception_handler()
def start_single_bot(bot_id, current_user):
    """
    Starts a single trading bot by updating its `bot_running` status in the database.
    
    Args:
        bot_id (int): The ID of the bot to be started.
        current_user (User): The user requesting to start the bot.
    
    Logs and notifies the admin via email if the bot starts successfully.
    """
    bot_settings = BotSettings.query.get(bot_id)
    if bot_settings.bot_running:
        flash(f'Bot {bot_settings.id} is already running.', 'info')
    else:
        bot_settings.bot_running = True
        db.session.commit()
        logger.trade(f'Bot {bot_settings.id} {bot_settings.symbol} {bot_settings.strategy} has been started.')
        flash(f'Bot {bot_settings.id} has been started.', 'success')
        send_admin_email(f'Bot {bot_settings.id} started.', f'Bot {bot_settings.id} has been started by {current_user.name}.\n\nSymbol: {bot_settings.symbol}\nStrategy: {bot_settings.strategy}\nLookback period: {bot_settings.lookback_period}\nInterval: {bot_settings.interval}\n\nComment: {bot_settings.comment}')
    

@exception_handler()
def stop_single_bot(bot_id, current_user):
    """
    Stops a single trading bot by updating its `bot_running` status in the database.
    
    Args:
        bot_id (int): The ID of the bot to be stopped.
        current_user (User): The user requesting to stop the bot.
    
    Logs and notifies the admin via email if the bot stops successfully.
    """
    bot_settings = BotSettings.query.get(bot_id)
    if not bot_settings.bot_running:
        flash(f'Bot {bot_settings.id} is already stopped.', 'info')
    else:
        bot_settings.bot_running = False
        db.session.commit()
        logger.trade(f'Bot {bot_settings.id} {bot_settings.symbol} {bot_settings.strategy} has been stopped.')
        flash(f'Bot {bot_settings.id} has been stopped.', 'success')
        send_admin_email(f'Bot {bot_settings.id} stopped.', f'Bot {bot_settings.id} {bot_settings.symbol} {bot_settings.strategy} has been stopped by {current_user.login if current_user.login else current_user}.')


@exception_handler()
def stop_all_bots(current_user):
    """
    Stops all active trading bots.
    
    Args:
        current_user (User): The user requesting to stop all bots.
    
    If a bot has an active trade, it attempts to place a sell order before stopping it.
    Logs and notifies the admin in case of errors.
    """
    all_bots_settings = BotSettings.query.all()
    with current_app.app_context():
        for bot_settings in all_bots_settings:
            bot_id = bot_settings.id
            if bot_settings.bot_current_trade.is_active:
                place_sell_order(bot_id)
            stop_single_bot(bot_id, current_user)
            

@exception_handler()
def start_all_bots(current_user='undefined'):
    """
    Starts all available trading bots.
    
    Args:
        current_user (User, optional): The user requesting to start all bots. Defaults to 'undefined'.
    
    Logs and notifies the admin in case of errors.
    """
    all_bots_settings = BotSettings.query.all()
    with current_app.app_context():
        for bot_settings in all_bots_settings:
            bot_id = bot_settings.id
            start_single_bot(bot_id, current_user)         


@exception_handler(default_return=False, db_rollback=True)
def is_bot_suspended(bot_settings):
    """
    Checks if the bot is suspended after a negative trade. If the bot is suspended, it decreases
    the remaining suspension cycles and returns True. If the suspension period is over, it resets 
    the suspension flag and sends a report email.

    Args:
        bot_settings (BotSettings): The settings of the bot to check for suspension.

    Returns:
        bool: True if the bot is still suspended, False otherwise.
    """
    if bot_settings.is_suspended_after_negative_trade:
        if bot_settings.suspension_cycles_remaining > 0:
            bot_settings.suspension_cycles_remaining -= 1
            db.session.commit()
            return True

        bot_settings.is_suspended_after_negative_trade = False
        bot_settings.suspension_cycles_remaining = 0
        db.session.commit()
        
        now = dt.now()
        formatted_now = now.strftime('%Y-%m-%d %H:%M:%S')
        logger.info(f"Bot {bot_settings.id} suspension after negative trade finished.")
        send_trade_email(f"Bot {bot_settings.id} suspend_after_negative_trade report.", f"StafanCryptoTradingBotBot suspend_after_negative_trade report.\n{formatted_now}\n\nBot {bot_settings.id} {bot_settings.strategy} {bot_settings.symbol}.\ncomment: {bot_settings.comment}\n\nSuspension after negative trade finished.\nBot {bot_settings.id} is back in operation")
    
    return False


@exception_handler(db_rollback=True)
def suspend_after_negative_trade(bot_settings):
    """
    Suspends the bot after a negative trade by setting the `is_suspended_after_negative_trade` flag
    and initializing the suspension cycle count. It then sends a report email about the suspension.

    Args:
        bot_settings (BotSettings): The settings of the bot to suspend.

    Returns:
        None
    """
    now = dt.now()
    formatted_now = now.strftime('%Y-%m-%d %H:%M:%S') 
    
    bot_settings.is_suspended_after_negative_trade = True
    bot_settings.suspension_cycles_remaining = bot_settings.cycles_of_suspension_after_negative_trade
    db.session.commit()
        
    logger.info(f"Bot {bot_settings.id} suspended after negative trade. Cycles remaininig: {bot_settings.cycles_of_suspension_after_negative_trade}.")
    send_trade_email(f"Bot {bot_settings.id} suspend_after_negative_trade report.", f"StafanCryptoTradingBotBot suspend_after_negative_trade report.\n{formatted_now}\n\nBot {bot_settings.id} {bot_settings.strategy} {bot_settings.symbol}.\ncomment: {bot_settings.comment}\n\nBot {bot_settings.id} is suspended after negative trade.\nCycles of suspension: {bot_settings.cycles_of_suspension_after_negative_trade}\nCycles remaininig: {bot_settings.cycles_of_suspension_after_negative_trade}")