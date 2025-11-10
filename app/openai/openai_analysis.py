import os
import json
from typing import Optional
from pandas import DataFrame
from openai import OpenAI
from dotenv import load_dotenv
from ..utils.logging import logger
from ..utils.exception_handlers import exception_handler
from ..utils.retry_connection import retry_connection
from .news_fetcher import fetch_all_crypto_news
from ..utils.trades_utils import (
    update_gpt_technical_analysis_data,
    update_bot_capital_utilization_pct
)

load_dotenv()


@exception_handler()
@retry_connection()
def check_gpt_trade_signal(
    df_calculated: Optional[DataFrame],
    signal_type: str,
    bot_settings: object
) -> bool:
    """
    Analyze trading signals using a GPT model and determine if a buy/sell/hold signal is triggered.

    This function sends the calculated market data (`df_calculated`) and a bot-specific
    prompt to the OpenAI GPT model, parses the JSON response, updates the GPT analysis
    in the database, and returns True if the GPT signal matches the expected `signal_type`.

    Args:
        df_calculated (Optional[DataFrame]): The calculated historical market data. Can be None or empty.
        signal_type (str): The expected signal type to check against ('BUY', 'SELL', 'HOLD').
        bot_settings (object): Bot settings object containing GPT model info and prompt.

    Returns:
        bool: True if GPT signal matches `signal_type`, False otherwise.

    Raises:
        Exception: Any errors during GPT request or database update are handled by
            the `@exception_handler` decorator.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    if not client:
        logger.error("analyse_with_gpt_model error during OpenAI client initialization.")
        return False

    if df_calculated is None or df_calculated.empty or not signal_type:
        logger.error("analyse_with_gpt_model called with empty or None df_calculated")
        return False

    news_context = fetch_all_crypto_news(bot_settings) if bot_settings.gpt_prompt_with_news else ""
    content = f"{bot_settings.gpt_prompt}\n\n{news_context}\n\n{df_calculated}"

    logger.trade(f"[DEBUG] check_gpt_trade_signal content:\n{content}")
    
    try:
        response = client.chat.completions.create(
            model=bot_settings.gpt_model,
            messages=[{"role": "user", "content": content}],
        )

        if not response or not getattr(response, "choices", None):
            logger.error("GPT response is empty or malformed")
            return False

        choice = response.choices[0]
        content_text = getattr(choice.message, "content", None)

        if not content_text:
            logger.error("GPT response content is missing")
            return False

        response_extracted = content_text.strip()

        try:
            response_json = json.loads(response_extracted)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse GPT response as JSON: {e}")
            logger.error(f"Raw GPT content: {response_extracted}")
            return False

        update_gpt_technical_analysis_data(bot_settings, response_json)
        update_bot_capital_utilization_pct(bot_settings, response_json)

        gpt_signal = response_json.get("signal", "").upper()
        return signal_type.upper() == gpt_signal

    except Exception as e:
        logger.error(f"Error during GPT analysis: {e}")
        return False
