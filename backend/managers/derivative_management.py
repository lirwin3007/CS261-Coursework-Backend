# Local application imports
from backend.derivatex_models import Derivative, Action, ActionType
from backend.db import db


def getDerivative(derivative_id):
    # Query database for the derivative
    return Derivative.query.filter_by(deleted=False, id=derivative_id).first()


def addDerivative(derivative, user_id):
    # Add the derivative to the database session
    db.session.add(derivative)
    db.session.flush()

    # Add corrosponding user action to the database session
    action = Action(derivative_id=derivative.id, user_id=user_id, type=ActionType.ADD)
    db.session.add(action)
    db.session.flush()


def updateDerivative(derivative, user_id, updates):
    # Apply and log all updates to the derivative
    update_log = []
    for attribute, new_value in updates.items():
        # Restrict updatable attributes
        if not hasattr(derivative, attribute) or attribute in ['id', 'deleted', 'modified']:
            continue

        # Retrieve the current value
        old_value = getattr(derivative, attribute)

        # Perform update
        setattr(derivative, attribute, new_value)

        # Log update
        update_log.append({
            'attribute': attribute,
            'old_value': old_value,
            'new_value': new_value
        })

    # Register the derivative updates and corrosponding user action to the database session
    action = Action(derivative_id=derivative.id, user_id=user_id, type=ActionType.UPDATE, update_info=update_log)
    db.session.add(action)
    db.session.add(derivative)
    db.session.flush()

    # Return the update log
    return update_log


def deleteDerivative(derivative, user_id):
    # The derivative is already flagged as deleted, return
    if derivative.deleted:
        return

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
