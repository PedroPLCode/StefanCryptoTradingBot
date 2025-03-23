import time
import requests
import smtplib
from binance.exceptions import BinanceAPIException
from app.utils.logging import logger


def retry_connection(max_retries=3, delay=1):
    """
    A decorator that retries connecting to the API in case of connection issues.

    :param max_retries: Maximum number of retry attempts.
    :param delay: Time in seconds between each retry attempt.
    """

    def retry_connection_decorator(func):
        def retry_connection_wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except (
                    ConnectionError,
                    TimeoutError,
                    requests.exceptions.RequestException,
                    BinanceAPIException,
                    smtplib.SMTPException,
                    OSError,
                ) as e:
                    retries += 1
                    logger.warning(
                        f"retry_connection Connection failed (attempt {retries}/{max_retries}). Retrying in {delay} seconds..."
                    )
                    time.sleep(delay)
            error_msg = f"retry_connection. Max retries reached. Connection failed. max_retries: {max_retries}, delay: {delay}"
            logger.error(error_msg)
            raise Exception(error_msg)

        return retry_connection_wrapper

    return retry_connection_decorator
