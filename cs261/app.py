from flask import Flask

from cs261.blueprints.DerivativeManagement import DerivativeManagementBlueprint


class Blueprint:

    @staticmethod
    def run():
        app = Flask(__name__)
        app.register_blueprint(DerivativeManagementBlueprint)
        app.run(host='127.0.0.1')
