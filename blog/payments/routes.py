from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint, current_app, send_from_directory, send_file)
from flask_login import current_user, login_required
from blog import db, ALLOWED_EXTENSIONS
from blog.models import Race, Marshal,Activity, Gruppo, Payment
from blog.payments.forms import PaymentForm, GroupPay
from datetime import datetime, time
import os
from werkzeug.utils import secure_filename

payments = Blueprint('payments', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@payments.route("/payment/new", methods=['GET', 'POST'])
@login_required
def new_payment():
    form = PaymentForm()
    gs = Gruppo.query.filter_by(race_id=current_user.id).all()

    for gr in gs:
        gf = GroupPay()
        gf.gid = gr.id
        gf.nome = gr.nome
        p = db.session.query(Gruppo.payments).first()
        if p: gf.payed = 1

        form.teammembers.append_entry(gf)


    if form.submit.data:
        endofday= datetime.combine(form.data.data, time(23,59,59))
        payment = Payment(causale=form.causale.data, race_id=current_user.id, tipo=form.modo.data, inizio=endofday, note=form.note.data)
        if form.doc.data and allowed_file(form.doc.data.filename):
                filename = secure_filename(str(form.causale.data) + '_' + str(form.data.data))
                form.doc.data.save(os.path.join(current_app.root_path, 'static/payment_files', filename))
                payment.image_file = filename
        for data in form.teammembers.entries:
            if data.selezione.data == 1:
                gr = Gruppo.query.get_or_404(data.gid.data)
                payment.gruppi.append(gr)
                db.session.commit()
        db.session.add(payment)
        db.session.commit()
        flash('Pagamento inserito con successo', 'success')
        return redirect(url_for('payments.overview'))

    return render_template('create_pay.html', title='Inserimento Pagamento',
                               form=form, legend='Inserimento Pagamento')

@payments.route("/payment/<int:payment_id>/update", methods=['GET','POST'])
@login_required
def update_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    if payment.race_id != current_user.id:
        abort(403)

    form = PaymentForm()


    gs = Gruppo.query.filter_by(race_id=current_user.id).all()

    for gr in gs:
        gf = GroupPay()
        gf.gid = gr.id
        gf.nome = gr.nome
        p = db.session.query(Gruppo.payments).first()
        if p: gf.payed = 1
        group =  Gruppo.query.filter_by(id=gr.id).first()
        for pay in group.payments:
            if pay.id==payment.id: gf.selezione = 1

        form.teammembers.append_entry(gf)

    if form.submit.data:
        endofday = datetime.combine(form.data.data, time(23, 59, 59))
        payment.causale=form.causale.data
        payment.tipo=form.modo.data
        payment.inizio=endofday
        payment.note=form.note.data
        if form.doc.data and allowed_file(form.doc.data.filename):
            filename = secure_filename(str(form.causale.data) + '_' + str(form.data.data))
            form.doc.data.save(os.path.join(current_app.root_path, 'static/payment_files', filename))
            payment.image_file = filename
        for data in form.teammembers.entries:
            if data.selezione.data == 1:
                gr = Gruppo.query.get_or_404(data.gid.data)
                payment.gruppi.append(gr)
                db.session.commit()
        db.session.commit()
        flash('Pagamento aggiornato con successo', 'success')
        return redirect(url_for('payments.overview'))
    elif request.method == 'GET':
        form.causale.data = payment.causale
        form.modo.data = payment.tipo
        form.data.data = payment.inizio.date()
        form.note.data = payment.note



    return render_template('create_pay.html', title='Modifica Pagamento',
                           form=form, legend='Modifica Pagamento')

@payments.route("/payment/<int:payment_id>/delete", methods=['GET','POST'])
@login_required
def delete_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    if payment.race_id != current_user.id:
        abort(403)

    for gr in payment.gruppi:
        payment.gruppi.remove(gr)
        db.session.commit()

    db.session.delete(payment)
    db.session.commit()
    flash('Elemento rimosso con successo', 'success')
    return redirect(url_for('payments.overview'))

@payments.route("/payment/overview", methods=['GET', 'POST'])
@login_required
def overview():
    ps = Payment.query.filter_by(race_id=current_user.id).order_by()

    return render_template('pay_overview.html', paylist=ps)

@payments.route('/payment/files/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(os.path.join(current_app.root_path, 'static/payment_files'), filename)

@payments.route('/payment/files/dl/<string:payment_id>/<filename>')
@login_required
def download_file(filename, payment_id):
         return send_file((os.path.join(current_app.root_path, 'static/payment_files'), filename), attachment_filename=payment_id)

