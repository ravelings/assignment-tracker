from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField
from wtforms.validators import InputRequired, NumberRange, Optional

class SetScoreMode(FlaskForm):
    function = RadioField(
        "Function",
        choices=[(0, "Logistic Function"), (1, "Exponential Decay")],
        coerce=int,
        default=1
    ) 

    submit = SubmitField()