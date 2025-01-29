from .. import db
import pandas as pd
from datetime import datetime as dt
from decimal import Decimal
from datetime import datetime
from ..models import BotSettings, TradesHistory, BotCurrentTrade
from ..utils.logging import logger
from ..utils.app_utils import (
    send_admin_email,
    send_trade_email,
    update_technical_analysis_data
)
from .api_utils import (
    fetch_data,
    place_buy_order, 
    place_sell_order
)
from .calc_utils import (
    calculate_ta_indicators,
    calculate_ta_averages,
    check_ta_trend
)
from .buy_signals import check_classic_ta_buy_signal
from .sell_signals import check_classic_ta_sell_signal
from ..mariola.mariola_predict import check_ml_trade_signal

def is_df_valid(df, bot_id):
    if df is None or df.empty or len(df) < 2:
        logger.trade(f'DataFrame is empty or too short for bot {bot_id}.')
        return False
    return True


def fetch_data_and_validate(symbol, interval, lookback_period, bot_id):
    try:
        df = fetch_data(
            symbol=symbol, 
            interval=interval, 
            lookback=lookback_period
            )
        if not is_df_valid(df, bot_id):
            return None
        return df
    
    except Exception as e:
        logger.error(f"Bot {bot_id} Exception in fetch_data_and_validate: {str(e)}")
        send_admin_email(f'Bot {bot_id} Exception in fetch_data_and_validate', str(e))
        return None


def get_current_price(df, bot_id):
    try:
        current_price = float(df['close'].iloc[-1])
        logger.trade(f'Current price for bot {bot_id} is: {current_price}')
        return current_price
    
    except IndexError as e:
        logger.error(f'Bot {bot_id} IndexError in get_current_price: {str(e)}')
        send_admin_email(f'Bot {bot_id} IndexError in get_current_price', str(e))
        return None
    except ValueError as e:
        logger.error(f'Bot {bot_id} ValueError in get_current_price: {str(e)}')
        send_admin_email(f'Bot {bot_id} ValueError in get_current_price', str(e))
        return None
    except Exception as e:
        logger.error(f"Bot {bot_id} Exception in fetch_data_and_validate: {str(e)}")
        send_admin_email(f'Bot {bot_id} Exception in fetch_data_and_validate', str(e))
        return None


def manage_trading_logic(bot_settings, current_trade, current_price, df):
    try:
        use_stop_loss = bot_settings.use_stop_loss
        use_trailing_stop_loss = bot_settings.use_trailing_stop_loss
        stop_loss_price = float(current_trade.stop_loss_price)
        
        use_take_profit = bot_settings.use_take_profit and current_trade.use_take_profit
        use_trailing_take_profit = bot_settings.use_trailing_take_profit
        take_profit_price = float(current_trade.take_profit_price)
        
        calculate_ta_indicators(
            df, 
            bot_settings
            )   
        
        previous_price = float(current_trade.previous_price if current_trade.is_active else 0)
        latest_data = df.iloc[-1]
        previous_data = df.iloc[-2]
        atr = latest_data['atr']
        
        price_rises = current_price > previous_price if current_trade.is_active else False
        price_drops = current_price < previous_price if current_trade.is_active else False
        price_hits_stop_loss = current_price <= stop_loss_price
        price_hits_take_profit = current_price >= take_profit_price
        
        trend = check_ta_trend(
            df, 
            bot_settings
            )
        
        averages = calculate_ta_averages(
            df, 
            bot_settings
            )

        if not current_trade.is_active:
            
            buy_signal = check_signal(
                'buy', 
                df, 
                bot_settings, 
                trend, 
                averages, 
                latest_data, 
                previous_data
                )

            if isinstance(buy_signal, pd.Series):
                buy_signal = buy_signal.all()

            if buy_signal:
                execute_buy_order(
                    bot_settings, 
                    current_price, 
                    atr
                    )
            else:
                logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} no buy signal.")
            
        elif current_trade.is_active:
            
            sell_signal = check_signal(
                'sell',
                df, 
                bot_settings, 
                trend, 
                averages, 
                latest_data, 
                previous_data
                )
            
            if isinstance(sell_signal, pd.Series):
                sell_signal = sell_signal.all()
    
            stop_loss_activated = False
            take_profit_activated = False
            full_sell_signal = False
        
            if price_hits_stop_loss and use_stop_loss:
                logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} stop_loss activated.")
                stop_loss_activated = True
                
            if price_hits_take_profit and use_take_profit:
                if use_trailing_take_profit and not current_trade.trailing_take_profit_activated:
                        activate_trailing_take_profit(
                            bot_settings, 
                            current_trade, 
                            current_price, 
                            atr
                            )
                else:
                    logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} take_profit activated.")
                    take_profit_activated = True
        
            full_sell_signal = stop_loss_activated or take_profit_activated or sell_signal
            if bot_settings.sell_signal_only_stop_loss_or_take_profit:
                full_sell_signal = stop_loss_activated or take_profit_activated
        
            if full_sell_signal:
                execute_sell_order(
                    bot_settings, 
                    current_trade, 
                    current_price, 
                    stop_loss_activated, 
                    take_profit_activated
                    )
            elif price_rises:
                if use_trailing_stop_loss:
                    update_trailing_stop(
                        bot_settings, 
                        current_trade, 
                        current_price, 
                        atr
                        )  
                else:
                    handle_price_rises(
                        bot_settings, 
                        current_price
                        )
            elif price_drops:
                handle_price_drops(
                    bot_settings, 
                    current_price
                    )
                
        update_technical_analysis_data(
            bot_settings, 
            df,
            trend, 
            averages, 
            latest_data
            )
                                
        logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} loop completed.")
        
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in manage_trading_logic: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in manage_trading_logic', str(e))


