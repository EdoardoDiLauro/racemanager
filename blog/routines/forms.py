from flask_wtf import FlaskForm, Form
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, SelectField, FieldList, FormField, RadioField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Optional

class RoutineForm(FlaskForm):
    nome = StringField('Nome Routine', validators=[DataRequired()])
    note = TextAreaField()
    submit=SubmitField('Inserimento Routine')

class AddActivityForm(FlaskForm):
    stage = SelectField(u'Impiego', coerce=int, validators=[Optional()])
    stay = SelectField(u'Alloggio', coerce=int, validators=[Optional()])
    transport = SelectField(u'Trasporto', coerce=int, validators=[Optional()])
    submit = SubmitField('Inserimento')