from flask_wtf import FlaskForm 
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length

class UsernameForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=2, max=20)],
                        render_kw={"placeholder": "Username"})
    
    submit = SubmitField("Login")