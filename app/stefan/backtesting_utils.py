import pandas as pd
import talib
from .. import db
import json
from app.models import BacktestResult

def update_trade_log(
    action, 
    trade_log, 
    current_price, 
    latest_data, 
    crypto_balance, 
    usdc_balance, 
    stop_loss_price,
    take_profit_price
    ):
    
    trade_log.append({
        'action': action,
        'price': float(current_price),
        'time': int(latest_data['open_time']),
        'crypto_balance': float(crypto_balance),
        'usdc_balance': float(usdc_balance),
        'stop_loss_price': float(stop_loss_price),
        'take_profit_price': float(take_profit_price)
    })
    
    
def save_backtest_results(
    bot_settings, 
    backtest_settings, 
    initial_balance, 
    final_balance, 
    trade_log
    ):
    
    new_backtest = BacktestResult(
        bot_id = bot_settings.id,
        symbol = bot_settings.symbol,
        strategy = bot_settings.strategy,
        algorithm = bot_settings.algorithm,
        start_date = backtest_settings.start_date,
        end_date = backtest_settings.end_date,
        initial_balance = initial_balance,
        final_balance = final_balance,
        profit = final_balance - initial_balance,
        trade_log=json.dumps(trade_log)
    )
    db.session.add(new_backtest)
    db.session.commit()