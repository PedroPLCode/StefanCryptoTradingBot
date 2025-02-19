from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
import re
from wtforms.validators import ValidationError
from ..models import User


def is_login_exits(form, field):
    """
    Validator to check if the login is already in use.

    Args:
        form (FlaskForm): The form instance.
        field (Field): The field containing the login data.

    Raises:
        ValidationError: If the login already exists in the database.
    """
    login = field.data
    user = User.query.filter_by(login=login).first()
    if user:
        raise ValidationError("This login is in use.")


def is_email_exists(form, field):
    """
    Validator to check if the email is already in use.

    Args:
        form (FlaskForm): The form instance.
        field (Field): The field containing the email data.

    Raises:
        ValidationError: If the email already exists in the database.
    """
    email = field.data
    user = User.query.filter_by(email=email).first()
    if user:
        raise ValidationError("This email is in use.")


def password_complexity(form, field):
    """
    Validator to enforce password complexity rules.

    Args:
        form (FlaskForm): The form instance.
        field (Field): The field containing the password data.

    Raises:
        ValidationError: If the password does not meet complexity requirements.
    """
    password = field.data
    if not re.search(r"[A-Z]", password):  # Check for uppercase letters
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):  # Check for lowercase letters
        raise ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r"[0-9]", password):  # Check for digits
        raise ValidationError("Password must contain at least one digit.")
    if not re.search(
        r"[!@#$%^&*(),.?\":{}|<>]", password
    ):  # Check for special characters
        raise ValidationError("Password must contain at least one special character.")


class RegistrationForm(FlaskForm):
    """
    Form for user registration.

    Attributes:
        recaptcha (RecaptchaField): A field for reCAPTCHA validation.
        login (StringField): A field for entering the user's login.
                             Requires input and must be unique.
        name (StringField): A field for entering the user's name.
                            Requires input.
        email (StringField): A field for entering the user's email.
                             Requires input, must be a valid email, and unique.
        password (PasswordField): A field for entering the user's password.
                                  Requires input, must be between 10-50 characters,
                                  and meet complexity requirements.
        confirm_password (PasswordField): A field for confirming the password.
                                          Requires input and must match `password`.
        submit (SubmitField): A button to submit the form.
    """

    recaptcha = RecaptchaField()
    login = StringField(
        render_kw={"placeholder": "Login"}, validators=[DataRequired(), is_login_exits]
    )
    name = StringField(render_kw={"placeholder": "Name"}, validators=[DataRequired()])
    email = StringField(
        render_kw={"placeholder": "Email"},
        validators=[DataRequired(), Email(), is_email_exists],
    )
    password = PasswordField(
        render_kw={"placeholder": "Password"},
        validators=[DataRequired(), Length(min=10, max=50), password_complexity],
    )
    confirm_password = PasswordField(
        render_kw={"placeholder": "Confirm Password"},
        validators=[DataRequired(), EqualTo("password")],
    )
    submit = SubmitField("Register")
