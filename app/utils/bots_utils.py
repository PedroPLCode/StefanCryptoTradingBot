from flask import flash, current_app
import datetime as dt
from typing import Union
from .. import db
from app.models import BotSettings, User
from ..utils.logging import logger
from ..utils.exception_handlers import exception_handler
from ..utils.email_utils import send_admin_email, filter_users_and_send_trade_emails


@exception_handler()
def start_single_bot(bot_id: int, current_user: User) -> None:
    """
    Starts a single trading bot by updating its `bot_running` status in the database.

    Args:
        bot_id (int): The ID of the bot to be started.
        current_user (User): The user requesting to start the bot.
    """
    bot_settings = BotSettings.query.get(bot_id)
    if bot_settings.bot_running:
        flash(f"Bot {bot_settings.id} is already running.", "info")
    else:
        bot_settings.bot_running = True
        db.session.commit()
        logger.trade(
            f"Bot {bot_settings.id} {bot_settings.symbol} {bot_settings.strategy} has been started."
        )
        flash(f"Bot {bot_settings.id} has been started.", "success")
        send_admin_email(
            f"Bot {bot_settings.id} started.",
            f"Bot {bot_settings.id} has been started by {current_user.name}.\n\nSymbol: {bot_settings.symbol}\nStrategy: {bot_settings.strategy}\nLookback period: {bot_settings.lookback_period}\nInterval: {bot_settings.interval}\n\nComment: {bot_settings.comment}",
        )


@exception_handler()
def stop_single_bot(bot_id: int, current_user: User) -> None:
    """
    Stops a single trading bot by updating its `bot_running` status in the database.

    Args:
        bot_id (int): The ID of the bot to be stopped.
        current_user (User): The user requesting to stop the bot.
    """
    bot_settings = BotSettings.query.get(bot_id)
    if not bot_settings.bot_running:
        flash(f"Bot {bot_settings.id} is already stopped.", "info")
    else:
        bot_settings.bot_running = False
        db.session.commit()
        logger.trade(
            f"Bot {bot_settings.id} {bot_settings.symbol} {bot_settings.strategy} has been stopped."
        )
        flash(f"Bot {bot_settings.id} has been stopped.", "success")
        send_admin_email(
            f"Bot {bot_settings.id} stopped.",
            f"Bot {bot_settings.id} {bot_settings.symbol} {bot_settings.strategy} has been stopped by {current_user.login if current_user.login else current_user}.\n\nCheck CurrentTrade in Flask Admin Panel.\nCurrentTrade needs to be deactivated and all params needs to be set on 0.",
        )


@exception_handler()
def stop_all_bots(current_user: User) -> None:
    """
    Stops all active trading bots.

    Args:
        current_user (User): The user requesting to stop all bots.
    """
    all_bots_settings = BotSettings.query.all()

    with current_app.app_context():
        for bot_settings in all_bots_settings:
            if bot_settings.bot_current_trade.is_active:
                handle_emergency_sell_order(bot_settings)
            stop_single_bot(bot_settings.id, current_user)


@exception_handler()
def start_all_bots(current_user: Union[User, str] = "undefined") -> None:
    """
    Starts all available trading bots.

    Args:
        current_user (User, optional): The user requesting to start all bots. Defaults to 'undefined'.
    """
    all_bots_settings = BotSettings.query.all()
    with current_app.app_context():
        for bot_settings in all_bots_settings:
            bot_id = bot_settings.id
            start_single_bot(bot_id, current_user)


@exception_handler(default_return=False, db_rollback=True)
def is_bot_suspended(bot_settings: BotSettings) -> bool:
    """
    Checks if the bot is suspended after a negative trade.

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

        now = dt.datetime.now()
        formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"Bot {bot_settings.id} suspension after negative trade finished.")
        filter_users_and_send_trade_emails(
            f"Bot {bot_settings.id} suspend_after_negative_trade report.",
            f"StefanCryptoTradingBotBot\nsuspend_after_negative_trade report.\n{formatted_now}\n\nBot {bot_settings.id} {bot_settings.strategy} {bot_settings.symbol}.\ncomment: {bot_settings.comment}\n\nSuspension after negative trade finished.\nBot {bot_settings.id} is back in operation",
        )

    return False


@exception_handler(db_rollback=True)
def suspend_after_negative_trade(bot_settings: BotSettings) -> None:
    """
    Suspends the bot after a negative trade by setting the `is_suspended_after_negative_trade` flag
    and initializing the suspension cycle count.

    Args:
        bot_settings (BotSettings): The settings of the bot to suspend.
    """
    now = dt.datetime.now()
    formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")

    bot_settings.is_suspended_after_negative_trade = True
    bot_settings.suspension_cycles_remaining = (
        bot_settings.cycles_of_suspension_after_negative_trade
    )
    db.session.commit()

    logger.info(
        f"Bot {bot_settings.id} suspended after negative trade. Cycles remaining: {bot_settings.cycles_of_suspension_after_negative_trade}."
    )
    filter_users_and_send_trade_emails(
        f"Bot {bot_settings.id} suspend_after_negative_trade report.",
        f"StefanCryptoTradingBotBot\nsuspend_after_negative_trade report.\n{formatted_now}\n\nBot {bot_settings.id} {bot_settings.strategy} {bot_settings.symbol}.\ncomment: {bot_settings.comment}\n\nBot {bot_settings.id} is suspended after negative trade.\nCycles of suspension: {bot_settings.cycles_of_suspension_after_negative_trade}\nCycles remaining: {bot_settings.cycles_of_suspension_after_negative_trade}",
    )


@exception_handler()
def handle_emergency_sell_order(bot_settings: BotSettings) -> None:
    """
    Handles the emergency sell order for the given bot.

    This function retrieves the technical analysis data for the specified bot,
    loads the corresponding DataFrame, gets the current price, and executes a sell
    order for the bot's active trade. The emergency sell order is executed by
    passing the bot settings, current trade, current price, and additional flags.

    Args:
        bot_settings (BotSettings): The settings and configuration for the bot,
                                     including technical analysis data and current trade.

    Returns:
        None: This function does not return any value, it triggers a sell order action.
    """
    from ..stefan.logic_utils import execute_sell_order

    execute_sell_order(
        bot_settings,
        bot_settings.bot_current_trade,
        bot_settings.bot_current_trade.current_price,
        False,
        False,
    )
