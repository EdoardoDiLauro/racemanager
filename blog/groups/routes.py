import toolz
from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from sqlalchemy import func

from blog import db
from blog.models import Race, Marshal,Activity, Gruppo
from blog.groups.forms import GroupForm, AddMarshalForm, FilterForm, AddActivityForm

groups = Blueprint('groups', __name__)


@groups.route("/group/new", methods=['GET', 'POST'])
@login_required
def new_group():
    teamform = GroupForm()
    filterform = FilterForm()
    filterform.acf.choices = [("all","Tutti gli AC"), ("DSA","DSA")]+[(str(item)[3:8], str(item)[3:8]) for item in db.session.query(Marshal.acrinnovo).distinct().order_by(Marshal.acrinnovo).filter(~Marshal.acrinnovo.contains('DSA'))]
    filterform.qualificaf.choices = [("all","Tutte")]+[('CP', "CP"), ('CPP', "CPP"), ('CPQ', "CPQ")]

    ms=[]
    ps=[]
    pps=[]
    licenza = request.values.get('licenza')
    cognome = request.values.get('cognome')
    nome = request.values.get('nome')
    acrinnovo = request.values.get('ac')
    qualifica = request.values.get('qualifica')
    groupwip = request.values.get('groupwip')

    if licenza:
        ps = [m for m in Marshal.query.distinct().filter_by(licenza=licenza)]
    elif cognome and nome:
        ps = [m for m in Marshal.query.distinct().filter_by(cognome=cognome.upper(), nome=nome.upper())]
    elif cognome:
        ps = [m for m in Marshal.query.distinct().filter_by(cognome=cognome.upper())]
    elif nome:
        ps = [m for m in Marshal.query.distinct().filter_by(nome=nome.upper())]
    elif acrinnovo and qualifica:
        ps = [m for m in Marshal.query.distinct().filter_by(acrinnovo=acrinnovo, qualifica=qualifica)]
    elif acrinnovo:
        ps = [m for m in Marshal.query.distinct().filter_by(acrinnovo=acrinnovo)]
    elif qualifica:
        ps = [m for m in Marshal.query.distinct().filter_by(qualifica=qualifica)]
    else:
        ps = Marshal.query.distinct().limit(50).all()

    if qualifica:
        ms = toolz.unique(ps, key=lambda x: x.licenza)
    else:
        for p in ps:
            if p.flaltraq == 1 or p.flaltraq == 4:
                m = Marshal.query.filter_by(licenza=p.licenza, qualifica="CPP").first()
            elif p.flaltraq == 2:
                m = Marshal.query.filter_by(licenza=p.licenza, qualifica="CPQ").first()
            else:
                m = Marshal.query.filter_by(licenza=p.licenza).first()

            pps.append(m)

        ms = toolz.unique(pps, key=lambda x: x.licenza)

    if groupwip:
        teamform.nome.data = groupwip

    for marshal in ms: # some database function to get a list of team members
        marshal_form = AddMarshalForm()
        marshal_form.mid = marshal.id
        marshal_form.licenza = marshal.licenza
        marshal_form.nome = marshal.nome
        marshal_form.cognome = marshal.cognome
        marshal_form.ac = marshal.acrinnovo
        marshal_form.qualifica= marshal.qualifica
        m = Marshal.query.filter_by(id=marshal.id).first()
        for g in m.gruppi:
            gr = Gruppo.query.filter_by(id = g.id).first()
            if gr.race_id == current_user.id:
                marshal_form.gruppo = gr.nome
                marshal_form.busy = 1
                marshal_form.selezione = 0
        teamform.teammembers.append_entry(marshal_form)

    if filterform.submitf.data and filterform.validate_on_submit():
        if filterform.licenzaf.data:
            return redirect(url_for('groups.new_group', licenza=filterform.licenzaf.data))
        elif filterform.cognomef.data:
            return redirect(url_for('groups.new_group', cognome=filterform.cognomef.data))
        elif filterform.nomef.data:
            return redirect(url_for('groups.new_group', nome=filterform.nomef.data))
        elif filterform.acf.data != "all":
            if filterform.qualificaf.data != "all":
                return redirect(url_for('groups.new_group', ac=filterform.acf.data, qualifica=filterform.qualificaf.data))
            return redirect(url_for('groups.new_group', ac=filterform.acf.data))
        elif filterform.qualificaf.data != "all":
            return redirect(url_for('groups.new_group', qualifica=filterform.qualificaf.data))
        else: return redirect(url_for('groups.new_group'))

    if teamform.submitall.data:
        group = Gruppo.query.filter_by(nome = teamform.nome.data, race_id=current_user.id).first()
        if group:
            flash('Gruppo duplicato', 'warning')
            return redirect(url_for('groups.new_group'))
        group = Gruppo(nome=teamform.nome.data, race_id=current_user.id)
        for data in teamform.teammembers.entries:
            m = Marshal.query.get_or_404(data.mid.data)
            for g in m.gruppi:
                gr = Gruppo.query.filter_by(id=g.id).first()
                if gr.race_id == current_user.id:
                    m.gruppi.remove(gr)
                    gr.marshals.remove(m)
            group.marshals.append(m)
            db.session.commit()
        db.session.add(group)
        db.session.commit()
        flash('Gruppo inserito con successo', 'success')
        return redirect(url_for('groups.new_group', groupwip=teamform.nome.data))

    if teamform.submitallv.data:
        group = Gruppo.query.filter_by(nome=teamform.nome.data, race_id=current_user.id).first()
        if group:
            flash('Gruppo duplicato', 'warning')
            return redirect(url_for('groups.new_group'))
        group = Gruppo(nome=teamform.nome.data, race_id=current_user.id)
        for data in teamform.teammembers.entries:
            if data.busy.data != 1:
                m = Marshal.query.filter_by(id=data.mid.data).first()
                group.marshals.append(m)
                db.session.commit()
        db.session.add(group)
        db.session.commit()
        flash('Gruppo inserito con successo', 'success')
        return redirect(url_for('groups.new_group', groupwip=teamform.nome.data))

    if teamform.submit.data:
        group = Gruppo.query.filter_by(nome=teamform.nome.data, race_id=current_user.id).first()
        if group:
            flash('Gruppo duplicato', 'warning')
            return redirect(url_for('groups.new_group'))
        group = Gruppo(nome=teamform.nome.data, race_id=current_user.id)
        for data in teamform.teammembers.entries:
            if data.selezione.data == 1:
                m = Marshal.query.filter_by(id = data.mid.data).first()
                for g in m.gruppi:
                    gr = Gruppo.query.filter_by(id=g.id).first()
                    if gr.race_id == current_user.id:
                        m.gruppi.remove(gr)
                group.marshals.append(m)
                db.session.commit()
        db.session.add(group)
        db.session.commit()
        flash('Gruppo inserito con successo', 'success')
        return redirect(url_for('groups.new_group', groupwip=teamform.nome.data))

    return render_template('create_group.html', title='Inserimento Gruppo',
                           form=teamform, legend='Inserimento Gruppo', filterform=filterform, filterlegend='Filtro')

