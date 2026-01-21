from flask_wtf import FlaskForm
from wtforms import SubmitField, RadioField
from wtforms.validators import Optional


class EditAssignmentForm(FlaskForm):
    effort = RadioField(
        "Effort",
        choices=[(1, "Low"), (2, "Medium"), (3, "High")],
        coerce=int,
        validators=[Optional()],
        default=1
    )

    submit = SubmitField("Confirm")