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