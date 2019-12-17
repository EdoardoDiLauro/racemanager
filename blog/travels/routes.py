from flask import render_template, request, Blueprint, redirect, url_for, flash, abort
from flask_login import current_user, login_required

from blog import db
from blog.models import Travel, Post, Booking
from posts.forms import PostForm
from travels.forms import TravelForm

travels = Blueprint('travels', __name__)


@travels.route("/travel" , methods=['GET', 'POST'])
@login_required
def create_travel():
    if not current_user.is_authenticated:
        flash('You have to be logged in COZZONE!', 'danger')
        return redirect(url_for('main.home'))
    form = TravelForm()
    if form.validate_on_submit():
        new_travel = Travel(destination=form.destination.data, duration=form.duration.data, budget=form.budget.data,
                            participants=form.participants.data,description = form.description.data, user_id=current_user.id, available=form.participants.data)
        db.session.add(new_travel)
        db.session.commit()
        flash('Your travel has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_travel.html', title='Travel creation', form=form)

@travels.route("/travel/<int:travel_id>", methods=['GET', 'POST'])
@login_required
def travel(travel_id):
    booked = False
    travel = Travel.query.get_or_404(travel_id)
    posts = Post.query.filter_by(trip=travel).order_by(Post.date_posted.desc())
    form = PostForm()
    form.trip.choices = [(travel.id, travel.destination)]
    flag = Booking.query.filter_by(customer=current_user).filter_by(trip=travel).first()
    if flag:
        booked = True
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user, trip=travel)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been added!', 'success')
    return render_template('travel.html', title=travel.destination, booked=booked, travel=travel, posts=posts, form=form, legend='Add Post')

@travels.route("/travel/<int:travel_id>/update", methods=['GET', 'POST'])
@login_required
def update_travel(travel_id):
    travel = Travel.query.get_or_404(travel_id)
    if travel.creator != current_user:
        abort(403)
    form = TravelForm()
    if form.validate_on_submit():
        travel.budget = form.budget.data
        travel.duration = form.duration.data
        travel.participants = form.participants.data
        travel.description = form.description.data
        post = Post(title="Modifica Viaggio {}".format(travel.destination), content="Viaggio a {} Modificato, contattare organizzatore".format(travel.destination), author=current_user, trip=travel)
        db.session.add(post)
        db.session.commit()
        flash('Your travel has been updated!', 'success')
        return redirect(url_for('travels.travel', travel_id=travel.id))
    elif request.method == 'GET':
        travel.budget = travel.budget
        travel.duration = travel.duration
        travel.participants = travel.participants
        travel.description = travel.description
    return render_template('create_travel.html', title='Update travel',
                           form=form, legend='Update travel')


@travels.route("/travel/<int:travel_id>/delete", methods=['POST'])
@login_required
def delete_travel(travel_id):
    travel = Travel.query.get_or_404(travel_id)
    if travel.creator != current_user:
        abort(403)
    db.session.delete(travel)
    db.session.commit()
    flash('Your travel has been deleted!', 'success')
    return redirect(url_for('main.home'))

@travels.route("/travel/<int:travel_id>/join", methods=['GET', 'POST'])
@login_required
def join_travel(travel_id):
    travel = Travel.query.get_or_404(travel_id)
    booking = Booking(trip=travel, customer=current_user)
    travel.available= travel.available-1
    db.session.add(booking)
    db.session.commit()
    flash('Your booking has been added!', 'success')
    return redirect(url_for('travels.travel', travel_id=travel.id))

