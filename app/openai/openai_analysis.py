import os
import json
from typing import Optional
from pandas import DataFrame
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
from ..utils.logging import logger
from ..utils.exception_handlers import exception_handler
from ..utils.retry_connection import retry_connection
from .openai_error_formatter import format_openai_error
from ..utils.email_utils import send_admin_email
from .news_fetcher import fetch_all_crypto_news
from .prompt_trades_history import get_bot_last_trades_history
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

    news_context = fetch_all_crypto_news(bot_settings) if bot_settings.gpt_prompt_with_news else "\n\n"
    last_trades = get_bot_last_trades_history(bot_settings) if bot_settings.gpt_prompt_with_last_trades else "\n\n"
    content = f"{bot_settings.gpt_prompt}{news_context}{last_trades}{df_calculated}"

    response_json = None

    try:
        response = client.chat.completions.create(
            model=bot_settings.gpt_model,
            messages=[{"role": "user", "content": content}],
        )

        choice = response.choices[0]
        content_text = getattr(choice.message, "content", None)
        response_extracted = content_text.strip()
        
        try:
            response_json = json.loads(response_extracted)
            response_json["error"] = False
        except json.JSONDecodeError as e:
            response_json = {
                    "model": "N/A",
                    "timestamp": datetime.now().isoformat(),
                    "symbol": "N/A",
                    "interval": "N/A",
                    "signal": "N/A",
                    "capital_utilization_pct": 0,
                    "explanation": "json.JSONDecodeError: Invalid JSON returned from GPT model.",
                    "error": True,
                }
            logger.error(f"Failed to parse GPT response as JSON: {e}")
            logger.error(f"Raw GPT content: {response_extracted}")
            send_admin_email(f"Bot {bot_settings.id} Invalid JSON returned from GPT model.", f"Bot {bot_settings.id} {bot_settings.symbol} {bot_settings.comment}\n\njson.JSONDecodeError: Invalid JSON returned from GPT model.")

    except Exception as e:
        response_json = format_openai_error(e)
        logger.error(f"Error during GPT analysis: {e}")
        send_admin_email(f"Bot {bot_settings.id} Error during GPT analysis.", f"Bot {bot_settings.id} {bot_settings.symbol} {bot_settings.comment}\n\nError during GPT analysis\n\nresponse_json: {response_json}")

    update_gpt_technical_analysis_data(bot_settings, response_json)
    update_bot_capital_utilization_pct(bot_settings, response_json)

    gpt_signal = response_json.get("signal", "").upper()
    return signal_type.upper() == gpt_signal
