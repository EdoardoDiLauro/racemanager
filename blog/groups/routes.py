import toolz
from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from sqlalchemy import func

from blog import db
from blog.models import Race, Marshal,Activity, Gruppo
from blog.groups.forms import PostForm, GroupForm, AddMarshalForm, FilterForm

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
        marshal_form.licenza = marshal.licenza
        marshal_form.nome = marshal.nome
        marshal_form.cognome = marshal.cognome
        marshal_form.ac = marshal.acrinnovo
        marshal_form.qualifica= marshal.qualifica
        m = Marshal.query.filter_by(id=marshal.id).first()
        for g in m.gruppi:
            gr = Gruppo.query.filter_by(id = g.id).first()
            if gr.race_id == current_user.id:
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
            m = Marshal.query.filter_by(licenza = data.licenza.data).first()
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
                m = Marshal.query.filter_by(licenza=data.licenza.data).first()
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
                m = Marshal.query.filter_by(licenza = data.licenza.data).first()
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


    return render_template('group.html', title=group.nome , group=group)

@groups.route("/group/<int:group_id>/update", methods=['GET', 'POST'])
@login_required
def update_group(group_id):
    group = Gruppo.query.get_or_404(group_id)
    if group.race_id != current_user.id:
        abort(403)

    teamform = GroupForm()
    filterform = FilterForm()
    filterform.acf.choices = [("all", "Tutti gli AC"), ("DSA", "DSA")] + [(str(item)[3:8], str(item)[3:8]) for item in
                                                                          db.session.query(
                                                                              Marshal.acrinnovo).distinct().order_by(
                                                                              Marshal.acrinnovo).filter(
                                                                              ~Marshal.acrinnovo.contains('DSA'))]
    filterform.qualificaf.choices = [("all", "Tutte")] + [('CP', "CP"), ('CPP', "CPP"), ('CPQ', "CPQ")]

    ms = []
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

    if filterform.submitf.data and filterform.validate_on_submit():
        if filterform.licenzaf.data:
            return redirect(url_for('groups.update_group', licenza=filterform.licenzaf.data))
        elif filterform.cognomef.data:
            return redirect(url_for('groups.update_group', cognome=filterform.cognomef.data))
        elif filterform.nomef.data:
            return redirect(url_for('groups.update_group', nome=filterform.nomef.data))
        elif filterform.acf.data != "all":
            if filterform.qualificaf.data != "all":
                return redirect(
                    url_for('groups.update_group', ac=filterform.acf.data, qualifica=filterform.qualificaf.data))
            return redirect(url_for('groups.update_group', ac=filterform.acf.data))
        elif filterform.qualificaf.data != "all":
            return redirect(url_for('groups.update_group', qualifica=filterform.qualificaf.data))
        else:
            return redirect(url_for('groups.update_group'))

    if teamform.submitall.data:
        if teamform.nome.data:
            group.nome = teamform.nome.data
        for data in teamform.teammembers.entries:
            m = Marshal.query.filter_by(licenza=data.licenza.data).first()
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
                m = Marshal.query.filter_by(licenza=data.licenza.data).first()
                group.marshals.append(m)
                db.session.commit()
        db.session.add(group)
        db.session.commit()
        flash('Gruppo modificato con successo', 'success')
        return redirect(url_for('groups.update_group', groupwip=teamform.nome.data))

    if teamform.submit.data:
        if teamform.nome.data:
            group.nome = teamform.nome.data
        for data in teamform.teammembers.entries:
            if data.selezione.data == 1:
                m = Marshal.query.filter_by(licenza=data.licenza.data).first()
                for g in m.gruppi:
                    gr = Gruppo.query.filter_by(id=g.id).first()
                    if gr.race_id == current_user.id:
                        m.gruppi.remove(gr)
                group.marshals.append(m)
                db.session.commit()
        db.session.add(group)
        db.session.commit()
        flash('Gruppo modificato con successo', 'success')
        return redirect(url_for('groups.update_group', groupwip=teamform.nome.data))

    return render_template('update_group.html', title="Modifica Gruppo", form=teamform, legend='Modifica Gruppo - Aggiunta Personale', filterform=filterform, filterlegend='Filtro')


@groups.route("/post/<int:post_id>", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    form.trip.choices = [(g.id, g.destination) for g in Travel.query.order_by(Travel.date_posted.desc())]
    if form.validate_on_submit():
        if form.picture.data :
            picture_file = save_picture(form.picture.data)
            post.image_file=picture_file
        trip = Travel.query.get(form.trip.data)
        post.trip = trip
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('groups.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


