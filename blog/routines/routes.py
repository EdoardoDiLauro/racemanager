from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from sqlalchemy import func

from blog import db
from blog.models import Race, Marshal,Activity, Gruppo, Routine
from blog.routines.forms import RoutineForm, AddActivityForm

routines = Blueprint('routines', __name__)

@routines.route("/routine/add", methods=['GET', 'POST'])
@login_required
def new_routine():
    form=RoutineForm()

    if form.validate_on_submit():
        r = Routine(nome=form.nome.data, note=form.note.data, race_id=current_user.id)
        db.session.add(r)
        db.session.commit()

        flash('Routine inserita con successo', 'success')
        return redirect(url_for('routines.overview'))

    return render_template('create_routine.html', title='Inserimento Routine',
                           form=form, legend='Inserimento Routine')


@routines.route("/routine/overview", methods=['GET', 'POST'])
@login_required
def overview():
    routines = Routine.query.filter_by(race_id=current_user.id).all()

    return render_template('routine_overview.html', title ='Panoramica Routines', routines=routines)


@routines.route("/routine/<int:routine_id>/delete", methods=['GET','POST'])
@login_required
def delete_routine(routine_id):
    routine = Routine.query.get_or_404(routine_id)
    if routine.race_id != current_user.id:
        abort(403)

    for activity in routine.activities:
        activity.routines.remove(routine)
        db.session.commit()
    for group in routine.gruppi:
        group.routines.remove(routine)
        db.session.commit()

    db.session.delete(routine)
    db.session.commit()
    flash('Elemento rimosso con successo', 'success')
    return redirect(url_for('routines.overview'))

@routines.route("/routine/<int:routine_id>", methods=['GET','POST'])
@login_required
def routine(routine_id):
    routine = Routine.query.get_or_404(routine_id)
    if routine.race_id != current_user.id:
        abort(403)

    form=RoutineForm()

    activities=Activity.query.filter(Activity.routines.any(id=routine_id)).order_by(Activity.inizio)

    return render_template('routine.html', title='Dettaglio Routine',routine=routine, form=form, activities=activities)

@routines.route("/routine/<int:routine_id>/addtask", methods=['GET','POST'])
@login_required
def add_task(routine_id):
    routine = Routine.query.get_or_404(routine_id)
    if routine.race_id != current_user.id:
        abort(403)


    previous= request.values.get('previous')
    following= request.values.get('following')


    form = AddActivityForm()
    form.stage.choices= [(-1," ")]+[(item.id, item.luogo) for item in db.session.query(Activity).filter(Activity.race_id==current_user.id, Activity.tipo=="stage", ~Activity.routines.any(id=routine_id))]
    form.stay.choices= [(-1," ")]+[(item.id, item.struttura) for item in db.session.query(Activity).filter(Activity.race_id==current_user.id, Activity.tipo=="stay", ~Activity.routines.any(id=routine_id))]
    form.transport.choices= [(-1," ")]+[(item.id, item.partenza) for item in db.session.query(Activity).filter(Activity.race_id==current_user.id, Activity.tipo=="transport", ~Activity.routines.any(id=routine_id))]

    if form.submit.data and form.validate_on_submit():
        if form.stage.data!=-1:
            stage = Activity.query.get_or_404(form.stage.data)
            routine.activities.append(stage)
            db.session.commit()
            for gr in routine.gruppi:
                gr.activities.append(stage)
                db.session.commit()
        elif form.stay.data!=-1:
            stay = Activity.query.get_or_404(form.stay.data)
            routine.activities.append(stay)
            db.session.commit()
            for gr in routine.gruppi:
                gr.activities.append(stay)
                db.session.commit()
        elif form.transport.data!=-1:
            transport = Activity.query.get_or_404(form.transport.data)
            routine.activities.append(transport)
            db.session.commit()
            for gr in routine.gruppi:
                gr.activities.append(transport)
                db.session.commit()

        if routine.activities:
            routine.req = db.session.query(func.avg(Activity.unita)).filter(Activity.routines.any(id=routine_id),
                                                                            Activity.tipo == 'stage')
            db.session.commit()

        flash('Impiego inserito con successo', 'success')
        return redirect(url_for('routines.routine', routine_id=routine.id))

    return render_template('addtaskroutine.html', title= "Assegnazione Impiego" ,routine=routine,form=form, legend="Assegnazione Incarico")

@routines.route("/routine/<int:routine_id>/remove/<int:activity_id>", methods=['GET', 'POST'])
@login_required
def remove_task(routine_id, activity_id):
    routine = Routine.query.get_or_404(routine_id)
    if routine.race_id != current_user.id:
        abort(403)
    activity= Activity.query.get_or_404(activity_id)
    routine.activities.remove(activity)
    db.session.commit()
    for gr in routine.gruppi:
        gr.activities.remove(activity)
        db.session.commit()

    if routine.activities:
        routine.req = db.session.query(func.avg(Activity.unita)).filter(Activity.routines.any(id=routine_id), Activity.tipo=='stage')
        db.session.commit()

    flash('Impiego rimosso con successo', 'success')
    return redirect(url_for('routines.routine', routine_id=routine.id))
