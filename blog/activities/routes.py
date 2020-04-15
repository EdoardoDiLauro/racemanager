# coding=utf-8
from flask import render_template, request, Blueprint, redirect, url_for, flash, abort
from flask_login import current_user, login_required
from blog import db
from blog.models import Activity
from activities.forms import StageForm, StayForm, TransportForm

activities = Blueprint('activities', __name__)


@activities.route("/activity/stage" , methods=['GET', 'POST'])
@login_required
def create_stage():
    if not current_user.is_authenticated:
        flash('Attenzione effettuare login per accedere!', 'danger')
        return redirect(url_for('main.home'))
    form = StageForm()
    if form.validate_on_submit():
        new_activity=Activity(tipo='stage', luogo=form.luogo.data,inizio=form.inizio.data,fine=form.fine.data,unita=form.unita.data, durata=form.fine.data-form.inizio.data,note=form.note.data, race_id=current_user.id)
        db.session.add(new_activity)
        db.session.commit()
        flash('Impiego inserito con successo', 'success')
        return redirect(url_for('main.home')) #overview
    return render_template('create_stage.html', title='Inserimento Impiego', form=form, legend='Inserimento Impiego')

@activities.route("/activity/stay" , methods=['GET', 'POST'])
@login_required
def create_stay():
    if not current_user.is_authenticated:
        flash('Attenzione effettuare login per accedere!', 'danger')
        return redirect(url_for('main.home'))
    form = StayForm()
    if form.validate_on_submit():
        new_activity=Activity(tipo='stay', luogo=form.luogo.data,unita=form.unita.data, note=form.note.data)
        db.session.add(new_activity)
        db.session.commit()
        flash('Struttura inserita con successo', 'success')
        return redirect(url_for('main.home')) #overview
    return render_template('create_stay.html', title='Inserimento Struttura',form=form, legend='Inserimento Struttura')

@activities.route("/activity/transport" , methods=['GET', 'POST'])
@login_required
def create_transport():
    if not current_user.is_authenticated:
        flash('Attenzione effettuare login per accedere!', 'danger')
        return redirect(url_for('main.home'))
    form = TransportForm()
    if form.validate_on_submit():
        new_activity=Activity(tipo='transport', partenza=form.partenza.data,luogo=form.luogo.data,vettore=form.vettore.data,inizio=form.inizio.data,fine=form.fine.data,unita=form.unita.data, note=form.note.data)
        db.session.add(new_activity)
        db.session.commit()
        flash('Trasporto inserito con successo', 'success')
        return redirect(url_for('main.home')) #overview
    return render_template('create_transport.html', title='Inserimento Trasporto',form=form, legend='Inserimento Trasporto')

@activities.route("/activity/overview", methods=['GET', 'POST'])
@login_required
def overview():
    stagelist = Activity.query.filter_by(race_id=current_user.id, tipo="stage")
    transportlist = Activity.query.filter_by(race_id=current_user.id, tipo="transport")
    staylist = Activity.query.filter_by(race_id=current_user.id, tipo="stay")

    return render_template('activity_overview.html', stagelist=stagelist, transportlist=transportlist, staylist=staylist)

@activities.route("/activity/stage/<int:activity_id>/groups", methods=['GET', 'POST'])
@login_required
def stage_detail(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    if activity.race_id != current_user.id:
        abort(403)
    form = TravelForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            travel.image_file= picture_file
        travel.budget = form.budget.data
        travel.duration = form.duration.data
        travel.participants = form.participants.data
        travel.description = form.description.data
        post = Post(title="Modifica Viaggio {}".format(travel.destination),
                    content="Viaggio a {} Modificato, contattare organizzatore".format(travel.destination), author=current_user, trip=travel)
        db.session.add(post)
        db.session.commit()
        flash('Your travel has been updated!', 'success')
        return redirect(url_for('activities.travel', travel_id=travel.id))
    elif request.method == 'GET':
        travel.budget = travel.budget
        travel.duration = travel.duration
        travel.participants = travel.participants
        travel.description = travel.description
    return render_template('activity.html', title='Gestione Attività',
                           form=form, legend='Gestione Personale')

@activities.route("/activity/stage/<int:activity_id>/update", methods=['GET', 'POST'])
@login_required
def stage_update(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    if activity.race_id != current_user.id:
        abort(403)
    form=StageForm()

    return render_template('create_stage.html', title='Modifica Attività',
                           form=form, legend='Modifica Attività')
@activities.route("/activity/<int:activity_id>/delete", methods=['GET','POST'])
@login_required
def delete_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    if activity.race_id != current_user.id:
        abort(403)
    for group in activity.gruppi:
        group.activities.remove(activity)
        db.session.commit()
    db.session.delete(activity)
    db.session.commit()
    flash('Your travel has been deleted!', 'success')
    return redirect(url_for('main.home'))

@activities.route("/travel/<int:travel_id>/join", methods=['GET', 'POST'])
@login_required
def join_travel(travel_id):
    travel = Travel.query.get_or_404(travel_id)
    booking = Booking(trip=travel, customer=current_user)
    travel.available= travel.available-1
    db.session.add(booking)
    db.session.commit()
    flash('Your booking has been added!', 'success')
    return redirect(url_for('activities.travel', travel_id=travel.id))

