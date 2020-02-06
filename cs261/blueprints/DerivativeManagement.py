# Third party imports
from flask import Blueprint, request, abort

# Local application imports
from cs261.DerivatexModels import *
from cs261.application import db

# Instantiate new blueprint
DerivativeManagementBlueprint = Blueprint('derivativeManagement',
                                          __name__,
                                          url_prefix='/derivative-management')


# Routes
@DerivativeManagementBlueprint.route('/get-derivative/<derivativeId>')
def getDerivative(derivativeId):
    # Retreive the specified derivative
    derivative = Derivative.query.get(derivativeId)

    # The given derivative does not exist, respond with a 404
    if derivative is None:
        return abort(404)

    # Construct dictionary from derivative attributes
    request = derivative.as_dict()

    # Append underlying price, notional value and action history
    underlying_price = 0.0
    action_history = Action.query.filter_by(derivative_id=derivativeId).all()

    request['underlying_price'] = underlying_price
    request['notional_value'] = underlying_price * derivative.quantity
    request['actions'] = [action.id for action in action_history]

    # Return request
    return request

@DerivativeManagementBlueprint.route('/add-derivative', methods=['POST'])
def addDerivative():
    # Verify request type
    if not request.is_json:
        return abort(400)

    # Extract json body from request
    body = request.get_json()

    # Validate the body
    # if invalid body:
    #     return flask.abort(400)

    # Extract user_id and create derivative object
    user_id = body.get('user_id')
    derivative = Derivative(**body.get('derivative'))

    # Validate the derivative
    # if invalid derivative:
    #     return flask.abort(400)

    # Add the derivative and corrosponding user action to the database
    action = Action(derivative_id=derivative.id, user_id=user_id, type="ADD")
    db.session.add(action)
    db.session.add(derivative)
    db.session.commit()

    # Return the id of the new derivative to the client
    return {'id' : derivative.id}


@DerivativeManagementBlueprint.route('/update-derivative/<derivativeId>', methods=['POST'])
def updateDerivative(derivativeId):
    # Verify request type
    if not request.is_json:
        return abort(400)

    # Extract json body from request
    body = request.get_json()

    # Validate the body
    # if invalid body:
    #     return flask.abort(400)

    # Retreive the specified derivative
    derivative = Derivative.query.get(derivativeId)

    # The given derivative does not exist, respond with a 404
    if derivative is None:
        return abort(404)

    # Extract user_id and create derivative object
    user_id = body.get('user_id')
    updates = body.get('updates')

    # Apply and log all updates to the derivative
    update_log = []
    for attribute, new_value in updates.items():
        old_value = getattr(derivative, attribute)

        # Perform update
        setattr(derivative, attribute, new_value)

        # Log update
        update_log.append({
            "attribute": attribute,
            "old_value": old_value,
            "new_value": new_value
        })

    # Validate the updated derivative
    # if invalid derivative:
    #     return flask.abort(400)

    # Register the derivative updates and corrosponding user action to the database
    action = Action(derivative_id=derivativeId, user_id=user_id, type="UPDATE", update_log=update_log)
    db.session.add(action)
    db.session.add(derivative)
    db.session.commit()

    return {"updates": update_log}

@DerivativeManagementBlueprint.route('/delete-derivative/<derivativeId>')
def deleteDerivative(derivativeId):
    # Retreive the specified derivative
    derivative = Derivative.query.get(derivativeId)

    # The given derivative does not exist, respond with a 404
    if derivative is None:
        return abort(404)

    # TODO: potentially set deleted derivative flag

    # Register the user deleting the derivative
    action = Action(derivative_id=derivativeId, user_id=1, type="DELETE")
    db.session.add(action)

    # Commit changes to the database
    db.session.commit()

    # Return a 204. No Content
    return ('', 204)

@DerivativeManagementBlueprint.route('/index-derivatives')
def indexDerivatives():
    data_form = request.form.to_dict()

    # Determine query filters
    query_filters = set()
    if 'buying_party' in data_form:
        query_filters.add(Derivative.buying_party == data_form["buying_party"])
    if 'selling_party' in data_form:
        query_filters.add(Derivative.selling_party == data_form["selling_party"])
    if 'asset' in data_form:
        query_filters.add(Derivative.asset == data_form["asset"])
    if 'min_strike_price' in data_form:
        query_filters.add(Derivative.strike_price >= data_form["min_strike_price"])
    if 'max_strike_price' in data_form:
        query_filters.add(Derivative.strike_price <= data_form["max_strike_price"])

    # Determine order key
    order_key = None
    if 'order_key' in data_form:
        if data_form.get('order_key') == 'buying_party':
            order_key = Derivative.buying_party   # Note: this will sort by company ID not company name
        elif data_form.get('order_key') == 'selling_party':
            order_key = Derivative.selling_party
        elif data_form.get('order_key') == 'strike_price':
            order_key = Derivative.strike_price

    # Create base query
    query = Derivative.query

    # Apply all query filters
    for filter in query_filters:
        query = query.filter(filter)

    # Order the query
    if order_key is not None:
        query = query.order_by(order_key)

    # Paginate the query
    page_size = data_form.get('page_size') or 15
    page_number = data_form.get('page_number') or 0
    page_count = query.count() // page_size + 1
    query = query.limit(page_size).offset(page_size * page_number)

    # Execute query
    derivatives = query.all()

    # Post-query filters
    # if 'min_strike_price' in data_form:
    #     pass # derivatives.filter()
    # if 'max_strike_price' in data_form:
    #     pass
    # if 'search_term' in data_form:
    #     pass

    # Post-query ordering
    # if 'order_key' in data_form and order_key is None:
    #     pass # derivatives.sort()

    # Return JSON response
    return {
        "page_count" : page_count,
        "ids" : [d.id for d in derivatives]
    }
