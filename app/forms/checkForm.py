from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField
from wtforms.validators import Optional

class CheckForm(FlaskForm):
    
    check = BooleanField()
    
    submit = SubmitField("Submit")
