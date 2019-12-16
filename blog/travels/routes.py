from flask import render_template, request, Blueprint, redirect, url_for, flash
from flask_login import current_user

from blog import db
from models import Travel
from travels.forms import TravelForm

travels = Blueprint('travels', __name__)


@travels.route("/travel" , methods=['GET', 'POST'])
def travel():
    if not current_user.is_authenticated:
        flash('You have to be logged in COZZONE!', 'danger')
        return redirect(url_for('main.home'))
    form = TravelForm()
    if form.validate_on_submit():
        new_travel = Travel(destination=form.destination.data, duration=form.duration.data, budget=form.budget.data,
                            participants=form.participants.data,description = form.description.data, user_id=current_user.id)
        db.session.add(new_travel)
        db.session.commit()
        flash('Your travel has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('travel.html', title='Travel creation', form=form)







