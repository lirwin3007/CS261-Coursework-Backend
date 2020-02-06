from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from cs261.Models import db
from cs261.blueprints.DerivativeManagement import DerivativeManagementBlueprint
from cs261.blueprints.UserManagement import UserManagementBlueprint
from cs261.blueprints.ActionManagement import ActionManagementBlueprint


class Application:

    @staticmethod
    def setup():
        app = Flask(__name__)
        app.app_context().push()

        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://derivatex_backend:qwerty123@localhost/derivatex'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_BINDS'] = {'external': 'mysql+mysqlconnector://derivatex_backend:qwerty123@localhost/external'}

        db.init_app(app)
        db.create_all()

        app.register_blueprint(DerivativeManagementBlueprint)
        app.register_blueprint(UserManagementBlueprint)
        app.register_blueprint(ActionManagementBlueprint)
        return app

    @staticmethod
    def run():
        app = Application.setup()
        app.run()

    @staticmethod
    def get_app():
        app = Application.setup()
        return app
