from .. import db
from ..models import TradesHistory
from ..utils.logging import logger
from ..utils.app_utils import send_admin_email

def save_active_trade(current_trade, amount, price, buy_price):
    try:
        current_trade.is_active = True
        current_trade.amount = amount
        current_trade.price = price
        current_trade.buy_price = buy_price
        db.session.commit()
    except Exception as e:
        logger.error(f"Exception in save_active_trade: {str(e)}")
        send_admin_email(f'Exception in save_active_trade', str(e))


def save_deactivated_trade(current_trade):
    try:
        current_trade.is_active = False
        current_trade.amount = None
        current_trade.buy_price = None
        current_trade.price = None
        current_trade.previous_price = None
        current_trade.trailing_stop_loss = None
        db.session.commit()
    except Exception as e:
        logger.error(f"Exception in save_deactivated_trade: {str(e)}")
        send_admin_email(f'Exception in save_deactivated_trade', str(e))


def update_trailing_stop_loss(current_price, trailing_stop_price, atr):
    try:
        current_price = float(current_price)
        trailing_stop_price = float(trailing_stop_price)
        atr = float(atr)

        dynamic_trailing_stop = max(
            trailing_stop_price, 
            current_price * (1 - (0.5 * atr / current_price))
        )
        minimal_trailing_stop = current_price * 0.98

        return max(dynamic_trailing_stop, minimal_trailing_stop)

    except ValueError as e:
        logger.error(f"ValueError in update_trailing_stop_loss: {str(e)}")
        send_admin_email(f'ValueError in update_trailing_stop_loss', str(e))
        return trailing_stop_price
    except Exception as e:
        logger.error(f"Exception in update_trailing_stop_loss: {str(e)}")
        send_admin_email(f'Exception in update_trailing_stop_loss', str(e))
        return trailing_stop_price


def save_trailing_stop_loss(trailing_stop_price, current_trade):
    try:
        if current_trade:
            current_trade.trailing_stop_loss = trailing_stop_price
            db.session.commit()
    except Exception as e:
        logger.error(f"Exception in save_trailing_stop_loss: {str(e)}")
        send_admin_email(f'Exception in save_trailing_stop_loss', str(e))
        

def save_previous_price(price, current_trade):
    try:
        if current_trade:
            current_trade.previous_price = price
            db.session.commit()
    except Exception as e:
        logger.error(f"Exception in save_previous_price: {str(e)}")
        send_admin_email(f'Exception in save_previous_price', str(e))


def save_trade_to_history(current_trade, order_type, amount, buy_price, sell_price):
    try:
        trade = TradesHistory(
            bot_id=current_trade.id, 
            strategy=current_trade.bot_settings.strategy,
            amount=amount, 
            buy_price=buy_price,
            sell_price=sell_price
        )
        db.session.add(trade)
        db.session.commit()
        logger.info(
            f'Transaction {trade.id}: bot: {current_trade.id} {order_type}, strategy: {current_trade.bot_settings.strategy}'
            f'amount: {amount}, symbol: {current_trade.bot_settings.symbol}, timestamp: {trade.timestamp}'
        )
    except Exception as e:
        logger.error(f"Exception in save_trade_to_history: {str(e)}")
        send_admin_email(f'Exception in save_trade_to_history', str(e))
        db.session.rollback()