import pytest
from unittest.mock import MagicMock
from app import create_app, db
from app.models import User
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class MockUser(UserMixin):
    def __init__(self, login, name, email, password):
        self.login = login
        self.name = name
        self.email = email
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    
@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def mock_db(mocker):
    hashed_password = generate_password_hash('TestPassword123#')
    user = User(login='testlogin', name='testname', email='test@email.com', password_hash=hashed_password,)
    user.control_panel_access = True
    user.admin_panel_access = True
    user.account_suspended = False
    user.check_password = MagicMock(return_value=True)

    mock_query = MagicMock()
    mock_query.filter_by.return_value.first.return_value = user 

    mocker.patch('app.models.User.query', mock_query)
    
    db.session.add(user)
    db.session.commit()
    
    return user

@pytest.fixture
def test_client(app):
    return app.test_client()