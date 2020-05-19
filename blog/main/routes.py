from flask import render_template, request, Blueprint

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():

    return render_template('home.html')


@main.route("/faq")
def faq():
    return render_template('faq.html',)


