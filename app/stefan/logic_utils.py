from .. import db
import pandas as pd
from datetime import datetime as dt
from datetime import datetime
from ..models import BotSettings, BotCurrentTrade
from ..utils.logging import logger
from ..utils.exception_handlers import exception_handler
from ..utils.bots_utils import suspend_after_negative_trade
from ..utils.email_utils import send_trade_email
from ..utils.trades_utils import update_technical_analysis_data
from .buy_signals import check_classic_ta_buy_signal
from .sell_signals import check_classic_ta_sell_signal
from ..mariola.predict import check_ml_trade_signal
from .api_utils import fetch_data, place_buy_order, place_sell_order
from .calc_utils import (
    calculate_ta_indicators,
    calculate_ta_averages,
    check_ta_trend,
    get_atr_value,
)


@exception_handler()
def is_df_valid(df, bot_info):
    """
    Checks if a DataFrame is valid for use in the bot's trading logic.

    This function validates that the provided DataFrame is not empty, has at least two rows,
    and is not None. If the DataFrame fails these conditions, it logs a message and returns False.

    Args:
        df (pandas.DataFrame): The DataFrame to validate, containing market data.
        bot_id (int): The ID of the bot, used for logging purposes.

    Returns:
        bool: True if the DataFrame is valid, False otherwise.
    """
    if df is None or df.empty:
        logger.trade(f"DataFrame is empty or too short for bot {bot_info.id}.")
        return False
    return True


@exception_handler()
def fetch_data_and_validate(symbol, interval, lookback_period, bot_id):
    """
    Fetches market data and validates the resulting DataFrame.

    This function fetches the market data using the specified symbol, interval, and lookback period,
    then checks if the fetched DataFrame is valid using the `is_df_valid` function.
    If the DataFrame is invalid, it returns None.

    Args:
        symbol (str): The trading pair symbol, e.g., 'BTCUSDC'.
        interval (str): The interval for the market data (e.g., '1m', '5m').
        lookback_period (int): The lookback period for fetching historical data.
        bot_id (int): The ID of the bot, used for logging purposes.

    Returns:
        pandas.DataFrame or None: The validated DataFrame containing market data, or None if invalid.

    Raises:
        Exception: If any error occurs during the data fetching process.
    """
    df = fetch_data(symbol=symbol, interval=interval, lookback=lookback_period)
    if not is_df_valid(df, bot_id):
        return None
    return df


@exception_handler()
def get_current_price(df, bot_id):
    """
    Retrieves the current market price from the provided DataFrame.

    This function extracts the current market price from the last row of the DataFrame, assuming
    that the DataFrame has a 'close' column. If any error occurs during this process, it logs the error
    and returns None.

    Args:
        df (pandas.DataFrame): The DataFrame containing market data with a 'close' column.
        bot_id (int): The ID of the bot, used for logging purposes.

    Returns:
        float or None: The current market price as a float, or None if there was an error.

    Raises:
        IndexError: If the DataFrame is empty or does not have the expected structure.
        ValueError: If there is a conversion issue while extracting the price.
        Exception: If any other unexpected error occurs.
    """
    current_price = float(df["close"].iloc[-1])
    logger.trade(f"Current price for bot {bot_id} is: {current_price}")
    return current_price


