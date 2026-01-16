from flask_wtf import FlaskForm 
from wtforms import SubmitField, SelectField, HiddenField

class CourseWeightForm(FlaskForm):

    course_id = HiddenField()
    
    weight = SelectField("Weight", choices=[
        ('1', 'Low'),
        ('2', 'Medium'),
        ('3', 'High')
    ])

    submit = SubmitField("Update")