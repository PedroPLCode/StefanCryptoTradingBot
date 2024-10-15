import pytest
from flask import  __version__ as flask_version
from datetime import datetime as dt
import platform
import sys
import numpy as np
import pandas as pd
import platform
from app import app, create_app, db
from app.models import Settings
from app.routes.context_processors import (
    inject_date_and_time,                 
    inject_system_info, 
    inject_python_version, 
    inject_flask_version, 
    inject_numpy_version, 
    inject_pandas_version, 
    inject_db_info
)

@pytest.fixture
def client():
    app = create_app('testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.test_request_context():
            yield app

def test_inject_date_and_time():
    with app.test_request_context():
        date_and_time_real = dt.utcnow()
        current_time = inject_date_and_time()['date_and_time']
        current_time_dt = dt.strptime(str(current_time), '%Y-%m-%d %H:%M:%S.%f')
        assert abs((current_time_dt - date_and_time_real).total_seconds()) < 1

def test_inject_system_info():
    with app.test_request_context():
        system_name = platform.system()
        system_version = platform.version()
        release = platform.release()
        system_info_real = f'{system_name} {release} {system_version}'
        system_info_test = inject_system_info()['system_info']
        assert system_info_test == system_info_real

def test_inject_python_version():
    with app.test_request_context():
        python_version_real = sys.version
        python_version_test = inject_python_version()['python_version']
        assert python_version_real == python_version_test

def test_inject_flask_version():
    with app.test_request_context():
        flask_version_real=flask_version
        flask_version_test = inject_flask_version()['flask_version']
        assert flask_version_real == flask_version_test

def test_inject_numpy_version():
    with app.test_request_context():
        numpy_version_real = np.__version__
        numpy_version_test = inject_numpy_version()['numpy_version']
        assert numpy_version_real == numpy_version_test

def test_inject_pandas_version():
    with app.test_request_context():
        pandas_version_real = pd.__version__
        pandas_version_test = inject_pandas_version()['pandas_version']
        assert pandas_version_real == pandas_version_test

def test_inject_db_info():
    with app.test_request_context():
        engine = db.get_engine()
        db_dialect = engine.dialect.name
        db_engine_real=db_dialect
        db_engine_test = inject_db_info()['db_engine']
        assert db_engine_real == db_engine_test