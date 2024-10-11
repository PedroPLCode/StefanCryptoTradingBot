from flask import current_app
from ..models import Settings
from ..utils.logging import logger
from ..utils.app_utils import send_admin_email
from ..utils.api_utils import fetch_data, place_buy_order, place_sell_order
from ..utils.stefan_utils import (
    calculate_indicators, 
    check_buy_signal, 
    check_sell_signal,
    save_trailing_stop_loss, 
    save_previous_price, 
    load_current_trade, 
    update_trailing_stop_loss
)

def run_trading_logic():
    try:
        with current_app.app_context():
            settings = Settings.query.first()
            current_trade = load_current_trade()
            
            if settings and settings.bot_running:
                symbol = settings.symbol
                trailing_stop_pct = settings.trailing_stop_pct
                interval = settings.interval
                lookback_period = settings.lookback_period
      
                df = fetch_data(symbol, interval=interval, lookback=lookback_period)
                calculate_indicators(df)
                current_price = df['close'].iloc[-1]
                trailing_stop_price = current_trade.trailing_stop_loss
                previous_price = current_trade.previous_price
                buy_signal = check_buy_signal(df)
                sell_signal = current_price <= trailing_stop_price #or check_sell_signal(df) #test and choose strategy
                price_rises = current_price >= previous_price
                
                if not current_trade and buy_signal:
                    place_buy_order(symbol)
                    trailing_stop_price = current_price * (1 - trailing_stop_pct)
                    save_trailing_stop_loss(trailing_stop_price) 
                    save_previous_price(current_price)
                
                elif current_trade and sell_signal:
                        place_sell_order(symbol)
                        
                elif current_trade and price_rises:
                    trailing_stop_price = update_trailing_stop_loss(current_price, trailing_stop_price, df['atr'].iloc[-1])
                    save_trailing_stop_loss(trailing_stop_price) 
                    save_previous_price(current_price)

                logger.trade(f"Aktualna cena: {current_price}, Trailing stop loss: {trailing_stop_price}")

    except Exception as e:
        logger.error(f'Błąd w pętli handlowej: {str(e)}')
        send_admin_email('Błąd w pętli handlowej', {str(e)})