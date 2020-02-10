# Third party imports
from flask import Blueprint, abort, jsonify, request

# Local application imports
from backend.managers import derivative_management
from backend.derivatex_models import Derivative
from backend.db import db

# Instantiate new blueprint
DerivativeBlueprint = Blueprint('derivativeManagement',
                                __name__,
                                url_prefix='/derivative-management')


# Routes
@DerivativeBlueprint.route('/get-derivative/<derivative_id>')
def getDerivative(derivative_id):
    # Get derivative from database
    derivative = derivative_management.getDerivative(derivative_id)
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
    derivative_management.addDerivative(derivative, user_id)

    # Validate the new derivative
    # if invalid derivative:
    #     abort(418)

    # Commit the derivative addition to the database
    db.session.commit()

    # Make response
    return jsonify(id=derivative.id)


@DerivativeBlueprint.route('/update-derivative/<derivative_id>', methods=['POST'])
def updateDerivative(derivative_id):
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
    derivative = derivative_management.getDerivative(derivative_id)
    if derivative is None:
        return abort(404)

    # Update the derivative
    update_log = derivative_management.updateDerivative(derivative, user_id, updates)

    # Validate the updated derivative
    # if invalid derivative:
    #     abort(418)

    # Commit the derivative updates to the database
    db.session.commit()

    # Make response
    return jsonify(update_log=update_log)


@DerivativeBlueprint.route('/delete-derivative/<derivative_id>', methods=['DELETE'])
def deleteDerivative(derivative_id):
    # Verify request
    if not request.data or not request.is_json:
        return abort(400)

    # Obtatin user_id
    body = request.get_json()
    user_id = body.get('user_id')
    if user_id is None:
        return abort(400)

    # Retreive the specified derivative
    derivative = derivative_management.getDerivative(derivative_id)
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
