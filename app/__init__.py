from flask import Flask, render_template, redirect, url_for, flash, request, __version__ as flask_version
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from functools import partial
from flask_login import LoginManager, current_user
from flask_mail import Mail
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask import current_app
from apscheduler.schedulers.background import BackgroundScheduler
from flask_limiter import Limiter
from flask_cors import CORS
from datetime import datetime as dt
import platform
import sys
import logging
from datetime import datetime

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()
jwt = JWTManager()
scheduler = BackgroundScheduler()
    
def create_app(config_name=None):
    app = Flask(__name__)

    try:
        if config_name == 'testing':
            app.config.from_object('config.TestingConfig')
        else:
            app.config.from_object('config.DevelopmentConfig')

        db.init_app(app)
        login_manager.init_app(app)
        mail.init_app(app)
        migrate.init_app(app, db)
        jwt.init_app(app)
        CORS(app)

        logging.info('Flask app initialized successfully.')
        
    except Exception as e:
        logging.error(f'Error initializing Flask app: {e}')
        from .utils.app_utils import send_email
        send_email('piotrek.gaszczynski@gmail.com', 'App Initialization Error', str(e))
        raise  # Re-raise the exception for further handling if needed

    return app

app = create_app()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename="stefan.log"
                    )
logging.info('StefanCryptoTradingBot starting.')

limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",
    )

def run_job_with_context(func, *args, **kwargs):
    logging.info(f'Running job: {func.__name__} with args: {args} and kwargs: {kwargs}')
    with app.app_context():
        try:
            result = func(*args, **kwargs)
            logging.info(f'Job {func.__name__} executed successfully. Result: {result}')
            return result
        except Exception as e:
            logging.error(f'Error executing job {func.__name__}: {e}')
            raise
        
def start_scheduler():
    logging.info('Starting scheduler.')
    try:
        from .utils.app_utils import send_24h_report_email
        from .stefan.stefan import run_trading_logic  
        scheduler.add_job(
            func=partial(run_job_with_context, send_24h_report_email),
            trigger="interval",
            hours=24
        )
        scheduler.add_job(
            func=partial(run_job_with_context, run_trading_logic),
            trigger='interval',
            minutes=1
        )
        scheduler.start()
        logging.info('Scheduler started successfully.')
    except Exception as e:
        logging.error(f'Error starting scheduler: {e}')
        from .utils.app_utils import send_email
        send_email('piotrek.gaszczynski@gmail.com', 'Scheduler Error', str(e))

with app.app_context():
    start_scheduler()

from .routes import main
app.register_blueprint(main)

from .models.admin import MyAdmin, MyAdminIndexView, UserAdmin, SettingsAdmin, BuyAdmin, SellAdmin
admin = MyAdmin(app, name='StefanCryptoTradingBot', index_view=MyAdminIndexView(), template_mode='bootstrap4')
from .models import User, Settings, Buy, Sell
admin.add_view(UserAdmin(User, db.session))
admin.add_view(SettingsAdmin(Settings, db.session))
admin.add_view(BuyAdmin(Buy, db.session))
admin.add_view(SellAdmin(Sell, db.session))

#def start_stefan():
#    logging.info('Starting Stefan.')
#    with app.app_context():    
#        from .stefan import stefan
#start_stefan()