def check_signal(
    signal_type,
    df,
    bot_settings,
    trend,
    averages,
    latest_data,
    previous_data
    ):
    try:
        
        if bot_settings.use_technical_analysis:
            if signal_type == 'buy':
                return check_classic_ta_buy_signal(
                    df, 
                    bot_settings, 
                    trend, 
                    averages, 
                    latest_data, 
                    previous_data
                    )
            elif signal_type == 'sell':
                return check_classic_ta_sell_signal(
                    df, 
                    bot_settings,
                    trend, 
                    averages, 
                    latest_data, 
                    previous_data
                    )
                
            raise ValueError(f"Unsupported signal_type: {signal_type}")
        
        elif bot_settings.use_machine_learning:
            return check_ml_trade_signal(
                df,
                signal_type,
                bot_settings
                )
            
        else:
            logger.error(f"Bot {bot_settings.id} not use_technical_analysis and not use_machine_learning")
            return False

    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in check_signal ({signal_type}): {str(e)}")
        send_admin_email(f"Bot {bot_settings.id} Exception in check_signal ({signal_type})", str(e))
        return None
    
    
def execute_buy_order(
    bot_settings, 
    current_price, 
    atr_value
    ):
    now = datetime.now()
    formatted_now = now.strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} BUY signal.")
        buy_success, amount = place_buy_order(bot_settings.id)

        if buy_success:
            
            stop_loss_price = 0
            take_profit_price = 0
            
            if bot_settings.use_stop_loss:
                stop_loss_price = update_stop_loss(
                    current_price, 
                    0, 
                    bot_settings
                )
                
                if bot_settings.trailing_stop_with_atr:
                    stop_loss_price = update_atr_trailing_stop_loss(
                        current_price, 
                        0, 
                        atr_value,
                        bot_settings
                    )
                
            if bot_settings.use_take_profit:
                take_profit_price = calculate_take_profit(
                    current_price, 
                    bot_settings
                )
                
                if bot_settings.take_profit_with_atr:
                    take_profit_price = calculate_atr_take_profit(
                        current_price, 
                        atr_value, 
                        bot_settings
                    )
                
            current_trade = update_current_trade(
                bot_id=bot_settings.id,
                is_active=True,
                amount=amount,
                current_price=current_price,
                previous_price=current_price,
                buy_price=current_price,
                stop_loss_price=stop_loss_price,
                take_profit_price=take_profit_price,
                trailing_take_profit_activated=False,
                use_take_profit=True,
                buy_timestamp=dt.now()
            )
            
            bot_settings = change_bot_settings(
                bot_id=bot_settings.id,
                use_trailing_stop_loss=False,
                trailing_stop_with_atr=False,
                trailing_stop_atr_calc=2,
                stop_loss_pct=0.02,
            )
            
            logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} buy process completed.")
            send_trade_email(f"Bot {bot_settings.id} execute_buy_order report.", f"StafanCryptoTradingBotBot execute_buy_order report.\n{formatted_now}\n\nBot {bot_settings.id} {bot_settings.strategy} {bot_settings.symbol}.\ncomment: {bot_settings.comment}\n\namount: {amount}\nbuy_price: {current_price}\nstop_loss_price: {stop_loss_price}\ntake_profit_price: {take_profit_price}\nbuy_timestamp: {formatted_now}\nbuy_success: {buy_success}")

    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in execute_buy_order: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in execute_buy_order', str(e))


