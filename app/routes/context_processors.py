from flask import request, __version__ as flask_version
from flask_login import current_user
from datetime import datetime as dt
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
    user_agent = request.headers.get('User-Agent') 
    return dict(user_agent=user_agent)

@app.context_processor
def inject_system_info():
    system_name = platform.system()
    system_version = platform.version()
    release = platform.release()
    return dict(system_info=f'{system_name} {release} {system_version}')

@app.context_processor
def inject_python_version():
    python_version = sys.version
    return dict(python_version=python_version)

@app.context_processor
def inject_flask_version():
    return dict(flask_version=flask_version)

@app.context_processor
def inject_numpy_version():
    return dict(numpy_version = np.__version__)

@app.context_processor
def inject_pandas_version():
    return dict(pandas_version = pd.__version__)

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
        "BotSettings": app.models.BotSettings,
        "BotCurrentTrade": app.models.BotCurrentTrade,
        "TradesHistory": app.models.TradesHistory,
        "BacktestSettings": app.models.BacktestSettings,
        "BacktestResult": app.models.BacktestResult,
    }