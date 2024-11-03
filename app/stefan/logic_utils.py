from .. import db
from ..models import TradesHistory, BotCurrentTrade
from ..utils.logging import logger
from ..utils.app_utils import send_admin_email
from .api_utils import (
    fetch_data,
    place_buy_order, 
    place_sell_order
)
from .scalping_logic import (
    calculate_scalp_indicators,
    check_scalping_buy_signal_v1,
    check_scalping_sell_signal_v1,
    check_scalping_buy_signal_v2,
    check_scalping_sell_signal_v2,
    check_scalping_buy_signal_v3,
    check_scalping_sell_signal_v3,
    check_scalping_buy_signal_v4,
    check_scalping_sell_signal_v4,
    check_scalping_buy_signal_v5,
    check_scalping_sell_signal_v5,
    check_scalping_buy_signal_v6,
    check_scalping_sell_signal_v6
)
from .swing_logic import (
    calculate_swing_indicators,
    check_swing_buy_signal_v1,
    check_swing_sell_signal_v1,
    check_swing_buy_signal_v2,
    check_swing_sell_signal_v2,
    check_swing_buy_signal_v3,
    check_swing_sell_signal_v3,
    check_swing_buy_signal_v4,
    check_swing_sell_signal_v4,
    check_swing_buy_signal_v5,
    check_swing_sell_signal_v5,
    check_swing_buy_signal_v6,
    check_swing_sell_signal_v6
)

def is_df_valid(df, bot_id):
    if df is None or df.empty or len(df) < 5:
        logger.trade(f'DataFrame is empty or too short for bot {bot_id}.')
        return False
    return True


def fetch_data_and_validate(symbol, interval, lookback_period, bot_id):
    df = fetch_data(symbol=symbol, interval=interval, lookback=lookback_period)
    if not is_df_valid(df, bot_id):
        return None
    return df


def handle_scalp_strategy(bot_settings, df):
    calculate_scalp_indicators(df, bot_settings)
    

def handle_swing_strategy(bot_settings, df):
    df_for_ma = fetch_data(bot_settings.symbol, interval="1d", lookback="200d")
    if not is_df_valid(df_for_ma, bot_settings.id):
        return
    calculate_swing_indicators(df, df_for_ma, bot_settings)


def get_current_price(df, bot_id):
    try:
        current_price = float(df['close'].iloc[-1])
        logger.trade(f'Current price for bot {bot_id} is: {current_price}')
        return current_price
    except IndexError as e:
        logger.error(f'IndexError in get_current_price bot {bot_id}: {str(e)}')
        send_admin_email(f'IndexError in get_current_price bot {bot_id}', str(e))
        return None
    except ValueError as e:
        logger.error(f'ValueError in get_current_price bot {bot_id}: {str(e)}')
        send_admin_email(f'ValueError in get_current_price bot {bot_id}', str(e))
        return None


def manage_trading_logic(bot_settings, current_trade, current_price, trailing_stop_pct, df):
    trailing_stop_price = float(current_trade.trailing_stop_loss)
    previous_price = float(current_trade.previous_price if current_trade.is_active else 0)
    price_rises = current_price >= previous_price if current_trade.is_active else False
    buy_signal, sell_signal = check_signals(bot_settings, df)

    if current_price <= trailing_stop_price:
        sell_signal = True
    
    if not current_trade.is_active and buy_signal:
        execute_buy_order(bot_settings, current_price, trailing_stop_pct)
    elif current_trade.is_active and sell_signal:
        execute_sell_order(bot_settings, current_trade, current_price)
    elif current_trade.is_active and price_rises:
        update_trailing_stop(bot_settings, current_trade, current_price, df['atr'].iloc[-1])
    else:
        logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} no trade signal.")
    
    logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} loop completed.")