@groups.route("/group/overview", methods=['GET', 'POST'])
@login_required
def overview():
    groups = Gruppo.query.filter_by(race_id=current_user.id).all()

    for gr in groups:
        gr.cp= Marshal.query.filter_by(qualifica="CP").filter(Marshal.gruppi.any(id=gr.id)).count()
        gr.cpp= Marshal.query.filter_by(qualifica="CPP").filter(Marshal.gruppi.any(id=gr.id)).count()
        gr.cpq= Marshal.query.filter_by(qualifica="CPQ").filter(Marshal.gruppi.any(id=gr.id)).count()
        db.session.commit()

    return render_template('group_overview.html', title ='Panoramica Gruppi', groups=groups)

@groups.route("/group/<int:group_id>/delete", methods=['GET','POST'])
@login_required
def delete_group(group_id):
    group = Gruppo.query.get_or_404(group_id)
    if group.race_id != current_user.id:
        abort(403)
    for m in group.marshals:
        m.gruppi.remove(group)
        db.session.commit()
    db.session.delete(group)
    db.session.commit()
    flash('Gruppo eliminato', 'success')
    return redirect(url_for('groups.overview'))

@groups.route("/group/<int:group_id>", methods=['GET', 'POST'])
@login_required
def group(group_id):
    group = Gruppo.query.get_or_404(group_id)
    if group.race_id != current_user.id:
        abort(403)

    if group.coordinatore:
        coordinatore=Marshal.query.get_or_404(group.coordinatore)
    else: coordinatore=None

    activities=Activity.query.filter(Activity.gruppi.any(id=group_id)).order_by(Activity.inizio)

    return render_template('group.html', title=group.nome , coordinatore=coordinatore,group=group, activities=activities)

