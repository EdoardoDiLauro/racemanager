# coding=utf-8
from flask import render_template, request, Blueprint, redirect, url_for, flash, abort
from flask_login import current_user, login_required
from blog import db
from blog.models import Activity
from activities.forms import StageForm, StayForm, TransportForm
from datetime import datetime, time

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
        return redirect(url_for('activities.overview'))
    return render_template('create_stage.html', title='Inserimento Impiego', form=form, legend='Inserimento Impiego')

@activities.route("/activity/stay" , methods=['GET', 'POST'])
@login_required
def create_stay():
    if not current_user.is_authenticated:
        flash('Attenzione effettuare login per accedere!', 'danger')
        return redirect(url_for('main.home'))
    form = StayForm()
    if form.validate_on_submit():
        if not form.unita.data: form.unita.data=999
        endofday= datetime.combine(form.inizio.data, time(23,59,59))
        new_activity=Activity(tipo='stay', luogo=form.luogo.data,struttura=form.luogo.data, inizio=endofday,fine=endofday,unita=form.unita.data, note=form.note.data, race_id=current_user.id)
        db.session.add(new_activity)
        db.session.commit()
        flash('Struttura inserita con successo', 'success')
        return redirect(url_for('activities.overview'))
    return render_template('create_stay.html', title='Inserimento Struttura',form=form, legend='Inserimento Struttura')

@activities.route("/activity/transport" , methods=['GET', 'POST'])
@login_required
def create_transport():
    if not current_user.is_authenticated:
        flash('Attenzione effettuare login per accedere!', 'danger')
        return redirect(url_for('main.home'))
    form = TransportForm()
    if form.validate_on_submit():
        new_activity=Activity(tipo='transport', partenza=form.partenza.data,luogo=form.luogo.data,vettore=form.vettore.data,inizio=form.inizio.data,fine=form.fine.data,note=form.note.data, race_id=current_user.id)
        db.session.add(new_activity)
        db.session.commit()
        flash('Trasporto inserito con successo', 'success')
        return redirect(url_for('activities.overview'))
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

    return render_template('activity.html', title='Gestione Attività',
                           form=form, legend='Gestione Personale')

@activities.route("/activity/stage/<int:activity_id>/update", methods=['GET', 'POST'])
@login_required
def stage_update(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    if activity.race_id != current_user.id:
        abort(403)
    form=StageForm()

    flash('Impiego aggiornato con successo', 'success')
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
    flash('Elemento rimosso con successo', 'success')
    return redirect(url_for('main.home'))



