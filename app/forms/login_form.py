from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
    
class LoginForm(FlaskForm):
    login = StringField(render_kw={"placeholder": "Login"}, validators=[DataRequired()])
    password = PasswordField(render_kw={"placeholder": "Password"}, validators=[DataRequired()])
    submit = SubmitField('Login')