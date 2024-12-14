from .. import db
from datetime import datetime as dt
from decimal import Decimal
from datetime import datetime
from ..models import TradesHistory, BotCurrentTrade
from ..utils.logging import logger
from ..utils.app_utils import (
    send_admin_email,
    send_trade_email
)
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
    check_scalping_sell_signal_v6,
    check_scalping_buy_signal_v7,
    check_scalping_sell_signal_v7,
    check_scalping_buy_signal_v8,
    check_scalping_sell_signal_v8,
    check_scalping_buy_signal_v9,
    check_scalping_sell_signal_v9
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
    check_swing_sell_signal_v6,
    check_swing_buy_signal_v7,
    check_swing_sell_signal_v7,
    check_swing_buy_signal_v8,
    check_swing_sell_signal_v8,
    check_swing_buy_signal_v9,
    check_swing_sell_signal_v9
)

def is_df_valid(df, bot_id):
    if df is None or df.empty or len(df) < 2:
        logger.trade(f'DataFrame is empty or too short for bot {bot_id}.')
        return False
    return True


def fetch_data_and_validate(symbol, interval, lookback_period, bot_id):
    df = fetch_data(
        symbol=symbol, 
        interval=interval, 
        lookback=lookback_period
        )
    if not is_df_valid(df, bot_id):
        return None
    return df


def handle_scalp_strategy(bot_settings, df):
    calculate_scalp_indicators(df, bot_settings)
    

def handle_swing_strategy(bot_settings, df):
    df_for_ma = fetch_data(
        bot_settings.symbol, 
        interval="1d", 
        lookback="200d"
        )
    if not is_df_valid(df_for_ma, bot_settings.id):
        return
    calculate_swing_indicators(df, df_for_ma, bot_settings)


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


def manage_trading_logic(bot_settings, current_trade, current_price, df):
    try:
        use_stop_loss = bot_settings.use_stop_loss
        use_trailing_stop_loss = bot_settings.use_trailing_stop_loss
        stop_loss_price = float(current_trade.stop_loss_price)
        
        use_take_profit = bot_settings.use_stop_loss
        take_profit_price = float(current_trade.take_profit_price)
        
        previous_price = float(current_trade.previous_price if current_trade.is_active else 0)
        latest_data = df.iloc[-1]
        previous_data = df.iloc[-2]
        atr = df['atr'].iloc[-1]
        
        price_rises = current_price > previous_price if current_trade.is_active else False
        price_drops = current_price < previous_price if current_trade.is_active else False
        
        trend = check_trend(df, bot_settings)
        averages = calculate_averages(df, bot_settings)
        
        buy_signal, sell_signal = check_signals(
            bot_settings, 
            df, 
            trend, 
            averages, 
            latest_data, 
            previous_data
            )
        
        if not current_trade.is_active:
            if buy_signal:
                execute_buy_order(bot_settings, current_price, atr)
            else:
                logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} no buy signal.")
            
        elif current_trade.is_active:
            stop_loss_activated = False
            take_profit_activated = False
            full_sell_signal = False
        
            if use_stop_loss and current_price <= stop_loss_price:
                logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} stop loss activated.")
                stop_loss_activated = True
            if use_take_profit and current_price >= take_profit_price:
                logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} take profit activated.")
                take_profit_activated = True
        
            full_sell_signal = stop_loss_activated or take_profit_activated or sell_signal
            if bot_settings.sell_signal_only_stop_loss_or_take_profit:
                full_sell_signal = stop_loss_activated or take_profit_activated
        
            if full_sell_signal:
                execute_sell_order(bot_settings, current_trade, current_price)
            elif price_rises:
                if use_trailing_stop_loss:
                    update_trailing_stop(bot_settings, current_trade, current_price, atr)  
                else:
                    handle_price_rises(bot_settings, current_price)
            elif price_drops:
                handle_price_drops(bot_settings, current_price)
                                
        logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} loop completed.")
        
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in manage_trading_logic: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in manage_trading_logic', str(e))


