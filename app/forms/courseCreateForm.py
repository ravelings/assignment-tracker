from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import InputRequired, Length, NumberRange

class CourseCreateForm(FlaskForm):
    course_name = StringField(
        validators=[InputRequired(), Length(min=1, max=100)],
        render_kw={"placeholder": "Course Name"}
    )
    
    weight = FloatField(
        validators=[InputRequired(), NumberRange(min=0.0, max=2.0)],
        render_kw={"placeholder": "Course Weight (0.0 - 2.0)", "step": "0.1"},
        default=1.0
    )

    submit = SubmitField("Create Course")