def execute_sell_order(
    bot_settings, 
    current_trade, 
    current_price, 
    stop_loss_activated, 
    take_profit_activated
    ):
    now = datetime.now()
    formatted_now = now.strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} SELL signal.")
        sell_success, amount = place_sell_order(bot_settings.id)
        
        trade_buy_price = current_trade.buy_price
        trade_stop_loss_price = current_trade.stop_loss_price
        trade_take_profit_price = current_trade.take_profit_price
        trade_price_rises_counter = current_trade.price_rises_counter
        trade_trailing_take_profit_activated = current_trade.trailing_take_profit_activated
        trade_buy_timestamp = current_trade.buy_timestamp.strftime('%Y-%m-%d %H:%M:%S')
        is_trade_profit_negative = trade_buy_price > current_price

        if sell_success:
            trade = update_trade_history(
                bot_settings=bot_settings,
                strategy=bot_settings.strategy,
                amount=amount,
                buy_price=current_trade.buy_price,
                sell_price=current_price,
                stop_loss_price=current_trade.stop_loss_price,
                take_profit_price=current_trade.take_profit_price,
                price_rises_counter=current_trade.price_rises_counter,
                stop_loss_activated=stop_loss_activated,
                take_profit_activated=take_profit_activated,
                trailing_take_profit_activated=current_trade.trailing_take_profit_activated,
                buy_timestamp=current_trade.buy_timestamp,
                current_price=current_price,
            )
                        
            current_trade = update_current_trade(
                bot_id=bot_settings.id,
                is_active=False,
                amount=0,
                current_price=0,
                previous_price=0,
                buy_price=0,
                stop_loss_price=0,
                take_profit_price=0,
                trailing_take_profit_activated=False,
                use_take_profit=True,
                reset_price_rises_counter=True,
            )
            
            bot_settings = change_bot_settings(
                bot_id=bot_settings.id,
                use_trailing_stop_loss=False,
                trailing_stop_with_atr=False,
                trailing_stop_atr_calc=2,
                stop_loss_pct=0.02,
            )
            
            if is_trade_profit_negative and bot_settings.use_suspension_after_negative_trade:
                suspend_after_negative_trade(bot_settings)
        
            logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} sell process completed.")
            send_trade_email(f"Bot {bot_settings.id} execute_sell_order report.", f"StafanCryptoTradingBot execute_sell_order report.\n{formatted_now}\n\nBot {bot_settings.id} {bot_settings.strategy} {bot_settings.symbol}.\ncomment: {bot_settings.comment}\n\namount: {amount}\nbuy_price: {trade_buy_price}\nsell_price: {current_price}\nstop_loss_price: {trade_stop_loss_price}\ntake_profit_price: {trade_take_profit_price}\nprice_rises_counter: {trade_price_rises_counter}\nstop_loss_activated: {stop_loss_activated}\ntake_profit_activated: {take_profit_activated}\ntrailing_take_profit_activated: {trade_trailing_take_profit_activated}\nbuy_timestamp: {trade_buy_timestamp}\nsell_timestamp: {formatted_now}\nsell_success: {sell_success}")

    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in execute_sell_order: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in execute_sell_order', str(e))


