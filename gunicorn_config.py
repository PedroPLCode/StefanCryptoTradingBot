bind = '0.0.0.0:8000'
workers = 4
timeout = 256

accesslog = '/home/stefan/StefanCryptoTradingBot/gunicorn.log'
errorlog = '/home/stefan/StefanCryptoTradingBot/gunicorn.log'
loglevel = 'info'  # debug, info, warning, error, critical

def when_ready(server):
    from app import start_scheduler
    from .app.utils.app_utils import send_admin_email
    import os
    if os.getenv("SCHEDULER_ENABLED", "true") == "true":
        start_scheduler()
        send_admin_email("Back in operation", "Flask up and running. Scheduler started. All good. Back in operation.")