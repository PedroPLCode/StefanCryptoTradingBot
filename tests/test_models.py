import pytest
from app import create_app, db
from app.models import User

@pytest.fixture(scope='module')
def test_client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

@pytest.fixture
def new_user():
    user = User(login='testuser', name='Test User', email='test@example.com')
    user.set_password('testpassword')
    return user

def test_create_user(test_client, new_user):
    assert new_user.login == 'testuser'
    assert new_user.name == 'Test User'
    assert new_user.email == 'test@example.com'
    assert new_user.check_password('testpassword') is True

def test_update_last_login(new_user):
    new_user.update_last_login()
    assert new_user.last_login is not None

def test_increment_login_errors(new_user):
    new_user.increment_login_errors()
    assert new_user.login_errors == 1

def test_reset_login_errors(new_user):
    new_user.increment_login_errors()
    new_user.reset_login_errors()
    assert new_user.login_errors == 0