def activate_trailing_take_profit(
    bot_settings, 
    current_trade, 
    current_price, 
    atr_value
    ):
    now = datetime.now()
    formatted_now = now.strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        
        bot_settings = change_bot_settings(
                bot_id=bot_settings.id,
                use_stop_loss=True,
                use_trailing_stop_loss=True,
                trailing_stop_with_atr=True,
                trailing_stop_atr_calc=1,
                stop_loss_pct=0.01,
            )
        
        trailing_stop_price = update_atr_trailing_stop_loss(
                current_price, 
                float(current_trade.stop_loss_price), 
                atr_value, bot_settings
            )
        
        current_trade = update_current_trade(
            bot_id=bot_settings.id,
            current_price=current_price,
            previous_price=current_price,
            stop_loss_price=trailing_stop_price,
            price_rises=True,
            trailing_take_profit_activated=True,
            use_take_profit=False,
        )
        
        logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} trailing take profit activated.")
        send_trade_email(f"Bot {bot_settings.id} activate_trailing_take_profit report.", f"StafanCryptoTradingBot activate_trailing_take_profit report.\n{formatted_now}\n\nBot {bot_settings.id} {bot_settings.strategy} {bot_settings.symbol}.\ncomment: {bot_settings.comment}\n\nTrailing take profit has been activated.\n\namount: {current_trade.amount}\nbuy_price: {current_trade.buy_price}\nbuy_timestamp: {current_trade.buy_timestamp.strftime('%Y-%m-%d %H:%M:%S')}\ncurrent_price: {current_price}\nstop_loss_price: {current_trade.stop_loss_price}\ntake_profit_price: {current_trade.take_profit_price}\nprice_rises_counter: {current_trade.price_rises_counter}")
        
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in activate_trailing_take_profit: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in activate_trailing_take_profit', str(e))
                   
                        
def update_trailing_stop(
    bot_settings, 
    current_trade, 
    current_price, 
    atr_value
    ):
    try:
        logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} price rises.")
        
        trailing_stop_price = update_stop_loss(
            current_price, 
            float(current_trade.stop_loss_price), 
            bot_settings
        )
        
        if bot_settings.trailing_stop_with_atr:
            trailing_stop_price = update_atr_trailing_stop_loss(
                current_price, 
                float(current_trade.stop_loss_price), 
                atr_value, bot_settings
            )
        
        current_trade = update_current_trade(
            bot_id=bot_settings.id,
            current_price=current_price,
            previous_price=current_price,
            stop_loss_price=trailing_stop_price,
            price_rises=True
        )
        logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} previous price and trailing stop loss updated.")
        
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in update_trailing_stop: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in update_trailing_stop', str(e))
        
        
def handle_price_rises(
    bot_settings, 
    current_price
    ):
    
    current_trade = update_current_trade(
        bot_id=bot_settings.id, 
        current_price=current_price, 
        previous_price=current_price, 
        price_rises=True
    )
    logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} price_rises. previous price updated.")
    
    
def handle_price_drops(
    bot_settings, 
    current_price
    ):
    
    current_trade = update_current_trade(
        bot_id=bot_settings.id, 
        current_price=current_price
    )
    logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} price_drops. previous price not updated.")


