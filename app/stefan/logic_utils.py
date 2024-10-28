from .. import db
from ..models import TradesHistory, BotCurrentTrade
from ..utils.logging import logger
from ..utils.app_utils import send_admin_email

def round_to_step_size(amount, step_size):
    if step_size > 0:
        return round(amount / step_size) * step_size
    return amount


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


def update_current_trade(
    bot_id=None, 
    is_active=None, 
    amount=None, 
    buy_price=None, 
    current_price=None, 
    previous_price=None, 
    trailing_stop_loss=None
    ):
    
    if bot_id:
        
        try:
            current_trade = BotCurrentTrade.query.filter_by(id=bot_id).first()
            
            if is_active != None:
                current_trade.is_active = is_active
            if amount != None:
                current_trade.amount = amount
            if buy_price != None:
                current_trade.buy_price = buy_price
            if current_price != None:
                current_trade.current_price = current_price
            if previous_price != None:
                current_trade.previous_price = previous_price
            if trailing_stop_loss != None:
                current_trade.trailing_stop_loss = trailing_stop_loss
                
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Exception in update_current_trade bot {bot_id}: {str(e)}")
            send_admin_email(f'Exception in update_current_trade bot {bot_id}', str(e))
    
                        
def update_trade_history(
    bot_id, 
    strategy, 
    amount, 
    buy_price, 
    sell_price
    ):
    
    try:
        current_trade = BotCurrentTrade.query.filter_by(id=bot_id).first()
        trade = TradesHistory(
            bot_id=bot_id,
            strategy=strategy,
            amount=amount, 
            buy_price=buy_price,
            sell_price=sell_price
        )
        db.session.add(trade)
        db.session.commit()
        logger.info(
            f'Transaction {trade.id}: bot: {bot_id}, strategy: {strategy}'
            f'amount: {amount}, symbol: {current_trade.bot_settings.symbol}, timestamp: {trade.timestamp}'
        )
    except Exception as e:
        db.session.rollback()
        logger.error(f"Exception in update_trade_history bot {bot_id}: {str(e)}")
        send_admin_email(f'Exception in update_trade_history bot {bot_id}', str(e))