import pytest
from app import create_app, db
from app.models import User
from datetime import datetime as dt
from werkzeug.security import generate_password_hash, check_password_hash

@pytest.fixture
def test_app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        yield app

@pytest.fixture
def test_client(test_app):
    return test_app.test_client()

@pytest.fixture
def test_user(test_app):
    with test_app.app_context():
        user = User.query.filter_by(login='test_regular_user').first()
        return user

def test_set_and_check_password(test_user):
    test_user.set_password("ValidPass123!")
    db.session.commit()
    assert test_user.check_password("ValidPass123!")
    assert not test_user.check_password("WrongPassword!")

def test_update_last_login(test_user):
    old_login_time = test_user.last_login
    test_user.update_last_login()
    assert test_user.last_login > old_login_time

def test_increment_login_errors(test_user):
    test_user.login_errors = 0
    assert test_user.login_errors == 0
    test_user.increment_login_errors()
    assert test_user.login_errors == 1
    test_user.increment_login_errors()
    assert test_user.login_errors == 2

def test_reset_login_errors(test_user):
    test_user.login_errors = 0
    test_user.increment_login_errors()
    assert test_user.login_errors == 1
    test_user.reset_login_errors()
    assert test_user.login_errors == 0