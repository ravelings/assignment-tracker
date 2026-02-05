from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, SubmitField, HiddenField, BooleanField
from wtforms.validators import InputRequired, Length

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=2, max=20)],
                        render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=7)],
                            render_kw={"placeholder": "Password"})
    check = BooleanField(validators=[InputRequired()])
    submit = SubmitField("Login")
        
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=2, max=20)],
                        render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=7)],
                            render_kw={"placeholder": "Password"})
    password2 = PasswordField(validators=[InputRequired(), Length(min=7)],
                            render_kw={"placeholder": "Confirm Password"})
    check = BooleanField(validators=[InputRequired()])
    submit = SubmitField("Register")