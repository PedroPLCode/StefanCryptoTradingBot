from flask import Flask, redirect, url_for, flash, request, __version__ as flask_version
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_mail import Mail
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import datetime as dt
import platform
import sys
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename="stefan.log"
                    )
logging.info('StefanCryptoTradingBot starting.')

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()
jwt = JWTManager()
    

def create_app(config_name=None):
    app = Flask(__name__)
    
    if config_name == 'testing':
        app.config.from_object('config.TestingConfig')
    else:
        app.config.from_object('config.DevelopmentConfig')
        
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    #admin.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Register blueprints
    from .routes import main
    app.register_blueprint(main)

    return app

app = create_app()

# Import models after initializing db to avoid circular imports
from .models import User, Settings, Trades
from .routes.admin import MyAdmin, MyAdminIndexView, UserAdmin, SettingsAdmin, TradesAdmin
admin = MyAdmin(app, name='StefanCryptoTradingBot', index_view=MyAdminIndexView(), template_mode='bootstrap4')
# Setup admin views
from .models import User, Settings, Trades
admin.add_view(UserAdmin(User, db.session))
admin.add_view(SettingsAdmin(Settings, db.session))
admin.add_view(TradesAdmin(Trades, db.session))

@login_manager.user_loader
def inject_user(user_id):
    from .models import User
    return User.query.get(int(user_id))

@app.context_processor
def inject_date_and_time():
    return dict(date_and_time=dt.utcnow())

@app.context_processor
def inject_user_agent():
    user_agent = request.headers.get('User-Agent') 
    return dict(user_agent=user_agent)

@app.context_processor
def inhect_system_info():
    system_name = platform.system()
    system_version = platform.version()
    release = platform.release()
    return dict(system_info=f'{system_name} {release} ({system_version})')

@app.context_processor
def inject_python_version():
    python_version = sys.version
    return dict(python_version=python_version)

@app.context_processor
def inject_flask_version():
    return dict(flask_version=flask_version)

@app.context_processor
def inject_db_info():
    engine = db.get_engine()
    db_dialect = engine.dialect.name
    return dict(db_engine=db_dialect)

@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": app.models.User,
        "Settings": app.models.Settings,
        "Trades": app.models.Trades,
    }
    
@app.errorhandler(404)
def page_not_found(error_msg):
    flash(f'{error_msg}', 'warning')
    return redirect(url_for('main.login'))

@login_manager.unauthorized_handler
def unauthorized_callback():
    flash('Please log in to access this page.', 'warning')
    return redirect(url_for('main.login'))

@app.template_filter('to_datetime')
def to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp / 1000.0).strftime('%Y-%m-%d %H:%M:%S')