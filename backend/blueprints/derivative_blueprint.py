# Third party imports
from flask import Blueprint, abort, jsonify, request

# Local application imports
from backend.managers import derivative_management
from backend.derivatex_models import Derivative

# Instantiate new blueprint
DerivativeBlueprint = Blueprint('derivativeManagement',
                                __name__,
                                url_prefix='/derivative-management')


# Routes
@DerivativeBlueprint.route('/get-derivative/<derivativeId>')
def getDerivative(derivativeId):
    # Get derivative from database
    derivative = derivative_management.getDerivative(derivativeId)
    # Make response
    return derivative.as_dict() if derivative is not None else abort(404)


@DerivativeBlueprint.route('/add-derivative', methods=['POST'])
def addDerivative():
    # Verify request
    if not request.data or not request.is_json:
        return abort(400)

    # Extract json body from request
    body = request.get_json()

    # Validate the json body
    # if invalid body:
    #     return flask.abort(400)

    # Extract user_id and create derivative object
    user_id = body.get('user_id')
    derivative = Derivative(**body.get('derivative'))

    # Add derivative to database
    added = derivative_management.addDerivative(derivative, user_id)

    # Make response
    return jsonify(id=derivative.id) if added else abort(400)


@DerivativeBlueprint.route('/update-derivative/<derivativeId>', methods=['POST'])
def updateDerivative(derivativeId):
    # Verify request
    if not request.data or not request.is_json:
        return abort(400)

    # Extract json body from request
    body = request.get_json()

    # Validate the json body
    # if invalid body:
    #     return flask.abort(400)

    # Extract user_id and updates
    user_id = body.get('user_id')
    updates = body.get('updates')

    # Retreive the specified derivative
    derivative = derivative_management.getDerivative(derivativeId)
    if derivative is None:
        return abort(404)

    # Update the derivative
    updated = derivative_management.updateDerivative(derivative, user_id, updates)

    # Make response
    return jsonify(updates) if updated else abort(400)


@DerivativeBlueprint.route('/delete-derivative/<derivativeId>', methods=['POST'])
def deleteDerivative(derivativeId):
    # Verify request
    if not request.data or not request.is_json:
        return abort(400)

    # Obtatin user_id
    body = request.get_json()
    user_id = body.get('user_id')
    if user_id is None:
        return abort(400)

    # Retreive the specified derivative
    derivative = derivative_management.getDerivative(derivativeId)
    if derivative is None:
        return abort(404)

    # Delete the derivative
    derivative_management.deleteDerivative(derivative, user_id)

    # Return a 204, no content
    return '', 204


@DerivativeBlueprint.route('/index-derivatives')
def indexDerivatives():
    # Retreive form
    form_dict = request.form.to_dict()

    # Determine filters
    filters = []

    # Determine page parameters
    page_size = form_dict.get('page_size') or 15
    page_number = form_dict.get('page_number') or 0

    # Index derivatives
    derivatives, page_count = derivative_management.indexDerivatives(filters, page_size, page_number)

    # Make response
    return jsonify(page_count=page_count, derivatives=[d.id for d in derivatives])
