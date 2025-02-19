from datetime import datetime as dt, timedelta
from .. import db
from app.models import TradesHistory, BotSettings, BotCurrentTrade
from .logging import logger
from ..utils.exception_handlers import exception_handler
from ..utils.email_utils import send_admin_email


@exception_handler(db_rollback=True)
def clear_old_trade_history():
    """
    Clears old trade history based on each bot's configured retention period.

    This function iterates through all bot settings and removes trade records
    older than the configured `days_period_to_clean_history` value. It logs
    the process, sends a summary report via email, and handles any errors.

    Process:
        - Retrieves all bot settings.
        - Checks if `days_period_to_clean_history` is valid.
        - Deletes trades older than the specified period.
        - Logs the number of deleted trades.
        - Sends an email report summarizing the cleaning process.

    Returns:
        None

    Raises:
        Logs any exceptions encountered and notifies the admin.
    """
    now = dt.now()
    formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
    today = now.strftime("%Y-%m-%d")

    all_bot_settings = BotSettings.query.all()
    errors = []
    summary_logs = []

    for bot_settings in all_bot_settings:
        days_to_clean_history = bot_settings.days_period_to_clean_history

        if (
            not days_to_clean_history
            or not isinstance(days_to_clean_history, int)
            or days_to_clean_history <= 0
        ):
            error_message = f"Bot {bot_settings.id} has invalid 'days_period_to_clean_history': {days_to_clean_history}"
            logger.warning(error_message)
            errors.append(error_message)
            continue

        period_to_clean = now - timedelta(days=days_to_clean_history)

        deleted_count = (
            db.session.query(TradesHistory)
            .filter(
                TradesHistory.bot_id == bot_settings.id,
                TradesHistory.sell_timestamp < period_to_clean,
            )
            .delete(synchronize_session=False)
        )

        log_message = ""
        days_count_string = (
            f"{days_to_clean_history} day"
            if days_to_clean_history == 1
            else f"{days_to_clean_history} days"
        )
        if deleted_count > 0:
            log_message = (
                f"Bot {bot_settings.id}: {deleted_count} trades "
                f"older than {days_count_string} cleared succesfully."
            )
        else:
            log_message = (
                f"Bot {bot_settings.id}: No trades older than "
                f"{days_count_string} found. Nothing to clean."
            )

        logger.trade(log_message)
        summary_logs.append(log_message)

    db.session.commit()

    summary_message = (
        f"StafanCryptoTradingBot daily cleaning report.\n"
        f"{formatted_now}\n\nDays to clean history: {days_to_clean_history}\n\n"
    )
    error_message = (
        f"StafanCryptoTradingBot daily cleaning.\n"
        f"Errors during trade history cleaning.\n"
        f"{formatted_now}\n\n"
    )

    if summary_logs:
        summary_message += "\n".join(summary_logs)
        logger.trade("Trade history cleaning completed:\n" + summary_message)
        send_admin_email(f"{today} Daily Cleaning Report", summary_message)

    if errors:
        error_message += "\n".join(errors)
        logger.error("Errors during trade history cleaning:\n" + error_message)
        send_admin_email(
            f"{today} Errors in Daily Trade History Cleaning", error_message
        )


@exception_handler()
def next_trade_id(bot_id):
    """
    Generates the next trade ID for a given bot by querying the maximum existing trade ID
    from the `TradesHistory` table and incrementing it by 1. If no trades exist, it returns 1.

    Args:
        bot_id (int): The ID of the bot for which the trade ID is to be generated.

    Returns:
        int: The next trade ID for the specified bot.
        None: If an exception occurs during the process.
    """
    max_existing_trade_id = (
        db.session.query(db.func.max(TradesHistory.trade_id))
        .filter_by(bot_id=bot_id)
        .scalar()
    )
    return (max_existing_trade_id or 0) + 1


@exception_handler(db_rollback=True)
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
    current_price,
):
    """
    Updates the trade history for a given bot by creating a new `TradesHistory` entry with
    the provided trade details. The trade is then committed to the database.

    Args:
        bot_settings (BotSettings): The settings of the bot making the trade.
        strategy (str): The trading strategy used.
        amount (float): The amount of the asset traded.
        buy_price (float): The price at which the asset was bought.
        sell_price (float): The price at which the asset was sold.
        stop_loss_price (float): The price at which stop loss is triggered.
        take_profit_price (float): The price at which take profit is triggered.
        price_rises_counter (int): The number of price rises before the trade.
        stop_loss_activated (bool): Flag indicating if the stop loss was triggered.
        take_profit_activated (bool): Flag indicating if the take profit was triggered.
        trailing_take_profit_activated (bool): Flag indicating if the trailing take profit was activated.
        buy_timestamp (datetime): The timestamp when the asset was bought.
        current_price (float): The current price of the asset.

    Returns:
        TradesHistory: The created trade history record.
        None: If an exception occurs during the process.
    """
    from ..stefan.api_utils import get_account_balance

    bot_id = bot_settings.id
    symbol = bot_settings.symbol
    cryptocoin_symbol = symbol[:3]
    stablecoin_symbol = symbol[-4:]

    balance = get_account_balance(bot_id, [stablecoin_symbol, cryptocoin_symbol])
    stablecoin_balance = float(balance.get(stablecoin_symbol, 0))
    cryptocoin_balance = float(balance.get(cryptocoin_symbol, 0))
    total_stablecoin_balance = float(
        stablecoin_balance + (cryptocoin_balance * current_price)
    )

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
        sell_timestamp=dt.now(),
    )
    db.session.add(trade)
    db.session.commit()

    logger.trade(
        f"Transaction {trade.id}: bot: {bot_id}, strategy: {strategy}"
        f"amount: {amount}, symbol: {current_trade.bot_settings.symbol} saved in database."
    )

    return trade
