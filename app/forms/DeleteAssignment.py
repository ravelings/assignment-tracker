from flask_wtf import FlaskForm 
from wtforms import SubmitField, HiddenField

class DeleteAssignment(FlaskForm):

    assignment_id = HiddenField()

    submit = SubmitField("Delete")