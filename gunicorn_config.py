bind = '0.0.0.0:8000'
workers = 4
timeout = 256

accesslog = '/home/stefan/StefanCryptoTradingBot/gunicorn.log'
errorlog = '/home/stefan/StefanCryptoTradingBot/gunicorn.log'
loglevel = 'info' # debug, info, warning, error, critical

def when_ready(server):
    import os
    from app import start_scheduler
    if os.getenv("SCHEDULER_ENABLED", "true") == "true":
        start_scheduler()