def calculate_averages(df, bot_settings):
    try:
        averages = {}
        
        average_mappings = {
            'avg_volume': ('volume', bot_settings.avg_volume_period),
            'avg_rsi': ('rsi', bot_settings.avg_rsi_period),
            'avg_cci': ('cci', bot_settings.avg_cci_period),
            'avg_mfi': ('mfi', bot_settings.avg_mfi_period),
            'avg_atr': ('atr', bot_settings.avg_atr_period),
            'avg_stoch_rsi_k': ('stoch_rsi_k', bot_settings.avg_stoch_rsi_period),
            'avg_macd': ('macd', bot_settings.avg_macd_period),
            'avg_macd_signal': ('macd_signal', bot_settings.avg_macd_period),
            'avg_stoch_k': ('stoch_k', bot_settings.avg_stoch_period),
            'avg_stoch_d': ('stoch_d', bot_settings.avg_stoch_period),
            'avg_ema_fast': ('ema_fast', bot_settings.avg_ema_period),
            'avg_ema_slow': ('ema_slow', bot_settings.avg_ema_period),
            'avg_plus_di': ('plus_di', bot_settings.avg_di_period),
            'avg_minus_di': ('minus_di', bot_settings.avg_di_period),
        }

        for avg_name, (column, period) in average_mappings.items():
            averages[avg_name] = df[column].iloc[-period:].mean()

        return averages

    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in calculate_averages: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in calculate_averages', str(e))
        return None

    
def check_trend(df, bot_settings):
    try:
        latest_data = df.iloc[-1]
        
        avg_adx_period = bot_settings.avg_adx_period
        avg_adx = df['adx'].iloc[-avg_adx_period:].mean()
        adx_trend = (float(latest_data['adx']) > float(bot_settings.adx_strong_trend) or float(latest_data['adx']) > float(avg_adx))
        
        avg_di_period = bot_settings.avg_di_period
        avg_plus_di = df['plus_di'].iloc[-avg_di_period:].mean()
        avg_minus_di = df['minus_di'].iloc[-avg_di_period:].mean()
        di_difference_increasing = (abs(float(latest_data['plus_di']) - float(latest_data['minus_di'])) > 
                                    abs(float(avg_plus_di) - float(avg_minus_di)))
        
        significant_move = (float(latest_data['high']) - float(latest_data['low']) > float(latest_data['atr']))

        uptrend = (float(latest_data['plus_di']) > float(avg_minus_di) and 
                adx_trend and 
                di_difference_increasing and 
                float(latest_data['rsi']) < float(bot_settings.rsi_sell) and 
                float(latest_data['plus_di']) > float(bot_settings.adx_weak_trend) and
                significant_move)

        downtrend = (float(latest_data['plus_di']) < float(avg_minus_di) and 
                    adx_trend and 
                    di_difference_increasing and 
                    float(latest_data['minus_di']) > float(bot_settings.adx_weak_trend) and 
                    float(latest_data['rsi']) > float(bot_settings.rsi_buy) and
                    significant_move)

        horizontal = (latest_data['adx'] < avg_adx or avg_adx < float(bot_settings.adx_weak_trend) or 
                    abs(float(latest_data['plus_di']) - float(latest_data['minus_di'])) < float(bot_settings.adx_no_trend))
        
        if uptrend:
            logger.trade(f"Bot {bot_settings.id} {bot_settings.strategy} have BULLISH UPTREND")
            return 'uptrend'
        elif downtrend:
            logger.trade(f"Bot {bot_settings.id} {bot_settings.strategy} have BEARISH DOWNTREND")
            return 'downtrend'
        elif horizontal:
            logger.trade(f"Bot {bot_settings.id} {bot_settings.strategy} have HORIZONTAL TREND")
            return 'horizontal'
        else:
            logger.trade(f"Bot {bot_settings.id} {bot_settings.strategy} trend unidentified")
            return 'none'
        
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in check_trend: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in check_trend', str(e))
        return 'none'
    
    
