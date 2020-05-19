from flask import render_template, url_for, flash, redirect, request, Blueprint, app, abort
from flask_login import login_user, current_user, logout_user, login_required
from blog import db, bcrypt
from blog.models import Race
from blog.races.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                              RequestResetForm, ResetPasswordForm, ContactForm, RaceForm, RaceValidationForm)
from blog.races.utils import save_picture, send_reset_email
from flask_mail import Message
from blog import mail

races = Blueprint('races', __name__)


@races.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        pass1 = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user=Race(username=form.username.data,email=form.email.data, inizio=form.inizio.data, fine=form.fine.data ,password=pass1, onhold=True)
        db.session.add(new_user)
        db.session.commit()
        flash('Account creato con successo', 'success')
        return redirect(url_for('races.login'))
    return render_template('register.html', title='Registrazione', form=form)


@races.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Race.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data) and user.onhold==0:
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('races.account'))
        elif form.email.data=='admin@rm-racemanager.com' and form.password.data=='admin':
            return redirect(url_for('races.adminpanel', admin=1))
        elif user.onhold==1:
            flash('Errore nel login, verificare abilitazione account', 'danger')
        else:
            flash('Errore nel login, verificare credenziali', 'danger')
    return render_template('login.html', title='Accesso', form=form)

@races.route("/adminpanel", methods=['GET', 'POST'])
def adminpanel():
    if not request.values.get('admin'):
        return redirect(url_for('main.home'))

    teamform= RaceValidationForm()
    userlist=Race.query.all()

    for r in userlist:
        rform= RaceForm()
        rform.rid=r.id
        rform.nome=r.username
        if r.onhold==True:
            rform.status = "In Attesa"
        else: rform.status= "Convalidato"


        teamform.races.append_entry(rform)

    if teamform.submit.data:
        for data in teamform.races.entries:
            r = Race.query.filter_by(id=data.rid.data).first()
            if data.onhold.data == 0:
                r.onhold = False
            elif data.onhold.data == 1:
                r.onhold = True

            db.session.commit()


        return redirect(url_for('races.adminpanel', admin=1))

    return render_template('adminpanel.html', title='Gestione Manifestazioni', legend='Gestione Manifestazioni', form=teamform)



@races.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@races.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Informazioni aggiornate con successo', 'success')
        return redirect(url_for('races.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@races.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = Race.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Istruzioni per il reset password inviate, controllare la propria casella email.', 'info')
        return redirect(url_for('races.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@races.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = Race.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('races.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Password aggiornata! Accesso autorizzato', 'success')
        return redirect(url_for('races.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)









