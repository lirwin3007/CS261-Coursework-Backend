from flask import Flask

from cs261.blueprints.DerivativeManagement import DerivativeManagementBlueprint


class Application:

    @staticmethod
    def setup():
        app = Flask(__name__)

        app.register_blueprint(DerivativeManagementBlueprint)
        return app

    @staticmethod
    def run():
        app = Application.setup()
        app.run()

    @staticmethod
    def get_app():
        app = Application.setup()
        return app
