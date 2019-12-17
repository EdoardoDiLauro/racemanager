
from blog import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    idCard = db.Column(db.String(9), unique=True, nullable=False)
    travels = db.relationship('Travel', backref='creator', lazy=True)
    bookings = db.relationship('Booking', backref='customer', lazy=True)
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='commenter', lazy=True)




    def __repr__(self):
        return "User('{self.username}', '{self.email}', '{self.image_file}')"

class Travel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    image_file = db.Column(db.String(20))
    budget = db.Column(db.String(100), nullable=False)
    available = db.Column(db.Integer, nullable=False)
    participants = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.String(2), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    posts = db.relationship('Post', backref='trip', lazy=True)
    bookings = db.relationship('Booking', backref='trip', lazy=True)


    def __repr__(self):
        return "Travel('{self.destination}', '{self.date_posted}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    image_file = db.Column(db.String(20))
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    travel_id = db.Column(db.Integer, db.ForeignKey('travel.id'))
    comments = db.relationship('Comment', backref='topic', lazy=True)



    def __repr__(self):
        return "Post('{self.title}', '{self.date_posted}')"


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    travel_id = db.Column(db.Integer, db.ForeignKey('travel.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_booked = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return "Booking('{self.id}', '{self.date_booked}')"


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_commented = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __repr__(self):
        return "Comment('{self.id}', '{self.date_commented}')"





