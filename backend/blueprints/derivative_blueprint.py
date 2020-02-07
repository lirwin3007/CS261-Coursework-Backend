# Third party imports
from flask import Blueprint

# Local application imports
# You can import database models with 'from backend.derivatex_models import Derivative, User, Action'
from backend.managers.derivative_management import exampleFunction

# Instantiate new blueprint
DerivativeBlueprint = Blueprint('derivativeManagement',
                                __name__,
                                url_prefix='/derivative-management')


# Routes
@DerivativeBlueprint.route('/example-route/<exampleParam>')
def exampleRoute(exampleParam):
    return exampleFunction(exampleParam)
