from flask import Flask

from backend.db import db
from backend.blueprints.derivative_blueprint import DerivativeBlueprint
from backend.blueprints.user_blueprint import UserBlueprint
from backend.blueprints.action_blueprint import ActionBlueprint
from backend.blueprints.report_blueprint import ReportBlueprint


class Application:

    @staticmethod
    def setupApp(configObj):
        # Create flask app
        app = Flask(__name__)
        app.app_context().push()
        app.config.from_object(configObj)

        # Bind SQLAlchemy database engine to flask app
        db.init_app(app)
        # Create all schemas defined by ORM models
        db.create_all()

        # Register route blueprints
        app.register_blueprint(DerivativeBlueprint)
        app.register_blueprint(UserBlueprint)
        app.register_blueprint(ActionBlueprint)
        app.register_blueprint(ReportBlueprint)

        # Return app reference
        return app

    @staticmethod
    def runDevServer():
        # Setup app
        app = Application.setupApp(Config)
        # Run flask development server
        app.run()

    @staticmethod
    def getProductionApp():
        # Setup and return app
        return Application.setupApp(Config)

    @staticmethod
    def getTestApp():
        # Setup and return app
        return Application.setupApp(Config)


class Config:
    DEBUG = False
    TESTING = False
    JSON_SORT_KEYS = True
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://derivatex_backend:qwerty123@localhost/derivatex'
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_BINDS = {
        'external': 'mysql+mysqlconnector://derivatex_backend:qwerty123@localhost/external'
    }
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 100, 'pool_recycle': 1, 'pool_pre_ping': True
    }
