from flask import request, __version__ as flask_version
from flask_login import current_user
from datetime import datetime as dt
import subprocess
import platform
import sys
import numpy as np
import pandas as pd
import tensorflow.keras
import pytz
from datetime import datetime
from .. import app, db, login_manager


@login_manager.user_loader
def inject_user(user_id):
    """
    Loads a user from the database based on the user_id.

    Args:
        user_id (int): The unique identifier of the user.

    Returns:
        User: The user object if found, else None.
    """
    from ..models import User

    return User.query.get(int(user_id))


@app.template_filter("to_datetime")
def to_datetime(timestamp):
    """
    Converts a timestamp (in milliseconds) to a formatted datetime string.

    Args:
        timestamp (int): The timestamp to be converted.

    Returns:
        str: A formatted datetime string in 'YYYY-MM-DD HH:MM:SS' format.
    """
    return datetime.fromtimestamp(timestamp / 1000.0, tz=pytz.utc).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


@app.context_processor
def inject_current_user():
    """
    Injects the current logged-in user into the context for use in templates.

    Returns:
        dict: A dictionary with the key 'user' pointing to the current_user object,
              or False if no user is logged in.
    """
    return dict(user=current_user) if current_user else False


@app.context_processor
def inject_date_and_time():
    """
    Injects the current date and time into the context for use in templates.

    Returns:
        dict: A dictionary with the key 'date_and_time' pointing to the current date and time.
    """
    return dict(date_and_time=dt.now())


@app.context_processor
def inject_user_agent():
    """
    Injects the User-Agent header of the request into the context for use in templates.

    Returns:
        dict: A dictionary with the key 'user_agent' containing the value of the User-Agent header,
              or an error message if the header retrieval fails.
    """
    try:
        user_agent = request.headers.get("User-Agent")
    except Exception as e:
        user_agent = f"Error retrieving user agent: {e}"
    return dict(user_agent=user_agent)


@app.context_processor
def inject_system_info():
    """
    Injects the system's name, version, and release information into the context for use in templates.

    Returns:
        dict: A dictionary with the key 'system_info' containing the system information string,
              or an error message if the system information retrieval fails.
    """
    try:
        system_name = platform.system()
        system_version = platform.version()
        release = platform.release()
    except Exception as e:
        system_name = f"Error retrieving system info: {e}"
    return dict(system_info=f"{system_name} {release} {system_version}")


@app.context_processor
def inject_system_uptime():
    """
    Injects the system's uptime into the context for use in templates.

    Returns:
        dict: A dictionary with the key 'system_uptime' containing the system uptime string,
              or an error message if the uptime retrieval fails.
    """
    try:
        uptime = subprocess.check_output(["uptime"], text=True).strip()
    except Exception as e:
        uptime = f"Error retrieving system uptime: {e}"
    return dict(system_uptime=uptime)


@app.context_processor
def inject_python_version():
    """
    Injects the Python version into the context for use in templates.

    Returns:
        dict: A dictionary with the key 'python_version' containing the Python version string,
              or an error message if the Python version retrieval fails.
    """
    try:
        python_version = sys.version
    except Exception as e:
        python_version = f"Error retrieving python version: {e}"
    return dict(python_version=python_version)


@app.context_processor
def inject_flask_version():
    """
    Injects the Flask version into the context for use in templates.

    Returns:
        dict: A dictionary with the key 'flask_version' containing the Flask version string,
              or an error message if the Flask version retrieval fails.
    """
    try:
        flask_info = flask_version
    except Exception as e:
        flask_info = f"Error retrieving flask version: {e}"
    return dict(flask_version=flask_info)


@app.context_processor
def inject_numpy_version():
    """
    Injects the version of NumPy into the context for use in templates.

    Returns:
        dict: A dictionary with the key 'numpy_version' containing the NumPy version string,
              or an error message if the NumPy version retrieval fails.
    """
    try:
        numpy_version = np.__version__
    except Exception as e:
        numpy_version = f"Error retrieving numpy version: {e}"
    return dict(numpy_version=numpy_version)


@app.context_processor
def inject_pandas_version():
    """
    Injects the version of Pandas into the context for use in templates.

    Returns:
        dict: A dictionary with the key 'pandas_version' containing the Pandas version string,
              or an error message if the Pandas version retrieval fails.
    """
    try:
        pandas_version = pd.__version__
    except Exception as e:
        pandas_version = f"Error retrieving pandas version: {e}"
    return dict(pandas_version=pandas_version)


@app.context_processor
def inject_keras_version():
    """
    Injects the version of Keras into the context for use in templates.

    Returns:
        dict: A dictionary with the key 'keras_version' containing the Keras version string,
              or an error message if the Keras version retrieval fails.
    """
    try:
        keras_version = tensorflow.keras.__version__
    except Exception as e:
        keras_version = f"Error retrieving keras version: {e}"
    return dict(keras_version=keras_version)


@app.context_processor
def inject_db_info():
    """
    Injects the database engine type into the context for use in templates.

    Returns:
        dict: A dictionary with the key 'db_engine' containing the database engine type string,
              or an error message if the database engine retrieval fails.
    """
    try:
        engine = db.get_engine()
        db_dialect = engine.dialect.name
    except Exception as e:
        db_dialect = f"Error retrieving db info: {e}"
    return dict(db_engine=db_dialect)


@app.shell_context_processor
def make_shell_context():
    """
    Provides useful objects for use in the Flask shell.

    Returns:
        dict: A dictionary with useful objects such as 'db', 'User', 'BotSettings', etc.
    """
    return {
        "db": db,
        "User": app.models.User,
        "BotSettings": app.models.BotSettings,
        "BotCurrentTrade": app.models.BotCurrentTrade,
        "TradesHistory": app.models.TradesHistory,
        "BacktestSettings": app.models.BacktestSettings,
        "BacktestResult": app.models.BacktestResult,
    }
