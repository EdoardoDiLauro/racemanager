from flask_wtf import FlaskForm, Form
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, RadioField, FormField, FieldList
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from flask_login import current_user
from blog.models import Race


class RegistrationForm (FlaskForm):

    username = StringField('Denominazione Gara',
                           validators=[DataRequired()])
    email = StringField('Email',
                          validators=[DataRequired(), Email()])
    inizio = DateField('Data Inizio',
                           validators=[DataRequired()], format='%Y-%m-%d')
    fine = DateField('Data Fine',
                           validators=[DataRequired()], format='%Y-%m-%d')
    password= PasswordField('Password',
                          validators=[DataRequired()])
    confirm_password = PasswordField('Conferma Password',
                                   validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrazione')

    def validate_username(self, username):
        race = Race.query.filter_by(username=username.data).first()
        if race:
            raise ValidationError('Gara presente nel database, inserire denominazione gara completa di numero edizione o contattare amministratore')

    def validate_email(self, email):
        race = Race.query.filter_by(email=email.data).first()
        if race:
            raise ValidationError('Email utilizzata, utilizzare un indirizzo mail differente per ogni gara. Se non si desidera ricevere notifiche mail, inserire: denominazione gara @default.mail ')



class LoginForm (FlaskForm) :

    email = StringField('Email',
                          validators=[DataRequired(), Email()])
    password= PasswordField('Password',
                          validators=[DataRequired()])
    remember = BooleanField('Ricordami')
    submit = SubmitField('Login')

class UpdateAccountForm (FlaskForm) :
    username = StringField('Denominazione Gara',
                           validators=[DataRequired()])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    inizio = DateField('Data Inizio',
                       validators=[DataRequired()])
    fine = DateField('Data Fine',
                     validators=[DataRequired()])
    picture = FileField('Logo Gara (formati ammessi: .jpg, .png)', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Aggiorna')

    def validate_username(self, username):
        if username.data != current_user.username:
            race = Race.query.filter_by(username=username.data).first()
            if race:
                raise ValidationError('Gara presente nel database, inserire denominazione gara completa di numero edizione o contattare amministratore')

    def validate_email(self, email):
        if email.data != current_user.email:
            race = Race.query.filter_by(email=email.data).first()
            if race:
                raise ValidationError('Email utilizzata, utilizzare un indirizzo mail differente per ogni gara. Se non si desidera ricevere notifiche mail, inserire: denominazione gara @default.mail ')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Richiesta Reset Password')

    def validate_email(self, email):
        race = Race.query.filter_by(email=email.data).first()
        if race is None:
            raise ValidationError('Nessuna gara associata alla mail inserita')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Conferma Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class ContactForm(FlaskForm):
    subject = StringField('Oggetto',
                           validators=[DataRequired()])

    body = TextAreaField ('Messaggio',
                           validators=[DataRequired()])

    submit = SubmitField('Invia Email')

class RaceForm(FlaskForm):
    rid= IntegerField()
    status=StringField()
    nome=StringField()
    onhold = RadioField('', choices=[(0, 'Si'),(1, 'No')], coerce=int, validators=[Optional()])

class RaceValidationForm(Form):
    races = FieldList(FormField(RaceForm))
    submit=SubmitField('Convalida Utenti')