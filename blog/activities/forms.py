# coding=utf-8
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import DataRequired, Length


class StageForm (FlaskForm) :
    luogo = StringField('Luogo',
                        validators=[DataRequired()])
    inizio = DateTimeLocalField('Inizio Impiego',
                       validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    fine = DateTimeLocalField('Fine Impiego',
                     validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    unita = StringField('Totale personale stimato',
                        validators=[DataRequired()])
    note = TextAreaField('Note',
                         validators=[Length(max=200)])
    submit = SubmitField('Inserire Impiego')

class StayForm(FlaskForm):
    luogo = StringField('Struttura',
                        validators=[DataRequired()])
    unita = StringField('Totale personale alloggiabile',
                        validators=[DataRequired()])
    note = TextAreaField('Note',
                         validators=[Length(max=200)])
    submit = SubmitField('Inserire Struttura')

class TransportForm (FlaskForm) :
    partenza = StringField('Località di Partenza',
                        validators=[DataRequired()])
    luogo = StringField('Località di Arrivo',
                        validators=[DataRequired()])
    vettore = StringField('Vettore',
                        validators=[DataRequired()])
    inizio = DateTimeLocalField('Partenza',
                       validators=[DataRequired()])
    fine = DateTimeLocalField('Arrivo',
                     validators=[DataRequired()])
    note = TextAreaField('Note',
                         validators=[Length(max=200)])
    submit = SubmitField('Inserire Trasporto')