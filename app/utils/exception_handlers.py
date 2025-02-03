import sys
import functools
import logging
from binance.exceptions import BinanceAPIException

logger = logging.getLogger(__name__)

def exception_handler(default_return=None, db_rollback=False):
    """
    A decorator that catches exceptions, logs the error, optionally rolls back the database session, 
    and sends an email notification.

    Args:
        default_return (Any, optional): The value to return if an exception occurs. Defaults to None.
        db_rollback (bool, optional): If True, rolls back the database session upon an exception. Defaults to False.

    Returns:
        function: A wrapped function that handles exceptions.

    Exceptions Caught:
        - IndexError
        - BinanceAPIException
        - ConnectionError
        - TimeoutError
        - ValueError
        - TypeError
        - FileNotFoundError
        - General Exception (any other unexpected errors)
    
    Behavior:
        - Logs the exception with the bot ID (if available).
        - Sends an email notification to the administrator.
        - Optionally rolls back the database session if `db_rollback=True`.
        - Returns `default_return` in case of an error.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            bot_id = None

            if 'bot_settings' in kwargs and hasattr(kwargs['bot_settings'], 'id'):
                bot_id = kwargs['bot_settings'].id
            else:
                for arg in args:
                    if hasattr(arg, 'id') and hasattr(arg, 'bot_running'):
                        bot_id = arg.id
                        break
            
            if bot_id is None:
                if 'bot_id' in kwargs:
                    bot_id = kwargs['bot_id']
                else:
                    for arg in args:
                        if isinstance(arg, int):
                            bot_id = arg
                            break

            bot_str = f'Bot {bot_id} ' if bot_id else ''

            try:
                return func(*args, **kwargs)
            except (
                IndexError, 
                BinanceAPIException, 
                ConnectionError, 
                TimeoutError, 
                ValueError, 
                TypeError, 
                FileNotFoundError
            ) as e:
                exception_type = type(e).__name__
                logger.error(f"{bot_str}{exception_type} in {func.__name__}: {str(e)}")
                from .email_utils import send_admin_email
                send_admin_email(f"{bot_str}{exception_type} in {func.__name__}", str(e))
            except Exception as e:
                exception_type = "Exception"
                logger.error(f"{bot_str}{exception_type} in {func.__name__}: {str(e)}")
                from .email_utils import send_admin_email
                send_admin_email(f"{bot_str}{exception_type} in {func.__name__}", str(e))

            if db_rollback:
                from .. import db
                db.session.rollback()
                logger.error(f"db.session.rollback() Database transaction rollback executed.")
            
            if default_return is exit:
                logger.error('sys.exit(1) Exiting program due to an error.')
                sys.exit(1)
            elif callable(default_return):
                return default_return()
            return default_return

        return wrapper
    return decorator