@exception_handler()
def manage_trading_logic(bot_settings, current_trade, current_price, df_fetched):
    """
    Manages the core trading logic of the bot, including buying, selling, stop-loss, take-profit,
    trailing stop-loss, and technical analysis updates.

    This function handles the following trading actions based on the bot's settings and the current market data:
    - Checks for buy and sell signals using technical analysis indicators.
    - Executes buy or sell orders depending on the signal and market conditions.
    - Activates stop-loss or take-profit mechanisms if the price hits the respective levels.
    - Updates trailing stop-loss based on price movements.
    - Performs technical analysis (e.g., trend, averages, ATR) and updates relevant data.
    - Handles price rises and drops according to the trading strategy.

    Args:
        bot_settings (object): Configuration settings for the trading bot, including stop-loss,
                                take-profit, and other strategy settings.
        current_trade (object): The current trade object, which contains details about the ongoing trade
                                 (e.g., stop-loss price, take-profit price, previous price, etc.).
        current_price (float): The latest market price of the trading pair.
        df_fetched (pandas.DataFrame): A DataFrame containing the market data and technical indicators (e.g., ATR, trend, etc.).

    Returns:
        None: This function does not return any value, but performs trading actions like executing orders,
              updating settings, and logging trade information.

    Raises:
        Exception: If any unexpected error occurs during the execution of the trading logic.
    """
    use_stop_loss = bot_settings.use_stop_loss
    use_trailing_stop_loss = bot_settings.use_trailing_stop_loss
    stop_loss_price = float(current_trade.stop_loss_price)

    use_take_profit = bot_settings.use_take_profit and current_trade.use_take_profit
    use_trailing_take_profit = bot_settings.use_trailing_take_profit
    take_profit_price = float(current_trade.take_profit_price)

    df_raw = df_fetched.copy() if bot_settings.use_machine_learning else None

    df_calculated = calculate_ta_indicators(df_fetched, bot_settings)

    previous_price = float(
        current_trade.previous_price if current_trade.is_active else 0
    )

    price_rises = current_price > previous_price if current_trade.is_active else False
    price_drops = current_price < previous_price if current_trade.is_active else False
    price_hits_stop_loss = current_price <= stop_loss_price
    price_hits_take_profit = current_price >= take_profit_price

    trend = check_ta_trend(df_calculated, bot_settings)

    averages = calculate_ta_averages(df_calculated, bot_settings)

    atr_value = get_atr_value(df_calculated, bot_settings)

    if not current_trade.is_active:

        buy_signal = check_signal(
            "buy", df_calculated, df_raw, bot_settings, trend, averages
        )

        if isinstance(buy_signal, pd.Series):
            buy_signal = buy_signal.all()

        if buy_signal:
            execute_buy_order(bot_settings, current_price, atr_value)
        else:
            logger.trade(
                f"bot {bot_settings.id} {bot_settings.strategy} no buy signal."
            )

    elif current_trade.is_active:

        sell_signal = check_signal(
            "sell", df_calculated, df_raw, bot_settings, trend, averages
        )

        if isinstance(sell_signal, pd.Series):
            sell_signal = sell_signal.all()

        stop_loss_activated = False
        take_profit_activated = False
        full_sell_signal = False

        if price_hits_stop_loss and use_stop_loss:
            logger.trade(
                f"bot {bot_settings.id} {bot_settings.strategy} stop_loss activated."
            )
            stop_loss_activated = True

        if price_hits_take_profit and use_take_profit:
            if (
                use_trailing_take_profit
                and not current_trade.trailing_take_profit_activated
            ):
                activate_trailing_take_profit(
                    bot_settings, current_trade, current_price, atr_value
                )
            else:
                logger.trade(
                    f"bot {bot_settings.id} {bot_settings.strategy} take_profit activated."
                )
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
                take_profit_activated,
            )
        elif price_rises:
            if use_trailing_stop_loss:
                update_trailing_stop(
                    bot_settings, current_trade, current_price, atr_value
                )
            else:
                handle_price_rises(bot_settings, current_price)
        elif price_drops:
            handle_price_drops(bot_settings, current_price)

    update_technical_analysis_data(bot_settings, df_calculated, trend, averages)

    logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} loop completed.")


@exception_handler(default_return=False)
def check_signal(signal_type, df_calculated, df_raw, bot_settings, trend, averages):
    """
    Checks whether a buy or sell signal is triggered based on technical analysis or machine learning.

    Args:
        signal_type (str): Type of the signal to check ('buy' or 'sell').
        df (pandas.DataFrame): DataFrame containing historical market data.
        bot_settings (object): Settings of the trading bot.
        trend (str): The current market trend.
        averages (dict): Calculated technical analysis averages.

    Returns:
        bool: True if the signal condition is met, False otherwise.
        None: If an error occurs during signal checking.

    Raises:
        ValueError: If an unsupported signal type is provided.
    """
    if bot_settings.use_technical_analysis:
        if signal_type == "buy":
            return check_classic_ta_buy_signal(
                df_calculated, bot_settings, trend, averages
            )
        elif signal_type == "sell":
            return check_classic_ta_sell_signal(
                df_calculated, bot_settings, trend, averages
            )

        raise ValueError(f"Unsupported signal_type: {signal_type}")

    elif bot_settings.use_machine_learning:
        return check_ml_trade_signal(df_raw, signal_type, bot_settings)

    else:
        logger.error(
            f"Bot {bot_settings.id} not use_technical_analysis and not use_machine_learning"
        )
        return False


