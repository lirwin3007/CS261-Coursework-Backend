# Third party imports
from flask import Blueprint, abort, jsonify, request
from sqlalchemy.exc import IntegrityError

# Local application imports
from backend.managers import derivative_management
from backend.managers import user_management
from backend.derivatex_models import Derivative
from backend.db import db
from backend import utils
from backend.utils import AbsoluteDerivativeException

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
    # Verify request
    if not request.data or not request.is_json:
        return abort(400, 'empty request body')

    # Retreive json body from request
    body = request.get_json()
    user_id = body.get('user_id')

    # Validate user id
    if user_management.getUser(user_id) is None:
        return abort(404, f'user id {user_id} does not exist')

    try:
        # Create derivative and add it to database
        derivative = Derivative(**body.get('derivative'))
        derivative_management.addDerivative(derivative, user_id)

    except IntegrityError as e:
        return abort(400, f'invalid derivative data: {e.orig}')
    except Exception as e:
        return abort(400, f'invalid derivative data: {e}')

    # Commit addition to database
    db.session.commit()

    # Make response
    return jsonify(id=derivative.id)


@DerivativeBlueprint.route('/delete-derivative/<derivative_id>', methods=['DELETE'])
def deleteDerivative(derivative_id):
    # Verify request
    if not request.data or not request.is_json:
        return abort(400, 'empty request body')

    # Retreive json body from request
    body = request.get_json()
    user_id = body.get('user_id')

    # Verify user exists
    if user_management.getUser(user_id) is None:
        return abort(404, f'user id {user_id} does not exist')

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


@DerivativeBlueprint.route('/update-derivative/<derivative_id>', methods=['POST'])
def updateDerivative(derivative_id):
    # Verify request
    if not request.data or not request.is_json:
        return abort(400, 'empty request body')

    # Retreive json body from request
    body = request.get_json()
    user_id = body.get('user_id')
    tree_id = body.get('tree_id')

    # Verify user exists
    if user_management.getUser(user_id) is None:
        return abort(404, f'user id {user_id} does not exist')

    # Obtain updates
    updates = body.get('updates')

    # Retreive the specified derivative
    derivative = derivative_management.getDerivative(derivative_id)

    # Verify derivative exists
    if derivative is None:
        return abort(404, f'derivative id {derivative_id} does not exist')

    # Update the derivative
    try:
        update_log = derivative_management.updateDerivative(derivative, user_id, tree_id, updates)
    except AbsoluteDerivativeException:
        return abort(400, 'derivative is absolute, update denied')

    # If no updates were made to the derivative, abort
    if not update_log:
        return abort(400, 'no valid updates')

    # Commit the derivative updates to the database
    db.session.commit()

    # Make response
    return jsonify(update_log=update_log)


@DerivativeBlueprint.route('/index-derivatives')
def indexDerivatives():
    # Determine index page parameters
    page_size = request.args.get('page_size', default=15, type=int)
    page_number = request.args.get('page_number', default=0, type=int)

    # Determine index order
    order_key = request.args.get('order_key', default='id', type=str)
    reverse_order = request.args.get('reverse_order', default=False, type=bool)

    # Determine index filters
    search_term = request.args.get('search_term', default=None, type=str)
    min_notional = request.args.get('min_notional_value', default=None, type=float)
    max_notional = request.args.get('max_notional_value', default=None, type=float)
    min_strike = request.args.get('min_strike_price', default=None, type=float)
    max_strike = request.args.get('max_strike_price', default=None, type=float)
    min_maturity = request.args.get('min_maturity_date', default=None, type=utils.to_date)
    max_maturity = request.args.get('max_maturity_date', default=None, type=utils.to_date)
    min_trade_date = request.args.get('min_date_of_trade', default=None, type=utils.to_date)
    max_trade_date = request.args.get('max_date_of_trade', default=None, type=utils.to_date)
    buyers = request.args.getlist('buyers', type=str)
    sellers = request.args.getlist('sellers', type=str)
    assets = request.args.getlist('assets', type=str)
    show_deleted = request.args.get('show_deleted', default=False, type=bool)
    hide_not_deleted = request.args.get('hide_not_deleted', default=False, type=bool)

    # Index derivatives
    derivatives, page_count = derivative_management.indexDerivatives(
        page_size, page_number, order_key, reverse_order, search_term,
        min_notional, max_notional, min_strike, max_strike, min_maturity,
        max_maturity, min_trade_date, max_trade_date, buyers, sellers, assets,
        show_deleted, hide_not_deleted)

    # Make response
    return jsonify(page_count=page_count, derivatives=[d.id for d in derivatives])
