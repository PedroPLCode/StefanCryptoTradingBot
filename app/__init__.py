from flask import Flask, Blueprint
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from functools import partial
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from apscheduler.schedulers.background import BackgroundScheduler
from flask_limiter import Limiter
from flask_cors import CORS
from .utils.logging import logger

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
        CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]}})
        
        from .models.admin import (
            MyAdmin, 
            MyAdminIndexView,
            UserAdmin, 
            BotSettingsAdmin,
            BacktestSettingsAdmin,
            BacktestResultsAdmin,
            BotCurrentTradeAdmin, 
            TradesHistoryAdmin
        )
        admin = MyAdmin(
            app, 
            name='StefanCryptoTradingBot', 
            index_view=MyAdminIndexView(),
            template_mode='bootstrap4'
        )
        from .models import (
            User, 
            BotSettings, 
            BacktestSettings, 
            BacktestResult, 
            BotCurrentTrade, 
            TradesHistory
        )
        admin.add_view(UserAdmin(User, db.session))
        admin.add_view(BotSettingsAdmin(BotSettings, db.session))
        admin.add_view(BotCurrentTradeAdmin(BotCurrentTrade, db.session))
        admin.add_view(TradesHistoryAdmin(TradesHistory, db.session))
        admin.add_view(BacktestSettingsAdmin(BacktestSettings, db.session))
        admin.add_view(BacktestResultsAdmin(BacktestResult, db.session))
        
        main = Blueprint('main', __name__)

        logger.info('Flask app initialized.')
        
    except Exception as e:
        logger.error(f'Exception Error initializing Flask app: {e}')
        with app.app_context():
            from .utils.app_utils import send_admin_email
            send_admin_email('App Initialization Error Exception', str(e))
        raise
    
    return app

app = create_app()

limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["1000 per day", "200 per hour"],
        storage_uri="memory://",
    )

def run_job_with_context(func, *args, **kwargs):
    logger.info(f'Running job: {func.__name__} with args: {args} and kwargs: {kwargs}')
    with app.app_context():
        try:
            result = func(*args, **kwargs)
            logger.info(f'Job {func.__name__} executed successfully. Result: {result}')
            return result
        except Exception as e:
            logger.error(f'Error Exception executing job {func.__name__}: {e}')
            raise
        
def start_scheduler():
    logger.info('Starting scheduler.')
    try:
        from .stefan.trading_bot import (
            run_all_scalp_trading_bots, 
            run_all_swing_trading_bots
        )
        from .utils.app_utils import (
            send_report_via_email, 
            send_logs_via_email, 
            clear_logs, 
            clear_old_trade_history
        )
        scheduler.add_job(
            func=partial(run_job_with_context, run_all_scalp_trading_bots),
            trigger='interval',
            minutes=1
        )
        scheduler.add_job(
            func=partial(run_job_with_context, run_all_swing_trading_bots),
            trigger='interval',
            minutes=30
        )
        scheduler.add_job(
            func=partial(run_job_with_context, send_logs_via_email),
            trigger='interval',
            hours=24
        )
        scheduler.add_job(
            func=partial(run_job_with_context, clear_logs),
            trigger='interval',
            hours=24
        )
        scheduler.add_job(
            func=partial(run_job_with_context, send_report_via_email),
            trigger="interval",
            hours=24
        )
        scheduler.add_job(
            func=partial(run_job_with_context, clear_old_trade_history),
            trigger="interval",
            days=7
        )
        scheduler.start()
        logger.info('Scheduler started successfully (one instance). Stefan Bot initialized.')
    except Exception as e:
        logger.error(f'Exception Error starting scheduler: {e}')
        with app.app_context():
            from .utils.app_utils import send_admin_email
            send_admin_email('Scheduler Exception Error', str(e))

from .routes import main
app.register_blueprint(main)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)