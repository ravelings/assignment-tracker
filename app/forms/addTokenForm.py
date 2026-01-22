from flask_wtf import FlaskForm 
from wtforms import PasswordField, SubmitField
from wtforms.validators import InputRequired, Length

class AddTokenForm(FlaskForm):

    token = PasswordField(
    validators=[InputRequired(), Length(min=1, max=200)],
    render_kw={"placeholder": "Enter your Canvas Token"}
    )

    submit = SubmitField("Submit")