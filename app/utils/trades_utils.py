from datetime import datetime
import pandas as pd
from .. import db
from app.models import BotTechnicalAnalysis
from ..utils.logging import logger
from ..utils.exception_handlers import exception_handler
from ..stefan.api_utils import fetch_current_price
from typing import List, Dict, Union
from datetime import datetime


@exception_handler(default_return=False)
def show_account_balance(
    symbol: str,
    account_status: Dict[str, Union[List[Dict[str, str]], None]],
    assets_to_include: List[str],
) -> Union[List[Dict[str, Union[str, float]]], bool]:
    """
    Retrieves the account balance for specific assets and calculates their value in the given symbol.

    Args:
        symbol (str): The trading pair symbol (e.g., "BTCUSDC").
        account_status (dict): The current account status containing asset balances.
        assets_to_include (list): A list of asset symbols to filter (e.g., ["BTC", "ETH"]).

    Returns:
        list: A list of dictionaries containing asset name, amount, value, and price.
        bool: Returns False if account status is invalid or an error occurs.
    """
    if not account_status or "balances" not in account_status:
        return False

    asset_price = fetch_current_price(symbol)
    account_balance = [
        {
            "asset": single["asset"],
            "amount": float(single["free"]) + float(single["locked"]),
            "value": (float(single["free"]) + float(single["locked"]))
            * float(asset_price),
            "price": float(asset_price),
        }
        for single in account_status["balances"]
        if single["asset"] in assets_to_include
    ]
    return account_balance


@exception_handler(default_return=0)
def get_balance_for_symbol(
    account_status: List[Dict[str, Union[str, float]]], cryptocoin_symbol: str
) -> float:
    """
    Retrieves the balance amount for a specific cryptocurrency.

    Args:
        account_status (list): A list of account balances.
        cryptocoin_symbol (str): The symbol of the cryptocurrency (e.g., "BTC").

    Returns:
        float: The balance amount of the specified cryptocurrency.
        int: Returns 0 if the cryptocurrency is not found or an error occurs.
    """
    for balance in account_status:
        if balance["asset"] == cryptocoin_symbol:
            return balance["amount"]
    return 0


@exception_handler(default_return="unknown")
def calculate_profit_percentage(
    buy_price: float, sell_price: float
) -> Union[float, str]:
    """
    Calculates the profit percentage between the buy price and the sell price.

    Args:
        buy_price (float): The purchase price of the asset.
        sell_price (float): The selling price of the asset.

    Returns:
        float: The profit percentage.
        str: Returns "unknown" if an error occurs.
    """
    return ((sell_price - buy_price) / buy_price) * 100


@exception_handler(db_rollback=True)
def update_technical_analysis_data(
    bot_settings: object, df: pd.DataFrame, trend: str, averages: Dict[str, float]
) -> None:
    """
    Updates technical analysis data for a given bot and stores it in the database.

    Args:
        bot_settings (BotSettings): The bot settings instance.
        df (DataFrame): The historical data DataFrame.
        trend (str): The current trend direction.
        averages (dict): A dictionary containing averaged values of various indicators.

    Returns:
        None
    """
    latest_data = df.iloc[-1]

    technical_analysis = BotTechnicalAnalysis.query.filter_by(
        id=bot_settings.id
    ).first()

    technical_analysis.set_df(df)
    technical_analysis.current_trend = trend

    latest_data_fields = [
        "close",
        "high",
        "low",
        "volume",
        "rsi",
        "cci",
        "mfi",
        "ema_fast",
        "ema_slow",
        "macd",
        "macd_signal",
        "macd_histogram",
        "upper_band",
        "lower_band",
        "stoch_k",
        "stoch_d",
        "stoch_rsi",
        "stoch_rsi_k",
        "stoch_rsi_d",
        "atr",
        "psar",
        "vwap",
        "adx",
        "plus_di",
        "minus_di",
    ]

    for field in latest_data_fields:
        setattr(technical_analysis, f"current_{field}", latest_data.get(field, 0))

    technical_analysis.current_ma_50 = (
        latest_data["ma_50"] if bot_settings.ma50_signals else 0
    )
    technical_analysis.current_ma_200 = (
        latest_data["ma_200"] if bot_settings.ma200_signals else 0
    )

    averages_fields = [
        "avg_close",
        "avg_volume",
        "avg_rsi",
        "avg_cci",
        "avg_mfi",
        "avg_atr",
        "avg_stoch_rsi_k",
        "avg_macd",
        "avg_macd_signal",
        "avg_stoch_k",
        "avg_stoch_d",
        "avg_ema_fast",
        "avg_ema_slow",
        "avg_plus_di",
        "avg_minus_di",
        "avg_psar",
        "avg_vwap",
    ]

    for field in averages_fields:
        setattr(technical_analysis, field, averages.get(field, 0))

    technical_analysis.last_updated_timestamp = datetime.now()

    db.session.commit()
    logger.trade(
        f"BotTechnicalAnalysis {technical_analysis.id}: bot {bot_settings.id} updated in database."
    )


@exception_handler(db_rollback=True)
def update_gpt_trade_and_analysis_data(
    bot_settings: object, gpt_analysis: str
) -> None:
    """
    Update the GPT trade and analysis data for a specific trading bot in the database.

    This function updates the `gpt_analysis` field in the `BotTechnicalAnalysis`
    table for the given bot based on its ID. It also sets the 
    `last_updated_timestamp` to the current time and commits the changes 
    to the database.

    Args:
        bot_settings (object): The bot settings object containing at least the bot ID.
        gpt_analysis (dict): The GPT analysis data (as a JSON-serializable dictionary) 
            returned by the GPT model, containing information such as signal, 
            explanation, timestamp, etc.

    Returns:
        None

    Raises:
        Exception: Any database-related errors are caught and handled by the
            `@exception_handler` decorator, which performs a rollback if needed.
    """
    try:
        gpt_capital_utilization_pct = gpt_analysis.get("capital_utilization_pct", 0.95)
        bot_settings.capital_utilization_pct = float(gpt_capital_utilization_pct)
        logger.trade(f"gpt_capital_utilization_pct: {gpt_capital_utilization_pct}") # DEBUG
    except (ValueError, TypeError):
        bot_settings.capital_utilization_pct = 0.95
        logger.trade(f"gpt_capital_utilization_pct: ValueError, TypeError") # DEBUG
    
    technical_analysis = BotTechnicalAnalysis.query.filter_by(
        id=bot_settings.id
    ).first()
    technical_analysis.gpt_analysis = gpt_analysis
    technical_analysis.last_updated_timestamp = datetime.now()
    
    db.session.commit()
    
    logger.trade(
        f"BotTechnicalAnalysis {technical_analysis.id}: bot {bot_settings.id} GPT Analysis updated in database."
    )
