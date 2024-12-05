from flask import request, __version__ as flask_version
from flask_login import current_user
from datetime import datetime as dt
import subprocess
import psutil
import platform
import sys
import numpy as np
import pandas as pd
import pytz
from datetime import datetime
from .. import app, db, login_manager

@login_manager.user_loader
def inject_user(user_id):
    from ..models import User
    return User.query.get(int(user_id))

@app.template_filter('to_datetime')
def to_datetime(timestamp):
    return datetime.fromtimestamp(
        timestamp / 1000.0, tz=pytz.utc).strftime('%Y-%m-%d %H:%M:%S'
    )

@app.context_processor
def inject_current_user():
    return dict(user=current_user) if current_user else False

@app.context_processor
def inject_date_and_time():
    return dict(date_and_time=dt.utcnow())

@app.context_processor
def inject_user_agent():
    try:
        user_agent = request.headers.get('User-Agent') 
    except Exception as e:
        user_agent = f"Error retrieving user agent: {e}"
    return dict(user_agent=user_agent)

@app.context_processor
def inject_system_info():
    try:
        system_name = platform.system()
        system_version = platform.version()
        release = platform.release()
    except Exception as e:
        system_name = f"Error retrieving system info: {e}"
    return dict(system_info=f'{system_name} {release} {system_version}')

@app.context_processor
def inject_system_uptime():
    try:
        uptime = subprocess.check_output(['uptime'], text=True).strip()
    except Exception as e:
        uptime = f"Error retrieving system uptime: {e}"
    return dict(system_uptime=uptime)

@app.context_processor
def inject_gunicorn_version():
    try:
        gunicorn_path = '/usr/local/bin/gunicorn'
        gunicorn_version = subprocess.check_output([gunicorn_path, '--version'], text=True).strip()
    except Exception as e:
        gunicorn_version = f"Error retrieving gunicorn version: {e}"
    return dict(gunicorn_info=gunicorn_version)

@app.context_processor
def inject_gunicorn_uptime():
    try:
        for proc in psutil.process_iter(['name', 'create_time']):
            if 'gunicorn' in proc.info['name']:
                create_time = datetime.fromtimestamp(proc.info['create_time'])
                uptime_seconds = (datetime.now() - create_time).total_seconds()
                uptime_hours, remainder = divmod(uptime_seconds, 3600)
                uptime_minutes, uptime_seconds = divmod(remainder, 60)
                uptime = f"{int(uptime_hours)}h {int(uptime_minutes)}m {int(uptime_seconds)}s"
                break
        else:
            uptime = "Gunicorn process not found"
    except Exception as e:
        uptime = f"Error retrieving gunicorn uptime: {e}"
    return dict(gunicorn_uptime=uptime)

@app.context_processor
def inject_python_version():
    try:
        python_version = sys.version
    except Exception as e:
        python_version = f"Error retrieving python version: {e}"
    return dict(python_version=python_version)

@app.context_processor
def inject_flask_version():
    try:
        flask_info = flask_version
    except Exception as e:
        flask_info = f"Error retrieving flask version: {e}"
    return dict(flask_version=flask_info)

@app.context_processor
def inject_numpy_version():
    try:
        numpy_version = np.__version__
    except Exception as e:
        numpy_version = f"Error retrieving numpy version: {e}"
    return dict(numpy_version=numpy_version)

@app.context_processor
def inject_pandas_version():
    try:
        pandas_version = pd.__version__
    except Exception as e:
        pandas_version = f"Error retrieving pandas version: {e}"
    return dict(pandas_version=pandas_version)

@app.context_processor
def inject_db_info():
    try:
        engine = db.get_engine()
        db_dialect = engine.dialect.name
    except Exception as e:
        db_dialect = f"Error retrieving db info: {e}"
    return dict(db_engine=db_dialect)

@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": app.models.User,
        "BotSettings": app.models.BotSettings,
        "BotCurrentTrade": app.models.BotCurrentTrade,
        "TradesHistory": app.models.TradesHistory,
        "BacktestSettings": app.models.BacktestSettings,
        "BacktestResult": app.models.BacktestResult,
    }