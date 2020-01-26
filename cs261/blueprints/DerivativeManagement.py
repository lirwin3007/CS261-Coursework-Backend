# Third party imports
from flask import Blueprint, request, jsonify

# Local application imports
from cs261.modules import DerivativeManagement

# Instantiate new blueprint
DerivativeManagementBlueprint = Blueprint('derivativeManagement',
                                          __name__,
                                          url_prefix='/derivative-management')

# Routes
@DerivativeManagementBlueprint.route('/get-derivative/<derivativeId>')
def getDerviative(derivativeId):
    # Retreive derivative with the Id
    derivative = DerivativeManagement.getDerviative(derivativeId)

    return {} if derivative is None else derivative.as_dict()

@DerivativeManagementBlueprint.route('/get-derivatives')
def getDerviatives():
    # Retreive all derivatives from the database
    derivatives = DerivativeManagement.getDerviatives(True)

    return {"derivatives" : [d.as_dict() for d in derivatives]}

@DerivativeManagementBlueprint.route('/add-derivative', methods=['POST'])
def addDerivative():
    if request.is_json:
        # Extract json body from request
        derivative_json = request.get_json()
        print(derivative_json)
        # Create a new derivative using the json data
        DerivativeManagement.addDerivative(derivative_json)
