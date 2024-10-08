import logging

TRADE_LEVEL = 25
logging.addLevelName(TRADE_LEVEL, "TRADE")

def trade(self, message, *args, **kws):
    if self.isEnabledFor(TRADE_LEVEL):
        self._log(TRADE_LEVEL, message, args, **kws)

logging.Logger.trade = trade

logger = logging.getLogger('main_logger')
logger.setLevel(logging.DEBUG)

general_handler = logging.FileHandler('flask.log')
general_handler.setLevel(logging.DEBUG)
general_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
general_handler.setFormatter(general_formatter)

trade_handler = logging.FileHandler('stefan.log')
trade_handler.setLevel(TRADE_LEVEL)
trade_formatter = logging.Formatter('%(asctime)s TRADE: %(message)s')
trade_handler.setFormatter(trade_formatter)

logger.addHandler(general_handler)
logger.addHandler(trade_handler)