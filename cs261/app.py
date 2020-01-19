from flask import Flask

from cs261.blueprints.DerivativeManagement import DerivativeManagementBlueprint


class Blueprint:

    @staticmethod
    def setup():
        app = Flask(__name__)
        app.register_blueprint(DerivativeManagementBlueprint)
        return app

    @staticmethod
    def run():
        app = Blueprint.setup()
        app.run()

    @staticmethod
    def get_app():
        app = Blueprint.setup()
        return app
