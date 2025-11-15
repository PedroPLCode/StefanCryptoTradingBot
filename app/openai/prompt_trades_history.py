from ..models import BotSettings
from ..utils.exception_handlers import exception_handler


@exception_handler()
def get_bot_last_trades_history(bot_settings) -> str:
    """
    Generate a clean and structured summary of the bot's last trades
    to be used inside a GPT prompt.

    Args:
        bot_settings (BotSettings): The bot configuration.

    Returns:
        str: Formatted summary for GPT or an empty string if no trades exist.
    """
    bot = BotSettings.query.get(bot_settings.id)
    limit = bot.last_trades_limit or 5

    trades = sorted(
        bot.bot_trades_history,
        key=lambda t: t.buy_timestamp or t.id,
        reverse=True
    )[:limit]

    if not trades:
        return "\n\n"

    lines = []
    lines.append(f"\n\nRecent {len(trades)} trades summary:\n")

    for t in trades:
        if t.sell_price and t.buy_price and t.buy_price > 0:
            pnl_pct = ((t.sell_price - t.buy_price) / t.buy_price) * 100
            pnl_str = f"{pnl_pct:.2f}%"
        else:
            pnl_str = "N/A"
        buy_time = t.buy_timestamp.strftime("%Y-%m-%d %H:%M:%S") if t.buy_timestamp else "N/A"
        sell_time = t.sell_timestamp.strftime("%Y-%m-%d %H:%M:%S") if t.sell_timestamp else "N/A"

        lines.append(
            f"- Trade {t.trade_id or t.id}\n"
            f"  Buy:  {t.buy_price} @ {buy_time}\n"
            f"  Sell: {t.sell_price} @ {sell_time}\n"
            f"  Amount: {t.amount}\n"
            f"  PnL: {pnl_str}\n"
            f"  Strategy: {t.strategy}\n"
            f"  Flags: SL={t.stop_loss_activated}, TP={t.take_profit_activated}, "
            f"TTP={t.trailing_take_profit_activated}\n"
        )

    return "\n".join(lines) + "\n\n"
