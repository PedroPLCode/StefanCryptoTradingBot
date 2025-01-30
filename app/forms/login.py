from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    """
    Form for user login.

    Attributes:
        login (StringField): A field for entering the user's login. 
                             Requires input.
        password (PasswordField): A field for entering the user's password. 
                                  Requires input.
        submit (SubmitField): A button to submit the form.
    """
    login = StringField(render_kw={"placeholder": "Login"}, 
                        validators=[DataRequired()])
    password = PasswordField(render_kw={"placeholder": "Password"}, 
                             validators=[DataRequired()])
    submit = SubmitField('Login')