from flask import render_template, url_for, flash, redirect, request, Blueprint, app, abort
from flask_login import login_user, current_user, logout_user, login_required
from blog import db, bcrypt
from blog.models import Race
from blog.races.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                              RequestResetForm, ResetPasswordForm, ContactForm)
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
        new_user=Race(username=form.username.data,email=form.email.data, inizio=form.inizio.data, fine=form.fine.data ,password=pass1)
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
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('races.account'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Accesso', form=form)


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
        flash('An email has been sent with instructions to reset your password.', 'info')
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
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('races.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@races.route("/bookings", methods=['GET', 'POST'])
@login_required
def bookings():
    bookings = Booking.query.filter_by(customer=current_user).order_by(Booking.date_booked.desc())
    return render_template('bookings.html', bookings=bookings)

@races.route("/booking/<int:booking_id>/delete", methods=['GET','POST'])
@login_required
def delete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.customer != current_user:
        abort(403)
    travel = Travel.query.filter_by(id=booking.trip.id).first()
    travel.available = travel.available + 1
    db.session.delete(booking)
    db.session.commit()
    flash('Your booking has been deleted!', 'success')
    return redirect(url_for('main.home'))


@races.route("/user/<string:username>/contact", methods=['GET','POST'])
@login_required
def contact_user(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = ContactForm()
    if form.validate_on_submit():
        msg = Message(form.subject.data, body=form.body.data, sender=current_user.email, recipients=[user.email])
        mail.send(msg)
        flash('Your message has been sent!', 'success')
        return redirect(url_for('races.user_posts', username=username))
    return render_template('contact.html', title='Contact User', form=form, dest=user)


