import logging

stafan_log_filemane = 'stefan.log'
flask_log_filemane = 'flask.log'
gunicorn_log_filemane = 'gunicorn.log'
logs = [stafan_log_filemane, flask_log_filemane, gunicorn_log_filemane]

TRADE_LEVEL = 25
logging.addLevelName(TRADE_LEVEL, "TRADE")

def trade(self, message, *args, **kws):
    if self.isEnabledFor(TRADE_LEVEL):
        self._log(TRADE_LEVEL, message, args, **kws)

logging.Logger.trade = trade

logger = logging.getLogger('main_logger')
logger.setLevel(logging.DEBUG)

general_handler = logging.FileHandler(flask_log_filemane)
general_handler.setLevel(logging.DEBUG)
general_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
general_handler.setFormatter(general_formatter)

trade_handler = logging.FileHandler(stafan_log_filemane)
trade_handler.setLevel(TRADE_LEVEL)
trade_formatter = logging.Formatter('%(asctime)s TRADE: %(message)s')
trade_handler.setFormatter(trade_formatter)

logger.addHandler(general_handler)
logger.addHandler(trade_handler)