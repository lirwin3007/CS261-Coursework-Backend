# Third party imports
from flask import Blueprint, abort

# Local application imports
from cs261.DerivatexModels import *
from cs261.modules.DerivativeManagement import DerivativeManagement

# Instantiate new blueprint
DerivativeManagementBlueprint = Blueprint('derivativeManagement',
                                          __name__,
                                          url_prefix='/derivative-management')

# Instantiate module
DerivativeManagementModule = DerivativeManagement()

# Routes
@DerivativeManagementBlueprint.route('/example-route/<exampleParam>')
def exampleRoute(exampleParam):
    return DerivativeManagementModule.exampleFunction(exampleParam)
