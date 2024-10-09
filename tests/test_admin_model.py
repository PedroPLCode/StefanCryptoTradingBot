import pytest
from flask import Flask
from flask_login import current_user
from app import create_app, db
from app.models import User
from unittest.mock import patch

@pytest.fixture
def test_app():
    from app import app
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        yield app

@pytest.fixture
def test_client(test_app):
    return test_app.test_client()

@pytest.fixture
def create_admin_user(test_app):
    with test_app.app_context():
        admin_user = User.query.filter_by(login='test_admin_user').first()
        return admin_user

@pytest.fixture
def create_regular_user(test_app):
    with test_app.app_context():
        regular_user = User.query.filter_by(login='test_regular_user').first()
        return regular_user

def test_admin_access(test_client, create_admin_user, mocker):
    mocker.patch('flask_login.utils._get_user', return_value=create_admin_user)
    response = test_client.get('/admin/', follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Admin Panel" in response.data

def test_no_admin_access(test_client, create_regular_user, mocker):
    mocker.patch('flask_login.utils._get_user', return_value=create_regular_user)
    response = test_client.get('/admin/', follow_redirects=True)
    assert response.status_code == 200
    assert b"Please log in to access this page." in response.data

def test_admin_model_view_access(test_client, create_admin_user, mocker):
    mocker.patch('flask_login.utils._get_user', return_value=create_admin_user)
    response = test_client.get('/admin/user/', follow_redirects=True)

    assert response.status_code == 200
    assert b"Control Panel Access" in response.data
    assert b"Admin Panel Access" in response.data
    assert b"Email Raports Receiver" in response.data
    assert b"Account Suspended" in response.data
    assert b"Login Errors" in response.data
    assert b"Creation Date" in response.data
    assert b"Last Login" in response.data

def test_no_admin_model_view_access(test_client, create_regular_user, mocker):
    mocker.patch('flask_login.utils._get_user', return_value=create_regular_user)
    response = test_client.get('/admin/user/', follow_redirects=True)

    assert response.status_code == 200
    assert b"You do not have access to this page." in response.data