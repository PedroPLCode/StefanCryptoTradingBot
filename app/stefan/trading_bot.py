from ..models import BotSettings
from ..utils.logging import logger
from .scalping_logic import run_scalping_trading_logic
from .swing_logic import run_swing_trading_logic
from .day_trading_logic import run_day_trading_logic
from ..utils.app_utils import send_admin_email

def run_all_trading_bots():
    all_bots_settings = BotSettings.query.all()

    for bot_settings in all_bots_settings:
        try:
            if bot_settings.bot_current_trade:
                if bot_settings.algorithm == 'scalp': 
                    run_scalping_trading_logic(bot_settings)
                elif bot_settings.algorithm == 'swing': 
                    run_swing_trading_logic(bot_settings)
                elif bot_settings.algorithm == 'day': 
                    run_day_trading_logic(bot_settings)
                else:
                    error_message = f"No current algorithm found for bot: {bot_settings.id}"
                    send_admin_email(f'Błąd podczas pętli bota {bot_settings.id}', error_message)
                    logger.trade(error_message)
            else:
                error_message = f"No current trade found for settings id: {bot_settings.id}"
                send_admin_email(f'Błąd podczas pętli bota {bot_settings.id}', error_message)
                logger.trade(error_message)

        except Exception as e:
            logger.error(f'Błąd w pętli handlowej: {str(e)}')
            send_admin_email('Błąd w pętli handlowej', str(e))