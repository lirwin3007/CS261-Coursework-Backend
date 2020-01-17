# Third party imports
from flask import Blueprint

# Local application imports
from cs261.modules.DerivativeManagement import DerivativeManagement

# Instantiate new blueprint
DerivativeManagementBlueprint = Blueprint('derivativeManagement',
                                          __name__,
                                          url_prefix='/derivative-management')

# Instantiate module
derivativeManagementModule = DerivativeManagement()

# Routes
@DerivativeManagementBlueprint.route('/get-derivative/<derivativeId>')
def getDerviative(derivativeId):
    return derivativeManagementModule.getDerviative(derivativeId)
