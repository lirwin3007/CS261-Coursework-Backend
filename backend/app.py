# Third party imports
from flask import Flask
from flask_cors import CORS
from flask_apscheduler import APScheduler

# Local application imports
from backend.db import db
from backend.blueprints.derivative_blueprint import DerivativeBlueprint
from backend.blueprints.user_blueprint import UserBlueprint
from backend.blueprints.action_blueprint import ActionBlueprint
from backend.blueprints.report_blueprint import ReportBlueprint
from backend.managers import report_management
from backend.utils import MyJSONEncoder


class Application:

    @staticmethod
    def setupApp(config):
        # Create flask app
        app = Flask(__name__)
        app.app_context().push()
        app.config.from_object(config)

        # Create scheduler for generating reports
        scheduler = APScheduler()
        scheduler.init_app(app)
        scheduler.start()
        app.apscheduler.add_job(func=report_management.generateAllReports,
                                trigger='cron', hour='23', minute='59', id='j1')

        # Allow cross-origin requests
        CORS(app)

        # Bind SQLAlchemy database engine to flask app
        db.init_app(app)
        # Extend the default json encoder to support ORM models
        app.json_encoder = MyJSONEncoder
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
    def getProductionApp():
        # Setup and return app
        return Application.setupApp(BaseConfig)

    @staticmethod
    def runDevServer():
        # Setup app
        app = Application.setupApp(DevConfig)
        # Run flask development server
        app.run()

    @staticmethod
    def getTestApp():
        # Setup and return app
        return Application.setupApp(TestConfig)


class BaseConfig:
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


class DevConfig(BaseConfig):
    DEBUG = True


class TestConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://derivatex_backend:qwerty123@localhost/test'
