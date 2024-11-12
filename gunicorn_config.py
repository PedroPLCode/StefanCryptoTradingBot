bind = '0.0.0.0:8000'
workers = 1
timeout = 1024

accesslog = '/home/stefan/StefanCryptoTradingBot/gunicorn.log'
errorlog = '/home/stefan/StefanCryptoTradingBot/gunicorn.log'
loglevel = 'info'  # debug, info, warning, error, critical