def check_signals(bot_settings, df):
    indicators_ok = all([
        bot_settings.rsi_buy,
        bot_settings.rsi_sell,
        bot_settings.cci_buy,
        bot_settings.cci_sell,
        bot_settings.mfi_buy,
        bot_settings.mfi_sell,
        bot_settings.stoch_buy,
        bot_settings.stoch_sell,
        bot_settings.timeperiod
    ])

    if not indicators_ok:
        logger.trade(f'bot {bot_settings.id} {bot_settings.strategy} missing indicators in database')
        send_admin_email(f'Error starting bot {bot_settings.id}', f'Missing indicators in database for bot {bot_settings.id} {bot_settings.strategy}')
        return None, None
    
    if bot_settings.algorithm < 1 or bot_settings.algorithm > 6:
        logger.trade(f'Wrong algorithm {bot_settings.algorithm} declared for bot {bot_settings.id} {bot_settings.strategy}')
        send_admin_email(f'Wrong algorithm bot {bot_settings.id}', f'Wrong algorithm {bot_settings.algorithm} declared for bot {bot_settings.id} {bot_settings.strategy}')
        return None, None
    
    buy_signal, sell_signal = None, None
    
    if bot_settings.strategy == 'swing':
        if bot_settings.algorithm == 1:
            buy_signal = check_swing_buy_signal_v1(df, bot_settings)
            sell_signal = check_swing_sell_signal_v1(df, bot_settings)
        elif bot_settings.algorithm == 2:
            buy_signal = check_swing_buy_signal_v2(df, bot_settings)
            sell_signal = check_swing_sell_signal_v2(df, bot_settings)
        elif bot_settings.algorithm == 3:
            buy_signal = check_swing_buy_signal_v3(df, bot_settings)
            sell_signal = check_swing_sell_signal_v3(df, bot_settings)
        elif bot_settings.algorithm == 4:
            buy_signal = check_swing_buy_signal_v4(df, bot_settings)
            sell_signal = check_swing_sell_signal_v4(df, bot_settings)
        elif bot_settings.algorithm == 5:
            buy_signal = check_swing_buy_signal_v5(df, bot_settings)
            sell_signal = check_swing_sell_signal_v5(df, bot_settings)
        elif bot_settings.algorithm == 6:
            buy_signal = check_swing_buy_signal_v6(df, bot_settings)
            sell_signal = check_swing_sell_signal_v6(df, bot_settings)
    elif bot_settings.strategy == 'scalp':
        if bot_settings.algorithm == 1:
            buy_signal = check_scalping_buy_signal_v1(df, bot_settings)
            sell_signal = check_scalping_sell_signal_v1(df, bot_settings)
        elif bot_settings.algorithm == 2:
            buy_signal = check_scalping_buy_signal_v2(df, bot_settings)
            sell_signal = check_scalping_sell_signal_v2(df, bot_settings)
        elif bot_settings.algorithm == 3:
            buy_signal = check_scalping_buy_signal_v3(df, bot_settings)
            sell_signal = check_scalping_sell_signal_v3(df, bot_settings)
        elif bot_settings.algorithm == 4:
            buy_signal = check_scalping_buy_signal_v4(df, bot_settings)
            sell_signal = check_scalping_sell_signal_v4(df, bot_settings)
        elif bot_settings.algorithm == 5:
            buy_signal = check_scalping_buy_signal_v5(df, bot_settings)
            sell_signal = check_scalping_sell_signal_v5(df, bot_settings)
        elif bot_settings.algorithm == 6:
            buy_signal = check_scalping_buy_signal_v6(df, bot_settings)
            sell_signal = check_scalping_sell_signal_v6(df, bot_settings)
    return buy_signal, sell_signal


def execute_buy_order(bot_settings, current_price, trailing_stop_pct):
    logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} BUY signal.")
    buy_success, amount = place_buy_order(bot_settings.id)

    if buy_success:
        trailing_stop_price = current_price * (1 - trailing_stop_pct)
        update_current_trade(
            bot_id=bot_settings.id,
            is_active=True,
            amount=amount,
            current_price=current_price,
            previous_price=current_price,
            buy_price=current_price,
            trailing_stop_loss=trailing_stop_price
        )
        logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} buy process completed.")


def execute_sell_order(bot_settings, current_trade, current_price):
    logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} SELL signal.")
    sell_success, amount = place_sell_order(bot_settings.id)

    if sell_success:
        update_trade_history(
            bot_id=bot_settings.id,
            strategy=bot_settings.strategy,
            amount=amount,
            buy_price=current_trade.buy_price,
            sell_price=current_price
        )
        update_current_trade(
            bot_id=bot_settings.id,
            is_active=False,
            amount=0,
            current_price=0,
            previous_price=0,
            buy_price=0,
            trailing_stop_loss=0
        )
        logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} sell process completed.")


def update_trailing_stop(bot_settings, current_trade, current_price, atr_value):
    logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} price rises.")
    trailing_stop_price = update_trailing_stop_loss(
        current_price,
        float(current_trade.trailing_stop_loss),
        atr_value,
        bot_settings
    )
    update_current_trade(
        bot_id=bot_settings.id,
        previous_price=current_price,
        trailing_stop_loss=trailing_stop_price
    )
    logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} previous price and trailing stop loss updated.")


def round_to_step_size(amount, step_size):
    if step_size > 0:
        decimal_places = len(str(step_size).split('.')[-1])
        logger.trade(f'step_size: {step_size}, decimal_places: {decimal_places}')
        return round(amount, decimal_places)
    return amount


def update_trailing_stop_loss(current_price, trailing_stop_price, atr, bot_settings):
    try:
        current_price = float(current_price)
        trailing_stop_price = float(trailing_stop_price)
        atr = float(atr)
        
        dynamic_trailing_stop = max(
            trailing_stop_price, 
            current_price * (1 - (0.5 * atr / current_price))
        )
        
        minimal_trailing_stop = current_price * (1 - bot_settings.trailing_stop_pct)

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
        logger.trade(
            f'Transaction {trade.id}: bot: {bot_id}, strategy: {strategy}'
            f'amount: {amount}, symbol: {current_trade.bot_settings.symbol} saved in database.'
        )
    except Exception as e:
        db.session.rollback()
        logger.error(f"Exception in update_trade_history bot {bot_id}: {str(e)}")
        send_admin_email(f'Exception in update_trade_history bot {bot_id}', str(e))