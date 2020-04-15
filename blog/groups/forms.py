from flask_wtf import FlaskForm, Form
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, SelectField, FieldList, FormField, RadioField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Optional




class AddMarshalForm(FlaskForm):
    mid = HiddenField()
    gruppo = StringField()
    licenza = IntegerField()
    nome = StringField()
    cognome = StringField()
    ac = StringField()
    qualifica = StringField()
    busy = RadioField('', choices=[(1, 'busy'), (0, '')], coerce=int, validators=[Optional()])
    selezione = RadioField('', choices=[(1, ' '), (0, 'No')], coerce=int, validators=[Optional()])
    changeg = SelectField(u'Gruppo', coerce=int)
    changeq = SelectField(u'Qualifica', coerce=str)

class GroupForm(Form):
    nome = StringField('Nome Gruppo', validators=[DataRequired()])
    teammembers = FieldList(FormField(AddMarshalForm))
    submit = SubmitField('Inserimento Selezionati')
    submitall = SubmitField('Inserimento Elenco Completo')
    submitallv = SubmitField('Inserimento Disponibili')
    submitmod = SubmitField('Inserimento Modifiche')

class AddActivityForm(FlaskForm):
    stage = SelectField(u'Impiego', coerce=int, validators=[Optional()])
    stay = SelectField(u'Alloggio', coerce=int, validators=[Optional()])
    travel = SelectField(u'Trasporto', coerce=int, validators=[Optional()])
    submit = SubmitField('Inserimento')

class FilterForm(FlaskForm):
    licenzaf = IntegerField('Numero Licenza', validators=[Optional(strip_whitespace=True)])
    nomef = StringField('Nome')
    cognomef = StringField('Cognome')
    acf = SelectField(u'AC', coerce=str)
    qualificaf = SelectField(u'Qualifica', coerce=str)
    submitf = SubmitField('Ricerca')




