# Third party imports
from flask import Blueprint, abort

# Local application imports
from cs261.DerivatexModels import *
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
