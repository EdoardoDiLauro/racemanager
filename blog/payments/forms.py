from flask_wtf import FlaskForm, Form
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, SelectField, FieldList, FormField, HiddenField, RadioField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Optional


class GroupPay(FlaskForm):
    gid = HiddenField()
    nome = StringField()
    payed = RadioField('', choices=[(1, 'payed'), (0, '')], coerce=int, validators=[Optional()])
    selezione = RadioField('', choices=[(1, ' '), (0, 'No')], coerce=int, validators=[Optional()])


class PaymentForm(Form):
    causale = StringField('Causale', validators=[DataRequired()])
    modo = StringField('Modalita', validators=[DataRequired()])
    doc = FileField('Allegato')
    data = DateField('Data Effettuazione',
                       validators=[DataRequired()], format='%Y-%m-%d')
    teammembers = FieldList(FormField(GroupPay))
    note = TextAreaField('Note')
    submit = SubmitField('Inserimento Pagamento')






