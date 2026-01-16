from flask_wtf import FlaskForm
from wtforms import FloatField, HiddenField, SubmitField
from wtforms.validators import InputRequired, NumberRange, Optional

class ScoreForm(FlaskForm):
    """Form for entering or updating assignment scores"""
    
    assignment_id = HiddenField(
        validators=[InputRequired()]
    )
    
    score = FloatField(
        'Score',
        validators=[Optional(), NumberRange(min=0)],
        render_kw={"placeholder": "Enter score", "step": "0.01"}
    )
    
    submit = SubmitField("Save Score")