def get_signal_functions(strategy, algorithm):
    try:
        strategy_prefix = 'swing' if strategy == 'swing' else 'scalping'
        buy_func_name = f"check_{strategy_prefix}_buy_signal_v{algorithm}"
        sell_func_name = f"check_{strategy_prefix}_sell_signal_v{algorithm}"
        
        buy_func = globals().get(buy_func_name)
        sell_func = globals().get(sell_func_name)
        
        if not buy_func or not sell_func:
            raise ValueError(f"Functions for strategy {strategy}, algorytm {algorithm} not found.")
        
        return buy_func, sell_func

    except Exception as e:
        logger.error(f"Bot strategy: {strategy} algprithm: {algorithm} Exception in get_signal_functions: {str(e)}")
        send_admin_email(f'Bot strategy: {strategy} algprithm: {algorithm} Exception in get_signal_functions', str(e))
        return None, None


def get_signals(df, bot_settings, trend, averages, latest_data, previous_data):
    try:
        buy_func, sell_func = get_signal_functions(bot_settings.strategy, bot_settings.algorithm)
        
        buy_signal = buy_func(df, bot_settings, trend, averages, latest_data, previous_data)
        sell_signal = sell_func(df, bot_settings, trend, averages, latest_data, previous_data)
        
        return buy_signal, sell_signal

    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in check_signals: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in check_signals', str(e))
        return None, None


def check_signals(bot_settings, df, trend, averages, latest_data, previous_data):
    try:
        indicators_ok = all([
            bot_settings.rsi_buy,
            bot_settings.rsi_sell,
            bot_settings.cci_buy,
            bot_settings.cci_sell,
            bot_settings.mfi_buy,
            bot_settings.mfi_sell,
            bot_settings.stoch_buy,
            bot_settings.stoch_sell
        ])

        if not indicators_ok:
            logger.trade(f'bot {bot_settings.id} {bot_settings.strategy} missing indicators in database')
            send_admin_email(f'Error starting bot {bot_settings.id}', f'Missing indicators in database for bot {bot_settings.id} {bot_settings.strategy}')
            return None, None
        
        if bot_settings.algorithm < 1 or bot_settings.algorithm > 9:
            logger.trade(f'Wrong algorithm {bot_settings.algorithm} declared for bot {bot_settings.id} {bot_settings.strategy}')
            send_admin_email(f'Wrong algorithm bot {bot_settings.id}', f'Wrong algorithm {bot_settings.algorithm} declared for bot {bot_settings.id} {bot_settings.strategy}')
            return None, None
        
        buy_signal, sell_signal = get_signals(df, bot_settings, trend, averages, latest_data, previous_data)
        
        return buy_signal, sell_signal
    
    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in check_signals: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in check_signals', str(e))
        return None, None


def execute_buy_order(bot_settings, current_price, atr_value):
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
                
            update_current_trade(
                bot_id=bot_settings.id,
                is_active=True,
                amount=amount,
                current_price=current_price,
                previous_price=current_price,
                buy_price=current_price,
                stop_loss_price=stop_loss_price,
                take_profit_price=take_profit_price,
                buy_timestamp=dt.now()
            )
            logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} buy process completed.")
            
            send_trade_email(
                f"StafanCryptoTradingBot buy process report.\n"
                f"{formatted_now}\n\n"
                f"Bot {bot_settings.id} {bot_settings.strategy} {bot_settings.symbol}\n\n"
                f"algorithm {bot_settings.algorithm}\n"
                f"{bot_settings.comment}\n\n",
                (
                    f"Bot {bot_settings.id} {bot_settings.strategy} {bot_settings.symbol} "
                    f"buy process.\n"
                    f"amount: {amount}\n"
                    f"buy_price: {current_price}\n"
                    f"stop_loss_price: {stop_loss_price}\n"
                    f"take_profit_price: {take_profit_price}\n"
                    f"buy_timestamp: {dt.now()}\n"
                    f"buy_success: {buy_success}"
                ),
            )

    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in execute_buy_order: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in execute_buy_order', str(e))


