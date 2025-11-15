from ..models import BotSettings, TradesHistory
from ..utils.exception_handlers import exception_handler


@exception_handler
def get_bot_last_trades_history(bot_settings, limit: int = 5) -> str:
    """
    Generate a short summary of the last trades for GPT prompt.

    Args:
        bot_settings: BotSettings instance.
        limit (int): How many recent trades to include.

    Returns:
        str: Formatted summary text for GPT, or empty string if no trades.
    """
    bot = BotSettings.query.get(bot_settings.id)
    
    if bot.last_trades_limit:
        limit = bot.last_trades_limit

    trades = (
        TradesHistory.query
        .filter_by(bot_id=bot_settings.id)
        .order_by(TradesHistory.id.desc())
        .limit(limit)
        .all()
    )

    if not trades:
        return "\n\n"

    summary_lines = []
    summary_lines.append(f"Recent {len(trades)} trades summary:")

    for t in trades:
        if t.sell_price and t.buy_price:
            pnl_pct = ((t.sell_price - t.buy_price) / t.buy_price) * 100
            pnl_str = f"{pnl_pct:.2f}%"
        else:
            pnl_str = "N/A"

        summary_lines.append(
            f"- Trade {t.trade_id or t.id}: "
            f"Buy {t.buy_price}, Sell {t.sell_price}, PnL: {pnl_str}, "
            f"Strategy: {t.strategy}, "
            f"SL:{t.stop_loss_activated}, TP:{t.take_profit_activated}, TTP:{t.trailing_take_profit_activated}"
        )

    return "\n\n".join(summary_lines) + "\n\n"
