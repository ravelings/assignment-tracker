from flask_wtf import FlaskForm 
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length

class AddInstanceForm(FlaskForm):

    instance = StringField(
    validators=[InputRequired(), Length(min=1, max=200)],
    render_kw={"placeholder": "Enter your Canvas URL"}
    )

    submit = SubmitField("Submit")