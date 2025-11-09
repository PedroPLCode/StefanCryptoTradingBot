from flask import current_app
from ..models import BotSettings
from typing import Optional
from ..utils.logging import logger
from ..utils.exception_handlers import exception_handler
from ..utils.email_utils import send_admin_email
from ..utils.bots_utils import is_bot_suspended
from .logic_utils import (
    get_current_price,
    fetch_data_and_validate,
    manage_trading_logic,
)


def initial_run_all_trading_bots():
    """
    Runs all trading bots across different intervals for both scalp and swing strategies.

    This function triggers the execution of multiple trading bots, categorized by their
    respective intervals (1m, 3m, 5m, 15m, 30m, 1h, 4h, 1d). After running the bots, it logs
    the completion of the operation.

    Returns:
        None
    """
    run_all_scalp_1m_trading_bots()
    run_all_scalp_3m_trading_bots()
    run_all_scalp_5m_trading_bots()
    run_all_scalp_15m_trading_bots()
    run_all_swing_30m_trading_bots()
    run_all_swing_1h_trading_bots()
    run_all_swing_4h_trading_bots()
    run_all_swing_1d_trading_bots()
    logger.trade("All trading bots initial run completed.")


def run_all_scalp_1m_trading_bots():
    """Runs all scalp trading bots with a 1-minute interval"""
    run_selected_trading_bots("1m")
    logger.trade("1m interval bots run completed.")


def run_all_scalp_3m_trading_bots():
    """Runs all scalp trading bots with a 3-minute interval"""
    run_selected_trading_bots("3m")
    logger.trade("3m interval bots run completed.")


def run_all_scalp_5m_trading_bots():
    """Runs all scalp trading bots with a 5-minute interval"""
    run_selected_trading_bots("5m")
    logger.trade("5m interval bots run completed.")


def run_all_scalp_15m_trading_bots():
    """Runs all scalp trading bots with a 15-minute interval"""
    run_selected_trading_bots("15m")
    logger.trade("15m interval bots run completed.")


def run_all_swing_30m_trading_bots():
    """Runs all swing trading bots with a 30-minute interval"""
    run_selected_trading_bots("30m")
    logger.trade("30m interval bots run completed.")


def run_all_swing_1h_trading_bots():
    """Runs all swing trading bots with a 1-hour interval"""
    run_selected_trading_bots("1h")
    logger.trade("1h interval bots run completed.")


def run_all_swing_4h_trading_bots():
    """Runs all swing trading bots with a 4-hours interval"""
    run_selected_trading_bots("4h")
    logger.trade("4h interval bots run completed.")


def run_all_swing_1d_trading_bots():
    """Runs all swing trading bots with a 1-day interval"""
    run_selected_trading_bots("1d")
    logger.trade("1d interval bots run completed.")


@exception_handler()
def run_selected_trading_bots(interval: str) -> Optional[int]:
    """
    Runs selected trading bots based on the specified interval.

    This function queries the database for all bots configured with the given interval
    and attempts to start each bot's trading logic if it is active and configured with the
    necessary analysis methods. Any issues or missing configurations are logged and emailed to the admin.

    Args:
        interval (str): The interval for the bots to run (e.g., '1m', '3m', etc.).

    Returns:
        None
    """
    all_selected_bots = BotSettings.query.filter(BotSettings.interval == interval).all()

    for bot_settings in all_selected_bots:
        if bot_settings.bot_running and (
            bot_settings.use_technical_analysis or 
            bot_settings.use_machine_learning or 
            bot_settings.use_gpt_analysis
        ):

            if bot_settings.bot_current_trade and bot_settings.bot_technical_analysis:
                run_single_trading_logic(bot_settings)
            else:
                error_message = f"No BotCurrentTrade or BotTechnicalAnalysis found for Bot: {bot_settings.id}"
                send_admin_email(
                    f"Error starting bot {bot_settings.id}",
                    f"Error starting bot {bot_settings.id}\n{error_message}",
                )
                logger.trade(error_message)


@exception_handler()
def run_single_trading_logic(bot_settings: BotSettings) -> Optional[int]:
    """
    Runs the trading logic for a single bot based on its settings.

    This function fetches market data, validates it, and executes the trading logic based on
    the bot's current settings and analysis methods. The trading logic includes checking
    the bot's suspension status, fetching the current price, and managing the trade.

    Args:
        bot_settings (BotSettings): The settings for the specific bot to run.

    Returns:
        None
    """
    with current_app.app_context():
        if not bot_settings:
            logger.info(f"Bot {bot_settings.id} BotSettings not found. Cycle skipped.")
            return

        if is_bot_suspended(bot_settings):
            logger.info(
                f"Bot {bot_settings.id} is suspended after negative trade. Cycles remaining: {bot_settings.suspension_cycles_remaining}"
            )
            return

        current_trade = bot_settings.bot_current_trade
        symbol = bot_settings.symbol
        interval = bot_settings.interval
        lookback_period = bot_settings.lookback_period
        lookback_extended = (
            f"{int(bot_settings.interval[:-1]) * 205}{bot_settings.interval[-1:]}"
        )

        logger.trade(
            f"Bot {bot_settings.id} {bot_settings.strategy} Fetching data for {symbol} with interval {interval} and lookback {lookback_period}"
        )
        df_fetched = fetch_data_and_validate(
            symbol, interval, lookback_extended, bot_settings.id
        )

        if df_fetched is None:
            return

        current_price = get_current_price(df_fetched, bot_settings.id)
        if current_price is None:
            return

        manage_trading_logic(bot_settings, current_trade, current_price, df_fetched)
