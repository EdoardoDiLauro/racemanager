
from blog import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return Race.query.get(int(user_id))

linksag=db.Table('linksag',
            db.Column('activity_id', db.Integer, db.ForeignKey('activity.id'), nullable=False),
            db.Column('gruppo_id', db.Integer, db.ForeignKey('gruppo.id'), nullable=False)
)

linksgm=db.Table('linksgm',
            db.Column('marshal_id', db.Integer, db.ForeignKey('marshal.id'), nullable=False),
            db.Column('gruppo_id', db.Integer, db.ForeignKey('gruppo.id'), nullable=False)
)

linksar=db.Table('linksar',
            db.Column('activity_id', db.Integer, db.ForeignKey('activity.id'), nullable=False),
            db.Column('routine_id', db.Integer, db.ForeignKey('routine.id'), nullable=False)
)

linksgr=db.Table('linksgr',
            db.Column('gruppo_id', db.Integer, db.ForeignKey('gruppo.id'), nullable=False),
            db.Column('routine_id', db.Integer, db.ForeignKey('routine.id'), nullable=False)
)

linksgp=db.Table('linksgp',
            db.Column('gruppo_id', db.Integer, db.ForeignKey('gruppo.id'), nullable=False),
            db.Column('payment_id', db.Integer, db.ForeignKey('payment.id'), nullable=False)
)

class Race(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    inizio = db.Column(db.DateTime, nullable=False)
    fine = db.Column(db.DateTime, nullable=False)
    turni = db.relationship('Activity', backref='gara', lazy=True)
    gruppi = db.relationship('Gruppo', backref='gara', lazy=True)
    tot=db.Column(db.Integer, nullable=True)
    totcp=db.Column(db.Integer, nullable=True)
    totcpp=db.Column(db.Integer, nullable=True)
    totcpq=db.Column(db.Integer, nullable=True)
    onhold=db.Column(db.Boolean)


    def __repr__(self):
        return "Race('{self.username}', '{self.email}')"

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(30), nullable=False)
    luogo = db.Column(db.String(100), nullable=False)
    partenza = db.Column(db.String(100), nullable=True)
    vettore = db.Column(db.String(100), nullable=True)
    struttura = db.Column(db.String(100), nullable=True)
    inizio = db.Column(db.DateTime, nullable=False)
    fine = db.Column(db.DateTime, nullable=False, default=inizio)
    unita = db.Column(db.Integer, nullable=False, default=0)
    confermati = db.Column(db.Integer, nullable=False, default=0)
    durata = db.Column(db.Interval, nullable=True)
    note = db.Column(db.String(200), nullable=True)
    race_id = db.Column(db.Integer, db.ForeignKey('race.id'), nullable=False)
    gruppi = db.relationship('Gruppo', secondary=linksag, backref='acts', lazy=True)
    routines = db.relationship('Routine', secondary=linksar, backref='steps', lazy=True)
    tot=db.Column(db.Integer, nullable=True)
    totcp=db.Column(db.Integer, nullable=True)
    totcpp=db.Column(db.Integer, nullable=True)
    totcpq=db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return "Activity('{self.luogo}', '{self.inizio}')"


class Gruppo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    activities = db.relationship('Activity', secondary=linksag, backref='assegnati', lazy=True)
    race_id = db.Column(db.Integer, db.ForeignKey('race.id'), nullable=False)
    marshals = db.relationship('Marshal', secondary=linksgm, backref='grs', lazy=True)
    routines = db.relationship('Routine', secondary=linksgr, backref='following', lazy=True)
    payments = db.relationship('Payment', secondary=linksgp, backref='paying', lazy=True)
    coordinatore = db.Column(db.Integer, db.ForeignKey('marshal.id'), nullable=True)
    cp=db.Column(db.Integer, default=0)
    cpp=db.Column(db.Integer, default=0)
    cpq=db.Column(db.Integer, default=0)



    def __repr__(self):
        return "Gruppo ('{self.id}')"


class Marshal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    licenza = db.Column(db.Integer, nullable=False)
    acrilascio = db.Column(db.String(100), nullable=False)
    acrinnovo = db.Column(db.String(100), nullable=False)
    anno = db.Column(db.Integer, nullable=False)
    qualifica = db.Column(db.String(30), nullable=False)
    cognome = db.Column(db.String(100), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    datanascita = db.Column(db.String(100), nullable=False)
    luogonascita = db.Column(db.String(100))
    email = db.Column(db.String(120))
    flaltraq = db.Column(db.Integer, nullable=False, default=0)
    gruppi = db.relationship('Gruppo', secondary=linksgm, backref='componenti', lazy=True)

    def __repr__(self):
        return "Marshal('{self.id}', '{self.nome}', '{self.cognome}')"

class Routine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    note = db.Column(db.String(200), nullable=True)
    activities = db.relationship('Activity', secondary=linksar, backref='using', lazy=True)
    race_id = db.Column(db.Integer, db.ForeignKey('race.id'), nullable=False)
    gruppi = db.relationship('Gruppo', secondary=linksgr, backref='rts', lazy=True)
    req = db.Column(db.Integer, nullable=True)
    tot = db.Column(db.Integer, nullable=True)
    totcp = db.Column(db.Integer, nullable=True)
    totcpp = db.Column(db.Integer, nullable=True)
    totcpq = db.Column(db.Integer, nullable=True)
    avgd = db.Column(db.Interval, nullable=True)


    def __repr__(self):
        return "Routine('{self.id}')"

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_file = db.Column(db.String(20), nullable=True)
    tipo = db.Column(db.String(30), nullable=False)
    inizio = db.Column(db.DateTime, nullable=False)
    causale = db.Column(db.String(30), nullable=True)
    note = db.Column(db.String(200), nullable=True)
    race_id = db.Column(db.Integer, db.ForeignKey('race.id'), nullable=False)
    gruppi = db.relationship('Gruppo', secondary=linksgp, backref='payed', lazy=True)

    def __repr__(self):
        return "Payment('{self.id}')"









