from flask_wtf import FlaskForm 
from wtforms import SubmitField, RadioField, HiddenField

class CourseWeightForm(FlaskForm):

    course_id = HiddenField()
    
    weight = RadioField(
        "Course Weight",
        choices=[(1, "Low"), (2, "Medium"), (3, "High")],
        coerce=int,
    )

    submit = SubmitField("Update")