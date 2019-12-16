from sqlalchemy.orm import relationship

from blog import db, login_manager
from datetime import datetime
from flask_login import UserMixin
from flask import current_app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Travel(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    destination = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    budget = db.Column(db.String(100), nullable=False)
    participants = db.Column(db.String(2), nullable=False)
    duration = db.Column(db.String(2), nullable=False)
    description = db.Column(db.String(200), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return "Travel('{self.destination}', '{self.date_posted}')"

class Post(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return "Post('{self.title}', '{self.date_posted}')"


class User(db.Model, UserMixin):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    idCard = db.Column(db.String(9), unique=True, nullable=False)
    #viaggi = db.relationship("Travel", backref='creator',)
    #posts = db.relationship('Post', backref='author')

    def __repr__(self):
        return "User('{self.username}', '{self.email}', '{self.image_file}')"

