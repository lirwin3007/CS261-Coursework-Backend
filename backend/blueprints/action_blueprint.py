# Third party imports
from flask import Blueprint

# Local application imports
# You can import database models with 'from backend.derivatex_models import Derivative, User, Action'
from backend.managers import action_management

# Instantiate new blueprint
ActionBlueprint = Blueprint('actionManagement',
                            __name__,
                            url_prefix='/action-management')


# Routes
@ActionBlueprint.route('/example-route/<exampleParam>')
def exampleRoute(exampleParam):
    return action_management.exampleFunction(exampleParam)