@groups.route("/group/<int:group_id>/addtask", methods=['GET', 'POST'])
@login_required
def add_task(group_id):
    group = Gruppo.query.get_or_404(group_id)
    if group.race_id != current_user.id:
        abort(403)

    if group.coordinatore:
        coordinatore=Marshal.query.get_or_404(group.coordinatore)
    else: coordinatore=None
    previous= request.values.get('previous')
    following= request.values.get('following')


    form = AddActivityForm()
    form.stage.choices= [(-1," ")]+[(item.id, item.luogo) for item in db.session.query(Activity).filter(Activity.race_id==current_user.id, Activity.tipo=="stage", ~Activity.gruppi.any(id=group_id))]
    form.stay.choices= [(-1," ")]+[(item.id, item.struttura) for item in db.session.query(Activity).filter(Activity.race_id==current_user.id, Activity.tipo=="stay", ~Activity.gruppi.any(id=group_id))]
    form.transport.choices= [(-1," ")]+[(item.id, item.partenza) for item in db.session.query(Activity).filter(Activity.race_id==current_user.id, Activity.tipo=="transport", ~Activity.gruppi.any(id=group_id))]

    if form.submit.data and form.validate_on_submit():
        if form.stage.data!=-1:
            stage = Activity.query.get_or_404(form.stage.data)
            group.activities.append(stage)
            db.session.commit()
        elif form.stay.data!=-1:
            stay = Activity.query.get_or_404(form.stay.data)
            group.activities.append(stay)
            db.session.commit()
        elif form.transport.data!=-1:
            transport = Activity.query.get_or_404(form.transport.data)
            group.activities.append(transport)
            db.session.commit()

        flash('Impiego inserito con successo', 'success')
        return redirect(url_for('groups.group', group_id=group.id))

    return render_template('addtask.html', title= "Assegnazione Impiego" ,coordinatore=coordinatore, group=group, form=form, legend="Assegnazione Incarico")

@groups.route("/group/<int:group_id>/remove/<int:activity_id>", methods=['GET', 'POST'])
@login_required
def remove_task(group_id, activity_id):
    group = Gruppo.query.get_or_404(group_id)
    if group.race_id != current_user.id:
        abort(403)
    activity= Activity.query.get_or_404(activity_id)
    group.activities.remove(activity)
    db.session.commit()
    flash('Impiego rimosso con successo', 'success')
    return redirect(url_for('groups.group', group_id=group.id))

