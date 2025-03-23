import os
import asyncio
from flask.cli import load_dotenv
from telegram import Bot as TelegramBot
from flask import current_app
from app.models import User
from ..utils.logging import logger
from ..utils.email_utils import send_admin_email
from ..utils.exception_handlers import exception_handler
from ..utils.retry_connection import retry_connection

load_dotenv()


@exception_handler(default_return=False)
@retry_connection()
def init_telegram_bot() -> TelegramBot:
    """
    Initializes and returns a Telegram bot instance.

    Returns:
        TelegramBot: An instance of the Telegram bot.
    """
    TELEGRAM_API_SECRET = os.environ["TELEGRAM_API_SECRET"]
    return TelegramBot(token=TELEGRAM_API_SECRET)


@exception_handler(default_return=False)
@retry_connection()
def send_telegram(chat_id: str, msg: str) -> bool:
    """
    Sends a message to a specific Telegram chat.

    Args:
        chat_id (str): The Telegram chat ID where the message should be sent.
        msg (str): The message content.

    Returns:
        bool: True if the message was sent successfully.
    """
    telegram_bot = init_telegram_bot()

    if telegram_bot:
        asyncio.run(telegram_bot.send_message(chat_id=chat_id, text=msg))
        logger.info(f"Telegram {chat_id} {msg} sent succesfully.")
        return True

    return False


@exception_handler()
def send_trade_telegram(msg: str) -> None:
    """
    Sends a trade-related notification to all users with Telegram notifications enabled.

    Args:
        msg (str): The message content to be sent.

    Raises:
        Logs an error if the message fails to send.
    """
    with current_app.app_context():
        users = User.query.filter_by(telegram_trades_receiver=True).all()

        for user in users:
            success = send_telegram(chat_id=user.telegram_chat_id, msg=msg)
            if not success:
                logger.error(
                    f"Failed to send trade info telegram to {user.email}. {msg}"
                )
                send_admin_email(
                    f"Error in send_trade_telegram",
                    f"Failed to send trade info telegram to {user.email}",
                )
