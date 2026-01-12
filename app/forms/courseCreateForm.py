from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length

class CourseCreateForm(FlaskForm):
    course_name = StringField(
        validators=[InputRequired(), Length(min=1, max=100)],
        render_kw={"placeholder": "Course Name"}
    )

    submit = SubmitField("Create Course")
