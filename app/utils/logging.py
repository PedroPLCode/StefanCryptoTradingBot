import logging

stafan_log_filename = 'stefan.log'
flask_log_filename = 'flask.log'
gunicorn_log_filename = 'gunicorn.log'
logs = [stafan_log_filename, flask_log_filename, gunicorn_log_filename]

TRADE_LEVEL = 25
logging.addLevelName(TRADE_LEVEL, "TRADE")

def trade(self, message, *args, **kws):
    """
    Custom logging function for the TRADE level.
    
    Args:
        message (str): The log message to be logged.
        *args: Additional arguments passed to the log.
        **kws: Additional keyword arguments passed to the log.
    
    Logs the trade information if the trade level is enabled for the logger.
    """
    if self.isEnabledFor(TRADE_LEVEL):
        self._log(TRADE_LEVEL, message, args, **kws)

logging.Logger.trade = trade

logger = logging.getLogger('main_logger')
logger.setLevel(logging.DEBUG)

general_handler = logging.FileHandler(flask_log_filename)
general_handler.setLevel(logging.DEBUG)
general_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
general_handler.setFormatter(general_formatter)

trade_handler = logging.FileHandler(stafan_log_filename)
trade_handler.setLevel(TRADE_LEVEL)
trade_formatter = logging.Formatter('%(asctime)s TRADE: %(message)s')
trade_handler.setFormatter(trade_formatter)

logger.addHandler(general_handler)
logger.addHandler(trade_handler)