from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, TextAreaField, DateField, SubmitField, RadioField, SelectField
from wtforms.validators import InputRequired, Optional, Length, NumberRange

class AssignmentCreateForm(FlaskForm):
    course_id = SelectField(
        "Courses",
        coerce=int,
        validators=[InputRequired()],
        choices=[]
    )

    title = StringField(
        validators=[InputRequired(), Length(min=1, max=200)],
        render_kw={"placeholder": "e.g. Final Lab Report"}
    )

    description = TextAreaField(
        validators=[Optional(), Length(max=5000)],
        render_kw={"placeholder": "Briefly describe the task requirements... (optional)"}
    )

    # If you prefer to store ISO-8601 TEXT, you can still parse it here then serialize.
    due = DateField(
        validators=[Optional()],
        render_kw={"type": "date"}
    )

    points = IntegerField(
        validators=[Optional(), NumberRange(min=0)],
        render_kw={"placeholder": "Points (optional)"}
    )

    effort = RadioField(
        "Effort",
        choices=[(1, "Low"), (2, "Medium"), (3, "High")],
        coerce=int,
        validators=[Optional()],
        default=1
    )

    status = SelectField(
        "Status",
        choices=[(0, "Pending"), (1, "In Progress"), (2, "Finished")],
        coerce=int,
        validators=[Optional()],
        default=0
    )

    submit = SubmitField("Create Assignment")

    def updateCourseSelect(self, course_list):
        choice_map = []
        for course in course_list:
            choice_map.append((course.course_id, course.course_name))
        else:
            self.course_id.choices = choice_map
            return self