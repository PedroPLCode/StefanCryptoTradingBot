from pandas import DataFrame
from ..models import BotSettings
from ..utils.exception_handlers import exception_handler


@exception_handler()
def prepare_df_info(bot_settings: BotSettings, df_calculated: DataFrame) -> str:
    """
    Prepare a structured text block describing the dataframe context for GPT analysis.
    
    This helper function extracts basic bot metadata such as symbol, interval,
    and strategy, and combines them with the provided pandas DataFrame. The output
    string is intended to be included inside a GPT prompt so the model can interpret
    the data correctly.

    Args:
        bot_settings (BotSettings): The bot configuration instance containing trading parameters.
        df_calculated (DataFrame): The calculated historical market data to include for GPT.

    Returns:
        str: A formatted string containing metadata and the dataframe content.
    """
    return (
        f"Pandas DataFrame for analysis.\n"
        f"Symbol: {bot_settings.symbol}, Interval: {bot_settings.interval}, Strategy: {bot_settings.strategy}\n\n"
        f"{df_calculated}"
    )
