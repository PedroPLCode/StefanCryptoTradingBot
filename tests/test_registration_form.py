import pytest
from app import create_app, db, app
from app.forms import RegistrationForm
from app.models import User
from flask_wtf.csrf import generate_csrf

@pytest.fixture
def add_user():
    with app.app_context():
        user = User(
            login='existing_login',
            name='TestUser',
            email='existing@example.com',
        )
        user.set_password('TestPassword123#')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.mark.parametrize("login, name, email, password, confirm_password, expected", [
    ("", "John Doe", "john@example.com", "ValidPass123!", "ValidPass123!", False),  # Empty login
    ("testuser", "", "john@example.com", "ValidPass123!", "ValidPass123!", False),  # Empty name
    ("testuser", "John Doe", "", "ValidPass123!", "ValidPass123!", False),  # Empty email
    ("testuser", "John Doe", "invalid_email", "ValidPass123!", "ValidPass123!", False),  # Invalid email
    ("testuser", "John Doe", "existing@example.com", "ValidPass123!", "ValidPass123!", False),  # Existing email
    ("existing_login", "John Doe", "john@example.com", "ValidPass123!", "ValidPass123!", False),  # Existing login
    ("testuser", "John Doe", "john@example.com", "short", "short", False),  # Invalid password (too short)
    ("testuser", "John Doe", "john@example.com", "validpassword", "validpassword", False),  # Invalid password (no upper, no digit, no special char)
    ("testuser", "John Doe", "john@example.com", "ValidPass123!", "DifferentPass123!", False),  # Passwords do not match
    ("testuser", "John Doe", "john@example.com", "ValidPass123!", "ValidPass123!", True)   # Valid case
])
def test_registration_form(login, name, email, password, confirm_password, expected, add_user):
    with app.test_request_context():
        app.config['WTF_CSRF_ENABLED'] = True
        app.secret_key = 'supersecretkey'
        csrf_token = generate_csrf()

        form = RegistrationForm(
            login=login,
            name=name,
            email=email,
            password=password,
            confirm_password=confirm_password
        )
        form.csrf_token.data = csrf_token 

        # Mock existing user if testing existing login or email
        if login == 'existing_login':
            User.create(login='existing_login', name='testName', email='unique@example.com')
        elif email == 'existing@example.com':
            User.create(login='unique_login', name='testName', email='existing@example.com')

        is_valid = form.validate()
        
        assert is_valid == expected