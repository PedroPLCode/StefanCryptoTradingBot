import pytest

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

def test_404_page_not_found(test_client):
    response = test_client.get('/error-url', follow_redirects=True)
    assert response.status_code == 200
    assert b'404 Not Found: The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.' in response.data

def test_429_too_many_requests(test_client):
    for _ in range(10):
        test_client.get('/login')

    response = test_client.get('/login', follow_redirects=True)
    assert response.status_code == 200
    assert b'429 Too Many Requests: 6 per 1 hour' in response.data

def test_unauthorized_access(test_client):
    response = test_client.get('/control', follow_redirects=True)
    assert response.status_code == 200
    assert b'Please log in to access the control panel.' in response.data