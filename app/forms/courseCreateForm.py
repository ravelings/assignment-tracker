from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import InputRequired, Length, Optional

class CourseCreateForm(FlaskForm):
    course_name = StringField(
        validators=[InputRequired(), Length(min=1, max=100)],
        render_kw={"placeholder": "Course Name"}
    )
    
    weight = RadioField(
        "Course Weight",
        choices=[(1, "Low"), (2, "Medium"), (3, "High")],
        coerce=int,
        validators=[Optional()],
        default=1
    )

    submit = SubmitField("Create Course")
