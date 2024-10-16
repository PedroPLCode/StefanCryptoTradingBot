from flask import current_app
from ..models import BotSettings
from ..utils.logging import logger
from ..utils.app_utils import send_admin_email
from ..utils.api_utils import (
    fetch_data, 
    place_buy_order, 
    place_sell_order
)
from ..utils.stefan_utils import (
    calculate_indicators, 
    check_buy_signal, 
    check_sell_signal,
    save_trailing_stop_loss, 
    save_previous_price, 
    update_trailing_stop_loss
)

def run_all_trading_bots():
    all_bots_settings = BotSettings.query.all()

    for bot_settings in all_bots_settings:
        try:
            if bot_settings.bot_current_trade:
                run_single_bot_trading_logic(bot_settings)
            else:
                error_message = f"No current trade found for settings id: {bot_settings.id}"
                send_admin_email(f'Błąd podczas pętli bota {bot_settings.id}', error_message)
                logger.trade(error_message)

        except Exception as e:
            logger.error(f'Błąd w pętli handlowej: {str(e)}')
            send_admin_email('Błąd w pętli handlowej', str(e))


def run_single_bot_trading_logic(bot_settings):
    try:
        with current_app.app_context():
            if bot_settings and bot_settings.bot_running:
                bot_current_trade = bot_settings.bot_current_trade
                symbol = bot_settings.symbol
                trailing_stop_pct = bot_settings.trailing_stop_pct
                interval = bot_settings.interval
                lookback_period = bot_settings.lookback_period

                df = fetch_data(symbol, interval=interval, lookback=lookback_period)
                calculate_indicators(df)
                current_price = df['close'].iloc[-1]
                trailing_stop_price = bot_current_trade.trailing_stop_loss
                previous_price = bot_current_trade.previous_price
                price_rises = current_price >= previous_price
                buy_signal = check_buy_signal(df)
                sell_signal = None

                if bot_settings.sell_signal_extended:
                    sell_signal = check_sell_signal(df) or current_price <= trailing_stop_price
                else:
                    sell_signal = current_price <= trailing_stop_price

                if not bot_current_trade.is_active and buy_signal:
                    place_buy_order(bot_settings)
                    trailing_stop_price = current_price * (1 - trailing_stop_pct)
                    save_trailing_stop_loss(trailing_stop_price, bot_current_trade)
                    save_previous_price(current_price, bot_current_trade)

                elif bot_current_trade.is_active and sell_signal:
                    place_sell_order(bot_settings)

                elif bot_current_trade.is_active and price_rises:
                    trailing_stop_price = update_trailing_stop_loss(
                        current_price,
                        trailing_stop_price,
                        df['atr'].iloc[-1]
                    )
                    save_trailing_stop_loss(trailing_stop_price, bot_current_trade)
                    save_previous_price(current_price, bot_current_trade)

                logger.trade(f"Aktualna cena: {current_price}, Trailing stop loss: {trailing_stop_price}")

    except Exception as e:
        logger.error(f'Błąd w pętli handlowej: {str(e)}')
        send_admin_email('Błąd w pętli handlowej', str(e))