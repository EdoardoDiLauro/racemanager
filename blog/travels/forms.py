from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class TravelForm (FlaskForm) :
    destination= StringField('Destination',
                        validators=[DataRequired()])
    budget = StringField('Budget',
                        validators=[DataRequired()])
    duration = StringField('Duration in days',
                        validators=[DataRequired()])
    participants = StringField('Participants',
                        validators=[DataRequired()])
    description = TextAreaField('Description',
                        validators=[DataRequired()])
    picture = FileField('Upload Travel Picture', validators=[FileAllowed(['jpg', 'png'])])

    submit = SubmitField('Create Travel')
