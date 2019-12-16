from flask import render_template, request, Blueprint
from blog.models import Post, Travel

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    travels = Travel.query.order_by(Travel.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', travels=travels)


@main.route("/about")
def about():
    page = request.args.get('page', 1, type=int)
    travels = Travel.query.order_by(Travel.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('about.html', travels=travels)


