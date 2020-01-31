# Third party imports
from flask import Blueprint, request, abort

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

    # The given derivative does not exist, return a 404
    if derivative is None:
        return abort(404)

    # Construct dictionary from derivative attributes
    request = derivative.as_dict()

    # Append underlying price, notional value and action history
    underlying_price = 0.0
    request['underlying_price'] = underlying_price
    request['notional_value'] = underlying_price * derivative.quantity
    request['actions'] = []

    # Return request
    return request

@DerivativeManagementBlueprint.route('/add-derivative', methods=['POST'])
def addDerivative():
    if not request.is_json:
        return abort(400)

    # Extract json body from reques
    body = request.get_json()

    # TODO: if incomplete json body: return flask.abort(400)

    # Create a new derivative using the json data
    derivative = DerivativeManagement.addDerivative(body['derivative'], body['user_id'])

    # Return the id of the new derivative to the client
    return {'id' : derivative.id}

@DerivativeManagementBlueprint.route('/delete-derivative/<derivativeId>')
def deleteDerviative(derivativeId):
    pass
