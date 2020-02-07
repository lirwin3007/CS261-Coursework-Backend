# Third party imports
from flask import Blueprint

# Local application imports
# You can import database models with 'from backend.derivatex_models import Derivative, User, Action'
from backend.managers.action_management import exampleFunction

# Instantiate new blueprint
ActionBlueprint = Blueprint('actionManagement',
                            __name__,
                            url_prefix='/action-management')


# Routes
@ActionBlueprint.route('/example-route/<exampleParam>')
def exampleRoute(exampleParam):
    return exampleFunction(exampleParam)
