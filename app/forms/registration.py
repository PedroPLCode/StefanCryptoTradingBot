from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
import re
from wtforms.validators import ValidationError
from ..models import User

def is_login_exits(form, field):
    login = field.data
    user = User.query.filter_by(login=login).first()
    if user:
        raise ValidationError("This login is in use.")
    
def is_email_exists(form, field):
    email = field.data
    user = User.query.filter_by(email=email).first()
    if user:
        raise ValidationError("This email is in use.")
    
def password_complexity(form, field):
    password = field.data
    if not re.search(r"[A-Z]", password):  # Check for uppercase letters
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):  # Check for lowercase letters
        raise ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r"[0-9]", password):  # Check for digits
        raise ValidationError("Password must contain at least one digit.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):  # Check for special characters
        raise ValidationError("Password must contain at least one special character.")


class RegistrationForm(FlaskForm):
    recaptcha = RecaptchaField()
    login = StringField(render_kw={"placeholder": "Login"}, validators=[DataRequired(), is_login_exits])
    name = StringField(render_kw={"placeholder": "Name"}, validators=[DataRequired()])
    email = StringField(render_kw={"placeholder": "Email"}, validators=[DataRequired(), Email(), is_email_exists])
    password = PasswordField(render_kw={"placeholder": "Password"}, validators=[DataRequired(), Length(min=10, max=50), password_complexity])
    confirm_password = PasswordField(render_kw={"placeholder": "Confirm Password"}, validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')