@exception_handler()
def execute_buy_order(bot_settings, current_price, atr_value):
    """
    Executes a buy order for the trading bot, including setting stop loss, take profit,
    and trailing stop loss prices based on the bot settings and ATR value.

    Args:
        bot_settings (object): Settings of the trading bot.
        current_price (float): The current market price for the asset.
        atr_value (float): The Average True Range (ATR) value used for calculating stop loss and take profit.

    Returns:
        None: Executes the buy order and updates the trade status.

    Raises:
        Exception: If an error occurs during the buy order execution process.
    """
    from .calc_utils import (
        calculate_take_profit,
        calculate_atr_take_profit,
        calculate_stop_loss,
        calculate_atr_trailing_stop_loss,
    )

    now = datetime.now()
    formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")

    logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} BUY signal.")
    buy_success, amount = place_buy_order(bot_settings.id)

    if buy_success:
        stop_loss_price = 0
        take_profit_price = 0

        if bot_settings.use_stop_loss:
            stop_loss_price = calculate_stop_loss(current_price, 0, bot_settings)

            if bot_settings.trailing_stop_with_atr:
                stop_loss_price = calculate_atr_trailing_stop_loss(
                    current_price, 0, atr_value, bot_settings
                )

        if bot_settings.use_take_profit:
            take_profit_price = calculate_take_profit(current_price, bot_settings)

            if bot_settings.take_profit_with_atr:
                take_profit_price = calculate_atr_take_profit(
                    current_price, atr_value, bot_settings
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
            buy_timestamp=dt.now(),
        )

        bot_settings = change_bot_settings(
            bot_id=bot_settings.id,
            use_trailing_stop_loss=False,
            trailing_stop_with_atr=False,
            trailing_stop_atr_calc=2,
            stop_loss_pct=0.02,
        )

        logger.trade(
            f"bot {bot_settings.id} {bot_settings.strategy} buy process completed."
        )
        send_trade_email(
            f"Bot {bot_settings.id} execute_buy_order report.",
            f"StafanCryptoTradingBotBot execute_buy_order report.\n{formatted_now}\n\nBot {bot_settings.id} {bot_settings.strategy} {bot_settings.symbol}.\ncomment: {bot_settings.comment}\n\namount: {amount}\nbuy_price: {current_price}\nstop_loss_price: {stop_loss_price}\ntake_profit_price: {take_profit_price}\nbuy_timestamp: {formatted_now}\nbuy_success: {buy_success}",
        )


@exception_handler()
def execute_sell_order(
    bot_settings,
    current_trade,
    current_price,
    stop_loss_activated,
    take_profit_activated,
):
    """
    Executes a sell order for the trading bot, including updating trade history and handling
    stop loss, take profit, and other conditions.

    Args:
        bot_settings (object): Settings of the trading bot.
        current_trade (object): The current active trade.
        current_price (float): The current market price for the asset.
        stop_loss_activated (bool): Whether the stop loss condition has been met.
        take_profit_activated (bool): Whether the take profit condition has been met.

    Returns:
        None: Executes the sell order and updates the trade status.

    Raises:
        Exception: If an error occurs during the sell order execution process.
    """
    from ..utils.history_utils import update_trade_history

    now = datetime.now()
    formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")

    logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} SELL signal.")
    sell_success, amount = place_sell_order(bot_settings.id)

    trade_buy_price = current_trade.buy_price
    trade_stop_loss_price = current_trade.stop_loss_price
    trade_take_profit_price = current_trade.take_profit_price
    trade_price_rises_counter = current_trade.price_rises_counter
    trade_trailing_take_profit_activated = current_trade.trailing_take_profit_activated
    trade_buy_timestamp = current_trade.buy_timestamp.strftime("%Y-%m-%d %H:%M:%S")
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

        if (
            is_trade_profit_negative
            and bot_settings.use_suspension_after_negative_trade
        ):
            suspend_after_negative_trade(bot_settings)

        logger.trade(
            f"bot {bot_settings.id} {bot_settings.strategy} sell process completed."
        )
        send_trade_email(
            f"Bot {bot_settings.id} execute_sell_order report.",
            f"StafanCryptoTradingBot execute_sell_order report.\n{formatted_now}\n\nBot {bot_settings.id} {bot_settings.strategy} {bot_settings.symbol}.\ncomment: {bot_settings.comment}\n\namount: {amount}\nbuy_price: {trade_buy_price}\nsell_price: {current_price}\nstop_loss_price: {trade_stop_loss_price}\ntake_profit_price: {trade_take_profit_price}\nprice_rises_counter: {trade_price_rises_counter}\nstop_loss_activated: {stop_loss_activated}\ntake_profit_activated: {take_profit_activated}\ntrailing_take_profit_activated: {trade_trailing_take_profit_activated}\nbuy_timestamp: {trade_buy_timestamp}\nsell_timestamp: {formatted_now}\nsell_success: {sell_success}",
        )


