from flask import Flask

from backend.db import db
from backend.blueprints.derivative_blueprint import DerivativeBlueprint
from backend.blueprints.user_blueprint import UserBlueprint
from backend.blueprints.action_blueprint import ActionBlueprint
from backend.blueprints.report_blueprint import ReportBlueprint


class Application:

    @staticmethod
    def setup():
        app = Flask(__name__)
        app.app_context().push()

        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://derivatex_backend:qwerty123@localhost/derivatex'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_BINDS'] = {'external':
                                          'mysql+mysqlconnector://derivatex_backend:qwerty123@localhost/external'}
        app.config['SQLALCHEMY_POOL_SIZE'] = 100
        app.config['SQLALCHEMY_POOL_RECYCLE'] = 1

        db.init_app(app)
        db.create_all()

        app.register_blueprint(DerivativeBlueprint)
        app.register_blueprint(UserBlueprint)
        app.register_blueprint(ActionBlueprint)
        app.register_blueprint(ReportBlueprint)
        return app

    @staticmethod
    def run():
        app = Application.setup()
        app.run()

    @staticmethod
    def get_app():
        app = Application.setup()
        return app
