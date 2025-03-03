from flask import jsonify
from datetime import datetime
from ..utils.logging import logger
from ..utils.exception_handlers import exception_handler
from ..utils.email_utils import send_admin_email
from typing import List, Optional


@exception_handler()
def process_bot_emergency_stop(
    bot_settings: object, passwd: str
) -> Optional[object]:
    """
    Processes the emergency stop for a single bot by verifying the password, placing a sell order if needed,
    and setting the bot's status to not running.

    Args:
        bot_settings (BotSettings): The bot settings object containing bot information.
        passwd (str): The password provided for the emergency stop.

    Returns:
        Optional[BotSettings]: The updated bot settings if the emergency stop was successful, or None if the password was incorrect.
    """
    if bot_settings.etop_passwd != passwd:
        logger.trade(
            f"Bot {bot_settings.id} {bot_settings.symbol} {bot_settings.strategy} - Wrong Emergency stop password."
        )
        send_admin_email(
            f"Bot {bot_settings.id} Emergency stop Error.",
            f"Wrong password attempt for Bot {bot_settings.id} {bot_settings.symbol} {bot_settings.strategy}.",
        )
        return None

    from ..utils.bots_utils import handle_emergency_sell_order

    if bot_settings.bot_current_trade and bot_settings.bot_current_trade.is_active:
        handle_emergency_sell_order(bot_settings) 

    bot_settings.bot_running = False
    logger.trade(
        f"Bot {bot_settings.id} {bot_settings.symbol} {bot_settings.strategy} Emergency stopped."
    )
    send_admin_email(
        f"Bot {bot_settings.id} Emergency stopped.",
        f"Bot {bot_settings.id} {bot_settings.symbol} {bot_settings.strategy} Emergency stopped.\n\nCheck CurrentTrade in Flask Admin Panel.\nCurrentTrade needs to be deactivated and all params needs to be set on 0.",
    )
    return bot_settings


@exception_handler()
def handle_no_bots() -> tuple:
    """
    Handles the case when there are no bots to stop.

    Returns:
        tuple: A tuple containing the response message and HTTP status code (404).
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.trade("No Bots Found to Emergency stop.")
    send_admin_email(
        "Bots Emergency stop Error.",
        f"StafanCryptoTradingBot Emergency stop report.\n{now}\n\nNo Bots Found to Emergency stop.\n\nCheck it as soon as possible.\n\n-- \n\nStefanCryptoTradingBot\nhttps://stefan.ropeaccess.pro\n\nFomoSapiensCryptoDipHunter\nhttps://fomo.ropeaccess.pro\n\nCodeCave\nhttps://cave.ropeaccess.pro\n",
    )
    return jsonify({"error": "No bots to stop."}), 404


@exception_handler()
def handle_bots_stopped(bots_stopped: List) -> tuple:
    """
    Handles the response when bots have been successfully stopped.

    Args:
        bots_stopped (List[BotSettings]): A list of bot settings that were stopped.

    Returns:
        tuple: A tuple containing the response message and HTTP status code (200).
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.trade(f"{len(bots_stopped)} Bots Emergency stopped.")
    send_admin_email(
        "All Bots Emergency stopped.",
        f"StafanCryptoTradingBot Emergency stop report.\n{now}\n\n{len(bots_stopped)} Bots Emergency stopped.\n\nProbably due to power loss.\nCheck it as soon as possible.\n\n-- \n\nStefanCryptoTradingBot\nhttps://stefan.ropeaccess.pro\n\nFomoSapiensCryptoDipHunter\nhttps://fomo.ropeaccess.pro\n\nCodeCave\nhttps://cave.ropeaccess.pro\n",
    )
    return jsonify({"success": f"{len(bots_stopped)} Bots Emergency stopped."}), 200
