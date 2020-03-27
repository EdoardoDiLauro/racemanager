from flask_wtf import FlaskForm, Form
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, SelectField, FieldList, FormField, RadioField, IntegerField
from wtforms.validators import DataRequired, Optional


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    trip = SelectField(u'Trip', coerce=int)
    picture = FileField('Upload Post Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Post')

class AddMarshalForm(FlaskForm):
    licenza = IntegerField()
    nome = StringField()
    cognome = StringField()
    ac = StringField()
    qualifica = StringField()
    busy = RadioField('', choices=[(1, 'busy'), (0, '')], coerce=int, validators=[Optional()])
    selezione = RadioField('', choices=[(1, 'Si'), (0, 'No')], coerce=int, validators=[Optional()])

class GroupForm(Form):
    nome = StringField('Nome Gruppo', validators=[DataRequired()])
    teammembers = FieldList(FormField(AddMarshalForm))
    submit = SubmitField('Inserimento Selezionati')
    submitall = SubmitField('Inserimento Elenco Completo')
    submitallv = SubmitField('Inserimento Disponibili')





class FilterForm(FlaskForm):
    licenzaf = IntegerField('Numero Licenza', validators=[Optional(strip_whitespace=True)])
    nomef = StringField('Nome')
    cognomef = StringField('Cognome')
    acf = SelectField(u'AC', coerce=str)
    qualificaf = SelectField(u'Qualifica', coerce=str)
    submitf = SubmitField('Ricerca')