@groups.route("/group/<int:group_id>/update", methods=['GET', 'POST'])
@login_required
def update_group(group_id):
    group = Gruppo.query.get_or_404(group_id)
    if group.race_id != current_user.id:
        abort(403)

    if group.coordinatore:
        coordinatore=Marshal.query.get_or_404(group.coordinatore)
    else: coordinatore=None
    
    teamform = GroupForm()
    filterform = FilterForm()
    filterform.acf.choices = [("all", "Tutti gli AC"), ("DSA", "DSA")] + [(str(item)[3:8], str(item)[3:8]) for item in
                                                                          db.session.query(
                                                                              Marshal.acrinnovo).distinct().order_by(
                                                                              Marshal.acrinnovo).filter(
                                                                              ~Marshal.acrinnovo.contains('DSA'))]
    filterform.qualificaf.choices = [("all", "Tutte")] + [('CP', "CP"), ('CPP', "CPP"), ('CPQ', "CPQ")]

    ms = []
    ts = []
    ps = []
    pps = []
    licenza = request.values.get('licenza')
    cognome = request.values.get('cognome')
    nome = request.values.get('nome')
    acrinnovo = request.values.get('ac')
    qualifica = request.values.get('qualifica')
    groupwip = group.nome

    if licenza:
        ps = [m for m in Marshal.query.distinct().filter_by(licenza=licenza)]
    elif cognome and nome:
        ps = [m for m in Marshal.query.distinct().filter_by(cognome=cognome.upper(), nome=nome.upper())]
    elif cognome:
        ps = [m for m in Marshal.query.distinct().filter_by(cognome=cognome.upper())]
    elif nome:
        ps = [m for m in Marshal.query.distinct().filter_by(nome=nome.upper())]
    elif acrinnovo and qualifica:
        ps = [m for m in Marshal.query.distinct().filter_by(acrinnovo=acrinnovo, qualifica=qualifica)]
    elif acrinnovo:
        ps = [m for m in Marshal.query.distinct().filter_by(acrinnovo=acrinnovo)]
    elif qualifica:
        ps = [m for m in Marshal.query.distinct().filter_by(qualifica=qualifica)]
    else:
        ps = Marshal.query.distinct().limit(50).all()

    if qualifica:
        ms = toolz.unique(ps, key=lambda x: x.licenza)
    else:
        for p in ps:
            if p.flaltraq == 1 or p.flaltraq == 4:
                m = Marshal.query.filter_by(licenza=p.licenza, qualifica="CPP").first()
            elif p.flaltraq == 2:
                m = Marshal.query.filter_by(licenza=p.licenza, qualifica="CPQ").first()
            else:
                m = Marshal.query.filter_by(licenza=p.licenza).first()

            pps.append(m)

        ms = toolz.unique(pps, key=lambda x: x.licenza)

    if groupwip:
        teamform.nome.data = groupwip

    for marshal in ms:  # some database function to get a list of team members
        marshal_form = AddMarshalForm()
        marshal_form.mid = marshal.id
        marshal_form.licenza = marshal.licenza
        marshal_form.nome = marshal.nome
        marshal_form.cognome = marshal.cognome
        marshal_form.ac = marshal.acrinnovo
        marshal_form.qualifica = marshal.qualifica
        ids = Marshal.query.filter_by(licenza=marshal.licenza)
        for identity in ids:
            m = Marshal.query.filter_by(id=identity.id).first()
            for g in m.gruppi:
                gr = Gruppo.query.filter_by(id=g.id).first()
                if gr.race_id == current_user.id:
                    marshal_form.gruppo = gr.nome
                    marshal_form.busy = 1
                    marshal_form.selezione = 0
        teamform.teammembers.append_entry(marshal_form)

    if filterform.submitf.data and filterform.validate_on_submit():
        if filterform.licenzaf.data:
            return redirect(url_for('groups.update_group',group_id=group_id, licenza=filterform.licenzaf.data))
        elif filterform.cognomef.data:
            return redirect(url_for('groups.update_group',group_id=group_id, cognome=filterform.cognomef.data))
        elif filterform.nomef.data:
            return redirect(url_for('groups.update_group',group_id=group_id, nome=filterform.nomef.data))
        elif filterform.acf.data != "all":
            if filterform.qualificaf.data != "all":
                return redirect(
                    url_for('groups.update_group', ac=filterform.acf.data, qualifica=filterform.qualificaf.data,group_id=group_id))
            return redirect(url_for('groups.update_group',group_id=group_id, ac=filterform.acf.data))
        elif filterform.qualificaf.data != "all":
            return redirect(url_for('groups.update_group',group_id=group_id, qualifica=filterform.qualificaf.data))
        else:
            return redirect(url_for('groups.update_group', group_id=group_id))

    if teamform.submitall.data:
        if teamform.nome.data:
            group.nome = teamform.nome.data
        for data in teamform.teammembers.entries:
            m = Marshal.query.filter_by(id=data.mid.data).first()
            for g in m.gruppi:
                gr = Gruppo.query.filter_by(id=g.id).first()
                if gr.race_id == current_user.id:
                    m.gruppi.remove(gr)
                    gr.marshals.remove(m)
            group.marshals.append(m)
            db.session.commit()
        db.session.add(group)
        db.session.commit()
        flash('Gruppo modificato con successo', 'success')
        return redirect(url_for('groups.update_group', groupwip=teamform.nome.data))

    if teamform.submitallv.data:
        if teamform.nome.data:
            group.nome = teamform.nome.data
        for data in teamform.teammembers.entries:
            if data.busy.data != 1:
                m = Marshal.query.filter_by(id=data.mid.data).first()
                group.marshals.append(m)
                db.session.commit()
        db.session.add(group)
        db.session.commit()
        flash('Gruppo modificato con successo', 'success')
        return redirect(url_for('groups.update_group', group_id=group_id, groupwip=teamform.nome.data))

    if teamform.submit.data:
        if teamform.nome.data:
            group.nome = teamform.nome.data
        for data in teamform.teammembers.entries:
            if data.selezione.data == 1:
                m = Marshal.query.filter_by(id=data.mid.data).first()
                for g in m.gruppi:
                    gr = Gruppo.query.filter_by(id=g.id).first()
                    if gr.race_id == current_user.id:
                        m.gruppi.remove(gr)
                group.marshals.append(m)
                db.session.commit()
        db.session.add(group)
        db.session.commit()
        flash('Gruppo modificato con successo', 'success')
        return redirect(url_for('groups.update_group', group_id=group_id, groupwip=teamform.nome.data))

    return render_template('update_group.html', title="Modifica Gruppo", coordinatore=coordinatore,group=group, group_id=group_id, form=teamform, legend='Aggiunta Personale', filterform=filterform, filterlegend='Filtro')




