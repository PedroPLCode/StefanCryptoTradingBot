from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
import re
from wtforms.validators import ValidationError

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
    login = StringField('Login', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=10, max=50), password_complexity])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')