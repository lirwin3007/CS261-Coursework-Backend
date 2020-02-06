# Third party imports
from flask import Blueprint

# Local application imports
# You can import database models with 'from cs261.DerivatexModels import Derivative, User, Action'
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
