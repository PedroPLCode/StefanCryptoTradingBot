from flask import current_app, url_for
from bs4 import BeautifulSoup
import pytest
from unittest.mock import MagicMock
from app import create_app, db
from app.models import User
from flask_login import UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

def test_register(test_client):
    response = test_client.get(url_for('main.register'))
    soup = BeautifulSoup(response.data, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']

    response = test_client.post(url_for('main.register'), data={
        'login': 'testlogin',
        'name': 'TestName',
        'email': 'test@email.com',
        'password': 'TestPassword123#',
        'confirm_password': 'TestPassword123#',
        'csrf_token': csrf_token
    })
    assert response.status_code == 200
    assert b'Account created successfully' in response.data
    assert User.query.filter_by(login='testlogin').first() is not None
    
    
def test_register_email_exists(test_client):
    existing_user = User(
        login='testloginqqq',
        name='TestUser',
        email='test@email.com',
    )
    existing_user.set_password('TestPassword123#')
    db.session.add(existing_user)
    db.session.commit()
    
    response = test_client.get(url_for('main.register'))
    soup = BeautifulSoup(response.data, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']

    response = test_client.post(url_for('main.register'), data={
        'login': 'testlogin',
        'name': 'TestName',
        'email': 'test@email.com',
        'password': 'TestPassword123#',
        'confirm_password': 'TestPassword123#',
        'csrf_token': csrf_token
    })
    assert response.status_code == 200
    assert b'This email is in use.' in response.data
    assert User.query.filter_by(name='TestName').first() == None
    
    
def test_register_login_exists(test_client):
    existing_user = User(
        login='testlogin',
        name='TestUser',
        email='testqqq@email.com',
    )
    existing_user.set_password('TestPassword123#')
    db.session.add(existing_user)
    db.session.commit()
    
    response = test_client.get(url_for('main.register'))
    soup = BeautifulSoup(response.data, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']  # Extract CSRF token

    response = test_client.post(url_for('main.register'), data={
        'login': 'testlogin',
        'name': 'TestName',
        'email': 'test@email.com',
        'password': 'TestPassword123#',
        'confirm_password': 'TestPassword123#',
        'csrf_token': csrf_token
    })
    assert response.status_code == 200
    assert b'This login is in use.' in response.data
    assert User.query.filter_by(name='TestName').first() == None


def test_successful_login(test_client):
    user = User(
        login='testlogin',
        name='TestUser',
        email='test@example.com',
    )
    user.set_password('TestPassword123#')
    db.session.add(user)
    db.session.commit()

    response = test_client.get(url_for('main.login'))
    soup = BeautifulSoup(response.data, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    response = test_client.post(url_for('main.login'), data={
        'login': 'testlogin',
        'password': 'TestPassword123#',
        'csrf_token': csrf_token
    })

    assert response.status_code == 302
    assert response.location == '/'
    
    with test_client.session_transaction() as session:
        assert '_user_id' in session
        assert session['_user_id'] == str(user.id)

    
def test_wrong_login(test_client):
    user = User(
        login='testlogin',
        name='TestUser',
        email='test@example.com',
    )
    user.set_password('TestPassword123#')
    db.session.add(user)
    db.session.commit()
    
    response = test_client.get(url_for('main.login'))
    soup = BeautifulSoup(response.data, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    response = test_client.post(url_for('main.login'), data={
        'login': 'WrongLogin',
        'password': 'WrongPassword#',
        'csrf_token': csrf_token
    })
    assert response.status_code == 200
    assert current_user == None
    assert b'Error: Login or Password Incorrect.' in response.data

"""
def test_logout(test_client):
    user = User(
        login='testlogin',
        name='TestUser',
        email='test@example.com',
    )
    user.set_password('TestPassword123#')
    db.session.add(user)
    db.session.commit()
    
    response = test_client.get(url_for('main.login'))
    soup = BeautifulSoup(response.data, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    
    response = test_client.post(url_for('main.login'), data={
        'login': 'testlogin',
        'password': 'TestPassword123#',
        'csrf_token': csrf_token
    })

    with test_client.session_transaction() as session:
        assert '_user_id' in session
        assert session['_user_id'] == str(user.id)

    # Now test the logout
    response = test_client.get(url_for('main.logout'), follow_redirects=True)

    # Check for the logout message in the redirected response
    assert session.get('_flashes')  # Check if there are flash messages
    print(session.get('_flashes'))
    assert any('User testlogin logged out successfully.' in message for category, message in session['_flashes'])

    with test_client.session_transaction() as session:
        assert '_user_id' not in session
"""