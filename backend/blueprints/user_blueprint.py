# Third party imports
from flask import Blueprint

# Local application imports
# You can import database models with 'from backend.derivatex_models import Derivative, User, Action'
from backend.managers import user_management

# Instantiate new blueprint
UserBlueprint = Blueprint('userManagement',
                          __name__,
                          url_prefix='/user-management')


# Routes
@UserBlueprint.route('/example-route/<exampleParam>')
def exampleRoute(exampleParam):
    return user_management.exampleFunction(exampleParam)
