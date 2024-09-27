import pytest
from flask import Flask, get_flashed_messages
from flask_login import LoginManager
from app import create_app, db, inject_date_and_time, inject_user_agent, inhect_system_info, inject_python_version, inject_flask_version, inject_db_info

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_inject_date_and_time(app):
    with app.test_request_context():
        context = app.context_processor(inject_date_and_time)()
        assert 'date_and_time' in context

def test_inject_user_agent(app):
    with app.test_request_context(headers={'User-Agent': 'test-agent'}):
        context = app.context_processor(inject_user_agent)()
        assert context['user_agent'] == 'test-agent'

def test_inject_system_info(app):
    with app.test_request_context():
        context = app.context_processor(inhect_system_info)()
        assert 'system_info' in context

def test_inject_python_version(app):
    with app.test_request_context():
        context = app.context_processor(inject_python_version)()
        assert 'python_version' in context

def test_inject_flask_version(app):
    with app.test_request_context():
        context = app.context_processor(inject_flask_version)()
        assert 'flask_version' in context

def test_inject_db_info(app):
    with app.test_request_context():
        context = app.context_processor(inject_db_info)()
        assert 'db_engine' in context

def test_errorhandler_404(test_client):
    response = test_client.get('/non-existent-url', follow_redirects=True)  # No need to follow redirects
    assert response.status_code == 302  # Expect a redirect

    # Follow the redirect to the login page and check the response
    follow_response = test_client.get(response.headers['Location'])
    assert follow_response.status_code == 200  # Ensure the login page is rendered

    # Check for flash messages
    messages = get_flashed_messages()
    assert messages is not None
    assert '404 Not Found' in messages[0]  # Check that the error message was flashed