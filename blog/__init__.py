from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from blog.config import Config


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'races.login'
login_manager.login_message_category = 'info'
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    db.drop_all.__init__(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from blog.races.routes import races
    from blog.main.routes import main
    from blog.activities.routes import activities
    from blog.groups.routes import groups


    #from blog.errors.handlers import errors

    db.create_all(app=app)

    app.register_blueprint(races)
    app.register_blueprint(main)
    app.register_blueprint(activities)
    app.register_blueprint(groups)
    #app.register_blueprint(errors)



    return app