def execute_sell_order(bot_settings, current_trade, current_price):
    now = datetime.now()
    formatted_now = now.strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} SELL signal.")
        sell_success, amount = place_sell_order(bot_settings.id)

        if sell_success:
            update_trade_history(
                bot_settings=bot_settings,
                strategy=bot_settings.strategy,
                amount=amount,
                buy_price=current_trade.buy_price,
                sell_price=current_price,
                stop_loss_price=current_trade.stop_loss_price,
                take_profit_price=current_trade.take_profit_price,
                price_rises_counter=current_trade.price_rises_counter,
                buy_timestamp=current_trade.buy_timestamp,
                current_price=current_price,
            )
                        
            update_current_trade(
                bot_id=bot_settings.id,
                is_active=False,
                amount=0,
                current_price=0,
                previous_price=0,
                buy_price=0,
                stop_loss_price=0,
                take_profit_price=0,
                reset_price_rises_counter=True,
            )
            logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} sell process completed.")
            
            send_trade_email(
                f"StafanCryptoTradingBot buy process report.\n"
                f"{formatted_now}\n\n"
                f"Bot {bot_settings.id} {bot_settings.strategy} {bot_settings.symbol}\n\n"
                f"algorithm {bot_settings.algorithm}\n"
                f"{bot_settings.comment}\n\n",
                (
                    f"Bot {bot_settings.id} {bot_settings.strategy} {bot_settings.symbol} "
                    f"sell process.\n"
                    f"amount: {amount}\n"
                    f"buy_price: {current_trade.buy_price}\n"
                    f"sell_price: {current_price}\n"
                    f"stop_loss_price: {current_trade.stop_loss_price}\n"
                    f"take_profit_price: {current_trade.take_profit_price}\n"
                    f"price_rises_counter: {current_trade.price_rises_counter}\n"
                    f"buy_timestamp: {current_trade.buy_timestamp}\n"
                    f"sell_timestamp: {dt.now()}\n"
                    f"sell_success: {sell_success}"
                ),
            )

    except Exception as e:
        logger.error(f"Bot {bot_settings.id} Exception in execute_sell_order: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in execute_sell_order', str(e))


def update_trailing_stop(bot_settings, current_trade, current_price, atr_value):
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
        
        update_current_trade(
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
        
        
def handle_price_rises(bot_settings, current_price):
    update_current_trade(bot_id=bot_settings.id, current_price=current_price, previous_price=current_price)
    logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} price_rises. previous price updated.")
    
    
def handle_price_drops(bot_settings, current_price):
    update_current_trade(bot_id=bot_settings.id, current_price=current_price)
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
        

def update_stop_loss(current_price, trailing_stop_price, bot_settings):
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
    
    
def update_atr_trailing_stop_loss(current_price, trailing_stop_price, atr, bot_settings):
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
                
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Bot {bot_id} Exception in update_current_trade: {str(e)}")
            send_admin_email(f'Bot {bot_id} Exception in update_current_trade', str(e))
    

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
            buy_timestamp=buy_timestamp,
            sell_timestamp=dt.now()
        )
        db.session.add(trade)
        db.session.commit()
        logger.trade(
            f'Transaction {trade.id}: bot: {bot_id}, strategy: {strategy}'
            f'amount: {amount}, symbol: {current_trade.bot_settings.symbol} saved in database.'
        )
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Bot {bot_settings.id} Exception in update_trade_history bot {bot_id}: {str(e)}")
        send_admin_email(f'Bot {bot_settings.id} Exception in update_trade_history bot {bot_id}', str(e))