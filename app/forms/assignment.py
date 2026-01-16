from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, TextAreaField, DateField, SubmitField, SelectField
from wtforms.validators import InputRequired, Optional, Length, NumberRange

class AssignmentCreateForm(FlaskForm):
    course_name = StringField(
        validators=[InputRequired(), Length(min=1, max=100)],
        render_kw={"placeholder": "Course Name"}
    )

    title = StringField(
        validators=[InputRequired(), Length(min=1, max=200)],
        render_kw={"placeholder": "Title"}
    )

    description = TextAreaField(
        validators=[Optional(), Length(max=5000)],
        render_kw={"placeholder": "Description (optional)"}
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

    effort = SelectField(
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
