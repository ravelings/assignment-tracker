from flask_wtf import FlaskForm 
from wtforms import SubmitField, HiddenField

class DeleteCourseForm(FlaskForm):

    course_id = HiddenField()

    submit = SubmitField("Delete")