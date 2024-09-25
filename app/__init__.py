from flask import Flask, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_mail import Mail
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import datetime as dt

    
# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()
jwt = JWTManager()
    
    
class MyAdmin(Admin):
    @expose('/')
    def index(self):
        if current_user.is_authenticated and current_user.admin:
            return super().index()
        else:
            flash('Please log in to access the admin panel.', 'warning')
            return redirect(url_for('main.index'))
        
        
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.admin

    def inaccessible_callback(self, name, **kwargs):
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('main.login'))
    
    
class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('main.admin_login'))

class UserAdmin(AdminModelView):
    column_list = ('id', 'login', 'name', 'email', 'control_panel_access', 'admin_panel_access', 'email_raports_receiver', 'account_suspended', 'creation_date', 'last_login')
    column_filters = ('login', 'name', 'email', 'control_panel_access', 'admin_panel_access', 'email_raports_receiver', 'account_suspended')
    form_excluded_columns = ('password_hash',)

class SettingsAdmin(AdminModelView):
    column_list = ('id', 'strategy', 'trading_enabled')

class TradesAdmin(AdminModelView):
    column_list = ('id', 'trade_time', 'buy_or_sell', 'amount', 'price')
    column_filters = ('trade_time', 'buy_or_sell', 'amount', 'price')

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    admin = MyAdmin(app, name='Stefan CryptoTradingBot', index_view=MyAdminIndexView(), template_mode='bootstrap4')
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

    # Import models after initializing db to avoid circular imports
    from .models import User, Settings, Trades

    # Setup admin views
    admin.add_view(UserAdmin(User, db.session))
    admin.add_view(SettingsAdmin(Settings, db.session))
    admin.add_view(TradesAdmin(Trades, db.session))

    return app

app = create_app()

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))

# Context processor for injecting date and time
@app.context_processor
def inject_date_and_time():
    print('kall')  # Debugging print statement
    return dict(date_and_time=dt.utcnow())