@exception_handler()
def activate_trailing_take_profit(
    bot_settings, current_trade, current_price, atr_value
):
    """
    Activates the trailing take profit for the bot. This function adjusts the stop loss
    based on the ATR value and updates the current trade with the new stop loss value.

    Args:
        bot_settings (object): The settings of the trading bot.
        current_trade (object): The current trade being executed.
        current_price (float): The current price of the asset.
        atr_value (float): The current Average True Range (ATR) value used for calculating trailing stop loss.

    Returns:
        None: Updates the current trade and bot settings without returning a value.

    Raises:
        Exception: If an error occurs during the process, it is logged and reported.
    """
    from .calc_utils import calculate_atr_trailing_stop_loss

    now = datetime.now()
    formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")

    bot_settings = change_bot_settings(
        bot_id=bot_settings.id,
        use_stop_loss=True,
        use_trailing_stop_loss=True,
        trailing_stop_with_atr=True,
        trailing_stop_atr_calc=1,
        stop_loss_pct=0.01,
    )

    trailing_stop_price = calculate_atr_trailing_stop_loss(
        current_price, float(current_trade.stop_loss_price), atr_value, bot_settings
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

    logger.trade(
        f"bot {bot_settings.id} {bot_settings.strategy} trailing take profit activated."
    )
    send_trade_email(
        f"Bot {bot_settings.id} activate_trailing_take_profit report.",
        f"StafanCryptoTradingBot activate_trailing_take_profit report.\n{formatted_now}\n\nBot {bot_settings.id} {bot_settings.strategy} {bot_settings.symbol}.\ncomment: {bot_settings.comment}\n\nTrailing take profit has been activated.\n\namount: {current_trade.amount}\nbuy_price: {current_trade.buy_price}\nbuy_timestamp: {current_trade.buy_timestamp.strftime('%Y-%m-%d %H:%M:%S')}\ncurrent_price: {current_price}\nstop_loss_price: {current_trade.stop_loss_price}\ntake_profit_price: {current_trade.take_profit_price}\nprice_rises_counter: {current_trade.price_rises_counter}",
    )


@exception_handler()
def update_trailing_stop(bot_settings, current_trade, current_price, atr_value):
    """
    Updates the trailing stop loss for the current trade. This function recalculates
    the stop loss based on the current price and ATR value, and updates the trade's stop loss accordingly.

    Args:
        bot_settings (object): The settings of the trading bot.
        current_trade (object): The current trade being executed.
        current_price (float): The current price of the asset.
        atr_value (float): The current Average True Range (ATR) value used for adjusting the trailing stop loss.

    Returns:
        None: Updates the current trade's stop loss without returning a value.

    Raises:
        Exception: If an error occurs during the process, it is logged and reported.
    """
    from .calc_utils import calculate_stop_loss, calculate_atr_trailing_stop_loss

    logger.trade(f"bot {bot_settings.id} {bot_settings.strategy} price rises.")

    trailing_stop_price = calculate_stop_loss(
        current_price, float(current_trade.stop_loss_price), bot_settings
    )

    if bot_settings.trailing_stop_with_atr:
        trailing_stop_price = calculate_atr_trailing_stop_loss(
            current_price, float(current_trade.stop_loss_price), atr_value, bot_settings
        )

    current_trade = update_current_trade(
        bot_id=bot_settings.id,
        current_price=current_price,
        previous_price=current_price,
        stop_loss_price=trailing_stop_price,
        price_rises=True,
    )
    logger.trade(
        f"bot {bot_settings.id} {bot_settings.strategy} previous price and trailing stop loss updated."
    )


@exception_handler()
def handle_price_rises(bot_settings, current_price):
    """
    Handles the event when the price rises. Updates the current trade with the new price
    and marks that the price has risen.

    Args:
        bot_settings (object): The settings of the trading bot.
        current_price (float): The current price of the asset.

    Returns:
        None: Updates the current trade without returning a value.

    Raises:
        Exception: If an error occurs during the update process, it is logged and reported.
    """
    current_trade = update_current_trade(
        bot_id=bot_settings.id,
        current_price=current_price,
        previous_price=current_price,
        price_rises=True,
    )
    logger.trade(
        f"bot {bot_settings.id} {bot_settings.strategy} price_rises. previous price updated."
    )


@exception_handler()
def handle_price_drops(bot_settings, current_price):
    """
    Handles the event when the price drops. Updates the current trade without changing the
    previous price, as the drop does not trigger any specific action.

    Args:
        bot_settings (object): The settings of the trading bot.
        current_price (float): The current price of the asset.

    Returns:
        None: Updates the current trade without returning a value.

    Raises:
        Exception: If an error occurs during the update process, it is logged and reported.
    """
    current_trade = update_current_trade(
        bot_id=bot_settings.id, current_price=current_price
    )
    logger.trade(
        f"bot {bot_settings.id} {bot_settings.strategy} price_drops. previous price not updated."
    )


@exception_handler(db_rollback=True)
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
    reset_price_rises_counter=None,
):
    """
    Updates the current trade details in the database based on the provided parameters.
    It will modify the values of the trade fields such as price, stop loss, take profit, etc.

    Args:
        bot_id (int): The ID of the bot associated with the current trade.
        is_active (bool, optional): Indicates whether the trade is active or not.
        amount (float, optional): The amount of the asset involved in the trade.
        buy_price (float, optional): The price at which the asset was purchased.
        current_price (float, optional): The current price of the asset.
        previous_price (float, optional): The previous price of the asset.
        stop_loss_price (float, optional): The price at which the stop loss is set.
        take_profit_price (float, optional): The price at which the take profit is set.
        trailing_take_profit_activated (bool, optional): Indicates if trailing take profit is activated.
        use_take_profit (bool, optional): Whether to use take profit for the current trade.
        buy_timestamp (datetime, optional): The timestamp when the asset was bought.
        price_rises (bool, optional): Indicates whether the price has risen.
        reset_price_rises_counter (bool, optional): Whether to reset the price rise counter.

    Returns:
        current_trade (object): The updated current trade object.

    Raises:
        Exception: If an error occurs during the update process, it is logged and reported.
    """
    if bot_id:
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
            current_trade.trailing_take_profit_activated = (
                trailing_take_profit_activated
            )
        if use_take_profit != None:
            current_trade.use_take_profit = use_take_profit

        db.session.commit()

        return current_trade


@exception_handler(db_rollback=True)
def change_bot_settings(
    bot_id=None,
    use_stop_loss=None,
    use_trailing_stop_loss=None,
    trailing_stop_with_atr=None,
    trailing_stop_atr_calc=None,
    stop_loss_pct=None,
):
    """
    Changes the settings of the trading bot based on the provided parameters. Updates the bot's
    stop loss, trailing stop loss, ATR-based trailing stop, and other configuration options.

    Args:
        bot_id (int): The ID of the bot whose settings are to be changed.
        use_stop_loss (bool, optional): Whether to use stop loss for the bot.
        use_trailing_stop_loss (bool, optional): Whether to use trailing stop loss for the bot.
        trailing_stop_with_atr (bool, optional): Whether to use ATR-based trailing stop.
        trailing_stop_atr_calc (float, optional): The ATR calculation method for the trailing stop.
        stop_loss_pct (float, optional): The percentage for stop loss.

    Returns:
        bot_settings (object): The updated bot settings object.

    Raises:
        Exception: If an error occurs during the settings update process, it is logged and reported.
    """
    if bot_id:
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
