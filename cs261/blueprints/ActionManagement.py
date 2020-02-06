# Third party imports
from flask import Blueprint

# Local application imports
# You can import database models with 'from cs261.DerivatexModels import Derivative, User, Action'
from cs261.modules.ActionManagement import ActionManagement

# Instantiate new blueprint
ActionManagementBlueprint = Blueprint('actionManagement',
                                      __name__,
                                      url_prefix='/action-management')

# Instantiate module
ActionManagementModule = ActionManagement()

# Routes
@ActionManagementBlueprint.route('/example-route/<exampleParam>')
def exampleRoute(exampleParam):
    return ActionManagementModule.exampleFunction(exampleParam)