def round_down_to_step_size(amount, step_size):
    
    try:
        if step_size > 0:
            amount_decimal = Decimal(str(amount))
            step_size_decimal = Decimal(str(step_size))
            rounded_amount = (amount_decimal // step_size_decimal) * step_size_decimal
            return float(rounded_amount)
        return float(amount)
    
    except Exception as e:
            logger.error(f"Exception in round_down_to_step_size: {str(e)}")
            send_admin_email(f'Exception in round_down_to_step_size', str(e))
            return float(amount)
        

def update_stop_loss(
    current_price, 
    trailing_stop_price, 
    bot_settings
    ):
    
    try:
        trailing_stop_price = float(trailing_stop_price)
        current_price = float(current_price)
        new_stop_price = current_price * (1 - bot_settings.stop_loss_pct)

        return max(trailing_stop_price, new_stop_price)

    except ValueError as e:
        logger.error(f"Bot {bot_settings.id} ValueError in update_stop_loss: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} ValueError in update_stop_loss', str(e))
        return trailing_stop_price
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in update_stop_loss: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in update_stop_loss', str(e))
        return trailing_stop_price
    
    
def update_atr_trailing_stop_loss(
    current_price, 
    trailing_stop_price, 
    atr, 
    bot_settings
    ):
    
    try:
        current_price = float(current_price)
        trailing_stop_price = float(trailing_stop_price)
        atr = float(atr)
        
        dynamic_trailing_stop = current_price * (1 - (bot_settings.trailing_stop_atr_calc * atr / current_price))
        minimal_trailing_stop = current_price * (1 - bot_settings.stop_loss_pct)
        new_trailing_stop = max(dynamic_trailing_stop, minimal_trailing_stop)

        return max(trailing_stop_price, new_trailing_stop)

    except ValueError as e:
        logger.error(f"Bot {bot_settings.id} ValueError in update_atr_trailing_stop_loss: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} ValueError in update_atr_trailing_stop_loss', str(e))
        return trailing_stop_price
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in update_atr_trailing_stop_loss: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in update_atr_trailing_stop_loss', str(e))
        return trailing_stop_price


def calculate_take_profit(current_price, bot_settings):
    
    try:
        current_price = float(current_price)

        if not (0 < bot_settings.take_profit_pct < 1):
            raise ValueError("bot_settings.take_profit_pct must be between 0 and 1.")

        take_profit_price = current_price + (current_price * (bot_settings.take_profit_pct))
        logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} "
                     f"Calculated take profit: current_price={current_price}, "
                     f"take_profit_pct={bot_settings.take_profit_pct}, "
                     f"take_profit_price={take_profit_price}")
        return take_profit_price

    except ValueError as e:
        logger.error(f"Bot {bot_settings.id} ValueError in calculate_take_profit: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} ValueError in calculate_take_profit', str(e))
        return None
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in calculate_take_profit: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in calculate_take_profit', str(e))
        return None
    
    
def calculate_atr_take_profit(current_price, atr, bot_settings):
    
    try:
        current_price = float(current_price)
        atr = float(atr)

        if bot_settings.take_profit_atr_calc <= 0:
            raise ValueError("bot_settings.take_profit_atr_calc must be a positive value.")
        if atr <= 0:
            raise ValueError("ATR must be a positive value.")

        take_profit_price = current_price + (atr * bot_settings.take_profit_atr_calc)
        logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} "
                    f"Calculated ATR-based take profit: {take_profit_price}, "
                    f"current_price={current_price}, atr={atr}, multiplier={bot_settings.take_profit_atr_calc}")
        return take_profit_price

    except ValueError as e:
        logger.error(f"Bot {bot_settings.id} ValueError in calculate_atr_take_profit: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} ValueError in calculate_atr_take_profit', str(e))
        return None
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in calculate_atr_take_profit: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in calculate_atr_take_profit', str(e))
        return None
    

def update_current_trade(
    bot_id=None, 
    is_active=None, 
    amount=None, 
    buy_price=None, 
    current_price=None, 
    previous_price=None, 
    stop_loss_price=None,
    take_profit_price=None,
    trailing_take_profit_activated=None,
    use_take_profit=None,
    buy_timestamp=None,
    price_rises=None,
    reset_price_rises_counter=None
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
            if stop_loss_price != None:
                current_trade.stop_loss_price = stop_loss_price
            if take_profit_price != None:
                current_trade.take_profit_price = take_profit_price
            if buy_timestamp != None:
                current_trade.buy_timestamp = buy_timestamp
            if price_rises != None:
                current_counter = current_trade.price_rises_counter
                updated_counter = current_counter + 1
                current_trade.price_rises_counter = updated_counter
            if reset_price_rises_counter != None:
                current_trade.price_rises_counter = 0
            if trailing_take_profit_activated != None:
                current_trade.trailing_take_profit_activated = trailing_take_profit_activated
            if use_take_profit != None:
                current_trade.use_take_profit = use_take_profit
                
            db.session.commit()
            
            return current_trade
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Bot {bot_id} Exception in update_current_trade: {str(e)}")
            send_admin_email(f'Bot {bot_id} Exception in update_current_trade', str(e))
    

def change_bot_settings(
    bot_id=None, 
    use_stop_loss=None,
    use_trailing_stop_loss=None, 
    trailing_stop_with_atr=None, 
    trailing_stop_atr_calc=None, 
    stop_loss_pct=None, 
    ):
    
    if bot_id:
        
        try:
            bot_settings = BotSettings.query.filter_by(id=bot_id).first()
            
            if use_stop_loss != None:
                bot_settings.use_stop_loss = use_stop_loss
            if use_trailing_stop_loss != None:
                bot_settings.use_trailing_stop_loss = use_trailing_stop_loss
            if trailing_stop_with_atr != None:
                bot_settings.trailing_stop_with_atr = trailing_stop_with_atr
            if trailing_stop_atr_calc != None:
                bot_settings.trailing_stop_atr_calc = trailing_stop_atr_calc
            if stop_loss_pct != None:
                bot_settings.stop_loss_pct = stop_loss_pct
                
            db.session.commit()
            
            return bot_settings
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Bot {bot_id} Exception in change_bot_settings: {str(e)}")
            send_admin_email(f'Bot {bot_id} Exception in change_bot_settings', str(e))
            
            
def next_trade_id(bot_id):
    
    try:
        max_existing_trade_id = (
            db.session.query(db.func.max(TradesHistory.trade_id))
            .filter_by(bot_id=bot_id)
            .scalar()
        )
        return (max_existing_trade_id or 0) + 1

    except Exception as e:
        logger.error(f"Bot {bot_id} Exception in next_trade_id: {str(e)}")
        send_admin_email(f'Bot {bot_id} Exception in next_trade_id', str(e))
        return None

                        
def update_trade_history(
    bot_settings, 
    strategy, 
    amount, 
    buy_price, 
    sell_price,
    stop_loss_price,
    take_profit_price,
    price_rises_counter,
    stop_loss_activated,
    take_profit_activated,
    trailing_take_profit_activated,
    buy_timestamp,
    current_price
    ):
    from .api_utils import get_account_balance
        
    try:
        bot_id = bot_settings.id
        symbol = bot_settings.symbol
        cryptocoin_symbol = symbol[:3]
        stablecoin_symbol = symbol[-4:]

        balance = get_account_balance(bot_id, [stablecoin_symbol, cryptocoin_symbol])
        stablecoin_balance = float(balance.get(stablecoin_symbol, 0))
        cryptocoin_balance = float(balance.get(cryptocoin_symbol, 0))
        total_stablecoin_balance = float(stablecoin_balance + (cryptocoin_balance * current_price))
    
        current_trade = BotCurrentTrade.query.filter_by(id=bot_id).first()
        trade = TradesHistory(
            bot_id=bot_id,
            trade_id=next_trade_id(bot_id),
            strategy=strategy,
            amount=amount, 
            buy_price=buy_price,
            sell_price=sell_price,
            stablecoin_balance=total_stablecoin_balance,
            stop_loss_price=stop_loss_price,
            take_profit_price=take_profit_price,
            price_rises_counter=price_rises_counter,
            stop_loss_activated=stop_loss_activated,
            take_profit_activated=take_profit_activated,
            trailing_take_profit_activated=trailing_take_profit_activated,
            buy_timestamp=buy_timestamp,
            sell_timestamp=dt.now()
        )
        db.session.add(trade)
        db.session.commit()
        
        logger.trade(
            f'Transaction {trade.id}: bot: {bot_id}, strategy: {strategy}'
            f'amount: {amount}, symbol: {current_trade.bot_settings.symbol} saved in database.'
        )
        
        return trade
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Bot {bot_settings.id} Exception in update_trade_history: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in update_trade_history', str(e))
        
        
def is_bot_suspended(bot_settings):
    
    try:
        
        if bot_settings.is_suspended_after_negative_trade:
            if bot_settings.suspension_cycles_remaining > 0:
                bot_settings.suspension_cycles_remaining -= 1
                db.session.commit()
                return True
            
            bot_settings.is_suspended_after_negative_trade = False
            bot_settings.suspension_cycles_remaining = 0
            db.session.commit()
            
            now = datetime.now()
            formatted_now = now.strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"Bot {bot_settings.id} suspension after negative trade finished.")
            send_trade_email(f"Bot {bot_settings.id} suspend_after_negative_trade report.", f"StafanCryptoTradingBotBot suspend_after_negative_trade report.\n{formatted_now}\n\nBot {bot_settings.id} {bot_settings.strategy} {bot_settings.symbol}.\ncomment: {bot_settings.comment}\n\nSuspension after negative trade finished.\nBot {bot_settings.id} is back in operation")
        
        return False

    except Exception as e:
        db.session.rollback()
        logger.error(f"Bot {bot_settings.id} Exception in is_bot_suspended: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in is_bot_suspended', str(e))
        return False


def suspend_after_negative_trade(bot_settings):
    
    try:
        
        now = datetime.now()
        formatted_now = now.strftime('%Y-%m-%d %H:%M:%S') 
        
        bot_settings.is_suspended_after_negative_trade = True
        bot_settings.suspension_cycles_remaining = bot_settings.cycles_of_suspension_after_negative_trade
        db.session.commit()
            
        logger.info(f"Bot {bot_settings.id} suspended after negative trade. Cycles remaininig: {bot_settings.cycles_of_suspension_after_negative_trade}.")
        send_trade_email(f"Bot {bot_settings.id} suspend_after_negative_trade report.", f"StafanCryptoTradingBotBot suspend_after_negative_trade report.\n{formatted_now}\n\nBot {bot_settings.id} {bot_settings.strategy} {bot_settings.symbol}.\ncomment: {bot_settings.comment}\n\nBot {bot_settings.id} is suspended after negative trade.\nCycles of suspension: {bot_settings.cycles_of_suspension_after_negative_trade}\nCycles remaininig: {bot_settings.cycles_of_suspension_after_negative_trade}")
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Bot {bot_settings.id} Exception in suspend_after_negative_trade: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in suspend_after_negative_trade', str(e))