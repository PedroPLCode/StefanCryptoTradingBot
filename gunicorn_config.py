bind = "0.0.0.0:8001"
workers = 4
timeout = 256

accesslog = '/home/pedro/StefanCryptoTradingBot/gunicorn.log'
errorlog = '/home/pedro/StefanCryptoTradingBot/gunicorn.log'
loglevel = "info"  # debug, info, warning, error, critical


def when_ready(server):
    """
    Callback function for Gunicorn that is executed when the server is ready.
    If the 'SCHEDULER_ENABLED' environment variable is set to "true", it will
    initialize the scheduler by calling the `start_scheduler` function from the
    application.

    Args:
        server (object): The Gunicorn server object.

    Returns:
        None: No value is returned from this function.
    """
    import os
    from app import start_scheduler

    if os.getenv("SCHEDULER_ENABLED", "true") == "true":
        start_scheduler()