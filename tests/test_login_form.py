import pytest
from app import app
from app.forms import LoginForm
from flask_wtf.csrf import generate_csrf

@pytest.mark.parametrize("login, password, expected", [
    ("", "", False),  # Both fields are empty
    ("testlogin", "", False),  # Login is filled, password is empty
    ("", "password", False),  # Login is empty, password is filled
    ("testlogin", "password", True)  # Both fields are filled
])
def test_login_form(login, password, expected):
    with app.test_request_context():
        app.config['WTF_CSRF_ENABLED'] = True
        app.secret_key = 'supersecretkey'
        csrf_token = generate_csrf()

        form = LoginForm(login=login, password=password)
        form.csrf_token.data = csrf_token
        is_valid = form.validate()
        
        assert is_valid == expected