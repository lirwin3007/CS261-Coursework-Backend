# Third party imports
from flask import Blueprint, request, abort

# Local application imports
from cs261 import DerivatexModels
from cs261.application import db

# Instantiate new blueprint
DerivativeManagementBlueprint = Blueprint('derivativeManagement',
                                          __name__,
                                          url_prefix='/derivative-management')


# Routes
@DerivativeManagementBlueprint.route('/get-derivative/<derivativeId>')
def getDerviative(derivativeId):
    # Retreive the specified derivative
    derivative = DerivatexModels.Derivative.query.get(derivativeId)

    # The given derivative does not exist, respond with a 404
    if derivative is None:
        return abort(404)

    # Construct dictionary from derivative attributes
    request = derivative.as_dict()

    # Append underlying price, notional value and action history
    underlying_price = 0.0
    action_history = DerivatexModels.Action.query.filter_by(derivative_id=derivativeId).all()

    request['underlying_price'] = underlying_price
    request['notional_value'] = underlying_price * derivative.quantity
    request['actions'] = [action.id for action in action_history]

    # Return request
    return request

@DerivativeManagementBlueprint.route('/add-derivative', methods=['POST'])
def addDerivative():
    if not request.is_json:
        return abort(400)

    # Extract json body from reques
    body = request.get_json()

    # Extract user_id and create derivative object
    user_id = body['user_id']
    derivative = DerivatexModels.Derivative(**body['derivative'])

    # Validate the derivative
    # if invalid derivative:
    #     return flask.abort(400)

    # Add the derivative and corrosponding user action to the database
    action = DerivatexModels.Action(derivative_id=derivative.id, user_id=user_id, type="ADD")
    db.session.add(action)
    db.session.add(derivative)
    db.session.commit()

    # Return the id of the new derivative to the client
    return {'id' : derivative.id}


@DerivativeManagementBlueprint.route('/update-derivative', methods=['POST'])
def updateDerivative():
    return ('', 204)

@DerivativeManagementBlueprint.route('/delete-derivative/<derivativeId>')
def deleteDerviative(derivativeId):
    # Retreive the specified derivative
    derivative = DerivatexModels.Derivative.query.get(derivativeId)

    # The given derivative does not exist, respond with a 404
    if derivative is None:
        return abort(404)

    # Delete the derivative
    # db.session.delete(derivative)

    # Register the user deleting the derivative
    action = DerivatexModels.Action(derivative_id=derivativeId, user_id=1, type="DELETE")
    db.session.add(action)

    # Commit changes to the database
    db.session.commit()

    # Return a 204. No Content
    return ('', 204)

@DerivativeManagementBlueprint.route('/index-derivatives')
def indexDerviatives():
    data_form = request.form.to_dict()
    filters = set()

    # Determine filters
    if 'buying_party' in data_form:
        filters.add(DerivatexModels.Derivative.buying_party == data_form["buying_party"])
    if 'selling_party' in data_form:
        filters.add(DerivatexModels.Derivative.selling_party == data_form["selling_party"])
    if 'asset' in data_form:
        filters.add(DerivatexModels.Derivative.asset == data_form["asset"])
    if 'min_strike_price' in data_form:
        filters.add(DerivatexModels.Derivative.strike_price >= data_form["min_strike_price"])
    if 'max_strike_price' in data_form:
        filters.add(DerivatexModels.Derivative.strike_price <= data_form["max_strike_price"])
    if 'min_notional_value' in data_form:
        filters.add(DerivatexModels.Derivative.notional_value >= data_form["min_notional_value"])
    if 'max_notional_value' in data_form:
        filters.add(DerivatexModels.Derivative.notional_value <= data_form["max_notional_value"])

    # Create base query
    query = DerivatexModels.Derivative.query

    # Apply all the filters
    for filter in filters:
        query = query.filter(filter)

    # Order the query
    query = query.order_by(DerivatexModels.Derivative.id)

    # Paginate the query
    page_size = 10
    page_number = 2
    page_count = query.count() // page_size + 1
    query = query.limit(page_size).offset(page_size * page_number)

    # Execute query
    derivatives = query.all()

    # Return JSON response
    return {"ids":[d.id for d in derivatives]}
