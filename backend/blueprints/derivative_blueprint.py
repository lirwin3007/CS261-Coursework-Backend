# Third party imports
from flask import Blueprint, abort, jsonify, request
from sqlalchemy.exc import IntegrityError

# Local application imports
from backend.managers import derivative_management
from backend.managers import user_management
from backend.managers import derivative_validation
from backend.derivatex_models import Derivative
from backend.db import db
from backend.util import AbsoluteDerivativeException

# Instantiate new blueprint
DerivativeBlueprint = Blueprint('derivativeManagement',
                                __name__,
                                url_prefix='/derivative-management')


# Routes
@DerivativeBlueprint.route('/get-derivative/<derivative_id>')
def getDerivative(derivative_id):

        # Get derivative from database
        derivative = derivative_management.getDerivative(derivative_id)

        # Verify derivative exists
        if derivative is None:
            return abort(404, f'derivative with id {derivative_id} not found')

        # Make response
        return jsonify(derivative=derivative)



@DerivativeBlueprint.route('/add-derivative', methods=['POST'])
def addDerivative():

    if derivative_validation.isValidDerivative(request):

        try:

            body = request.get_json()
            user_id = body.get('user_id')

            derivative = Derivative(**body.get('derivative'))
            derivative_management.addDerivative(derivative, user_id)

        except IntegrityError as e:
            return abort(400, f'invalid derivative data: {e.orig}')
        except Exception:
            return abort(400, 'invalid derivative data')

    else:
        return abort(400, 'invalid derivative')

    # Commit addition to database
    db.session.commit()

    # Make response
    return jsonify(id=derivative.id)


@DerivativeBlueprint.route('/delete-derivative/<derivative_id>', methods=['DELETE'])
def deleteDerivative(derivative_id):

    if derivative_validation.isValidDerivative(request):

        body = request.get_json()
        user_id = body.get('user_id')

        # Retreive derivative from database
        derivative = derivative_management.getDerivative(derivative_id)

        # Verify derivative exists
        if derivative is None:
            return abort(404, f'derivative id {derivative_id} does not exist')

        # Delete the derivative
        try:
            derivative_management.deleteDerivative(derivative, user_id)
        except AbsoluteDerivativeException:
            return abort(400, 'derivative is absolute, deletion denied')

        # Commit the deletion
        db.session.commit()

        # Return a 204, no content
        return '', 204
    else:
        return abort(400, "MYEROR")


@DerivativeBlueprint.route('/update-derivative/<derivative_id>', methods=['POST'])
def updateDerivative(derivative_id):

    if derivative_validation.isValidDerivative(request):

        body = request.get_json()

        user_id = body.get('user_id')
        # Obtain updates
        updates = body.get('updates')

        # Retreive the specified derivative
        derivative = derivative_management.getDerivative(derivative_id)

        # Verify derivative exists
        if derivative is None:
            return abort(404, f'derivative id {derivative_id} does not exist')

        # Update the derivative
        try:
            update_log = derivative_management.updateDerivative(derivative, user_id, updates)
        except AbsoluteDerivativeException:
            return abort(400, 'derivative is absolute, update denied')

        # If no updates were made to the derivative, abort
        if not update_log:
            return abort(400, 'no valid updates')

        # Validate the updated derivative
        # if invalid derivative:
        #     return abort(418)

        # Commit the derivative updates to the database
        db.session.commit()

        # Make response
        return jsonify(update_log=update_log)


@DerivativeBlueprint.route('/index-derivatives')
def indexDerivatives():
    # Determine body from request
    try:
        body = derivative_validation.getJSON(request);

        # Determine page parameters
        page_size = max(body.get('page_size') or 15, 1)
        page_number = request.args.get('page_number', default=0, type=int)

        # Index derivatives
        derivatives, page_count = derivative_management.indexDerivatives(body,
                                                                     page_size,
                                                                     page_number)

        # Make response
        return jsonify(page_count=page_count, derivatives=[d.id for d in derivatives])
    except Exception:
        return abort(400, 'invalid derivative')
