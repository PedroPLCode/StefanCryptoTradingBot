from datetime import datetime, timedelta
from app.models import TradesHistory, BotSettings
from ..utils.logging import logger
from ..utils.exception_handlers import exception_handler
from ..utils.trades_utils import calculate_profit_percentage


@exception_handler()
def generate_trade_report(period):
    """
    Generates a trade report for a specified period.

    This function retrieves trade data for all bots from the last 24 hours or 7 days,
    formats it into a readable report, and returns the report as a string.

    Args:
        period (str): The time period for the report. Accepted values are:
            - '24h': Last 24 hours
            - '7d': Last 7 days

    Returns:
        str: A formatted trade report containing trade details for all bots.

    Raises:
        ValueError: If an unsupported period is provided.
        Logs any exceptions encountered and notifies the admin.
    """
    now = datetime.now()
    formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")

    if period == "24h":
        last_period = now - timedelta(hours=24)
    elif period == "7d":
        last_period = now - timedelta(days=7)
    else:
        raise ValueError("Unsupported period specified. Use '24h' or '7d'.")

    all_bots = BotSettings.query.all()

    report_data = (
        f"StafanCryptoTradingBot {'daily' if period == '24h' else 'requested'} trades report.\n"
        f"{formatted_now}\n\n"
        f"All trades in last {period}.\n\n"
    )

    for single_bot in all_bots:
        trades_in_period = (
            TradesHistory.query.filter(TradesHistory.bot_id == single_bot.id)
            .filter(TradesHistory.sell_timestamp >= last_period)
            .order_by(TradesHistory.sell_timestamp.asc())
            .all()
        )

        total_trades = len(trades_in_period)

        report_data += (
            f"--\n\nBot {single_bot.id} "
            f"{single_bot.strategy} {single_bot.symbol}.\n"
            f"comment: {single_bot.comment}\n"
        )

        if total_trades == 0:
            report_data += f"\nNo transactions in last {period}.\n\n"
        else:
            report_data += f"\nTransactions count in last {period}: {total_trades}\n\n"

            for trade in trades_in_period:
                profit_percentage = calculate_profit_percentage(
                    trade.buy_price, trade.sell_price
                )
                report_data += (
                    f"id: {trade.trade_id}\n"
                    f"buy_timestamp: {trade.buy_timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"sell_timestamp: {trade.sell_timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"amount: {trade.amount} {trade.bot_settings.symbol[:3]}\n"
                    f"buy_price: {trade.buy_price:.2f} {trade.bot_settings.symbol[-4:]}\n"
                    f"sell_price: {trade.sell_price:.2f} {trade.bot_settings.symbol[-4:]}\n"
                    f"stop_loss_price: {trade.stop_loss_price}\n"
                    f"take_profit_price: {trade.take_profit_price}\n"
                    f"price_rises_counter: {trade.price_rises_counter}\n"
                    f"stop_loss_activated: {trade.stop_loss_activated}\n"
                    f"take_profit_activated: {trade.take_profit_activated}\n"
                    f"trailing_take_profit_activated: {trade.trailing_take_profit_activated}\n"
                    f"profit_percentage: {profit_percentage:.2f}%\n\n"
                )
    return report_data