@groups.route("/group/<int:group_id>/alter", methods=['GET', 'POST'])
@login_required
def alter_group(group_id):
    group = Gruppo.query.get_or_404(group_id)
    if group.race_id != current_user.id:
        abort(403)

    if group.coordinatore:
        coordinatore=Marshal.query.get_or_404(group.coordinatore)
    else: coordinatore=None

    teamform = GroupForm()
    filterform = FilterForm()
    filterform.acf.choices = [("all", "Tutti gli AC"), ("DSA", "DSA")] + [(str(item)[3:8], str(item)[3:8]) for item in
                                                                          db.session.query(
                                                                              Marshal.acrinnovo).distinct().order_by(
                                                                              Marshal.acrinnovo).filter(
                                                                              ~Marshal.acrinnovo.contains('DSA'))]
    filterform.qualificaf.choices = [("all", "Tutte")] + [('CP', "CP"), ('CPP', "CPP"), ('CPQ', "CPQ")]

    ms = []
    ts = []
    ps = []
    pps = []
    licenza = request.values.get('licenza')
    cognome = request.values.get('cognome')
    nome = request.values.get('nome')
    acrinnovo = request.values.get('ac')
    qualifica = request.values.get('qualifica')
    groupwip = group.nome

    if licenza:
        ps = [m for m in Marshal.query.distinct().filter_by(licenza=licenza).filter(Marshal.gruppi.any(id=group_id))]
    elif cognome and nome:
        ps = [m for m in Marshal.query.distinct().filter_by(cognome=cognome.upper(), nome=nome.upper()).filter(Marshal.gruppi.any(id=group_id))]
    elif cognome:
        ps = [m for m in Marshal.query.distinct().filter_by(cognome=cognome.upper()).filter(Marshal.gruppi.any(id=group_id))]
    elif nome:
        ps = [m for m in Marshal.query.distinct().filter_by(nome=nome.upper()).filter(Marshal.gruppi.any(id=group_id))]
    elif acrinnovo and qualifica:
        ps = [m for m in Marshal.query.distinct().filter_by(acrinnovo=acrinnovo, qualifica=qualifica).filter(Marshal.gruppi.any(id=group_id))]
    elif acrinnovo:
        ps = [m for m in Marshal.query.distinct().filter_by(acrinnovo=acrinnovo).filter(Marshal.gruppi.any(id=group_id))]
    elif qualifica:
        ps = [m for m in Marshal.query.distinct().filter_by(qualifica=qualifica).filter(Marshal.gruppi.any(id=group_id))]
    else:
        ps = Marshal.query.distinct().filter(Marshal.gruppi.any(id=group_id))


    if groupwip:
        teamform.nome.data = groupwip

    othergroups=  [(0, "Mantieni") , (-1, "Rimuovi"), (-2, "Coordinatore")]+[ (int(item.id), str(item.nome)) for item in db.session.query(Gruppo).filter(Gruppo.race_id==current_user.id, ~Gruppo.id.__eq__(group_id)) ]

    for marshal in ps:  # some database function to get a list of team members
        marshal_form = AddMarshalForm()
        marshal_form.mid = marshal.id
        marshal_form.licenza = marshal.licenza
        marshal_form.nome = marshal.nome
        marshal_form.cognome = marshal.cognome
        marshal_form.ac = marshal.acrinnovo
        marshal_form.qualifica = marshal.qualifica
        m = Marshal.query.filter_by(id=marshal.id).first()
        for g in m.gruppi:
            gr = Gruppo.query.filter_by(id=g.id).first()
            if gr.race_id == current_user.id:
                marshal_form.busy = 1
                marshal_form.selezione = 0

        teamform.teammembers.append_entry(marshal_form)

    for marshal_form in teamform.teammembers.entries:

        marshal_form.changeg.choices = othergroups

        m = Marshal.query.filter_by(id=marshal_form.mid.data).first()

        if m:
            if m.flaltraq == 1 or m.flaltraq == 4:
                marshal_form.changeq.choices = [("ok", " "), ("CP", "CP"), ("CPP", "CPP")]
            elif m.flaltraq == 2:
                marshal_form.changeq.choices = [("ok", " "), ("CP", "CP"), ("CPQ", "CPQ")]
            else:
                marshal_form.changeq.choices = [("ok", " ")]

    if filterform.submitf.data and filterform.validate_on_submit():
        if filterform.licenzaf.data:
            return redirect(url_for('groups.alter_group', group_id=group_id, licenza=filterform.licenzaf.data))
        elif filterform.cognomef.data:
            return redirect(url_for('groups.alter_group', group_id=group_id, cognome=filterform.cognomef.data))
        elif filterform.nomef.data:
            return redirect(url_for('groups.alter_group', group_id=group_id, nome=filterform.nomef.data))
        elif filterform.acf.data != "all":
            if filterform.qualificaf.data != "all":
                return redirect(
                    url_for('groups.alter_group', ac=filterform.acf.data, qualifica=filterform.qualificaf.data))
            return redirect(url_for('groups.alter_group', group_id=group_id, ac=filterform.acf.data))
        elif filterform.qualificaf.data != "all":
            return redirect(url_for('groups.alter_group', group_id=group_id, qualifica=filterform.qualificaf.data))
        else:
            return redirect(url_for('groups.alter_group', group_id=group_id))

    if teamform.submitmod.data:
        if teamform.nome.data:
            group.nome = teamform.nome.data

        for data in teamform.teammembers.entries:
            if data.changeg.data == -1:
                m = Marshal.query.filter_by(id=data.mid.data).first()
                m.gruppi.remove(group)
                db.session.commit()
            elif data.changeg.data == -2:
                m = Marshal.query.filter_by(id=data.mid.data).first()
                group.coordinatore=m.id
                db.session.commit()
            elif data.changeg.data != 0:
                m = Marshal.query.filter_by(id=data.mid.data).first()
                m.gruppi.remove(group)
                gr = Gruppo.query.filter_by(id=data.changeg.data).first()
                m.gruppi.append(gr)
                db.session.commit()

            if data.changeq.data != "ok":
                m = Marshal.query.filter_by(id=data.mid.data).first()
                m.gruppi.remove(group)
                db.session.commit()
                m = Marshal.query.filter_by(licenza=data.licenza.data, qualifica=data.changeq.data).first()
                m.gruppi.append(group)

        db.session.commit()
        flash('Gruppo modificato con successo', 'success')
        return redirect(url_for('groups.alter_group', group_id=group_id, groupwip=teamform.nome.data))

    return render_template('alter_group.html', title="Modifica Gruppo", group=group,coordinatore=coordinatore, group_id=group_id, form=teamform, legend='Spostamento Personale', filterform=filterform, filterlegend='Filtro')
