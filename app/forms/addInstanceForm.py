from flask_wtf import FlaskForm 
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length

class AddInstanceForm(FlaskForm):

    token = StringField(
    validators=[InputRequired(), Length(min=1, max=200)],
    render_kw={"placeholder": "Enter your Canvas instance"}
    )

    submit = SubmitField("Submit")