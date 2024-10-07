#tests 100% ok
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

class MyAdmin(Admin):
    @expose('/')
    def index(self):
        if current_user.is_authenticated and current_user.admin_panel_access:
            return super().index()
        else:
            flash('Please log in to access the admin panel.', 'warning')
            return redirect(url_for('main.index'))
        
        
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.admin_panel_access

    def inaccessible_callback(self, name, **kwargs):
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('main.login'))
    
    
class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.admin_panel_access

    def inaccessible_callback(self, name, **kwargs):
        flash('You do not have access to this page.', 'danger')
        return redirect(url_for('main.login'))


class UserAdmin(AdminModelView):
    column_list = ('id', 'login', 'name', 'email', 'control_panel_access', 'admin_panel_access', 'email_raports_receiver', 'account_suspended', 'login_errors', 'creation_date', 'last_login')
    column_filters = ('login', 'name', 'email', 'control_panel_access', 'admin_panel_access', 'email_raports_receiver', 'account_suspended', 'login_errors')
    form_excluded_columns = ('password_hash',)


class SettingsAdmin(AdminModelView):
    column_list = ('id', 'bot_running', 'symbol', 'stop_loss_pct', 'trailing_stop_pct', 'take_profit_pct', 'lookback_days')