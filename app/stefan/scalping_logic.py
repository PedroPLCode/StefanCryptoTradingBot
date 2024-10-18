from flask import current_app
import talib
from ..utils.logging import logger
from ..utils.app_utils import send_admin_email
from ..utils.api_utils import (
    fetch_data, 
    place_buy_order, 
    place_sell_order
)
from ..utils.stefan_utils import (
    calculate_indicators, 
    save_trailing_stop_loss, 
    save_previous_price, 
    update_trailing_stop_loss
)

def check_scalping_buy_signal(df):
    latest_data = df.iloc[-1]
    mfi = talib.MFI(df['high'], df['low'], df['close'], df['volume'], timeperiod=5)

    if (latest_data['rsi'] < 30 and
        latest_data['macd'] < latest_data['macd_signal'] and
        latest_data['cci'] < -100 and
        mfi.iloc[-1] < 20 and
        latest_data['close'] < latest_data['lower_band']):
        return True
    return False


def check_scalping_sell_signal(df):
    latest_data = df.iloc[-1]
    mfi = talib.MFI(df['high'], df['low'], df['close'], df['volume'], timeperiod=5)

    if (latest_data['rsi'] > 70 and
        latest_data['macd'] > latest_data['macd_signal'] and
        latest_data['cci'] > 100 and
        mfi.iloc[-1] > 80 and
        latest_data['close'] > latest_data['upper_band']):
        return True
    return False


def run_scalping_trading_logic(bot_settings):
    try:
        with current_app.app_context():
            if bot_settings and bot_settings.bot_running:
                current_trade = bot_settings.bot_current_trade
                symbol = bot_settings.symbol
                trailing_stop_pct = float(bot_settings.trailing_stop_pct)
                interval = bot_settings.interval
                lookback_period = bot_settings.lookback_period

                df = fetch_data(symbol, interval=interval, lookback=lookback_period)
                calculate_indicators(df)
                
                current_price = float(df['close'].iloc[-1])
                trailing_stop_price = float(current_trade.trailing_stop_loss)
                previous_price = float(current_trade.previous_price) if current_trade.is_active else None
                price_rises = current_price >= previous_price if current_trade.is_active else False
                buy_signal = check_scalping_buy_signal(df)
                sell_signal = None

                if bot_settings.signals_extended:
                    sell_signal = check_scalping_sell_signal(df) or current_price <= trailing_stop_price
                else:
                    sell_signal = current_price <= trailing_stop_price

                if not current_trade.is_active and buy_signal:
                    place_buy_order(bot_settings)
                    trailing_stop_price = current_price * (1 - trailing_stop_pct)
                    save_trailing_stop_loss(trailing_stop_price, current_trade)
                    save_previous_price(current_price, current_trade)

                elif current_trade.is_active and sell_signal:
                    place_sell_order(bot_settings)

                elif current_trade.is_active and price_rises:
                    trailing_stop_price = update_trailing_stop_loss(
                        current_price,
                        trailing_stop_price,
                        float(df['atr'].iloc[-1])
                    )
                    save_trailing_stop_loss(trailing_stop_price, current_trade)
                    save_previous_price(current_price, current_trade)

                logger.trade(f"Scalp Trading bot {bot_settings.id}: Aktualna cena: {current_price}, Trailing stop loss: {trailing_stop_price}")

    except Exception as e:
        logger.error(f'Błąd w pętli handlowej bota {bot_settings.id}: {str(e)}')
        send_admin_email(f'Błąd w pętli handlowej bota {bot_settings.id}', str(e))