from typing import Dict, Any
from datetime import datetime
from ..utils.exception_handlers import exception_handler


@exception_handler()
def format_openai_error(e: Exception) -> Dict[str, Any]:
    """
    Converts any OpenAI-related exception into a clean JSON-ready structure.
    The function is 100% safe: no KeyErrors, no missing attributes.
    """
    http_status = getattr(e, "http_status", "N/A")
    error_code = getattr(e, "code", "N/A")
    error_type = getattr(e, "type", e.__class__.__name__)
    error_message = str(e)

    error_message = (
        "OpenAI Response Error. "
        f"error_type: {error_type}, "
        f"http_status: {http_status}, "
        f"error_code: {error_code}, "
        f"error_message: {error_message}."
    )

    return {
        "model": "N/A",
        "timestamp": datetime.now().isoformat(),
        "symbol": "N/A",
        "interval": "N/A",
        "signal": "N/A",
        "capital_utilization_pct": 0,
        "explanation": error_message,
        "error": True,
    }
