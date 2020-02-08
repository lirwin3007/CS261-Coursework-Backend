# Local application imports
from backend.derivatex_models import Derivative, Action, ActionType
from backend.db import db


def getDerivative(derivativeId):
    # Query database for the derivative
    return Derivative.query.filter_by(deleted=False, id=derivativeId).first()


def addDerivative(derivative, user_id):
    # Validate the derivative
    # if invalid derivative:
    #     return False

    # Add the derivative and corrosponding user action to the database
    action = Action(derivative_id=derivative.id, user_id=user_id, type=ActionType.ADD)
    db.session.add(action)
    db.session.add(derivative)
    db.session.commit()

    # Return success
    return True


def updateDerivative(derivative, user_id, updates):
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
    #     return False

    # Register the derivative updates and corrosponding user action to the database
    action = Action(derivative_id=derivative.id, user_id=user_id, type=ActionType.UPDATE, update_info=update_log)
    db.session.add(action)
    db.session.add(derivative)
    db.session.commit()

    # Replace the update request with the update log
    updates.clear()
    updates['updates'] = update_log

    # Return success
    return True


def deleteDerivative(derivative, user_id):
    # Mark the derivative as deleted
    derivative.deleted = True

    # Register the user deleting the derivative
    action = Action(derivative_id=derivative.id, user_id=user_id, type=ActionType.DELETE)
    db.session.add(derivative)
    db.session.add(action)
    db.session.commit()


def indexDerivatives(filters, page_size, page_number):
    # Create base query
    query = Derivative.query

    # # Apply all query filters
    # for filter in filters:
    #     query = query.filter(filter)

    # # Order the query
    # if order_key is not None:
    #     query = query.order_by(order_key)

    # Paginate the query
    page_count = query.count() // page_size + 1
    query = query.limit(page_size).offset(page_size * page_number)

    # Execute query
    derivatives = query.all()

    # Return derivatives and page count
    return derivatives, page_count
