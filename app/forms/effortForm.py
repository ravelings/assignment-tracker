from flask_wtf import FlaskForm 
from wtforms import SubmitField, SelectField

class EffortForm(FlaskForm):

    effort = SelectField("Effort", choices=[
        ('1', 'Low'),
        ('2', 'Medium'),
        ('3', 'High')
    ])

    submit = SubmitField("Update")