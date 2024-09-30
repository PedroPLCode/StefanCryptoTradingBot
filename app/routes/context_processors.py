from flask import Flask, render_template, redirect, url_for, flash, request, __version__ as flask_version
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
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
from .. import app, db, login_manager

@login_manager.user_loader
def inject_user(user_id):
    from ..models import User
    return User.query.get(int(user_id))

@app.template_filter('to_datetime')
def to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp / 1000.0).strftime('%Y-%m-%d %H:%M:%S')

@app.context_processor
def inject_current_user():
    return dict(user=current_user) if current_user else False

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