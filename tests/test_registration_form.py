# Existing User in db is not mocked. Must be real.
# Needs real User(login=test_regular_user, name=Testowy, email=regular@example.com)
import pytest
from app import app
from app.forms import RegistrationForm
from flask_wtf.csrf import generate_csrf

def test_registration_form_fields():
    with app.test_request_context():
        form = RegistrationForm()
        assert 'login' in form
        assert 'name' in form
        assert 'email' in form
        assert 'password' in form
        assert 'confirm_password' in form
        assert 'recaptcha' in form

@pytest.mark.parametrize("login, name, email, password, confirm_password, expected, expected_errors", [
    ("", "John Doe", "john@example.com", "ValidPass123!", "ValidPass123!", False, {"login": ["This field is required."]}),  # Empty login
    ("testuser", "", "john@example.com", "ValidPass123!", "ValidPass123!", False, {"name": ["This field is required."]}),  # Empty name
    ("testuser", "John Doe", "", "ValidPass123!", "ValidPass123!", False, {"email": ["This field is required."]}),  # Empty email
    ("testuser", "John Doe", "invalid_email", "ValidPass123!", "ValidPass123!", False, {"email": ["Invalid email address."]}),  # Invalid email
    ("testuser", "John Doe", "regular@example.com", "ValidPass123!", "ValidPass123!", False, {"email": ["This email is in use."]}),  # Existing email
    ("test_regular_user", "John Doe", "john@example.com", "ValidPass123!", "ValidPass123!", False, {"login": ["This login is in use."]}),  # Existing login
    ("testuser", "John Doe", "john@example.com", "short", "short", False, {"password": ['Field must be between 10 and 50 characters long.', 'Password must contain at least one uppercase letter.']}),  # Invalid password (too short)
    ("testuser", "John Doe", "john@example.com", "validpassword", "validpassword", False, {"password": ["Password must contain at least one uppercase letter."]}),  # Invalid password (no upper, no digit, no special char)
    ("testuser", "John Doe", "john@example.com", "ValidPass123!", "DifferentPass123!", False, {"confirm_password": ["Field must be equal to password."]}),  # Passwords do not match
    ("testuser", "John Doe", "john@example.com", "ValidPass123!", "ValidPass123!", True, {})  # Valid case
])
def test_registration_form(login, name, email, password, confirm_password, expected, expected_errors):
    with app.test_request_context():
        app.config['WTF_CSRF_ENABLED'] = True
        app.secret_key = 'supersecretkey'
        app.testing = True
        
        csrf_token = generate_csrf()
        
        form = RegistrationForm(
            login=login,
            name=name,
            email=email,
            password=password,
            confirm_password=confirm_password,
        )
        form.csrf_token.data = csrf_token 

        is_valid = form.validate()
        
        assert is_valid == expected
        assert form.errors == expected_errors