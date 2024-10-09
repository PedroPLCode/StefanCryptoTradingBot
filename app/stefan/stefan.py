# TESTS NEEDED
import time
from flask import current_app
from ..utils.api_utils import fetch_data, place_order
from ..utils.stefan_utils import calculate_indicators, check_signals, save_trailing_stop_loss, load_current_trade, update_trailing_stop_loss
from ..models import Settings
from ..utils.logging import logger

def run_trading_logic():
    try:
        with current_app.app_context():
            settings = Settings.query.first()
            current_trade = load_current_trade()
            
            if settings and settings.bot_running:
                symbol = settings.symbol
                trailing_stop_pct = settings.trailing_stop_pct
                interval = settings.interval
                lookback_days = settings.lookback_days
                trailing_stop_price = None
                
                df = fetch_data(symbol, interval=interval, lookback=lookback_days)
                calculate_indicators(df)
                signal = check_signals(df)
                current_price = df['close'].iloc[-1]
                
                if current_trade:
                    trailing_stop_price = current_trade.trailing_stop_loss

                if signal == 'buy' and not current_trade:
                    place_order(symbol, 'buy')
                    trailing_stop_price = current_price * (1 - trailing_stop_pct)
                    save_trailing_stop_loss(trailing_stop_price) 

                elif signal == 'sell' and current_trade:
                    place_order(symbol, 'sell')
                    #trailing_stop_price = None # potrzebne ?
                    #save_trailing_stop_loss(trailing_stop_price) # potrzebne ?

                elif trailing_stop_price and current_trade:
                    trailing_stop_price = update_trailing_stop_loss(current_price, trailing_stop_price, df['atr'].iloc[-1])
                    save_trailing_stop_loss(trailing_stop_price) 
                    if current_price <= trailing_stop_price:
                        place_order(symbol, 'sell')
                        #trailing_stop_price = None # potrzebne ?
                        #save_trailing_stop_loss(trailing_stop_price) # potrzebne ?

                logger.trade(f"Aktualna cena: {current_price}, Trailing stop loss: {trailing_stop_price}")
                #time.sleep(60)

    except Exception as e:
        logger.error(f'Błąd w pętli handlowej: {str(e)}')
        #time.sleep(60)