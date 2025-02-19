from .. import db
import json
from app.models import BacktestResult


def update_trade_log(
    action,
    trade_log,
    current_price,
    latest_data,
    crypto_balance,
    usdc_balance,
    stop_loss_price,
    take_profit_price,
):
    """
    Updates the trade log with the details of a trade action.

    Args:
        action (str): The action taken ('buy' or 'sell').
        trade_log (list): The list of trade log entries to update.
        current_price (float): The current price of the asset.
        latest_data (dict): The latest data point with details like open time.
        crypto_balance (float): The amount of cryptocurrency held.
        usdc_balance (float): The amount of USDC held.
        stop_loss_price (float): The current stop-loss price.
        take_profit_price (float): The current take-profit price.

    Returns:
        None
    """
    trade_log.append(
        {
            "action": action,
            "price": float(current_price),
            "time": int(latest_data["open_time"]),
            "crypto_balance": float(crypto_balance),
            "usdc_balance": float(usdc_balance),
            "stop_loss_price": float(stop_loss_price),
            "take_profit_price": float(take_profit_price),
        }
    )


def save_backtest_results(
    bot_settings, backtest_settings, initial_balance, final_balance, trade_log
):
    """
    Saves the results of a backtest to the database.

    Args:
        bot_settings (object): The settings of the trading bot.
        backtest_settings (object): The settings used for the backtest.
        initial_balance (float): The initial balance before the backtest started.
        final_balance (float): The final balance after the backtest finished.
        trade_log (list): The log of all trades made during the backtest.

    Returns:
        None
    """
    new_backtest = BacktestResult(
        bot_id=bot_settings.id,
        symbol=bot_settings.symbol,
        strategy=bot_settings.strategy,
        algorithm=bot_settings.algorithm,
        start_date=backtest_settings.start_date,
        end_date=backtest_settings.end_date,
        initial_balance=initial_balance,
        final_balance=final_balance,
        profit=final_balance - initial_balance,
        trade_log=json.dumps(trade_log),
    )
    db.session.add(new_backtest)
    db.session.commit()
